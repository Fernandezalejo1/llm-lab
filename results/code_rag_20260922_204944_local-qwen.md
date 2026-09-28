# Código con contexto: SIN vs CON RAG — local-qwen:latest (20260922_204944)

| tarea | hit | sin RAG | con RAG |
|---|---|---|---|
| ct-01 | ✅ | ❌ | ✅ |
| ct-02 | ✅ | ❌ | ✅ |
| ct-03 | ✅ | ❌ | ❌ |
| ct-04 | ✅ | ✅ | ✅ |
| ct-05 | ✅ | ❌ | ✅ |
| ct-06 | ✅ | ❌ | ❌ |
| ct-07 | ✅ | ❌ | ❌ |

**Sin RAG: 1/7 · Con RAG: 4/7**

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
- con RAG: PASS

## ct-03
- hit retrieval: sí | chunks: apps/api/src/modules/reconciliation/reconciliation.service.ts; docs/07-RECONCILIATION.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert s['conciliatedCount'] == 2, s      # applied + reconciled
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'totalMovements': 5, 'totalCredits': 235.0, 'totalDebits': 60.0, 'conciliatedCount': 3, 'pendingCount': 1, 'unidentifiedCount': 0, 'errorCount': 0, 'duplicateCount': 1, 'advanceCount': 0, 'balanceForwardCount': 0}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import solution
  File "~\AppData\Local\Temp\tmp00krqbct\solution.py", line 30
    elif mapped
               ^
SyntaxError: expected ':'

## ct-04
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/02-DATABASE-SCHEMA.md; docs/08-UX-DESIGN.md
- sin RAG: PASS
- con RAG: PASS

## ct-05
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/02-DATABASE-SCHEMA.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: identification
- con RAG: PASS

## ct-06
- hit retrieval: sí | chunks: docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert r['type'] == 'full' and r.get('invoiceId') == 'F1', r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'type': 'partial', 'invoiceId': 'F2', 'details': 'Pago parcial aplicado a factura F2'}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 14, in <module>
    assert r['type'] == 'partial' and r.get('invoiceId') == 'F2', r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'type': 'partial', 'invoiceId': 'F1', 'details': 'Pago parcial a factura F1. Pendiente: $60.00'}

## ct-07
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; packages/shared-types/src/index.ts; packages/shared-types/src/index.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 4, in <module>
    assert r['Tipo'] == 'Abono', r
           ~^^^^^^^^
KeyError: 'Tipo'
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 3, in <module>
    r = solution.export_row(d)
  File "~\AppData\Local\Temp\tmpa_6vai_9\solution.py", line 8, in export_row
    "Cliente": detail['customer'].get('name', '') if detail['_customer'] else '',
                                                     ~~~~~~^^^^^^^^^^^^^
KeyError: '_customer'
