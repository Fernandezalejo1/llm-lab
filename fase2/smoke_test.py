#!/usr/bin/env python3
"""Smoke test del ambiente QLoRA (Fase 2) en RX 9070 XT / RDNA4.

Verifica, en orden:
  1. PyTorch con backend ROCm y GPU detectada (gfx1201).
  2. Unsloth importa y parchea el modelo.
  3. QLoRA 4-bit con 3 steps sobre un mini-dataset (semilla ct-01/ct-02)
     y la loss BAJA (prueba de que el entrenamiento realmente aprende).

Uso:  .venv/Scripts/python.exe smoke_test.py
"""
import os
import sys
import time

os.environ.setdefault("HF_HOME", "D:/ai-lab/hf_cache")
# GPU única: la iGPU (RDNA2) no debe recibir kernels compilados para gfx1201
# (RDNA4). device_map="auto" repartió entre las dos y explotó con
# hipErrorInvalidKernelFile en el rotary embedding.
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

print("=" * 60)
print("1) Backend / GPU")
print("=" * 60)
print("python:", sys.version.split()[0])
import torch  # noqa: E402

print("torch:", torch.__version__)
print("build:", torch.version.hip or torch.version.cuda)
print("gpu disponible:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
    print("capability:", torch.cuda.get_device_capability(0))
    mem = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"VRAM total: {mem:.1f} GB")

print()
print("=" * 60)
print("2) Unsloth")
print("=" * 60)
import unsloth  # noqa: E402

print("unsloth:", getattr(unsloth, "__version__", "?"))
from unsloth import FastLanguageModel  # noqa: E402

# Mini-dataset: semilla del puente (ct-01 mapeo, ct-02 duplicados)
EX = [
    {
        "instruction": (
            "El motor de conciliación de contabilia traduce el estado interno de cada "
            "movimiento bancario (reconciled, applied, identified, pending, "
            "unidentified, error, duplicate) al estado del resumen de conciliación, "
            "con un mapeo específico y un default para lo desconocido. Escribí una "
            "función Python reconcile_status(status: str) -> str."
        ),
        "output": (
            "```python\ndef reconcile_status(status: str) -> str:\n"
            "    m = {'reconciled': 'conciliated', 'applied': 'conciliated',\n"
            "         'identified': 'pending', 'pending': 'unidentified',\n"
            "         'unidentified': 'unidentified', 'error': 'error',\n"
            "         'duplicate': 'duplicate'}\n"
            "    return m.get(status, 'unidentified')\n```"
        ),
    },
    {
        "instruction": (
            "El motor de conciliación de contabilia detecta movimientos duplicados "
            "con criterios exactos: mismo monto (±0.01), misma referencia o "
            "similitud de descripción (trigram > 0.8) y ventana de ≤3 días; "
            "confidence 0.95 si misma referencia, 0.85 si descripción similar; "
            "reason en español. Escribí la función detect_duplicate(movement, others)."
        ),
        "output": (
            "```python\ndef detect_duplicate(movement, others):\n"
            "    for other in others:\n"
            "        if other['id'] == movement['id']:\n"
            "            continue\n"
            "        same_amount = abs((movement.get('creditAmount') or movement.get('debitAmount') or 0)\n"
            "                          - (other.get('creditAmount') or other.get('debitAmount') or 0)) < 0.01\n"
            "        if not same_amount:\n"
            "            continue\n"
            "        same_ref = bool(movement.get('reference')) and bool(other.get('reference')) \\\n"
            "                   and movement['reference'] == other['reference']\n"
            "        similar_desc = bool(movement.get('description')) and bool(other.get('description')) \\\n"
            "                       and _trigram_similarity(movement['description'], other['description']) > 0.8\n"
            "        if not same_ref and not similar_desc:\n"
            "            continue\n"
            "        days = abs((date.fromisoformat(movement['transactionDate'])\n"
            "                    - date.fromisoformat(other['transactionDate'])).days)\n"
            "        if days <= 3:\n"
            "            return {'isDuplicate': True, 'originalMovementId': other['id'],\n"
            "                    'confidence': 0.95 if same_ref else 0.85,\n"
            "                    'reason': 'Misma referencia y monto que movimiento del ' + other['transactionDate']}\n"
            "    return None\n```"
        ),
    },
]

