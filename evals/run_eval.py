#!/usr/bin/env python3
"""
Alejo AI Lab — harness de evaluación baseline (Fase 0).

Cada tarea en tasks.jsonl es verificable automáticamente (el código se
ejecuta o la respuesta se compara contra un valor exacto), igual que un
eval de OpenAI: respuesta del modelo -> verificación -> puntaje.

Uso:
    python run_eval.py --model local-qwen:latest --tasks tasks.jsonl
    python run_eval.py --model local-gpt-oss:latest --filter python_core
    python run_eval.py --limit 5 --out ../results/smoke.jsonl

Salida: resultados crudos (JSONL) + resumen por categoría (Markdown) en results/.
"""

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/v1")
SYSTEM_PROMPT = (
    "Sos un ingeniero de software riguroso. Completá la tarea EXACTAMENTE como se "
    "pide. Para tareas de código, respondé SOLO con el bloque de código solicitado "
    "y nada más. Para tareas de respuesta exacta, respondé SOLO con el resultado "
    "(número o palabra), sin explicaciones."
)


def load_tasks(path: Path):
    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def ask_model(model: str, prompt: str, max_tokens: int = 2000, timeout: int = 300):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"num_predict": max_tokens},
    }
    start = time.time()
    r = requests.post(f"{OLLAMA_URL}/chat/completions", json=payload, timeout=timeout)
    r.raise_for_status()
    msg = r.json()["choices"][0]["message"]
    return (
        msg.get("content", "") or "",
        msg.get("reasoning_content") or "",
        time.time() - start,
    )


def extract_code(answer: str) -> str:
    """Primer bloque fenced (cualquier lenguaje), o el texto completo."""
    m = re.search(r"```[a-zA-Z]*\s*(.*?)```", answer, re.S)
    return m.group(1).strip() if m else answer.strip()


def normalize(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")  # quita tildes
    return re.sub(r"\s+", " ", s).strip().lower()


def run_python_test(tmp: Path, code: str, test_code: str, timeout: int):
    (tmp / "solution.py").write_text(code, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-c", test_code],
        cwd=tmp, capture_output=True, text=True, timeout=timeout,
    )
    if proc.returncode == 0:
        return True, ""
    return False, (proc.stderr or proc.stdout).strip()[-800:]


def run_bash_test(tmp: Path, code: str, test_code: str, timeout: int):
    (tmp / "solution.sh").write_text(code, encoding="utf-8")
    proc = subprocess.run(
        ["bash", "-c", test_code],
        cwd=tmp, capture_output=True, text=True, timeout=timeout,
    )
    if proc.returncode == 0:
        return True, ""
    return False, (proc.stderr or proc.stdout).strip()[-800:]


def run_sql_test(tmp: Path, code: str, schema: str, expected_rows):
    (tmp / "solution.sql").write_text(code, encoding="utf-8")
    (tmp / "schema.sql").write_text(schema, encoding="utf-8")
    (tmp / "expected.json").write_text(
        json.dumps([list(r) for r in expected_rows], ensure_ascii=False), encoding="utf-8"
    )
    test_code = """
import sqlite3, json
conn = sqlite3.connect(':memory:')
conn.executescript(open('schema.sql', encoding='utf-8').read())
sql = open('solution.sql', encoding='utf-8').read().strip().rstrip(';')
rows = conn.execute(sql).fetchall()
exp = json.load(open('expected.json', encoding='utf-8'))
width = len(exp[0])
got = {tuple(str(x) for x in row[:width]) for row in rows}
want = {tuple(str(x) for x in row[:width]) for row in exp}
assert got == want, (got, want)
print('OK')
"""
    proc = subprocess.run(
        [sys.executable, "-c", test_code],
        cwd=tmp, capture_output=True, text=True, timeout=30,
    )
    if proc.returncode == 0:
        return True, ""
    return False, (proc.stderr or proc.stdout).strip()[-800:]


def verify(task: dict, answer: str, tmp: Path):
    kind = task.get("test_kind", "answer")
    if kind == "answer":
        ok = normalize(answer) == normalize(str(task.get("answer", "")))
        return ok, "" if ok else f"respuesta: '{answer[:120]}'"
    code = extract_code(answer)
    if not code:
        return False, "no se encontró bloque de código"
    if kind == "python":
        return run_python_test(tmp, code, task["test"], task.get("timeout", 30))
    if kind == "bash":
        return run_bash_test(tmp, code, task["test"], task.get("timeout", 30))
    if kind == "sql":
        return run_sql_test(tmp, code, task.get("schema", ""), task.get("expected", []))
    return False, f"test_kind desconocido: {kind}"


def main():
    ap = argparse.ArgumentParser(description="Harness de evals Alejo AI Lab")
    ap.add_argument("--model", default="local-qwen:latest")
    ap.add_argument("--tasks", default="tasks.jsonl")
    ap.add_argument("--results-dir", default="../results")
    ap.add_argument("--limit", type=int, default=0, help="correr solo N tareas")
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--filter", default="", help="solo categoría")
    args = ap.parse_args()

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    tasks = load_tasks(Path(args.tasks))
    if args.filter:
        tasks = [t for t in tasks if t.get("category") == args.filter]
    if args.limit:
        tasks = tasks[args.offset: args.offset + args.limit]

    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_model = args.model.replace("/", "_").replace(":", "-")
    run_file = results_dir / f"{stamp}_{safe_model}_baseline.jsonl"
    summary_file = results_dir / f"{stamp}_{safe_model}_summary.md"

    print(f"Modelo: {args.model} | tareas: {len(tasks)} | salida: {run_file}\n")
    results = []
    for i, task in enumerate(tasks, 1):
        tid, cat = task["id"], task.get("category", "?")
        print(f"[{i}/{len(tasks)}] {cat}/{tid} ... ", end="", flush=True)
        try:
            answer, reasoning, dur = ask_model(args.model, task["prompt"])
        except Exception as e:
            print(f"ERROR {e}")
            results.append({"id": tid, "category": cat, "pass": False,
                            "error": f"request: {e}", "duration_s": 0})
            continue
        with tempfile.TemporaryDirectory() as td:
            ok, err = verify(task, answer, Path(td))
        rec = {
            "id": tid, "category": cat, "model": args.model,
            "pass": ok, "error": err, "duration_s": round(dur, 1),
            "answer": answer[:400],
        }
        results.append(rec)
        print("PASS" if ok else f"FAIL ({err[:80]})")

    # Persistir
    with open(run_file, "w", encoding="utf-8") as f:
        for rec in results:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Resumen por categoría
    cats = {}
    for rec in results:
        cats.setdefault(rec["category"], [0, 0])
        cats[rec["category"]][0] += 1
        cats[rec["category"]][1] += 1 if rec["pass"] else 0
    lines = [f"# Baseline {args.model} — {stamp}", ""]
    lines.append("| Categoría | Resueltas | Total | % |")
    lines.append("|---|---|---|---|")
    total_ok = sum(1 for r in results if r["pass"])
    for cat, (n, ok) in sorted(cats.items()):
        pct = f"{100 * ok / n:.0f}%" if n else "—"
        lines.append(f"| {cat} | {ok} | {n} | {pct} |")
    lines.append(f"| **TOTAL** | **{total_ok}** | **{len(results)}** | "
                 f"**{100 * total_ok / len(results):.0f}%** |")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nResumen:\n{chr(10).join(lines[:4])}")
    print(f"...\nGuardado: {run_file.name} / {summary_file.name}")


if __name__ == "__main__":
    main()