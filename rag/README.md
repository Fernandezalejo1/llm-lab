# RAG del lab (Fase 1)

Retrieval aumentado sobre el corpus `corpus/contabilia` con embeddings
locales vía Ollama (`bge-m3`) y un vector store mínimo en numpy.

## Decisión de stack (D7, D8)

- **Embeddings:** Ollama `bge-m3` (multilingüe — los docs están en español).
  Reutiliza la infra existente; cero wheels nuevas.
- **Store:** `rag_store.py` — numpy + coseno + persistencia JSON/npy.
  ChromaDB baja ~200 MB de wheels y arriesga romper en Python 3.14; cuando
  necesitemos filtros potentes por metadata migramos sin tocar el resto.
- **Retrieval híbrido (D8):** BM25 + denso con stopwords es/en filtradas,
  `alpha=0.4` (40% denso / 60% léxico). El denso puro dejaba fuera la sección
  "Detección de Duplicados" (el PRD, gigante y repetitivo, dominaba el ranking);
  el BM25 con "duplicados" la recupera. Resultado: hit-rate **9/10 → 10/10**.

## Resultados del experimento orginal (denominador)

| Estrategia | Hit-rate (top-5) |
|---|---|
| denso puro (bge-m3) | 9/10 = 90% |
| híbrido BM25+denso (stopwords, alpha 0.4) | **10/10 = 100%** |

Cualitativo (10 preguntas de negocio): sin RAG el modelo alucina teoría
genérica (schema contable "estándar", estados de ERP); con RAG cita los
modelos reales del Prisma y los docs correctos. Detalle por pregunta en
`../results/rag_*.md`.

## Cómo correr

```bash
cd D:\ai-lab\rag
python index_rag.py          # corpus -> chunks + embeddings (rag/data/)
python run_rag_eval.py       # 10 preguntas SIN y CON RAG -> ../results/rag_*.md
```

## Archivos

| Archivo | Rol |
|---|---|
| `corpus/contabilia/` | copia readonly del proyecto (1.3 MB, sin node_modules/.git) |
| `index_rag.py` | chunking (md por secciones; código por párrafos) + embeddings |
| `rag_store.py` | VectorStore: embed vía Ollama, coseno, BM25 híbrido, persistir/cargar |
| `questions.jsonl` | 10 preguntas de negocio con archivos esperados (`src`) |
| `run_rag_eval.py` | control sin RAG vs con RAG; mide hit-rate de retrieval |
| `hybrid_test.py` | compara denso vs híbrido y barre `alpha` (sin llamar al LLM) |

## Métrica

**Hit rate**: qué fracción de preguntas trae al menos un archivo esperado en
los top-5 del retrieval. Es objetiva y verificable; la calidad de las
respuestas (sin vs con RAG) se compara lado a lado en el `.md` de salida.