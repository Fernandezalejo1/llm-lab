#!/usr/bin/env python3
"""Fase 3b: export a GGUF Q4_K_M del modelo RL-dense mergeado.

Paso 2 del pipeline RL2:  merged_qwen35_attn_rl2  ->  gguf_qwen35_attn_rl2

OJO: requiere PYTHONPATH=D:/ai-lab/fase2 para que el subproceso del converter
herede el sitecustomize (si no: AutoTokenizer no importa en mergekit).
"""
import os
import sys

os.environ.setdefault("HF_HOME", "D:/ai-lab/hf_cache")
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecustomize  # noqa: E402

from unsloth import FastLanguageModel  # noqa: E402

MERGED = "D:/ai-lab/fase2/merged_qwen35_attn_rl2"
GGUF_OUT = "D:/ai-lab/fase2/gguf_qwen35_attn_rl2"

print("Cargando modelo RL-dense mergeado (bf16)...", flush=True)
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