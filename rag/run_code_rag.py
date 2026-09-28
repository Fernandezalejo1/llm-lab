#!/usr/bin/env python3
"""Experimento puente Fase 1 -> Fase 2: tareas de CÓDIGO que requieren
conocimiento del corpus (contabilia). Sin RAG = memoria; con RAG = contexto.

Iteración 2:
- extractor de código robusto (fence sin cerrar por truncamiento, multi-bloque)
- max_tokens mayor (6000) para respuestas largas
- dedupe de chunks por archivo en el contexto
- guarda respuestas COMPLETAS + previsualización de chunks para diagnóstico
"""
import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals"))
from run_eval import run_python_test, run_sql_test  # noqa: E402

from rag_store import VectorStore  # noqa: E402

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/v1")
MAX_CONTEXT = 12000
MAX_TOKENS = 6000
ALPHA = 0.4
TOP_K = 8

BASE_SYS = ("Sos un ingeniero de software. Resolvé la tarea con precisión. "
            "Respondé solo con el bloque de código solicitado.")
RAG_SYS = ("Sos un ingeniero de software. Resolvé la tarea usando SOLO la "
           "información del CONTEXTO provisto (documentación del producto). "
           "Si el contexto referencia una técnica estándar de la ingeniería sin "
           "definirla (p. ej. trigram similarity), implementala con su forma "
           "convencional en lugar de omitirla. No inventes datos del negocio "
           "(campos, criterios, umbrales) que no estén en el contexto: si hacen "
           "falta, decilo explícitamente. Respondé solo con el bloque de código "
           "solicitado.")


def extract_code_robust(answer: str) -> str:
    """Extrae el mejor bloque de código posible, tolerando truncamiento."""
    # 1) bloque completo con lenguaje python
    m = re.search(r"```(?:python|py)\s*\n(.*?)```", answer, re.S)
    if m:
        return m.group(1).strip()
    # 2) cualquier bloque fenced completo
    m = re.search(r"```[a-zA-Z]*\s*\n(.*?)```", answer, re.S)
    if m:
        return m.group(1).strip()
    # 3) bloque python sin cerrar (truncado por tokens)
    idx = answer.find("```python")
    if idx != -1:
        rest = answer[idx + len("```python"):]
        end = rest.rfind("```")
        if end != -1:
            rest = rest[:end]
        return rest.strip()
    # 4) sin bloques: texto completo
    return answer.strip()


