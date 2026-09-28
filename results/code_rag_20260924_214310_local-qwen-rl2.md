# Código con contexto: SIN vs CON RAG — local-qwen-rl2:latest (20260924_214310)

| tarea | hit | sin RAG | con RAG |
|---|---|---|---|
| ct-01 | ✅ | ❌ | ✅ |
| ct-02 | ✅ | ❌ | ❌ |
| ct-03 | ✅ | ❌ | ❌ |
| ct-04 | ✅ | ❌ | ❌ |
| ct-05 | ✅ | ❌ | ✅ |
| ct-06 | ✅ | ✅ | ✅ |
| ct-07 | ✅ | ❌ | ❌ |

**Sin RAG: 1/7 · Con RAG: 3/7**

## ct-01
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/02-DATABASE-SCHEMA.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert got == v, (k, got, v)
           ^^^^^^^^
AssertionError: ('reconciled', 'conciliado', 'conciliated')
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
  File "~\AppData\Local\Temp\tmpqqshx3mx\solution.py", line 44, in detect_duplicate
    if not is_within_days(movement['transactionDate'], other['transactionDate']):
           ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "~\AppData\Local\Temp\tmpqqshx3mx\solution.py", line 26, in is_within_days
    day_diff = abs((date2.date() - date1.date()).days)
        

## ct-03
- hit retrieval: sí | chunks: apps/api/src/modules/reconciliation/reconciliation.service.ts; docs/07-RECONCILIATION.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 9, in <module>
    s = solution.generate_summary(movs)
  File "~\AppData\Local\Temp\tmpqiqi99fm\solution.py", line 28, in generate_summary
    summary[summary_status] += 1
    ~~~~~~~^^^^^^^^^^^^^^^^
KeyError: 'conciliated'
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 9, in <module>
    s = solution.generate_summary(movs)
  File "~\AppData\Local\Temp\tmpqiqi99fm\solution.py", line 26, in generate_summary
    summary[status] += 1
    ~~~~~~~^^^^^^^^
KeyError: 'conciliated'

## ct-04
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/02-DATABASE-SCHEMA.md; docs/08-UX-DESIGN.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: credit
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert got == want, (got, want)
           ^^^^^^^^^^^
AssertionError: (set(), {('credit_card', '1', '300.0', '0.0'), ('credit_transfer', '2', '300.0', '0.0'), ('debit_purchase', '2', '0.0', '75.0')})

## ct-05
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/02-DATABASE-SCHEMA.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: identificador
- con RAG: PASS

## ct-06
- hit retrieval: sí | chunks: docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md
- sin RAG: PASS
- con RAG: PASS

## ct-07
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; packages/shared-types/src/index.ts; packages/shared-types/src/index.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 4, in <module>
    assert r['Tipo'] == 'Abono', r
           ^^^^^^^^^^^^^^^^^^^^
AssertionError: {'Fecha': '2026-01-15', 'Descripción': 'pago cliente', 'Monto': '+100.00', 'Tipo': 'Crédito', 'Estado': 'conciliated', 'Elaborado por': 'ACME SA', 'Confianza': 'Coincide perfectamente', 'Aplicación': 'F2', 'Diferencia': '0.00'}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert r['Fecha'] == '2026-01-15' and r['Monto'] == 100 and r['Estado'] == 'conciliated' and r['Cliente'] == 'ACME SA' and r['Aplicación'] == 'F2', r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'Fecha': '2026-01-15', 'Descripción': 'pago cliente', 'Monto': 100, 'Tipo': 'Abono', 'Estado': 'unidentified', 'Cliente': 'ACME SA', 'Confianza': '95%', 'Aplicación': 'F2', 'Diferencia': ''}
