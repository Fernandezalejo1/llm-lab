#!/usr/bin/env python3
"""Diagnóstico 5: ¿rompe el forward multimodal si input_ids contiene tokens de
visión (<|vision_start|> 248053 .. <|video_pad|> 248057) sin pixel_values?
Ese es el único escenario no probado del crash del smoke GRPO."""
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
# batch pequeño de prompts reales + completions con tokens de visión insertados
texts = [
    "El motor de conciliación traduce estados. Escribí la función. ```python\ndef reconcile_status(status: str) -> str:\n    pass\n```",
    "Otro prompt para el batch. ```python\ndef main():\n    return 1\n```",
]
enc = tokenizer(text=texts, return_tensors="pt", padding=True).to("cuda:0")
ids = enc.input_ids
print("ids pre:", tuple(ids.shape), "max:", int(ids.max()), flush=True)

def try_forward(name, ids_in):
    try:
        with torch.no_grad():
            out = model(input_ids=ids_in, attention_mask=torch.ones_like(ids_in))
        print(f"{name}: OK | logits {tuple(out.logits.shape)}", flush=True)
    except Exception as e:
        print(f"{name}: CRASH | {type(e).__name__}: {str(e)[:300]}", flush=True)

# 1) baseline sin tokens de visión
try_forward("baseline", ids)

# 2) con cada token de visión del rango 248053..248057 insertado en distintas posiciones
VISION_TOKENS = {248053: "vision_start", 248054: "vision_end", 248055: "vision_pad",
                 248056: "image_pad", 248057: "video_pad"}
for tid, tname in VISION_TOKENS.items():
    x = ids.clone()
    x[0, 3:8] = tid  # insertar 5 tokens de visión en medio del texto
    try_forward(f"vision {tname} ({tid})", x)

# 3) con el token eos 248044/248069 repetido
for tid, tname in [(248044, "endoftext"), (248068, "thinking"), (248069, "response")]:
    x = ids.clone()
    x[0, 3:8] = tid
    try_forward(f"token {tname} ({tid})", x)

print("VRAM pico: %.2f GB" % (torch.cuda.max_memory_allocated() / 1e9), flush=True)