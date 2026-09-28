# Código con contexto: SIN vs CON RAG — local-qwen:latest (20260922_192754)

| tarea | hit | sin RAG | con RAG |
|---|---|---|---|
| ct-01 | ✅ | ❌ | ✅ |
| ct-02 | ✅ | ❌ | ❌ |
| ct-03 | ✅ | ❌ | ❌ |
| ct-04 | ✅ | ❌ | ✅ |
| ct-05 | ✅ | ❌ | ✅ |
| ct-06 | ✅ | ❌ | ❌ |
| ct-07 | ✅ | ❌ | ❌ |

**Sin RAG: 0/7 · Con RAG: 3/7**

## ct-01
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/02-DATABASE-SCHEMA.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert got == v, (k, got, v)
           ^^^^^^^^
AssertionError: ('reconciled', 'reconciled', 'conciliated')
- con RAG: PASS

## ct-02
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/04-AI-ENGINE.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 9, in <module>
    assert r and r['isDuplicate'] and r['originalMovementId'] == 'A' and abs(r['confidence'] - 0.95) < 1e-6, r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: None
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 8, in <module>
    r = solution.detect_duplicate(m('B', cred=100, ref='REF-1', desc='otra cosa', dt='2026-01-16'), others)
  File "~\AppData\Local\Temp\tmp5taazo5x\solution.py", line 31, in detect_duplicate
    same_ref = movement.get('reference') and reference == other.get('reference')
                                             ^^^^^^^^^
NameError: name 'reference' is not defined

## ct-03
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert s['conciliatedCount'] == 2, s      # applied + reconciled
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'totalMovements': 5, 'totalCredits': 235.0, 'totalDebits': 60.0, 'conciliatedCount': 0, 'pendingCount': 0, 'unidentifiedCount': 5, 'errorCount': 0, 'duplicateCount': 0, 'advanceCount': 0, 'balanceForwardCount': 0}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert s['conciliatedCount'] == 2, s      # applied + reconciled
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'totalMovements': 5, 'totalCredits': 235, 'totalDebits': 60, 'conciliatedCount': 0, 'pendingCount': 1, 'unidentifiedCount': 0, 'errorCount': 0, 'duplicateCount': 1, 'advanceCount': 0, 'balanceForwardCount': 0}

## ct-04
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/04-AI-ENGINE.md; docs/08-UX-DESIGN.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: credit
- con RAG: PASS

## ct-05
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/09-PRD-FULL-PLATFORM.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: duplicate_identifier
- con RAG: PASS

## ct-06
- hit retrieval: sí | chunks: docs/06-CASH-APPLICATION.md; apps/api/src/modules/cash-application/cash-application.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert r['type'] == 'full' and r.get('invoiceId') == 'F1', r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'type': 'partial', 'invoiceId': 'F2', 'details': 'Pago parcial aplicado a factura ID F2'}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    r = solution.application_decision(100, [], 40)
  File "~\AppData\Local\Temp\tmp2bi_nujm\solution.py", line 4, in application_decision
    if balance and balance.get('amount', 0) > 0:
                   ^^^^^^^^^^^
AttributeError: 'int' object has no attribute 'get'

## ct-07
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; packages/shared-types/src/index.ts; apps/api/src/modules/ingestion/ingestion.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 4, in <module>
    assert r['Tipo'] == 'Abono', r
           ^^^^^^^^^^^^^^^^^^^^
AssertionError: {'Fecha': '2026-01-15', 'Descripción': 'pago cliente', 'Importe': '100', 'Tipo': 'Crédito', 'Estado': 'conciliated', 'Cliente': 'ACME SA', 'Confianza': 95, 'Aplicación': 'F2', 'Diferencia': '0'}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 3, in <module>
    r = solution.export_row(d)
  File "~\AppData\Local\Temp\tmp0lwkm1hk\solution.py", line 8, in export_row
    "Cliente": detail.get("customer", {}).get("name", "") if detail.get("customer") else "",
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'
