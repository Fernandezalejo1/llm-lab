#!/usr/bin/env python3
"""Diagnóstico 2: reproducir EXACTAMENTE la vía del GRPO (processor multimodal +
chat template) generando con los defaults agresivos (temp 1.0/top_p 1.0) y ver
qué ids salen; y el forward del loss (logits_to_keep) para aislar el crash."""
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
TEXT_VOCAB_SIZE = 248320  # vocab_size del text-LM (model.language_model)

t0 = time.time()
model, tokenizer = FastLanguageModel.from_pretrained(
    MERGED, load_in_4bit=True, max_seq_length=2048, device_map="auto"
)
print(f"cargado en {time.time()-t0:.0f}s", flush=True)
print("processing class:", type(tokenizer).__name__, flush=True)

prompt = [{"role": "system", "content": BASE_SYS},
          {"role": "user", "content": "El motor de conciliación de contabilia traduce el estado interno de cada movimiento bancario (valores como reconciled, applied, identified, pending, unidentified, error, duplicate) al estado que figura en el resumen de conciliación, con un mapeo específico (hay estados que se agrupan en el mismo resumen y un default para lo desconocido). Escribí una función Python `reconcile_status(status: str) -> str` que implemente exactamente ese mapeo del motor. Respondé solo con el bloque ```python```."}]

# vía idéntica a trl: maybe_apply_chat_template -> str
from trl.data_utils import maybe_apply_chat_template
pt = maybe_apply_chat_template({"prompt": prompt}, tokenizer)["prompt"]
print("prompt str:", type(pt).__name__, len(pt), flush=True)

enc = tokenizer(text=pt, return_tensors="pt", padding=True).to("cuda:0")
print("input_ids shape:", tuple(enc.input_ids.shape), flush=True)
print("max id en prompt:", int(enc.input_ids.max()), flush=True)

import torch
gen = model.generate(
    input_ids=enc.input_ids,
    attention_mask=enc.attention_mask,
    max_new_tokens=200,
    temperature=1.0,
    top_p=1.0,
    do_sample=True,
    pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
    eos_token_id=tokenizer.eos_token_id,
)
ids = gen[0]
n_prompt = enc.input_ids.shape[1]
new_ids = ids[n_prompt:]
print("generados:", new_ids.shape[0], flush=True)
print("min id:", int(new_ids.min()), "| max id:", int(new_ids.max()), flush=True)
print(">=248320 (fuera text vocab):", int((new_ids >= TEXT_VOCAB_SIZE).sum()), flush=True)
if (new_ids >= TEXT_VOCAB_SIZE).any():
    print("  ids OOB:", [int(x) for x in new_ids[new_ids >= TEXT_VOCAB_SIZE]][:10], flush=True)
print("ids en rango vision 248053..248057:", int(((new_ids >= 248053) & (new_ids <= 248057)).sum()), flush=True)

# forward del loss GRPO: prompt+completion con logits_to_keep
cat_ids = torch.cat([enc.input_ids, new_ids.unsqueeze(0)], dim=1)
cat_mask = torch.ones_like(cat_ids)
ltk = new_ids.shape[0]
print("\nforward con logits_to_keep=", ltk, flush=True)
try:
    with torch.no_grad():
        out = model(input_ids=cat_ids, attention_mask=cat_mask, use_cache=False, logits_to_keep=ltk + 1)
    print("forward OK | logits:", tuple(out.logits.shape), flush=True)
except Exception as e:
    print("FORWARD CRASH:", type(e).__name__, str(e)[:300], flush=True)
print("VRAM pico: %.2f GB" % (torch.cuda.max_memory_allocated() / 1e9), flush=True)