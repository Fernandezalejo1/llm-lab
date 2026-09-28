#!/usr/bin/env python3
"""Compara hit-rate de retrieval: denso puro vs híbrido BM25+denso.

Sin llamadas al LLM: solo mide si el archivo esperado entra en los top-5.
Uso: python hybrid_test.py
"""

import json
import sys

from rag_store import VectorStore

try:
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

store = VectorStore.load("data")
qs = [json.loads(l) for l in open("questions.jsonl", encoding="utf-8") if l.strip()]

for mode in ("dense", "hybrid"):
    n_hit = 0
    misses = []
    for q in qs:
        top = store.query(q["question"], k=5, mode=mode)
        files = [h["file"] for h in top]
        hit = any(f.startswith(p) for p in q["src"] for f in files)
        n_hit += hit
        if not hit:
            misses.append(f"{q['id']} -> {files[0][:50]}")
    print(f"{mode:7s}: {n_hit}/{len(qs)} = {100*n_hit/len(qs):.0f}%  misses: {misses}")

print("\nBarrido de alpha (peso del denso) en modo hybrid:")
best = (0, None)
for alpha in (0.3, 0.4, 0.5, 0.6, 0.7):
    miss = []
    for q in qs:
        top = store.query(q["question"], k=5, mode="hybrid", alpha=alpha)
        files = [h["file"] for h in top]
        hit = any(f.startswith(p) for p in q["src"] for f in files)
        if not hit:
            miss.append(q["id"])
    n = len(qs) - len(miss)
    print(f"  alpha={alpha}: {n}/{len(qs)}  misses={miss}")
    if n > best[0]:
        best = (n, alpha)
print(f"\nmejor alpha: {best[1]}")