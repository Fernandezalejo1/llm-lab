# CONTABILIA - Motor de IA

## Principio Rector

La IA NO debe resolver todos los casos. Debe intervenir SOLO cuando las reglas no alcanzan suficiente confianza (< 90%). Cuando interviene, debe explicar su razonamiento de forma transparente.

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│             AI Engine (Python/FastAPI)             │
│                                                   │
│  ┌──────────────────────────────────────────┐     │
│  │ 1. Semantic Search Service                │     │
│  │    - Model: multilingual-e5-large         │     │
│  │    - Vector DB: Qdrant                    │     │
│  │    - Encuentra clientes similares         │     │
│  │      por similitud de texto               │     │
│  └──────────────────────────────────────────┘     │
│                                                   │
│  ┌──────────────────────────────────────────┐     │
│  │ 2. Fuzzy Classification Service          │     │
│  │    - Levenshtein distance                 │     │
│  │    - Token overlap score                  │     │
│  │    - Abbreviation expansion               │     │
│  │    - Name normalization                   │     │
│  └──────────────────────────────────────────┘     │
│                                                   │
│  ┌──────────────────────────────────────────┐     │
│  │ 3. LLM Reasoning Service                 │     │
│  │    - OpenAI / Claude API                 │     │
│  │    - Solo para casos complejos           │     │
│  │    - Recibe contexto estructurado        │     │
│  │    - Produce: análisis + candidatos      │     │
│  └──────────────────────────────────────────┘     │
│                                                   │
│  ┌──────────────────────────────────────────┐     │
│  │ 4. Confidence Calibrator                 │     │
│  │    - Platt scaling                       │     │
│  │    - Ajusta según precisión histórica    │     │
│  └──────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

## 1. Semantic Search Service

### Embedding Strategy

Se generan embeddings para los siguientes textos de cada cliente:

```python
def generate_customer_texts(customer):
    texts = []
    metadata = []

    # Razón social
    texts.append(customer.legal_name)
    metadata.append({"customer_id": customer.id, "type": "legal_name"})

    # Alias
    if customer.alias:
        texts.append(customer.alias)
        metadata.append({"customer_id": customer.id, "type": "alias"})

    # Atributos
    for attr in customer.attributes:
        texts.append(attr.value)
        metadata.append({
            "customer_id": customer.id,
            "type": attr.attribute_type,
            "confidence": attr.confidence
        })

    # Patrones de aprendizaje
    for pattern in customer.patterns:
        texts.append(pattern.source_text)
        metadata.append({
            "customer_id": customer.id,
            "type": "learning_pattern",
            "pattern_id": pattern.id
        })

    return texts, metadata
```

### Modelo

- **Modelo**: `intfloat/multilingual-e5-large` (multilingüe, soporta español)
- **Dimensión**: 1024
- **Batch size**: 32
- **Actualización**: Incremental (cuando se añaden nuevos clientes o patrones)

### Búsqueda

```python
async def semantic_search(query_text: str, top_k: int = 10):
    # Normalizar query
    normalized = normalize_text(query_text)

    # Generar embedding
    query_vector = embedding_model.encode(normalized)

    # Buscar en Qdrant
    results = qdrant_client.search(
        collection_name="customers",
        query_vector=query_vector,
        limit=top_k,
        score_threshold=0.5
    )

    # Agrupar por customer_id, promediar scores
    customers = {}
    for hit in results:
        cid = hit.payload["customer_id"]
        if cid not in customers:
            customers[cid] = {
                "customer_id": cid,
                "scores": [],
                "matches": []
            }
        customers[cid]["scores"].append(hit.score)
        customers[cid]["matches"].append({
            "type": hit.payload["type"],
            "text": hit.payload["text"],
            "score": hit.score
        })

    # Score final = max score de cualquier match
    for cid, data in customers.items():
        data["confidence"] = max(data["scores"])

    return sorted(customers.values(), key=lambda x: x["confidence"], reverse=True)
```

## 2. Fuzzy Classification Service

### Técnicas

```python
def fuzzy_match(query: str, targets: list[str]) -> list[dict]:
    results = []

    for target in targets:
        # 1. Levenshtein distance
        lev_score = 1 - (levenshtein_distance(query, target) / max(len(query), len(target)))

        # 2. Token overlap
        query_tokens = set(tokenize(query))
        target_tokens = set(tokenize(target))
        overlap = len(query_tokens & target_tokens) / max(len(query_tokens | target_tokens), 1)

        # 3. Substring match
        substr_score = 1.0 if query.lower() in target.lower() or target.lower() in query.lower() else 0.0

        # 4. Trigram similarity
        trigram_score = trigram_similarity(query, target)

        combined = (
            lev_score * 0.25 +
            overlap * 0.30 +
            substr_score * 0.25 +
            trigram_score * 0.20
        )

        results.append({
            "target": target,
            "combined_score": combined,
            "levenshtein": lev_score,
            "token_overlap": overlap,
            "substring": substr_score,
            "trigram": trigram_score
        })

    return sorted(results, key=lambda x: x["combined_score"], reverse=True)
```

