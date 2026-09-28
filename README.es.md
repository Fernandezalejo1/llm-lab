# Alejo AI Lab

Laboratorio personal de IA local e investigación en `D:\ai-lab`.

**Objetivo:** convertir la PC (RX 9070 XT 16 GB · 32 GB RAM) en un entorno
donde se pueda *medir*, *mejorar* y *entender* un agente de IA local con método
científico: baseline → hipótesis → experimento → evaluación → generalización.

## Estado actual

- [x] Fase 0.1 — Auditoría y limpieza del stack local (modelos, config, agentes)
- [x] Fase 0.2 — Scaffold del lab + harness de evaluaciones
- [x] Fase 0.3 — Baseline medible de `local-qwen:latest` ✅ **49/50 (98%)**
- [ ] Fase 1 — Contexto/memoria/RAG alrededor del modelo (RAG de contabilia ✅, puente de código ✅)
- [ ] Fase 2 — Primer QLoRA (solo capas de atención) + ablations
  - ✅ Ambiente Unsloth/RDNA4 verificado (smoke aprobado, 4 trampas de Windows resueltas)
  - ✅ Primer QLoRA real: Qwen3.5-9B-Base, LoRA solo en las 8 capas full-attention (0.068%),
    140 ejemplos del puente, 2 epochs, loss 1.51→0.86, VRAM 8.82 GB
  - ✅ Merge → GGUF Q4_K_M → importado a Ollama como `local-qwen-ft:latest`
  - ⏳ Eval del fine-tune: 7 tests del puente sin/con RAG vs baselina `local-qwen`
    - resultado: sin RAG **0/7** (baselina 1/7) · con RAG **4/7** (baselina 4/7
      con distinta composición — ganó ct-03, perdió ct-01). Veredicto honesto:
      el pipeline funciona, el LoRA attention-only de 140 ejemplos no mueve el
      agregado. Próximo paso: dataset más grande (kinetix) y/o partir del instruct.
- [ ] Fase 3 — RL con recompensa verificable (GRPO + tests como reward)

## RAG Fase 1 (en curso) — contabilia

Corpus `rag/corpus/contabilia` (811 chunks) + embeddings `bge-m3` vía Ollama +
retrieval híbrido BM25+denso (`alpha 0.4`):

- Hit-rate de retrieval: **10/10** (el denso puro daba 9/10 — el PRD gigante
  ahogaba la sección de duplicados; el BM25 la recuperó)
- Re-corrida v2 (hybrid alpha 0.4): **10/10** y respuestas de q04/q08
  corregidas (v1: 8/10). `results/rag_20260922_191127_*`
- Cualitativo (sin RAG vs con RAG): sin contexto el 9B alucina teoría contable
  genérica; con RAG cita modelos Prisma y docs reales. Ver `results/rag_*.md`.
- **Puente a Fase 2 (cerrado ✅):** evals de *código* con tests verificables que
  dependen del corpus (`rag/code_tasks.jsonl`, ct-01…ct-07: duplicados, mapeo
  de estados, resumen, SQL con schema, decisión de aplicación, exportación).
  - Resultado: **sin RAG ≈0-1/7 · con RAG ≈4-5/7** (varianza por sampling).
    El contexto del producto sube ~4-5 puntos sobre tareas que exigen la spec
    del repo; los tests que discriminan = semilla del dataset de Fase 2 y
    rewards de GRPO.
  - 5 iteraciones de método: prompts con fuga → chunking que partía funciones
    (re-index fence-aware 811→555) → contratos alineados al repo → técnicas
    estándar vs invento → sampling determinista. Diagnóstico en
    `docs/architecture.md` y resultados en `results/code_rag_2026*`.

## Baseline Fase 0 — `local-qwen:latest` (2026-09-22)

| Categoría | Resueltas | % |
|---|---|---|
| algorithms | 10/10 | 100% |
| debugging | 10/10 | 100% |
| python_core | 10/10 | 100% |
| reasoning | 10/10 | 100% |
| sql | 5/5 | 100% |
| bash | 4/5 | 80% |
| **TOTAL** | **49/50** | **98%** |

Único fallo: `sh-005` (extraer números con grep + uniq mal usado — deduplicó dígitos
dentro del mismo número). Detalle por tarea en `results/`. Este es el **punto
cero**: cualquier mejora futura (RAG, tools, QLoRA, RL) se mide contra estos números.

## Stack local (diciembre de línea base)

| Modelo | Tam. | Rol |
|---|---|---|
| `opencode/big-pickle` | cloud | Build default (planificación, análisis) |
| `ollama/local-qwen:latest` | 6.6 GB | Agente ejecutor local (Qwen3.5-9B Q4) |
| `ollama/local-qwen-ft:latest` | 5.8 GB | Fine-tune QLoRA attention-only (Fase 2, en evaluación) |
| `ollama/local-gpt-oss:latest` | 13 GB | Segundo cerebro local para tareas pesadas |
| `ollama/bge-m3:latest` | 1.2 GB | Embeddings (RAG) |

## Cómo correr el baseline

```bash
cd D:\ai-lab\evals
python run_eval.py --model local-qwen:latest --tasks tasks.jsonl
```

Resultados en `results/`. Detalles en [docs/architecture.md](docs/architecture.md)
y [evals/README.md](evals/README.md).