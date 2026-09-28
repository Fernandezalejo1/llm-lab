#!/usr/bin/env python3
"""Merge del adapter QLoRA attention-only al modelo base (Unsloth canónico).

save_pretrained_merged(..., save_method="merged_16bit") -> modelo bf16 con
los pesos fusionados, listo para GGUF ("Needed for llama.cpp / GGUF" según
la propia doc de Unsloth).

Este es el paso 1 del pipeline merge -> GGUF:
  out_qwen35_attn/  (adapter LoRA)  ->  merged_qwen35_attn/  (bf16 completo)
"""
import os
import sys

os.environ.setdefault("HF_HOME", "D:/ai-lab/hf_cache")
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecustomize  # noqa: E402

from unsloth import FastLanguageModel  # noqa: E402

BASE = "D:/ai-lab/models/qwen35-9b-base"
ADAPTER = "D:/ai-lab/fase2/out_qwen35_attn"
OUT = "D:/ai-lab/fase2/merged_qwen35_attn"

print("Cargando adapter (resuelve base desde adapter_config)...", flush=True)
model, tokenizer = FastLanguageModel.from_pretrained(
    ADAPTER,
    load_in_4bit=True,
    max_seq_length=4096,
    device_map="auto",
)

print("Merging adapter (merged_16bit)...", flush=True)
model.save_pretrained_merged(
    OUT,
    tokenizer=tokenizer,
    save_method="merged_16bit",
)
print("LISTO:", OUT, flush=True)