### Normalización de Texto

```python
def normalize_text(text: str) -> str:
    text = text.upper()
    text = unidecode(text)  # quitar acentos
    text = re.sub(r'[^\w\s]', ' ', text)  # quitar puntuación
    text = re.sub(r'\s+', ' ', text)  # espacios múltiples
    text = text.strip()

    # Normalizar razones sociales comunes
    replacements = {
        r'\bS\.?A\.?\s*DE\s*C\.?V\.?\b': 'SA DE CV',
        r'\bS\.?A\.?\b': 'SA',
        r'\bS\.?\s*DE\s*R\.?\s*L\.?\b': 'S DE RL',
        r'\bC\.?V\.?\b': 'CV',
        r'\bS\.?\s*E\.?\b': 'SE',
        r'\bE\.?\s*E\.?\b': 'EE',
        # etc.
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    return text.strip()
```

## 3. LLM Reasoning Service

### Cuándo Usar LLM

Solo se invoca al LLM cuando:
1. Semantic search encuentra candidatos pero todos con confianza < 80%
2. Fuzzy search produce resultados ambiguos (múltiples candidatos con scores similares)
3. No se encontraron candidatos por reglas ni búsqueda semántica

### Prompt Template

```
Eres un contador senior con 20 años de experiencia especializado en
conciliación bancaria y aplicación de cobros.

Contexto:
Un movimiento bancario no pudo ser identificado automáticamente por el
sistema de reglas. Necesito tu análisis para determinar quién realizó
este pago.

MOVIMIENTO BANCARIO:
- Fecha: {transaction_date}
- Descripción: {description}
- Referencia: {reference}
- Tipo: {movement_type}
- Monto: ${amount}
- Cuenta/CLABE Origen: {source_account}

CLIENTES CANDIDATOS (de búsqueda semántica):
{candidates}

INSTRUCCIONES:
1. Analiza cada campo del movimiento bancario
2. Por cada cliente candidato, evalúa qué evidencia lo conecta con el pago
3. Asigna un porcentaje de confianza (0-100%) a cada candidato
4. Explica DETALLADAMENTE tu razonamiento:
   - Qué texto analizaste
   - Qué similitudes encontraste
   - Por qué algunos clientes son más probables que otros
   - Qué evidencia concreta respalda tu conclusión
5. NO uses el monto como factor principal de identificación
6. Si ningún cliente es convincente, indícalo claramente

RESPONDE EN FORMATO JSON:
{
  "analysis": "texto explicando el razonamiento",
  "candidates": [
    {
      "customer_id": "uuid",
      "confidence": 85,
      "evidence": ["evidencia 1", "evidencia 2"],
      "explanation": "por qué este cliente"
    }
  ],
  "needs_human_review": true,
  "reason": "por qué no se puede determinar automáticamente"
}
```

### Límites y Seguridad

- Rate limiting: max 100 requests/hour/organization
- Cost tracking por organización
- Fallback a fuzzy search si LLM no responde
- Timeout: 30 segundos
- Solo se envía texto, nunca datos sensibles

## 4. Confidence Calibrator

### Platt Scaling

```python
def calibrate_confidence(raw_score: float, model_precision: float) -> float:
    """
    Ajusta la confianza según la precisión histórica del modelo.
    Si el modelo acierta el 90% de las veces cuando dice 85%,
    entonces 85% -> 85% * 0.9 / 0.85 (calibración)
    """
    if model_precision == 0:
        return raw_score
    # Simple calibration: raw_score * (precision / expected_precision)
    calibrated = raw_score * (model_precision / 0.85)
    return min(max(calibrated, 0), 1.0)
```

### Monitoreo de Precisión

```sql
-- Precisión del modelo de IA por mes
SELECT
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_interventions,
    SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct,
    AVG(confidence) as avg_confidence,
    SUM(CASE WHEN is_correct THEN 1 ELSE 0 END)::float / COUNT(*) as precision
FROM ai_engine_logs
GROUP BY month
ORDER BY month DESC;
```

## Evidencia Explicable

Cada intervención de IA debe devolver:

```json
{
  "movement_id": "uuid",
  "ai_version": "1.0.0",
  "semantic_search": {
    "query_normalized": "JUAN PEREZ CONSTRUCCIONES",
    "top_candidates": [
      {
        "customer_id": "uuid",
        "score": 0.89,
        "matched_on": "legal_representative",
        "matched_text": "JUAN PEREZ"
      }
    ]
  },
  "llm_analysis": {
    "used": true,
    "reason": "semantic search confidence < 80%",
    "prompt_tokens": 450,
    "response_tokens": 320,
    "analysis": "El pago fue realizado por JUAN PEREZ, quien es representante legal de CONSTRUCTORA ABC...",
    "candidates": [...]
  },
  "final_confidence": 0.87,
  "decision": "pending_review",
  "explanation": "Se identificó a JUAN PEREZ como representante legal de CONSTRUCTORA ABC. La confianza es alta pero requiere confirmación porque hay otro cliente (CONSTRUCTORA XYZ) con un representante similar."
}
```
