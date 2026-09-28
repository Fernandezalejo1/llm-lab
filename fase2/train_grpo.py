#!/usr/bin/env python3
"""GRPO real de Fase 3: RL sobre los 7 tests del puente como reward VERIFICABLE.

Punto de partida: merged_qwen35_attn (bf16 con el SFT de Fase 2 fundido) en
4-bit + LoRA RL nuevo. Así el LoRA RL aprende deltas sobre el SFT completo y
la referencia KL (disable_adapter) ES el SFT → aislamos RL vs SFT.

Reward = verify_task(0/1) reusando los mismos tests del eval (el prompt del
dataset NO revela los criterios del dominio: solo la tarea; el reward conoce
los tests).

Formato del prompt: conversacional [system=BASE_SYS, user=tarea], el mismo que
la eval con Ollama (train == eval). trl aplica el chat template del tokenizer.

Uso:  python train_grpo.py [--dry-run] [--steps N] [--g G] [--lr X] [--out N]
  --dry-run: carga modelo+LoRA, arma dataset+reward, instancia el trainer
             (tokeniza y prepara todo) y sale sin entrenar.
"""
import argparse
import concurrent.futures as cf
import json
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("HF_HOME", "D:/ai-lab/hf_cache")
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ.setdefault("UNSLOTH_DISABLE_TRITON_OUTPUT_MARKERS", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecustomize  # noqa: E402  (shims distributed del build ROCm Windows)

# ⚠️ unsloth ANTES que trl; y PatchFastRL ANTES de tomar GRPOTrainer
from unsloth import FastLanguageModel, PatchFastRL  # noqa: E402
PatchFastRL("GRPO", FastLanguageModel)  # noqa: E402  (genera UnslothGRPOTrainer)
# La clase LIVE es la del submódulo (patcheada por unsloth); trl.__init__ pudo
# fijar la referencia vieja durante el import de PatchFastRL.
from trl.trainer.grpo_trainer import GRPOTrainer  # noqa: E402  (UnslothGRPOTrainer)
from trl import GRPOConfig  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rag"))
from run_code_rag import BASE_SYS, verify_task  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reward_score import verify_score  # noqa: E402  (reward denso: assert-coverage)

MERGED_BASE = "D:/ai-lab/fase2/merged_qwen35_attn"
CODE_TASKS = "D:/ai-lab/rag/code_tasks.jsonl"
OUT_Root = "D:/ai-lab/fase2/out_grpo"


def load_tasks():
    return [json.loads(l) for l in open(CODE_TASKS, encoding="utf-8") if l.strip()]


def completion_text(completion):
    """tolera formatos string y conversacional ([{role,content}...])."""
    if isinstance(completion, str):
        return completion
    if isinstance(completion, list):
        return "".join(m.get("content", "") for m in completion if isinstance(m, dict))
    return str(completion)


def make_reward(mode: str = "dense"):
    """Reward por completion usando los tests del puente (CPU, en paralelo).

    mode="binary": 0/1 pelado (verify_task, el reward de Fase 3).
    mode="dense":  assert-coverage continuo 0..1 (verify_score) — el mismo
    test, pero una respuesta que pasa 2/3 asserts recibe 0.66 en vez de 0.
    """

    use_dense = mode == "dense"

    def reward_fn(prompts, completions, completion_ids=None, **reward_kwargs):
        # En trl 0.24 el sampler repite cada prompt num_generations veces DENTRO
        # del batch (mini_repeat_count) -> prompts, completions y reward_kwargs
        # llegan alineados 1:1 (largo B*G).
        tasks = reward_kwargs.get("task", [])
        out = [0.0] * len(completions)

        def _check(k):
            task = tasks[k] if k < len(tasks) else None
            if task is None:
                return k, 0.0
            txt = completion_text(completions[k])
            with tempfile.TemporaryDirectory() as td:
                if use_dense:
                    r = verify_score(task, txt, Path(td))
                else:
                    ok, _err = verify_task(task, txt, Path(td))
                    r = 1.0 if ok else 0.0
            return k, r

        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            for k, r in ex.map(_check, range(len(completions))):
                out[k] = r
        return out

    return reward_fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--g", type=int, default=4, help="num_generations de GRPO")
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--out", default=OUT_Root)
    ap.add_argument("--max-comp", type=int, default=2048, help="max_completion_length")
    ap.add_argument("--seq", type=int, default=4096, help="max_seq_length")
    ap.add_argument("--temp", type=float, default=0.8, help="temperature de sampling GRPO")
    ap.add_argument("--reward", choices=["binary", "dense"], default="dense",
                    help="binary = verify_task 0/1 (Fase 3); "
                         "dense = assert-coverage 0..1 (Fase 3b)")
    ap.add_argument("--adapter", default=None,
                    help="cargar un LoRA ya entrenado (checkpoint o adapter) y "
                         "continuar desde ahí en vez de partir del base SFT "
                         "(resume de un run interrumpido)")
    args = ap.parse_args()

    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print("=" * 60, flush=True)
    t0 = time.time()
    if args.adapter:
        print(f"RESUME: cargando LoRA existente {args.adapter} (continúa el entrenamiento)...", flush=True)
        model, tokenizer = FastLanguageModel.from_pretrained(
            args.adapter,
            load_in_4bit=True,
            max_seq_length=args.seq,
            device_map="auto",
        )
    else:
        print(f"Cargando merged SFT (bf16 → 4-bit) + LoRA RL attention-only...", flush=True)
        model, tokenizer = FastLanguageModel.from_pretrained(
            MERGED_BASE,
            load_in_4bit=True,
            max_seq_length=args.seq,
            device_map="auto",
        )
        model = FastLanguageModel.get_peft_model(
            model,
            r=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_alpha=16,
            lora_dropout=0,
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=7,
        )
    print(f"Modelo + LoRA RL en {time.time() - t0:.0f}s", flush=True)

    trainable = [n for n, p in model.named_parameters() if p.requires_grad]
    outside = [n for n in trainable if "language_model" not in n]
    if outside:
        print(f"  ⚠️ ALERTA {len(outside)} módulos fuera del text LM: {outside[:5]}", flush=True)
    else:
        print(f"  ✅ LoRA RL solo dentro del text LM ({len(trainable)} capas apuntadas)", flush=True)

    print(f"\nEsperando que el trainer parcheado sea UnslothGRPOTrainer: "
          f"{GRPOTrainer.__module__}", flush=True)

    tasks = load_tasks()
    reward_label = ("assert-coverage 0..1" if args.reward == "dense"
                    else "verify_task 0/1")
    print(f"Dataset: {len(tasks)} tareas puente (reward = {reward_label}).", flush=True)

    ds = [
        {
            "prompt": [
                {"role": "system", "content": BASE_SYS},
                {"role": "user", "content": t["prompt"]},
            ],
            "task": t,  # llega a la reward func vía reward_kwargs
        }
        for t in tasks
    ]

    reward_fn = make_reward(args.reward)

    out = args.out
    cfg_kwargs = dict(
        output_dir=out,
        per_device_train_batch_size=1,
        num_generations=args.g,
        max_completion_length=args.max_comp,
        temperature=args.temp,
        max_steps=args.steps if args.steps is not None else 28,
        learning_rate=args.lr,
        lr_scheduler_type="linear",
        warmup_steps=2,
        weight_decay=0.0,
        logging_steps=1,
        save_strategy="steps",
        save_steps=7,
        save_only_model=True,
        bf16=True,
        optim="adamw_8bit",
        seed=7,
        report_to=[],
        remove_unused_columns=False,
    )
    cfg = GRPOConfig(**cfg_kwargs)
    print(f"GRPOConfig: {cfg}", flush=True)

    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=reward_fn,
        args=cfg,
        train_dataset=ds,
    )
    print(f"Trainer instanciado OK ({time.time() - t0:.0f}s desde el arranque).", flush=True)

    for i in range(min(3, len(ds))):
        pt = trainer.train_dataset[i]["prompt"]
        enc = tokenizer.apply_chat_template(pt, add_generation_prompt=True)
        print(f"\n-- ej {i}: {len(enc)} tokens | prompt conv: {pt[0]['role']}/{pt[1]['role']}", flush=True)
        print(f"   user[:80]: {pt[1]['content'][:80]!r}", flush=True)

    if args.dry_run:
        print("\nDRY-RUN: dataset+reward+trainer listos, saliendo sin entrenar.", flush=True)
        return

    print("\nTraining GRPO (RL sobre los tests del puente)...", flush=True)

    # callback para registrar reward por step en rewards.jsonl + VRAM
    from transformers import TrainerCallback

    class _RewardLog(TrainerCallback):
        def on_log(self, args, state, control, logs=None, **kw):
            logs = logs or {}
            import torch
            vram_cur = 0.0
            vram_peak = 0.0
            try:
                if torch.cuda.is_available():
                    vram_cur = torch.cuda.memory_allocated() / 1e9
                    vram_peak = torch.cuda.max_memory_allocated() / 1e9
            except Exception:
                pass
            row = {"step": state.global_step,
                   "vram_gb": round(vram_cur, 2),
                   "vram_peak_gb": round(vram_peak, 2),
                   "logs": {k: v for k, v in logs.items()
                            if isinstance(v, (int, float))}}
            with open(Path(out) / "rewards.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(row, default=str) + "\n")
            print(f"\n[step {state.global_step}] vram_cur={vram_cur:.2f} GB "
                  f"peak={vram_peak:.2f} GB  rewards={logs.get('reward', 'n/a')}", flush=True)

        def on_step_begin(self, args, state, control, **kw):
            import torch
            try:
                if torch.cuda.is_available():
                    torch.cuda.reset_peak_memory_stats()
                    print(f"[inicio step {state.global_step}] vram_cur="
                          f"{torch.cuda.memory_allocated() / 1e9:.2f} GB", flush=True)
            except Exception:
                pass

        def on_step_end(self, args, state, control, **kw):
            import torch
            try:
                if torch.cuda.is_available():
                    print(f"[fin step {state.global_step}] vram_cur="
                          f"{torch.cuda.memory_allocated() / 1e9:.2f} GB", flush=True)
            except Exception:
                pass

    trainer.add_callback(_RewardLog())
    try:
        trainer.train()
    except Exception as e:
        import torch
        print("\n===== ERROR EN TRAINING =====", flush=True)
        print(f"{type(e).__name__}: {str(e)[:300]}", flush=True)
        try:
            if torch.cuda.is_available():
                print(f"vram_cur={torch.cuda.memory_allocated() / 1e9:.2f} GB "
                      f"peak={torch.cuda.max_memory_allocated() / 1e9:.2f} GB", flush=True)
                print(torch.cuda.memory_summary()[:2500], flush=True)
        except Exception as e2:
            print(f"(sin memory_summary: {e2})", flush=True)
        raise

    print("Guardando adapter RL...", flush=True)
    trainer.model.save_pretrained(out + "/adapter_rl")
    tokenizer.save_pretrained(out + "/adapter_rl")

    vram = 0.0
    try:
        import torch
        if torch.cuda.is_available():
            vram = torch.cuda.max_memory_allocated() / 1e9
    except Exception:
        pass
    json.dump({"base": MERGED_BASE, "num_generations": args.g, "lr": args.lr,
               "steps": args.steps, "vram_peak_gb": vram},
              open(out + "/train_meta.json", "w"), indent=2)
    print(f"VRAM pico: {vram:.2f} GB", flush=True)
    print("LISTO.", flush=True)


if __name__ == "__main__":
    main()