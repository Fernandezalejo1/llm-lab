# Código con contexto: SIN vs CON RAG — local-qwen:latest (20260922_191836)

| tarea | hit | sin RAG | con RAG |
|---|---|---|---|
| ct-01 | ✅ | ❌ | ❌ |
| ct-02 | ✅ | ❌ | ❌ |
| ct-03 | ✅ | ❌ | ❌ |
| ct-04 | ✅ | ✅ | ✅ |
| ct-05 | ✅ | ✅ | ✅ |
| ct-06 | ✅ | ❌ | ❌ |
| ct-07 | ✅ | ✅ | ❌ |

**Sin RAG: 3/7 · Con RAG: 2/7**

## ct-01
- hit retrieval: sí | top: docs/07-RECONCILIATION.md, docs/08-UX-DESIGN.md, docs/07-RECONCILIATION.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert got == v, (k, got, v)
           ^^^^^^^^
AssertionError: ('reconciled', 'cleared', 'conciliated')
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 4, in <module>
    got = solution.reconcile_status(k)
  File "~\AppData\Local\Temp\tmpo95_s4i4\solution.py", line 22, in reconci

## ct-02
- hit retrieval: sí | top: docs/07-RECONCILIATION.md, docs/01-ARCHITECTURE-OVERVIEW.md, docs/04-AI-ENGINE.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 9, in <module>
    assert r and r['isDuplicate'] and r['originalMovementId'] == 'A' and abs(r['confidence'] - 0.95) < 1e-6, r
           ^^^^
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 18, in <module>
    assert solution.detect_duplicate(m('F', cred=100, ref=None, desc='compra supermercado', dt='2026-01-16'), others) is None

## ct-03
- hit retrieval: sí | top: docs/07-RECONCILIATION.md, apps/api/src/modules/reconciliation/reconciliation.service.ts, apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 9, in <module>
    s = solution.generate_summary(movs)
  File "~\AppData\Local\Temp\tmpyn852etz\solution.py", line 3, in generat
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert s['conciliatedCount'] == 2, s      # applied + reconciled
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'

## ct-04
- hit retrieval: sí | top: docs/02-DATABASE-SCHEMA.md, docs/04-AI-ENGINE.md, docs/02-DATABASE-SCHEMA.md
- sin RAG: PASS
- con RAG: PASS

## ct-05
- hit retrieval: sí | top: docs/02-DATABASE-SCHEMA.md, docs/02-DATABASE-SCHEMA.md, docs/02-DATABASE-SCHEMA.md
- sin RAG: PASS
- con RAG: PASS

## ct-06
- hit retrieval: sí | top: docs/06-CASH-APPLICATION.md, docs/06-CASH-APPLICATION.md, docs/06-CASH-APPLICATION.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 7, in <module>
    assert r['type'] == 'balance_forward', r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'type': 'advance', 'in
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import solution
  File "~\AppData\Local\Temp\tmpyh425pym\solution.py", line 1
    ```python
    ^
SyntaxError

## ct-07
- hit retrieval: sí | top: docs/07-RECONCILIATION.md, packages/shared-types/src/index.ts, docs/04-AI-ENGINE.md
- sin RAG: PASS
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 3, in <module>
    r = solution.export_row(d)
  File "~\AppData\Local\Temp\tmpfji16ttf\solution.py", line 2, in export_row
    c
