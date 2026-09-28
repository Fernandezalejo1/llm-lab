# Código con contexto: SIN vs CON RAG — local-qwen:latest (20260922_195619)

| tarea | hit | sin RAG | con RAG |
|---|---|---|---|
| ct-01 | ✅ | ❌ | ✅ |
| ct-02 | ✅ | ❌ | ✅ |
| ct-03 | ✅ | ❌ | ✅ |
| ct-04 | ✅ | ❌ | ✅ |
| ct-05 | ✅ | ❌ | ✅ |
| ct-06 | ✅ | ❌ | ❌ |
| ct-07 | ✅ | ❌ | ❌ |

**Sin RAG: 0/7 · Con RAG: 5/7**

## ct-01
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/02-DATABASE-SCHEMA.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert got == v, (k, got, v)
           ^^^^^^^^
AssertionError: ('reconciled', 'cleared', 'conciliated')
- con RAG: PASS

## ct-02
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/04-AI-ENGINE.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 9, in <module>
    assert r and r['isDuplicate'] and r['originalMovementId'] == 'A' and abs(r['confidence'] - 0.95) < 1e-6, r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'isDuplicate': True, 'originalMovementId': 'A', 'confidence': 1.0, 'reason': 'Idéntico: referencia "REF-1" coincidente.', 'originalMovement': {'id': 'A', 'creditAmount': 100, 'debitAmount': 0, 'reference': 'REF-1', 'description': 'transferencia banco nacional', 'transactionDate': '2026-01-
- con RAG: PASS

## ct-03
- hit retrieval: sí | chunks: apps/api/src/modules/reconciliation/reconciliation.service.ts; docs/07-RECONCILIATION.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert s['conciliatedCount'] == 2, s      # applied + reconciled
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'totalMovements': 5, 'totalCredits': 235, 'totalDebits': 60, 'conciliatedCount': 3, 'pendingCount': 1, 'unidentifiedCount': 0, 'errorCount': 0, 'duplicateCount': 1, 'advanceCount': 0, 'balanceForwardCount': 0}
- con RAG: PASS

## ct-04
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/02-DATABASE-SCHEMA.md; docs/08-UX-DESIGN.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: amount
- con RAG: PASS

## ct-05
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/02-DATABASE-SCHEMA.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: identifier
- con RAG: PASS

## ct-06
- hit retrieval: sí | chunks: docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md
- sin RAG: FAIL — sin código
- con RAG: FAIL — sin código

## ct-07
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; packages/shared-types/src/index.ts; packages/shared-types/src/index.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 4, in <module>
    assert r['Tipo'] == 'Abono', r
           ^^^^^^^^^^^^^^^^^^^^
AssertionError: {'Fecha': '2026-01-15', 'Descripción': 'pago cliente', 'Monto': 100, 'Tipo': 'Crédito', 'Estado': 'conciliated', 'Cliente': 'ACME SA', 'Confianza': 95, 'Aplicación': 'F2', 'Diferencia': 0}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert r['Fecha'] == '2026-01-15' and r['Monto'] == 100 and r['Estado'] == 'conciliated' and r['Cliente'] == 'ACME SA' and r['Aplicación'] == 'F2', r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'Fecha': '2026-01-15', 'Descripción': 'pago cliente', 'Monto': 100, 'Tipo': 'Abono', 'Estado': 'unidentified', 'Cliente': 'ACME SA', 'Confianza': '95%', 'Aplicación': 'F2', 'Diferencia': 0}
