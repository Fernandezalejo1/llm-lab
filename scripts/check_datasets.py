#!/usr/bin/env python3
"""Valida los datasets JSONL del laboratorio.

No necesita GPU ni modelo: comprueba que cada linea parsea como JSON y que
ningun `id` se repite dentro de un mismo archivo. Es la red de seguridad de los
numeros publicados, porque todos los resultados de results/ salen de estos
archivos: una linea corrupta o un id duplicado invalidaria la comparacion entre
fases sin que se note en el resumen.

Uso:
    python scripts/check_datasets.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    files = sorted(
        p for p in ROOT.rglob("*.jsonl")
        if ".git" not in p.parts and ".venv" not in p.parts
    )
    if not files:
        print("No se encontro ningun .jsonl")
        return 1

    problems = 0
    total_rows = 0
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        rows = 0
        bad: list[str] = []
        seen: dict[object, list[int]] = {}
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                bad.append(f"linea {n}: JSON invalido ({e.msg})")
                continue
            rows += 1
            if isinstance(obj, dict) and "id" in obj:
                seen.setdefault(obj["id"], []).append(n)

        dupes = {k: v for k, v in seen.items() if len(v) > 1}
        total_rows += rows
        if bad or dupes:
            problems += 1
        print(f"{'PROBLEMA' if bad or dupes else 'OK      '} {rel}: {rows} filas, {len(seen)} ids")
        for b in bad[:5]:
            print("          ", b)
        for k, v in list(dupes.items())[:5]:
            print(f"           id duplicado {k!r} en las lineas {v}")

    print(f"\n{total_rows} filas en {len(files)} archivos, {problems} con problemas")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
