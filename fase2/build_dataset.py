#!/usr/bin/env python3
"""Construye el dataset SFT de Fase 2 (semilla del puente).

Convierte las 7 tareas de rag/code_tasks.jsonl + sus soluciones golden (de
rag/sanity_code_tasks.py) en pares instruction->response, con variantes
sintéticas de redacción para que el modelo aprenda la habilidad, no la
memorización.

Salida: fase2/dataset_sft.jsonl  (lista de {"instruction":..., "output":...})
"""
import json
import random
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
RAG = ROOT / "rag"
OUT = Path(__file__).resolve().parent / "dataset_sft.jsonl"

# --- 1. tareas (prompts) -------------------------------------------------
tasks = {}
for line in (RAG / "code_tasks.jsonl").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    tasks[r["id"]] = r["prompt"]

# --- 2. goldens (extraídos de sanity_code_tasks.py, copia canónica) ------
TRIGRAM = """def _trigrams(s):
    s = " " + s + " "
    return {s[i:i+3] for i in range(len(s) - 2)}

def _trigram_similarity(a, b):
    ta, tb = _trigrams(a), _trigrams(b)
    if not ta or not tb:
        return 0.0
    return 2 * len(ta & tb) / (len(ta) + len(tb))
"""

GOLDEN = {
    "ct-01": """def reconcile_status(status: str) -> str:
    m = {
        "reconciled": "conciliated",
        "applied": "conciliated",
        "identified": "pending",
        "pending": "unidentified",
        "unidentified": "unidentified",
        "error": "error",
        "duplicate": "duplicate",
    }
    return m.get(status, "unidentified")
""",
    "ct-02": TRIGRAM + """from datetime import date

def detect_duplicate(movement, others):
    for other in others:
        if other["id"] == movement["id"]:
            continue
        same_amount = abs(
            (movement.get("creditAmount") or movement.get("debitAmount") or 0)
            - (other.get("creditAmount") or other.get("debitAmount") or 0)
        ) < 0.01
        if not same_amount:
            continue
        same_ref = bool(movement.get("reference")) and bool(other.get("reference")) \\
            and movement["reference"] == other["reference"]
        similar_desc = bool(movement.get("description")) and bool(other.get("description")) \\
            and _trigram_similarity(movement["description"], other["description"]) > 0.8
        if not same_ref and not similar_desc:
            continue
        days = abs((date.fromisoformat(movement["transactionDate"])
                    - date.fromisoformat(other["transactionDate"])).days)
        if days <= 3:
            if same_ref:
                reason = f"Misma referencia y monto que movimiento del {other['transactionDate']}"
            else:
                reason = f"Descripción y monto similares a movimiento del {other['transactionDate']}"
            return {
                "isDuplicate": True,
                "originalMovementId": other["id"],
                "confidence": 0.95 if same_ref else 0.85,
                "reason": reason,
            }
    return None
""",
    "ct-03": """def _st(status):
    m = {
        "reconciled": "conciliated",
        "applied": "conciliated",
        "identified": "pending",
        "pending": "unidentified",
        "unidentified": "unidentified",
        "error": "error",
        "duplicate": "duplicate",
    }
    return m.get(status, "unidentified")

def generate_summary(movements):
    s = {
        "totalMovements": len(movements),
        "totalCredits": 0.0,
        "totalDebits": 0.0,
        "conciliatedCount": 0,
        "pendingCount": 0,
        "unidentifiedCount": 0,
        "errorCount": 0,
        "duplicateCount": 0,
        "advanceCount": 0,
        "balanceForwardCount": 0,
    }
    for mv in movements:
        st = _st(mv["status"])
        s[f"{st}Count"] += 1
        if mv.get("creditAmount"):
            s["totalCredits"] += mv["creditAmount"]
        if mv.get("debitAmount"):
            s["totalDebits"] += mv["debitAmount"]
    return s
""",
    "ct-04": """SELECT movement_type, COUNT(*) AS count, SUM(credit_amount) AS sum_credit, SUM(debit_amount) AS sum_debit
FROM bank_movements
GROUP BY movement_type
""",
    "ct-05": """SELECT hash, COUNT(*) AS cantidad
FROM bank_movements
GROUP BY hash
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
""",
    "ct-06": """def application_decision(amount, open_invoices, balance):
    if not open_invoices:
        if balance and balance.get("amount", 0) > 0:
            return {"type": "balance_forward",
                    "details": f"Saldo a favor actualizado: ${balance['amount'] + amount:.2f}"}
        return {"type": "advance",
                "details": "No hay facturas abiertas. Registrado como anticipo."}
    exact = next((inv for inv in open_invoices if abs(inv["balance"] - amount) < 0.01), None)
    if exact:
        return {"type": "full", "invoiceId": exact["id"],
                "details": "Factura cubierta en su totalidad."}
    oldest = min(open_invoices, key=lambda inv: inv["dueDate"])
    return {"type": "partial", "invoiceId": oldest["id"],
            "details": "Aplicación parcial por FIFO."}
""",
    "ct-07": """def export_row(detail):
    customer = detail["customer"].get("name") if isinstance(detail.get("customer"), dict) \\
        else detail.get("customer", "")
    return {
        "Fecha": detail["date"],
        "Descripción": detail["description"],
        "Monto": detail["amount"],
        "Tipo": "Abono" if detail["type"] == "credit" else "Cargo",
        "Estado": detail["status"],
        "Cliente": customer,
        "Confianza": f"{detail['confidence']}%" if detail.get("confidence") is not None else "",
        "Aplicación": detail["application"],
        "Diferencia": detail["difference"],
    }
""",
}

# --- 3. variantes sintéticas de redacción (no cambian la spec) -----------
VARIANT_PREFIX = [
    "",
    "En el contexto de contabilia, implementá lo siguiente: ",
    "Un desarrollador nuevo del equipo de contabilia te pide lo siguiente. ",
    "Tarea de implementación (repo contabilia): ",
    "De la base de conocimiento del producto: ",
]
VARIANT_SUFFIX = [
    "",
    " Escribí solo el código, sin explicaciones.",
    " Resolvelo con el comportamiento exacto que especifica contabilia.",
    " Cuidado con los casos borde: seguí la definición del motor.",
]

# --- 4. generar dataset ---------------------------------------------------
records = []
missing = [tid for tid in tasks if tid not in GOLDEN]
if missing:
    raise SystemExit(f"Faltan golden: {missing}")

for tid, prompt in tasks.items():
    golden = GOLDEN[tid]
    for pre in VARIANT_PREFIX:
        for suf in VARIANT_SUFFIX:
            records.append({
                "instruction": pre + prompt.rstrip() + suf,
                "output": golden.strip(),
            })

# dedup
seen, uniq = set(), []
for r in records:
    key = (r["instruction"], r["output"])
    if key not in seen:
        seen.add(key)
        uniq.append(r)

random.seed(7)
random.shuffle(uniq)

with OUT.open("w", encoding="utf-8") as f:
    for r in uniq:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"Dataset: {len(uniq)} ejemplos ({len(tasks)} tareas x variantes)")
print(f"Guardado: {OUT}")
from collections import Counter
print("Por tarea:", dict(Counter(r["instruction"][:5] for r in uniq)))