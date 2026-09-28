#!/usr/bin/env python3
"""Reward DENSIFICADO para GRPO: assert-coverage de los tests del puente.

El reward 0/1 pelado tira toda la información: una respuesta que pasa 2 de 3
asserts recibe 0 igual que una que no armó nada. Este módulo ejecuta el MISMO
test del eval pero devuelve una fracción continua (0.0..1.0):

  python  -> fracción de asserts del test que pasan (setup crasheado = 0.0,
             "sin código" = 0.0). Si TODOS pasan => 1.0 (igual que verify_task).
  sql     -> fracción de filas esperadas que coinciden con la query
             (query válida; si la query crashea => 0.0).

Regla del lab intacta: el reward conoce los tests, el prompt no.

Uso de debug:
    python reward_score.py <code_tasks.jsonl> <answers.jsonl>
    # answers.jsonl con campos id / ans_base / ans_rag (formato run_code_rag)
"""
import ast
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rag"))
from run_code_rag import extract_code_robust  # noqa: E402


def _score_python(tmp: Path, code: str, test_code: str, timeout: int = 30) -> float:
    (tmp / "solution.py").write_text(code, encoding="utf-8")

    # Transforma cada `assert X, msg` del test en un check individual con
    # try/except y registro en _sc (lista de bool). Un crash en el SETUP
    # (antes de los asserts, ej. la función pedida no existe o revienta en la
    # primer llamada) se propaga como excepción -> score 0.0.
    try:
        tree = ast.parse(test_code)
    except SyntaxError:
        return 0.0

    body = []
    for stmt in tree.body:
        if isinstance(stmt, ast.Assert):
            cond = ast.unparse(stmt.test)
            body.append(f"_sc.append(_try_(lambda: bool({cond})))")
        else:
            body.append(ast.unparse(stmt))

    wrapped = (
        "_sc = []\n"
        "def _try_(f):\n"
        "    try:\n"
        "        return bool(f())\n"
        "    except Exception:\n"
        "        return False\n"
    ) + "\n".join(body) + "\nprint('__SC__' + json.dumps(_sc))\n"
    # json import adicional por si el test no lo trae
    wrapped = "import json\n" + wrapped

    try:
        proc = subprocess.run(
            [sys.executable, "-c", wrapped], cwd=tmp,
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return 0.0
    if proc.returncode != 0:
        return 0.0  # crash en setup (la solución no construye la salida)
    m = re.search(r"__SC__(\[.*?\])", proc.stdout, re.S)
    if not m:
        return 0.0
    checks = json.loads(m.group(1))
    if not checks:
        return 0.0
    return sum(1 for c in checks if c) / len(checks)


def _score_sql(tmp: Path, code: str, schema: str, expected_rows) -> float:
    (tmp / "solution.sql").write_text(code, encoding="utf-8")
    (tmp / "schema.sql").write_text(schema, encoding="utf-8")
    (tmp / "expected.json").write_text(
        json.dumps([list(r) for r in expected_rows], ensure_ascii=False),
        encoding="utf-8",
    )
    test_code = (
        "import sqlite3, json\n"
        "conn = sqlite3.connect(':memory:')\n"
        "conn.executescript(open('schema.sql', encoding='utf-8').read())\n"
        "sql = open('solution.sql', encoding='utf-8').read().strip().rstrip(';')\n"
        "rows = conn.execute(sql).fetchall()\n"
        "exp = json.load(open('expected.json', encoding='utf-8'))\n"
        "width = len(exp[0])\n"
        "got = {tuple(str(x) for x in row[:width]) for row in rows}\n"
        "want = {tuple(str(x) for x in row[:width]) for row in exp}\n"
        "cov = len(got & want) / len(want) if want else (1.0 if not got else 0.0)\n"
        "print('__SC__' + json.dumps([cov]))\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", test_code], cwd=tmp,
        capture_output=True, text=True, timeout=30,
    )
    if proc.returncode != 0:
        return 0.0  # query inválida
    m = re.search(r"__SC__(\[.*?\])", proc.stdout, re.S)
    if not m:
        return 0.0
    checks = json.loads(m.group(1))
    return float(checks[0]) if checks else 0.0


def verify_score(task: dict, answer: str, tmp: Path) -> float:
    """Score densificado (0..1) de una respuesta contra el test real."""
    kind = task.get("test_kind", "python")
    code = extract_code_robust(answer)
    if not code:
        return 0.0
    if kind == "python":
        return _score_python(tmp, code, task["test"], task.get("timeout", 30))
    if kind == "sql":
        return _score_sql(tmp, code, task.get("schema", ""), task.get("expected", []))
    return 0.0


def main():
    tasks_file, answers_file = sys.argv[1], sys.argv[2]
    tasks = {json.loads(l)["id"]: json.loads(l)
             for l in open(tasks_file, encoding="utf-8") if l.strip()}
    print(f"{'id':8} {'base':>6} {'rag':>6}   (assert-coverage)")
    for line in open(answers_file, encoding="utf-8"):
        d = json.loads(line)
        tid = d["id"]
        t = tasks.get(tid)
        if not t:
            continue
        with tempfile.TemporaryDirectory() as td:
            sb = verify_score(t, d.get("ans_base", "") or "", Path(td)) if d.get("pass_base") is not None else None
        if sb is None:
            continue
        with tempfile.TemporaryDirectory() as td:
            sr = verify_score(t, d.get("ans_rag", "") or "", Path(td))
        print(f"{tid:8} {sb:6.2f} {sr:6.2f}")


if __name__ == "__main__":
    main()