#!/usr/bin/env python3
"""Experimento Fase 1: responde 10 preguntas de negocio SIN y CON RAG.

El control (sin RAG) mide lo que sabe local-qwen de memoria; el grupo RAG
recibe los top-5 chunks del corpus de contabilia. La métrica objetiva de
retrieval es el *hit rate*: qué fracción de preguntas trajo al menos un
archivo esperado (src) en los top-5.

Uso: python run_rag_eval.py [--model local-qwen:latest] [--k 5]
Salida: ../results/rag_<ts>.jsonl + ../results/rag_<ts>.md
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

from rag_store import VectorStore

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/v1")
MAX_CONTEXT = 7000  # chars de contexto máximo inyectado

BASE_SYS = ("Sos un ingeniero de software. Respondé la pregunta con precisión "
            "y concisión, en español.")
RAG_SYS = ("Sos un ingeniero de software. Respondé la pregunta usando SOLO la "
           "información del CONTEXTO provisto. Cuando uses un dato, citá el "
           "archivo de donde salió. Si el contexto no alcanza para responder, "
           "decilo explícitamente en vez de inventar.")


def ask(model, messages, max_tokens=1200, timeout=300):
    r = requests.post(
        f"{OLLAMA_URL}/chat/completions",
        json={"model": model, "messages": messages, "stream": False,
              "options": {"num_predict": max_tokens}},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"].get("content", "") or ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="local-qwen:latest")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--alpha", type=float, default=0.4,
                    help="peso del denso en hybrid (0.4 = 40%% denso / 60%% BM25)")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--questions", default="questions.jsonl")
    args = ap.parse_args()

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    store = VectorStore.load(args.data_dir)
    print(f"store: {len(store.chunks)} chunks | modelo RAG: {args.model}\n")

    questions = [json.loads(l) for l in open(args.questions, encoding="utf-8") if l.strip()]

    results = []
    for i, q in enumerate(questions, 1):
        qid = q["id"]
        print(f"[{i}/{len(questions)}] {qid} ... ", end="", flush=True)

        # --- control: sin RAG ---
        t0 = time.time()
        base = ask(args.model, [{"role": "system", "content": BASE_SYS},
                                {"role": "user", "content": q["question"]}])
        t_base = round(time.time() - t0, 1)

        # --- retrieval ---
        hits = store.query(q["question"], k=args.k, mode="hybrid", alpha=args.alpha)
        files = [h["file"] for h in hits]
        hit = any(f.startswith(prefix) for prefix in q["src"] for f in files)

        # --- con RAG ---
        ctx_parts, total = [], 0
        for h in hits:
            block = f"[archivo: {h['file']}]\n{h['text']}"
            if total + len(block) > MAX_CONTEXT:
                break
            ctx_parts.append(block)
            total += len(block)
        context = "\n\n---\n\n".join(ctx_parts)
        user_msg = (f"CONTEXTO:\n{context}\n\n"
                    f"PREGUNTA: {q['question']}")
        t0 = time.time()
        rag = ask(args.model, [{"role": "system", "content": RAG_SYS},
                               {"role": "user", "content": user_msg}])
        t_rag = round(time.time() - t0, 1)

        results.append({"id": qid, "category": q["category"], "hit": hit,
                        "top_files": files[:args.k], "answer_base": base,
                        "answer_rag": rag, "t_base_s": t_base, "t_rag_s": t_rag})
        print(f"{'HIT' if hit else 'MISS'} {files[0][:45]}")

    # persistir
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("../results")
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / f"rag_{stamp}_{args.model.split(':')[0]}.jsonl"
    with open(jsonl, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    md = out_dir / f"rag_{stamp}_{args.model.split(':')[0]}.md"
    n_hit = sum(1 for r in results if r["hit"])
    lines = [f"# RAG vs SIN RAG — {args.model} ({stamp})",
             "", f"**Hit rate retrieval (top-{args.k}): {n_hit}/{len(results)} "
                 f"= {100*n_hit/len(results):.0f}%**", ""]
    for r in results:
        lines.append(f"## {r['id']} ({r['category']}) — {'HIT' if r['hit'] else 'MISS'}")
        lines.append(f"- top files: {', '.join(r['top_files'][:3])}")
        lines.append(f"\n**SIN RAG:**\n{r['answer_base'][:900]}")
        lines.append(f"\n**CON RAG:**\n{r['answer_rag'][:900]}")
        lines.append("")
    md.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nHit rate: {n_hit}/{len(results)} = {100*n_hit/len(results):.0f}%")
    print(f"Guardado: {jsonl.name} / {md.name}")


if __name__ == "__main__":
    main()