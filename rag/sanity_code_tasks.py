#!/usr/bin/env python3
"""Sanity check de los tests de code_tasks.jsonl SIN LLM:
- golden solution (basada en el corpus) debe PASAR el test
- solution wrong (genérica, sin conocimiento del corpus) debe FALLAR
Si algún test no discrimina, hay que arreglarlo antes de quemar llamadas al modelo.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals"))
from run_eval import extract_code, run_python_test, run_sql_test  # noqa: E402

TRIGRAM = '''
def _trigrams(s):
    s = " " + s + " "
    return {s[i:i+3] for i in range(len(s) - 2)}

def _trigram_similarity(a, b):
    ta, tb = _trigrams(a), _trigrams(b)
    if not ta or not tb:
        return 0.0
    return 2 * len(ta & tb) / (len(ta) + len(tb))
'''

GOLDEN = {
    "ct-01": '''\
def reconcile_status(status: str) -> str:
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
''',
    "ct-02": TRIGRAM + '''\
from datetime import date

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
''',
    "ct-03": '''\
def _st(status):
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
''',
    "ct-04": """\
SELECT movement_type, COUNT(*) AS count, SUM(credit_amount) AS sum_credit, SUM(debit_amount) AS sum_debit
FROM bank_movements
GROUP BY movement_type
""",
    "ct-05": """\
SELECT hash, COUNT(*) AS cantidad
FROM bank_movements
GROUP BY hash
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
""",
    "ct-06": '''\
def application_decision(amount, open_invoices, balance):
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
''',
    "ct-07": '''\
def export_row(detail):
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
''',
}

WRONG = {
    "ct-01": '''\
def reconcile_status(status: str) -> str:
    return status
''',
    "ct-02": '''\
def detect_duplicate(movement, others):
    for other in others:
        if movement.get("description") and movement["description"] == other.get("description"):
            return {"isDuplicate": True, "originalMovementId": other["id"],
                    "confidence": 1.0, "reason": "misma descripcion"}
    return None
''',
    "ct-03": '''\
from collections import Counter

def generate_summary(movements):
    c = Counter(mv["status"] for mv in movements)
    s = {"totalMovements": len(movements),
         "totalCredits": sum(mv.get("creditAmount") or 0 for mv in movements),
         "totalDebits": sum(mv.get("debitAmount") or 0 for mv in movements),
         "conciliatedCount": c.get("applied", 0),
         "pendingCount": c.get("pending", 0),
         "unidentifiedCount": c.get("unidentified", 0),
         "errorCount": c.get("error", 0),
         "duplicateCount": c.get("duplicate", 0),
         "advanceCount": 0, "balanceForwardCount": 0}
    return s
''',
    "ct-04": """\
SELECT movementType, COUNT(*) AS count, SUM(creditAmount) AS sum_credit, SUM(debitAmount) AS sum_debit
FROM bank_movements
GROUP BY movementType
""",
    "ct-05": """\
SELECT reference, COUNT(*) AS c
FROM bank_movements
GROUP BY reference
HAVING COUNT(*) > 1
""",
    "ct-06": '''\
def application_decision(amount, open_invoices, balance):
    return {"type": "advance", "details": "anticipo"}
''',
    "ct-07": '''\
def export_row(detail):
    return {
        "Fecha": detail["date"],
        "Descripción": detail["description"],
        "Monto": detail["amount"],
        "Tipo": detail["type"],
        "Estado": detail["status"],
        "Cliente": detail["customer"],
        "Confianza": detail["confidence"],
        "Aplicación": detail["application"],
        "Diferencia": detail["difference"],
    }
''',
}


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    # Ruta relativa a este archivo: a mano se corre desde rag/, pero en CI el
    # cwd es la raiz del repo y la ruta relativa no resolveria.
    tasks_path = Path(__file__).resolve().parent / "code_tasks.jsonl"
    tasks = [json.loads(l) for l in open(tasks_path, encoding="utf-8") if l.strip()]
    fails = 0
    for t in tasks:
        tid = t["id"]
        kind = t["test_kind"]
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            if kind == "python":
                ok_g, e_g = run_python_test(tmp, extract_code(GOLDEN[tid]), t["test"], 30)
                ok_w, e_w = run_python_test(tmp, extract_code(WRONG[tid]), t["test"], 30)
            else:
                ok_g, e_g = run_sql_test(tmp, GOLDEN[tid], t["schema"], t["expected"])
                ok_w, e_w = run_sql_test(tmp, WRONG[tid], t["schema"], t["expected"])
        ok = ok_g and not ok_w
        if not ok:
            fails += 1
        print(f"{'OK' if ok else 'PROBLEMA':8s} {tid:6s} kind={kind:6s} golden PASS={ok_g} wrong FAIL={not ok_w}")
        if not ok_g:
            print("   golden debió pasar. error:", (e_g or "")[:200])
        if ok_w:
            print("   wrong NO debió pasar. salida:", (e_w or "")[:200])
    print(f"\nsanity fails: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())