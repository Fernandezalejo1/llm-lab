#!/usr/bin/env python3
"""Diagnóstico 3: batch multi-ejemplo con padding (vision_pad) + forward con
grad (training mode) + backward, reproduciendo las condiciones del loss GRPO
que crashearon con 'unspecified launch failure' en torch.embedding."""
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rag"))
from run_code_rag import BASE_SYS  # noqa: E402

MERGED = "D:/ai-lab/fase2/merged_qwen35_attn"

t0 = time.time()
model, tokenizer = FastLanguageModel.from_pretrained(
    MERGED, load_in_4bit=True, max_seq_length=4096, device_map="auto"
)
print(f"cargado en {time.time()-t0:.0f}s", flush=True)
print("pad_token_id:", tokenizer.pad_token_id, "| pad_token:", tokenizer.pad_token, flush=True)

# 3 prompts de distinta longitud para forzar padding
prompts = [
    [{"role": "system", "content": BASE_SYS},
     {"role": "user", "content": "Escribí una función Python que sume dos números. Respondé solo con el bloque ```python```."}],
    [{"role": "system", "content": BASE_SYS},
     {"role": "user", "content": "El motor de conciliación de contabilia traduce el estado interno de cada movimiento bancario (reconciled, applied, identified, pending, unidentified, error, duplicate) al estado del resumen. Escribí `reconcile_status(status: str) -> str`. Respondé solo con el bloque ```python```."}],
    [{"role": "system", "content": BASE_SYS},
     {"role": "user", "content": "El motor de contabilia genera el resumen de una conciliación. Escribí la función que lo implementa. Respondé solo con el bloque ```python```."}],
]

from trl.data_utils import maybe_apply_chat_template
texts = [maybe_apply_chat_template({"prompt": p}, tokenizer)["prompt"] for p in prompts]
print("largo prompts:", [len(t) for t in texts], flush=True)

enc = tokenizer(text=texts, return_tensors="pt", padding=True, pad_to_multiple_of=8).to("cuda:0")
ids = enc.input_ids
print("batch shape:", tuple(ids.shape), flush=True)
print("pad ids usados:", int((ids == tokenizer.pad_token_id).sum()), "| max id:", int(ids.max()), flush=True)

import torch
# forward training-mode + backward, con input_ids que contienen vision_pad
print("forward train+backward...", flush=True)
model.train()
try:
    # activamos grad sobre el embedding de entrada como aproximación mínima del loss
    emb = model.get_input_embeddings()(ids)
    loss = emb.float().sum()
    loss.backward()
    print("OK backward | loss:", float(loss), flush=True)
except Exception as e:
    print("CRASH train:", type(e).__name__, str(e)[:400], flush=True)

# Ahora la vía completa: logits del modelo con logits_to_keep y loss causal
print("\nforward causal completo + backward...", flush=True)
try:
    labels = ids.clone()
    labels[labels == tokenizer.pad_token_id] = -100
    out = model(input_ids=ids, attention_mask=enc.attention_mask, labels=labels, use_cache=False)
    loss = out.loss
    loss.backward()
    print("OK | loss:", float(loss), flush=True)
except Exception as e:
    print("CRASH causal:", type(e).__name__, str(e)[:400], flush=True)

print("VRAM pico: %.2f GB" % (torch.cuda.max_memory_allocated() / 1e9), flush=True)