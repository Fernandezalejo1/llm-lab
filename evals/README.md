# Evaluaciones (Fase 0)

Harness de baseline con **tareas verificables automáticamente** — el mismo
patrón que usa OpenAI (evals + verificación), y la base para el RL con reward
verificable de la Fase 3.

## Formato de `tasks.jsonl`

Un JSON por línea:

```json
{
  "id": "py-001",
  "category": "python_core",
  "prompt": "Escribí una función ... en un bloque ```python```.",
  "test_kind": "python" | "bash" | "sql" | "answer",
  "test": "código de verificación (python o bash)",
  "schema": "SQL de fixture (solo sql)",
  "expected": ["filas", "esperadas"] ,
  "answer": "respuesta exacta (solo answer)",
  "timeout": 30
}
```

| test_kind | Cómo se verifica |
|---|---|
| `python` | se escribe `solution.py` y se corre el `test` (python) que hace `import solution` y asserts |
| `bash` | se escribe `solution.sh` y se corre el `test` (bash) contra archivos de fixture |
| `sql` | se crea la base sqlite con `schema`, se ejecuta el SELECT del modelo y se comparan filas |
| `answer` | la respuesta debe coincidir con `answer` (normalizada) — mide seguir instrucciones |

## Cómo correr

```bash
cd D:\ai-lab\evals
python run_eval.py --model local-qwen:latest --tasks tasks.jsonl
python run_eval.py --model local-gpt-oss:latest --filter python_core   # una categoría
python run_eval.py --limit 10                                           # prueba rápida
```

## Resultados

- `results/<fecha>_<modelo>_baseline.jsonl` — respuesta cruda + pass/fail por tarea
- `results/<fecha>_<modelo>_summary.md` — % por categoría

## Reglas

- Nunca cambiar el harness a mitad de una comparación. Para medir algo nuevo
  (RAG, prompt, LoRA), se re-corre **el mismo** `tasks.jsonl`.
- Las tareas de código están pensadas para ser *recompensa verificable*:
  un test que pasa = reward 1. Esa es la puerta al RL de la Fase 3.