# Código con contexto: SIN vs CON RAG — local-qwen-rl:latest (20260923_200953)

| tarea | hit | sin RAG | con RAG |
|---|---|---|---|
| ct-01 | ✅ | ❌ | ✅ |
| ct-02 | ✅ | ❌ | ❌ |
| ct-03 | ✅ | ✅ | ✅ |
| ct-04 | ✅ | ❌ | ✅ |
| ct-05 | ✅ | ❌ | ✅ |
| ct-06 | ✅ | ✅ | ❌ |
| ct-07 | ✅ | ❌ | ❌ |

**Sin RAG: 2/7 · Con RAG: 4/7**

## ct-01
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/02-DATABASE-SCHEMA.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 5, in <module>
AssertionError: ('identified', 'conciliated', 'pending')
- con RAG: PASS

## ct-02
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/04-AI-ENGINE.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 9, in <module>
AssertionError: {'isDuplicate': True, 'originalMovementId': 'A', 'confidence': 1.0, 'reason': 'Duplicado por referencia y monto'}
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 9, in <module>
AssertionError: None

## ct-03
- hit retrieval: sí | chunks: apps/api/src/modules/reconciliation/reconciliation.service.ts; docs/07-RECONCILIATION.md; apps/api/src/modules/reconciliation/reconciliation.service.ts
- sin RAG: PASS
- con RAG: PASS

## ct-04
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/02-DATABASE-SCHEMA.md; docs/08-UX-DESIGN.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
sqlite3.OperationalError: no such column: credit
- con RAG: PASS

## ct-05
- hit retrieval: sí | chunks: docs/02-DATABASE-SCHEMA.md; docs/01-ARCHITECTURE-OVERVIEW.md; docs/02-DATABASE-SCHEMA.md
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 6, in <module>
sqlite3.OperationalError: no such column: identificador
- con RAG: PASS

## ct-06
- hit retrieval: sí | chunks: docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md; docs/06-CASH-APPLICATION.md
- sin RAG: PASS
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 10, in <module>
  File "~\AppData\Local\Temp\tmpb1wk9pcv\solution.py", line 26, in application_decision
    "details": f"Pago exacto de factura {exact['invoiceNumber']}"
                                         ~~~~~^^^^^^^^^^^^^^^^^
KeyError: 'invoiceNumber'

## ct-07
- hit retrieval: sí | chunks: docs/07-RECONCILIATION.md; packages/shared-types/src/index.ts; packages/shared-types/src/index.ts
- sin RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 4, in <module>
KeyError: 'Tipo'
- con RAG: FAIL — Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "~\AppData\Local\Temp\tmpn53uomyc\solution.py", line 15, in export_row
    'Fecha': detail['date'].strftime('%Y-%m-%d'),
             ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'strftime'
