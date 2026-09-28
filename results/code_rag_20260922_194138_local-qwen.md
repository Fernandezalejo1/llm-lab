# Código con contexto: SIN vs CON RAG — local-qwen:latest (20260922_194138)

| tarea | hit | sin RAG | con RAG |
|---|---|---|---|
| ct-01 | ✅ | ❌ | ✅ |
| ct-02 | ✅ | ❌ | ❌ |
| ct-03 | ✅ | ❌ | ❌ |
| ct-04 | ✅ | ❌ | ✅ |
| ct-05 | ✅ | ❌ | ❌ |
| ct-06 | ✅ | ❌ | ✅ |
| ct-07 | ✅ | ❌ | ✅ |

**Sin RAG: 0/7 · Con RAG: 4/7**

## ct-01
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/02-DATABASE-SCHEMA.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 4, in <module>
    got = solution.reconcile_status(k)
  File "~\AppData\Local\Temp\tmp36lbin75\solution.py", line 11, in reconcile_status
    default_statuses = set(map(mapping.keys()))
                           ~~~^^^^^^^^^^^^^^^^
TypeError: map() must have at least two arguments.
- con RAG: PASS

## ct-02
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/04-AI-ENGINE.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 9, in <module>
    assert r and r['isDuplicate'] and r['originalMovementId'] == 'A' and abs(r['confidence'] - 0.95) < 1e-6, r
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'isDuplicate': True, 'originalMovementId': 'B', 'confidence': 80, 'reason': 'duplicado detectado por: montos iguales, mismo mes, vencimiento cercano, referencia coincide; original B vs A, ventana de fechas ±2 días'}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 8, in <module>
    r = solution.detect_duplicate(m('B', cred=100, ref='REF-1', desc='otra cosa', dt='2026-01-16'), others)
  File "~\AppData\Local\Temp\tmpg4i0yqkt\solution.py", line 50, in detect_duplicate
    trigram_similarity(movement['description'], other['description']) > 0.8
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "~\AppData\Local\Temp\tmpg4i0yqkt\solution.py", line 29, in trigram_similarity
    return len(set(s1) & set(s2)) / len(set(s1 | s2)) if s1 and s2 else 0
  

## ct-03
- hit retrieval: sí | chunks: apps/api/src/modules/reconciliation/reconciliation.service.ts; docs/07-RECONCILIATION.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert s['conciliatedCount'] == 2, s      # applied + reconciled
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'totalMovements': 5, 'totalCredits': 235.0, 'totalDebits': 60.0, 'conciliatedCount': 0, 'pendingCount': 1, 'unidentifiedCount': 0, 'errorCount': 3, 'duplicateCount': 1, 'advanceCount': 0, 'balanceForwardCount': 0}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 11, in <module>
    assert s['conciliatedCount'] == 2, s      # applied + reconciled
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'totalMovements': 5, 'totalCredits': 235.0, 'totalDebits': 60.0, 'conciliatedCount': 0, 'pendingCount': 1, 'unidentifiedCount': 0, 'errorCount': 0, 'duplicateCount': 1, 'advanceCount': 0, 'balanceForwardCount': 0}

## ct-04
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/02-DATABASE-SCHEMA.md; docs/08-UX-DESIGN.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: is_credit
- con RAG: PASS

## ct-05
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/02-DATABASE-SCHEMA.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: identificador_calculado
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
    rows = conn.execute(sql).fetchall()
           ~~~~~~~~~~~~^^^^^
sqlite3.OperationalError: no such column: status

## ct-06
- hit retrieval: sí | chunks: docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md
- sin RAG: FAIL — sin código
- con RAG: PASS

## ct-07
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; packages/shared-types/src/index.ts; packages/shared-types/src/index.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 4, in <module>
    assert r['Tipo'] == 'Abono', r
           ~^^^^^^^^
KeyError: 'Tipo'
- con RAG: PASS
