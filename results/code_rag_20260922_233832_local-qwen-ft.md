# Código con contexto: SIN vs CON RAG — local-qwen-ft:latest (20260922_233832)

| tarea | hit | sin RAG | con RAG |
|---|---|---|---|
| ct-01 | ✅ | ❌ | ❌ |
| ct-02 | ✅ | ❌ | ✅ |
| ct-03 | ✅ | ❌ | ✅ |
| ct-04 | ✅ | ❌ | ✅ |
| ct-05 | ✅ | ❌ | ✅ |
| ct-06 | ✅ | ❌ | ❌ |
| ct-07 | ✅ | ❌ | ❌ |

**Sin RAG: 0/7 · Con RAG: 4/7**

## ct-01
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/02-DATABASE-SCHEMA.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert got == v, (k, got, v)
           ^^^^^^^^
AssertionError: ('identified', 'identified', 'pending')
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert got == v, (k, got, v)
           ^^^^^^^^
AssertionError: ('reconciled', 'conciled', 'conciliated')

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
  File "<string>", line 9, in <module>
    s = solution.generate_summary(movs)
  File "~\AppData\Local\Temp\tmpl2jgsc_l\solution.py", line 29, in generate_summary
    summary[mapping[status]] += 1
    ~~~~~~~^^^^^^^^^^^^^^^^^
KeyError: 'advance'
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
sqlite3.OperationalError: no such column: computed_id
- con RAG: PASS

## ct-06
- hit retrieval: sí | chunks: docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert r['type'] == 'full' and r.get('invoiceId') == 'F1', r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'type': 'full', 'details': 'Aplicó completa a la factura F1'}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 10, in <module>
    r = solution.application_decision(100, invs, 0)
  File "~\AppData\Local\Temp\tmpi32t0oeg\solution.py", line 19, in application_decision
    'details': f'Pago exacto de factura {exact_match["invoiceNumber"]}',
                                         ~~~~~~~~~~~^^^^^^^^^^^^^^^^^
KeyError: 'invoiceNumber'

## ct-07
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; packages/shared-types/src/index.ts; packages/shared-types/src/index.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 3, in <module>
    r = solution.export_row(d)
  File "~\AppData\Local\Temp\tmpboxrol97\solution.py", line 15, in export_row
    'Cliente': detail['customer'].name,
               ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'dict' object has no attribute 'name'
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert r['Fecha'] == '2026-01-15' and r['Monto'] == 100 and r['Estado'] == 'conciliated' and r['Cliente'] == 'ACME SA' and r['Aplicación'] == 'F2', r
           ~^^^^^^^^^
KeyError: 'Fecha'