def ask(model, messages, max_tokens=MAX_TOKENS, timeout=600):
    import requests
    opts = {"num_predict": max_tokens, "temperature": 0.2, "seed": 7}
    for attempt in (1, 2):
        r = requests.post(
            f"{OLLAMA_URL}/chat/completions",
            json={"model": model, "messages": messages, "stream": False,
                  "options": opts},
            timeout=timeout,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"].get("content", "") or ""
        if content.strip():
            return content
        if attempt == 1:
            print("   (respuesta vacía — reintento)", flush=True)
    return ""


def build_context(store, question, k=TOP_K):
    hits = store.query(question, k=k, mode="hybrid", alpha=ALPHA)
    # sin dedupe por archivo: para tareas de código hace falta más de un chunk
    # del mismo doc (ej. mapeo de estados + resumen están en 07 pero en chunks
    # distintos; el dedupe los descartaba)
    parts, total, chunk_info = [], 0, []
    for h in hits:
        block = f"[archivo: {h['file']}]\n{h['text']}"
        if total + len(block) > MAX_CONTEXT:
            break
        parts.append(block)
        total += len(block)
        chunk_info.append((h["file"], h["text"][:90].replace("\n", " ")))
    return "\n\n---\n\n".join(parts), chunk_info


def verify_task(task, answer, tmp):
    kind = task.get("test_kind", "python")
    code = extract_code_robust(answer)
    if not code:
        return False, "sin código"
    if kind == "python":
        return run_python_test(tmp, code, task["test"], task.get("timeout", 30))
    if kind == "sql":
        return run_sql_test(tmp, code, task.get("schema", ""), task.get("expected", []))
    return False, f"kind desconocido: {kind}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="local-qwen:latest")
    ap.add_argument("--retrieval-only", action="store_true")
    args = ap.parse_args()

    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    store = VectorStore.load("data")
    tasks = [json.loads(l) for l in open("code_tasks.jsonl", encoding="utf-8") if l.strip()]

    pre = []
    for t in tasks:
        _, chunks = build_context(store, t["prompt"])
        files = [f for f, _ in chunks]
        hit = any(f.startswith(p) for p in t["src"] for f in files)
        pre.append((t["id"], hit, chunks))
        print(f"{'HIT ' if hit else 'MISS'} {t['id']:6s} {files[0][:55] if files else '-'}")

    if args.retrieval_only:
        n = sum(1 for _, h, _ in pre if h)
        print(f"\nretrieval hit-rate: {n}/{len(pre)} = {100*n/len(pre):.0f}%")
        return

    results = []
    for i, (task, (_, _, chunks)) in enumerate(zip(tasks, pre), 1):
        tid = task["id"]
        print(f"\n[{i}/{len(tasks)}] {tid} ...", flush=True)

        ans_base = ask(args.model, [{"role": "system", "content": BASE_SYS},
                                    {"role": "user", "content": task["prompt"]}])
        context, chunks_rag = build_context(store, task["prompt"])
        ans_rag = ask(args.model, [{"role": "system", "content": RAG_SYS},
                                   {"role": "user",
                                    "content": f"CONTEXTO:\n{context}\n\nTAREA: {task['prompt']}"}])

        hit = any(f.startswith(p) for p in task["src"] for f, _ in chunks)
        with tempfile.TemporaryDirectory() as td:
            ok_base, err_base = verify_task(task, ans_base, Path(td))
            ok_rag, err_rag = verify_task(task, ans_rag, Path(td))

        results.append({"id": tid, "category": task["category"], "hit": hit,
                        "retrieved": chunks_rag, "pass_base": ok_base, "pass_rag": ok_rag,
                        "err_base": err_base[:600], "err_rag": err_rag[:600],
                        "ans_base": ans_base, "ans_rag": ans_rag})
        print(f"   hit={hit} | sin RAG: {'PASS' if ok_base else 'FAIL'} | "
              f"con RAG: {'PASS' if ok_rag else 'FAIL'}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("../results")
    out_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"code_rag_{stamp}_{args.model.split(':')[0]}"
    with open(out_dir / f"{base_name}.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    lines = [f"# Código con contexto: SIN vs CON RAG — {args.model} ({stamp})", "",
             "| tarea | hit | sin RAG | con RAG |", "|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['id']} | {'✅' if r['hit'] else '❌'} | "
                     f"{'✅' if r['pass_base'] else '❌'} | {'✅' if r['pass_rag'] else '❌'} |")
    n1 = sum(1 for r in results if r["pass_base"])
    n2 = sum(1 for r in results if r["pass_rag"])
    lines += ["", f"**Sin RAG: {n1}/{len(results)} · Con RAG: {n2}/{len(results)}**", ""]
    for r in results:
        lines.append(f"## {r['id']}")
        lines.append(f"- hit retrieval: {'sí' if r['hit'] else 'no'} | chunks: "
                     f"{'; '.join(f'{f}' for f, _ in r['retrieved'][:3])}")
        lines.append(f"- sin RAG: {'PASS' if r['pass_base'] else 'FAIL — ' + r['err_base']}")
        lines.append(f"- con RAG: {'PASS' if r['pass_rag'] else 'FAIL — ' + r['err_rag']}")
        lines.append("")
    (out_dir / f"{base_name}.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"\nResolución — sin RAG: {n1}/{len(results)} | con RAG: {n2}/{len(results)}")
    print(f"Guardado: {base_name}.jsonl / .md")


if __name__ == "__main__":
    main()