# Código con contexto: SIN vs CON RAG — local-qwen-rl2:latest (20260924_213624)

| tarea | hit | sin RAG | con RAG |
|---|---|---|---|
| ct-01 | ✅ | ❌ | ✅ |
| ct-02 | ✅ | ❌ | ❌ |
| ct-03 | ✅ | ❌ | ✅ |
| ct-04 | ✅ | ❌ | ✅ |
| ct-05 | ✅ | ❌ | ✅ |
| ct-06 | ✅ | ❌ | ❌ |
| ct-07 | ✅ | ❌ | ✅ |

**Sin RAG: 0/7 · Con RAG: 5/7**

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
  File "<string>", line 16, in <module>
    assert solution.detect_duplicate(m('E', cred=100, ref='REF-1', desc='x', dt='2026-01-25'), others) is None
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import solution
  File "~\AppData\Local\Temp\tmpq21163j7\solution.py", line 4, in <module>
    import holidays
ModuleNotFoundError: No module named 'holidays'

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
sqlite3.OperationalError: unrecognized token: ":"
- con RAG: PASS

## ct-06
- hit retrieval: sí | chunks: docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import solution
  File "~\AppData\Local\Temp\tmpivce8vex\solution.py", line 43
    open_invoices sorted by dueDate (ascending)
                  ^^^^^^
SyntaxError: invalid syntax
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 10, in <module>
    r = solution.application_decision(100, invs, 0)
  File "~\AppData\Local\Temp\tmpivce8vex\solution.py", line 62, in application_decision
    'details': f'Pago parcial de factura {inv["invoiceNumber"]}. Pendiente: {currency(remaining)}',
                                          ~~~^^^^^^^^^^^^^^^^^
KeyError: 'invoiceNumber'

## ct-07
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; packages/shared-types/src/index.ts; packages/shared-types/src/index.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 3, in <module>
    r = solution.export_row(d)
  File "~\AppData\Local\Temp\tmp8t0hwfat\solution.py", line 23, in export_row
    'Cliente': detail['customer'].name,
               ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'dict' object has no attribute 'name'
- con RAG: PASS