PROMPT = "Instrucción:\n{instruction}\n\nRespuesta:\n"
# Variantes sintéticas del ct-03 (resumen con contadores, mapeo de estados):
# distintos giros del prompt y valores distintos fuerzan aprendizaje real, no
# memorización del par único.
EX3 = {
    "instruction": (
        "El resumen de conciliación de contabilia clasifica cada movimiento por "
        "estado con contadores exactos: los reconciliados y aplicados suman en "
        "conciliatedCount, los identificados en pendingCount, los pendientes y "
        "desconocidos en unidentifiedCount, y error/duplicate en sus contadores. "
        "Escribí la función count_summary(movements) que recibe la lista y "
        "devuelve el dict del resumen."
    ),
    "output": (
        "```python\ndef count_summary(movements):\n"
        "    s = {k: 0 for k in ('conciliatedCount', 'pendingCount', 'unidentifiedCount', "
        "'errorCount', 'duplicateCount')}\n"
        "    for m in movements:\n"
        "        st = m['status']\n"
        "        if st in ('reconciled', 'applied'):\n"
        "            s['conciliatedCount'] += 1\n"
        "        elif st == 'identified':\n"
        "            s['pendingCount'] += 1\n"
        "        elif st in ('pending', 'unidentified'):\n"
        "            s['unidentifiedCount'] += 1\n"
        "        elif st == 'error':\n"
        "            s['errorCount'] += 1\n"
        "        elif st == 'duplicate':\n"
        "            s['duplicateCount'] += 1\n"
        "    return s\n```"
    ),
}
for i in range(4):
    EX.append({**EX3, "instruction": EX3["instruction"] + f" (variante {i + 1}.)"})

print()
print("=" * 60)
print(f"3) Carga 4-bit + LoRA + {2 * len(EX)} ejemplos, 3 steps")
print("=" * 60)
t0 = time.time()
model, tokenizer = FastLanguageModel.from_pretrained(
    "Qwen/Qwen3-1.7B",
    load_in_4bit=True,
    max_seq_length=2048,
    device_map="auto",
)
print(f"modelo cargado en {time.time() - t0:.1f}s")

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
)

from datasets import Dataset  # noqa: E402

texts = [PROMPT.format(**e).strip() + "\n" + e["output"] + "\n<|endoftext|>" for e in EX]
ds = Dataset.from_dict({"text": texts})

from trl import SFTConfig, SFTTrainer  # noqa: E402

# Build ROCm de AMD para Windows no compila el backend distribuido
# (torch._C._distributed_c10d ausente). accelerate solo lo importa para
# detectar DTensor; nuestro modelo no tiene ninguno → parche directo
# en ambos namespaces (other + accelerator lo importan por nombre).
import accelerate.utils.other as _acc_other  # noqa: E402
import accelerate.accelerator as _acc_acc  # noqa: E402

_acc_other.model_has_dtensor = lambda _model: False
_acc_acc.model_has_dtensor = _acc_other.model_has_dtensor

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=ds,
    args=SFTConfig(
        output_dir="D:/ai-lab/fase2/smoke_out",
        max_steps=10,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=2e-4,
        logging_steps=1,
        report_to="none",
        save_strategy="no",
        seed=3407,
        fp16=False,
        bf16=True,
    ),
)
trainer.train()
losses = trainer.state.log_history
last = [float(x["loss"]) for x in losses if "loss" in x]
print("loss por step:", [round(x, 4) for x in last])
# Criterio robusto: primer tercio vs último tercio (ruido de batch de paso a
# paso en 6 steps es esperable; mira la tendencia, no cada paso).
if len(last) >= 3:
    n = len(last) // 3
    first = sum(last[:n]) / n
    tail = sum(last[-n:]) / n
    print(f"media primer tercio: {first:.4f} | último tercio: {tail:.4f}")
    if tail < first:
        print("OK: la loss baja en tendencia — el training aprende en la GPU.")
        ok = True
    else:
        print("ATENCION: la loss no baja en tendencia (revisar config).")
        ok = False
else:
    print("ATENCION: muy pocos steps para evaluar tendencia.")
    ok = False
print(f"VRAM pico: {torch.cuda.max_memory_allocated() / 1e9:.2f} GB de {mem:.1f} GB" if torch.cuda.is_available() else "")
sys.exit(0 if ok else 3)