#!/usr/bin/env python3
"""Export a GGUF Q4_K_M del modelo fine-tuneado (atención-only).

Carga el modelo MERGEADO (safetensors bf16 ya fusionado por merge_gguf.py)
y lo convierte a GGUF vía Unsloth (save_pretrained_gguf) — mismo mecanismo
que usa el plan: merge -> GGUF, sin llama.cpp externo.

Nuevo modelo: local-qwen-custom (para Ollama import)
"""
import os
import sys

os.environ.setdefault("HF_HOME", "D:/ai-lab/hf_cache")
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecustomize  # noqa: E402

from unsloth import FastLanguageModel  # noqa: E402

MERGED = "D:/ai-lab/fase2/merged_qwen35_attn"
GGUF_OUT = "D:/ai-lab/fase2/gguf_qwen35_attn"

print("Cargando modelo mergeado (bf16)...", flush=True)
model, tokenizer = FastLanguageModel.from_pretrained(
    MERGED,
    max_seq_length=4096,
    device_map="auto",
)

print("Exportando GGUF q4_k_m...", flush=True)
model.save_pretrained_gguf(
    GGUF_OUT,
    tokenizer=tokenizer,
    quantization_method="q4_k_m",
)
print("LISTO:", GGUF_OUT, flush=True)