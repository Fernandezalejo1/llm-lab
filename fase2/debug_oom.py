#!/usr/bin/env python3
"""Diagnóstico 6: simular el forward+backward del loss GRPO con dimensiones
REALES (batch 4, secuencias ~2900 tokens, grad activos, sin no_grad).
Si falla con 'unspecified launch failure' -> es el OOM del conjunto."""
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HOME", "D:/ai-lab/hf_cache")
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecustomize  # noqa: E402
from unsloth import FastLanguageModel  # noqa: E402

MERGED = "D:/ai-lab/fase2/merged_qwen35_attn"

t0 = time.time()
model, tokenizer = FastLanguageModel.from_pretrained(
    MERGED, load_in_4bit=True, max_seq_length=4096, device_map="auto"
)
print(f"cargado en {time.time()-t0:.0f}s", flush=True)

import torch

# prompt real ~900 tok + completion simulada ~2000 tok => ~2900
texts = []
for i in range(4):
    texto = "El motor de conciliación de contabilia traduce cada estado interno del movimiento bancario " \
            "(reconciled, applied, identified, pending, unidentified, error, duplicate) al estado del resumen. " \
            "Escribí la función Python que implementa el mapeo. " + ("instrucción larga extra para llenar tokens " * 30 if i else "") \
            + "\n```python\ndef reconcile_status(status: str) -> str:\n    mapeo = {'reconciled':'ok'}\n    return mapeo.get(status, 'desconocido')\n```\n"
    texts.append(texto)

enc = tokenizer(text=texts, return_tensors="pt", padding=True, truncation=True, max_length=2900).to("cuda:0")
ids = enc.input_ids
print("batch shape:", tuple(ids.shape), flush=True)
if ids.shape[1] < 1000:
    # rellenar a ~2900 tokens para simular completions largas
    fill = ids[:, :1].repeat(1, 2900 - ids.shape[1])
    ids = torch.cat([ids, fill], dim=1)
    print("batch rellenado a:", tuple(ids.shape), flush=True)
mask = torch.ones_like(ids)

labels = ids.clone()
labels[mask == 0] = -100

print("forward+backward causal con grad (batch 4, ~2900 tok)...", flush=True)
model.train()
try:
    out = model(input_ids=ids, attention_mask=mask, labels=labels, use_cache=False)
    loss = out.loss
    print("loss:", float(loss), flush=True)
    loss.backward()
    print("BACKWARD OK", flush=True)
except Exception as e:
    print("CRASH:", type(e).__name__, str(e)[:500], flush=True)

print("VRAM pico: %.2f GB" % (torch.cuda.max_memory_allocated() / 1e9), flush=True)
print("VRAM resid: %.2f GB" % (torch.cuda.memory_reserved() / 1e9), flush=True)