#!/usr/bin/env python3
"""Diagnóstico 4: reproducir el forward del loss GRPO (línea ~2056 del
UnslothGRPOTrainer) con los prompts REALES y un hook en el embedding del
text-LM que imprime min/max de input_ids antes del kernel (para atrapar el
índice OOB en Python, sin depender del device-side assert)."""
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
from unsloth import PatchFastRL  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rag"))
from run_code_rag import BASE_SYS  # noqa: E402
import json  # noqa: E402

MERGED = "D:/ai-lab/fase2/merged_qwen35_attn"

t0 = time.time()
model, tokenizer = FastLanguageModel.from_pretrained(
    MERGED, load_in_4bit=True, max_seq_length=4096, device_map="auto"
)
print(f"cargado en {time.time()-t0:.0f}s", flush=True)
print("pad_token_id:", tokenizer.pad_token_id, "| pad_token:", tokenizer.pad_token, flush=True)

# dataset real (7 prompts del puente, conversacional como en RL)
tasks = [json.loads(l) for l in open("../rag/code_tasks.jsonl", encoding="utf-8")]
prompts = []
for t in tasks:
    prompts.append([{"role": "system", "content": BASE_SYS},
                    {"role": "user", "content": t["prompt"]}])
print("n prompts:", len(prompts), flush=True)

# tokenizar como trl: left-padding con pad_token_id, sin truncar
from transformers import BatchEncoding
encs = []
max_len = 0
for p in prompts:
    text = tokenizer.apply_chat_template(p, add_generation_prompt=True)
    enc = tokenizer(text=text, return_tensors="pt", padding=False)
    encs.append(enc.input_ids[0])
    max_len = max(max_len, encs[-1].shape[0])
print("largo prompts:", [e.shape[0] for e in encs], "| max:", max_len, flush=True)

import torch
# left-pad manual con pad_token_id
padded = torch.full((len(encs), max_len), tokenizer.pad_token_id, dtype=torch.long)
mask = torch.zeros((len(encs), max_len), dtype=torch.long)
for i, e in enumerate(encs):
    off = max_len - e.shape[0]
    padded[i, off:] = e
    mask[i, off:] = 1
padded = padded.to("cuda:0")
mask = mask.to("cuda:0")
print("batch shape:", tuple(padded.shape), "| pad ids:", int((padded == tokenizer.pad_token_id).sum()),
      "| max id:", int(padded.max()), flush=True)

# hook en el embedding del text-LM: imprime min/max antes del kernel
found = []
def make_hook(name):
    def hook(module, args):
        ids = args[0]
        vmin, vmax = int(ids.min()), int(ids.max())
        bad = ((ids < 0) | (ids >= module.weight.shape[0])).sum().item()
        print(f"EMBED {name}: min={vmin} max={vmax} numel={ids.numel()} OOB={bad} vocab={module.weight.shape[0]}", flush=True)
        if bad:
            idx = ((ids < 0) | (ids >= module.weight.shape[0])).nonzero()
            print(f"  -> primeros ids OOB: {[int(ids[i0, i1]) for i0, i1 in idx[:5].tolist()]}", flush=True)
    return hook

# localizar módulos embedding (el modelo multimodal: language_model.embed_tokens y el espejito)
for name, mod in model.named_modules():
    if isinstance(mod, torch.nn.Embedding) and "embed_tokens" in name:
        mod.register_forward_pre_hook(make_hook(name))
        found.append(name)
print("embeddings encontrados:", found, flush=True)

# forward exacto del loss GRPO (sin logits_to_keep, slice manual) con el batch
print("\nforward loss GRPO (batch real, train mode)...", flush=True)
model.train()
try:
    with torch.no_grad():
        out = model(input_ids=padded, attention_mask=mask)
        print("forward OK | logits:", tuple(out.logits.shape), flush=True)
        ls = out.logits[:, -(100 + 1):, :]
        print("descarta | hash:", float(ls.float().sum()), flush=True)
except Exception as e:
    print("CRASH loss:", type(e).__name__, str(e)[:400], flush=True)

print("VRAM pico: %.2f GB" % (torch.cuda.max_memory_allocated() / 1e9), flush=True)