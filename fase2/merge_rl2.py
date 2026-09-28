#!/usr/bin/env python3
"""Fase 3b: merge del adapter RL-dense (checkpoint resume) al SFT fundido.

Paso 1 del pipeline RL2:  out_grpo_dense_resume/adapter_rl  ->  merged_qwen35_attn_rl2
"""
import os
import sys

os.environ.setdefault("HF_HOME", "D:/ai-lab/hf_cache")
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecustomize  # noqa: E402

from unsloth import FastLanguageModel  # noqa: E402

ADAPTER = "D:/ai-lab/fase2/out_grpo_dense_resume/adapter_rl"
OUT = "D:/ai-lab/fase2/merged_qwen35_attn_rl2"

print("Cargando adapter RL-dense (resuelve base = merged_qwen35_attn)...", flush=True)
model, tokenizer = FastLanguageModel.from_pretrained(
    ADAPTER,
    load_in_4bit=True,
    max_seq_length=4096,
    device_map="auto",
)

print("Merging adapter RL-dense (merged_16bit)...", flush=True)
model.save_pretrained_merged(
    OUT,
    tokenizer=tokenizer,
    save_method="merged_16bit",
)
print("LISTO:", OUT, flush=True)