#!/usr/bin/env python3
"""QLoRA real de Fase 2: Qwen3.5-9B-Base, LoRA SOLO en las 8 capas
full-attention del híbrido (la DeltaNet queda congelada, paper 2026:
attention-only >= full-model con 5-10x menos params).

Mapa de arquitectura verificado (transformers 5.5):
  model.model.language_model.layers[0..31] (Qwen3_5DecoderLayer)
    - full_attention (capas 3,7,11,15,19,23,27,31): self_attn.Qwen3_5Attention
      → q_proj (out = heads*head_dim*2, gated), k_proj, v_proj, o_proj
    - linear_attention (resto): linear_attn.Qwen3_5GatedDeltaNet
      → in_proj_qkv / in_proj_a / in_proj_b / in_proj_z / out_proj / conv1d
  Los nombres q/k/v/o_proj SOLO existen en full-attention → el target
 _modules por nombre discrimina solo → 8 capas, nada más.

Uso:  python train_qwen35.py [--dry-run] [--epochs N] [--steps N]
  --dry-run: carga + aplica LoRA + cuenta parámetros entrenables y saltea
             el training (verificación de targeting sin quemar GPU).
"""
import argparse
import os
import sys
import time
import json

os.environ.setdefault("HF_HOME", "D:/ai-lab/hf_cache")
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecustomize  # noqa: E402  (monkeypatch accelerate DTensor del build ROCm Windows)

from datasets import load_dataset  # noqa: E402
from unsloth import FastLanguageModel  # noqa: E402
# ⚠️ unlsoth ANTES que trl: el lazy-import de transformers 5.5 necesita los
# patches de unsloth para resolver TrainingArguments etc. (sin eso: "Could
# not import module 'TrainingArguments'").
from trl import SFTConfig, SFTTrainer  # noqa: E402

MODEL_PATH = "D:/ai-lab/models/qwen35-9b-base"
DATASET = "D:/ai-lab/fase2/dataset_sft.jsonl"
OUT = "D:/ai-lab/fase2/out_qwen35_attn"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--epochs", type=float, default=2.0)
    ap.add_argument("--steps", type=int, default=None)
    args = ap.parse_args()

    print("=" * 60)
    print("Cargando Qwen3.5-9B-Base 4-bit + LoRA attention-only...", flush=True)
    t0 = time.time()
    model, tokenizer = FastLanguageModel.from_pretrained(
        MODEL_PATH,
        load_in_4bit=True,
        max_seq_length=4096,
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
    print(f"Modelo cargado y LoRA aplicado en {time.time() - t0:.0f}s", flush=True)

    # --- chequeo de targeting -------------------------------------------
    trainable = [n for n, p in model.named_parameters() if p.requires_grad]
    total_tr = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_all = sum(p.numel() for p in model.parameters())
    print(f"Parámetros entrenables: {total_tr:,} / {total_all:,} "
          f"({100 * total_tr / total_all:.3f}%)", flush=True)

    # rutas únicas: deberían ser self_attn de solo 8 capas
    layers_touched = sorted({int(n.split("layers.")[1].split(".")[0]) for n in trainable})
    mixed = [n for n in trainable if "linear_attn" in n]
    outside = [n for n in trainable if "language_model" not in n]
    print(f"Capas tocadas por LoRA: {layers_touched}", flush=True)
    if outside:
        print(f"  ⚠️ ALERTA: {len(outside)} módulos FUERA del text LM "
              f"(espejito de visión): {outside[:5]}", flush=True)
        trainable = [n for n in trainable if "language_model" in n]
    print(f"  (esperado [3, 7, 11, 15, 19, 23, 27, 31] — solo full-attention)", flush=True)
    if mixed:
        print(f"  ⚠️ ALERTA: {len(mixed)} módulos en linear_attn entrenándose: "
              f"{mixed[:3]}", flush=True)
    else:
        print("  ✅ Ningún módulo DeltaNet entrenándose.", flush=True)

    if args.dry_run:
        print("DRY-RUN: targeting verificado, saliendo sin entrenar.", flush=True)
        return

    # --- dataset --------------------------------------------------------
    ds = load_dataset("json", data_files=DATASET, split="train")
    print(f"Dataset: {len(ds)} ejemplos.", flush=True)
    ds = ds.map(lambda x: {
        "text": "Instrucción:\n" + x["instruction"] + "\n\nRespuesta:\n" + x["output"]
    }, remove_columns=["instruction", "output"])

    # --- trainer --------------------------------------------------------
    out = OUT if args.steps is None else OUT + "_short"
    cfg_kwargs = dict(
        output_dir=out,
        dataset_text_field="text",
        max_seq_length=4096,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        num_train_epochs=args.epochs,
        learning_rate=2e-4,
        lr_scheduler_type="linear",
        warmup_steps=4,
        weight_decay=0.01,
        logging_steps=2,
        save_steps=0,
        max_grad_norm=1.0,
        bf16=True,
        optim="adamw_8bit",
        seed=7,
        report_to=[],
        remove_unused_columns=False,
    )
    if args.steps is not None:
        cfg_kwargs["max_steps"] = args.steps
    cfg = SFTConfig(**cfg_kwargs)
    trainer = SFTTrainer(
        model=model,
        args=cfg,
        train_dataset=ds,
        tokenizer=tokenizer,
    )
    print("Training QLoRA real...", flush=True)
    trainer.train()

    print("Guardando adapter...", flush=True)
    trainer.model.save_pretrained(out)
    trainer.save_model(out)
    tokenizer.save_pretrained(out)

    # VRAM pico
    vram = 0
    try:
        import torch
        if torch.cuda.is_available():
            vram = torch.cuda.max_memory_allocated() / 1e9
    except Exception:
        pass
    print(f"VRAM pico: {vram:.2f} GB", flush=True)
    json.dump({"target_layers": layers_touched, "trainable": total_tr,
               "vram_peak_gb": vram}, open(out + "/train_meta.json", "w"), indent=2)
    print("LISTO.", flush=True)


if __name__ == "__main__":
    main()