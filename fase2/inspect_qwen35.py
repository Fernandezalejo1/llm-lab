#!/usr/bin/env python3
"""Inspecciona Qwen3.5-9B-Base cargado 4-bit: estructura de módulos de cada
capa para identificar las 8 capas Gated Attention (blanco del LoRA) vs las 24
Gated DeltaNet. Layout esperado: 8 x (3 DeltaNet + 1 Attention).
"""
import os
import sys
import json

os.environ.setdefault("HF_HOME", "D:/ai-lab/hf_cache")
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

sys.path.insert(0, "sitecustomize")
import sitecustomize  # noqa: E402  (monkeypatch accelerate DTensor)

from unsloth import FastLanguageModel  # noqa: E402

print("Cargando Qwen3.5-9B-Base 4-bit...", flush=True)
model, tokenizer = FastLanguageModel.from_pretrained(
    "D:/ai-lab/models/qwen35-9b-base",
    load_in_4bit=True,
    max_seq_length=4096,
    device_map="auto",
)
print("Modelo cargado.", flush=True)

layers = model.model.layers
print(f"Total capas: {len(layers)}", flush=True)
classes = {}
for i, layer in enumerate(layers):
    attn = layer.self_attn
    cls = type(attn).__name__
    classes.setdefault(cls, []).append(i)

for cls, idxs in classes.items():
    print(f"  {cls}: {len(idxs)} capas -> {idxs[:3]}{'...' if len(idxs) > 3 else ''}", flush=True)

# Muestro los nombres de parámetros de una capa attention y una deltanet
att_cls, del_cls = None, None
for cls, idxs in classes.items():
    if len(idxs) == 8 and "ttent" in cls:
        att_cls = cls
    elif len(idxs) == 24:
        del_cls = cls
print(f"\natt_cls={att_cls} del_cls={del_cls}", flush=True)

if att_cls:
    i = classes[att_cls][0]
    print(f"\n--- Capa Gated Attention (layer {i}) params ---", flush=True)
    for name, _ in layers[i].self_attn.named_parameters():
        print("  ", name, flush=True)
if del_cls:
    i = classes[del_cls][0]
    print(f"\n--- Capa Gated DeltaNet (layer {i}) params ---", flush=True)
    for name, _ in layers[i].self_attn.named_parameters():
        print("  ", name, flush=True)

json.dump(
    {"classes": {k: v for k, v in classes.items()}, "att_cls": att_cls, "del_cls": del_cls},
    open("D:/ai-lab/fase2/qwen35_arch.json", "w"),
    indent=2,
)
print("\nGuardado: fase2/qwen35_arch.json", flush=True)