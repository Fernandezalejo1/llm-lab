# CONTABILIA - Motor de Aprendizaje

## Filosofía

Cada corrección del usuario es oro. El sistema debe aprender de cada una para mejorar futuras conciliaciones. El aprendizaje es permanente y se refuerza con cada uso.

## Ciclo de Aprendizaje

```
Corrección del Usuario
        │
        ▼
┌──────────────────────────┐
│ 1. Registrar en           │
│    LearningLog            │
│    - input_text           │
│    - suggested_customer   │
│    - selected_customer    │
│    - confidence           │
│    - correction_type      │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ 2. Generar/Actualizar     │
│    SimilarityPattern      │
│    - source_text          │
│    - normalized_text      │
│    - target_customer_id   │
│    - pattern_type         │
│    - occurrences++        │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ 3. Actualizar Atributos   │
│    de Cliente             │
│    - Si aparece un nuevo  │
│      representante,       │
│      agregar como         │
│      CustomerAttribute    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ 4. Ajustar Pesos de      │
│    Reglas                │
│    - Reglas que acertaron │
│      → +peso             │
│    - Reglas que fallaron  │
│      → -peso             │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ 5. Re-entrenar Modelo    │
│    (batch programado)    │
│    - Nuevos embeddings   │
│    - Nuevos patrones     │
│    - Re-calibrar         │
└──────────────────────────┘
```

## Tipos de Corrección

### 1. Corrección Directa
Usuario dice explícitamente: "Este pago es de este cliente".

```typescript
async function handleDirectCorrection(params: {
  movementId: string;
  selectedCustomerId: string;
  suggestedCustomerId?: string;
  notes?: string;
}) {
  // 1. Crear/actualizar PaymentMatch
  const match = await updatePaymentMatch({
    movementId: params.movementId,
    customerId: params.selectedCustomerId,
    status: 'manual_confirmed',
    reviewedAt: new Date(),
    isCorrection: true
  });

  // 2. Registrar en LearningLog
  await createLearningLog({
    movementId: params.movementId,
    inputText: movement.description,
    suggestedCustomer: params.suggestedCustomerId,
    selectedCustomer: params.selectedCustomerId,
    correctionType: 'manual_match'
  });

  // 3. Generar SimilarityPattern
  await upsertSimilarityPattern({
    sourceText: movement.description,
    normalizedText: normalizeText(movement.description),
    targetCustomerId: params.selectedCustomerId,
    patternType: determinePatternType(movement),
    createdBy: 'user_correction'
  });

  // 4. Aprender nuevos atributos si aplica
  await learnNewAttributes(movement, params.selectedCustomerId);
}
```

### 2. Corrección por Rechazo
Usuario rechaza una sugerencia automática.

```typescript
async function handleRejection(params: {
  movementId: string;
  rejectedCustomerId: string;
  reason?: string;
}) {
  // Reducir peso de las reglas que sugirieron este match
  await adjustRuleWeights({
    movementId: params.movementId,
    correctCustomerId: null, // no sabemos quién es
    rejectedCustomerId: params.rejectedCustomerId,
    adjustDown: true
  });

  // Marcar el patrón como menos confiable
  await reducePatternConfidence({
    customerId: params.rejectedCustomerId,
    movementDescription: movement.description
  });
}
```

### 3. Confirmación de Sugerencia
Usuario confirma una sugerencia de baja confianza.

```typescript
async function handleConfirmation(params: {
  movementId: string;
  customerId: string;
}) {
  // Reforzar el patrón
  await upsertSimilarityPattern({
    sourceText: movement.description,
    targetCustomerId: params.customerId,
    occurrences: increment
  });

  // Reforzar pesos de reglas que participaron
  await adjustRuleWeights({
    movementId: params.movementId,
    correctCustomerId: params.customerId,
    adjustUp: true
  });
}
```

### 4. Creación de Nuevo Cliente
El pago es de un cliente que no existe en el sistema.

```typescript
async function handleNewCustomer(params: {
  movementId: string;
  customerData: { legalName: string; rfc?: string; alias?: string };
}) {
  // 1. Crear el cliente
  const customer = await createCustomer(params.customerData);

  // 2. Asociar el movimiento
  await updatePaymentMatch({
    movementId: params.movementId,
    customerId: customer.id,
    status: 'manual_confirmed'
  });

  // 3. Aprender de la descripción
  await createSimilarityPattern({
    sourceText: movement.description,
    targetCustomerId: customer.id,
    createdBy: 'manual'
  });

  // 4. Si hay nombres en la descripción, sugerir como atributos
  await suggestAttributes(movement, customer.id);
}
```

## Aprendizaje de Atributos

Cuando un usuario corrige una identificación, el sistema puede inferir nuevos atributos del cliente:

```typescript
async function learnNewAttributes(
  movement: BankMovement,
  customerId: string
) {
  const description = movement.description;
  const existingAttrs = await getCustomerAttributes(customerId);

  // Si la descripción contiene un nombre que no es la razón social,
  // probablemente es un representante
  const potentialRep = extractPersonName(description);
  if (potentialRep && !isLegalName(potentialRep, customerId)) {
    if (!existingAttrs.find(a =>
      a.attributeType === 'legal_representative' &&
      a.value === potentialRep
    )) {
      await createCustomerAttribute({
        customerId,
        attributeType: 'legal_representative',
        value: potentialRep,
        source: 'learning',
        confidence: 0.7
      });
    }
  }

  // Si hay una referencia de obra
  const potentialObra = extractConstructionSite(description);
  if (potentialObra) {
    // similar logic for obra
  }

  // Si hay un número de cheque
  const checkNum = extractCheckNumber(description);
  if (checkNum) {
    // similar logic for check pattern
  }
}
```

## SimilarityPattern - Algoritmo de Coincidencia

```typescript
async function findSimilarPatterns(
  text: string,
  organizationId: string
): Promise<PatternMatch[]> {
  const normalized = normalizeText(text);
  const tokens = tokenize(normalized);

  // Buscar patrones activos
  const patterns = await db.similarityPattern.findMany({
    where: {
      organizationId,
      isActive: true
    }
  });

  const matches: PatternMatch[] = [];

  for (const pattern of patterns) {
    const patternTokens = tokenize(pattern.normalizedText);

    // Calcular similitud
    const overlap = intersection(tokens, patternTokens);
    const union = union(tokens, patternTokens);
    const jaccard = overlap.length / union.length;

    // Substring match
    const substrMatch =
      normalized.includes(pattern.normalizedText) ||
      pattern.normalizedText.includes(normalized);

    // Score ponderado
    const score = Math.max(
      jaccard * 0.6 + (substrMatch ? 0.4 : 0),
      pattern.similarityScore * 0.5 // peso por relevancia histórica
    );

    if (score >= 0.5) {
      matches.push({
        patternId: pattern.id,
        customerId: pattern.targetCustomerId,
        score,
        patternType: pattern.patternType,
        occurrences: pattern.occurrences
      });
    }
  }

  return matches.sort((a, b) => b.score - a.score);
}
```

## Decaimiento de Patrones (Decay)

Los patrones pierden relevancia con el tiempo si no se usan:

```sql
-- Batch job diario
UPDATE similarity_patterns
SET
  similarity_score = similarity_score * 0.99,  -- decay 1% por día
  is_active = CASE
    WHEN similarity_score * 0.99 < 0.3 THEN false
    ELSE true
  END,
  updated_at = NOW()
WHERE
  is_active = true
  AND last_used_at < NOW() - INTERVAL '30 days';
```

Cuando un patrón se vuelve a usar, su score se restaura:

```typescript
async function reinforcePattern(patternId: string) {
  await db.similarityPattern.update({
    where: { id: patternId },
    data: {
      occurrences: { increment: 1 },
      similarityScore: Math.min(
        currentScore + 0.05, // +5% por uso
        1.0
      ),
      lastUsedAt: new Date(),
      isActive: true
    }
  });
}
```

## Ajuste de Pesos de Reglas

```typescript
async function adjustRuleWeights(params: {
  movementId: string;
  correctCustomerId: string | null;
  rejectedCustomerId?: string;
  adjustUp: boolean;
}) {
  const match = await getPaymentMatch(params.movementId);
  if (!match) return;

  const rulesUsed = match.matchedRules as RuleResult[];
  const orgConfig = await getOrgRulesConfig(match.organizationId);

  for (const ruleResult of rulesUsed) {
    const ruleWeight = orgConfig[ruleResult.ruleId]?.weight ?? 1.0;
    const isCorrect = ruleResult.customerId === params.correctCustomerId;
    const isWrong = ruleResult.customerId === params.rejectedCustomerId;

    if (params.adjustUp && isCorrect) {
      // Incrementar peso de la regla que acertó
      const newWeight = Math.min(ruleWeight + 0.05, 1.5);
      await updateRuleWeight(match.organizationId, ruleResult.ruleId, newWeight);
    } else if (isWrong) {
      // Reducir peso de la regla que falló
      const newWeight = Math.max(ruleWeight - 0.1, 0.1);
      await updateRuleWeight(match.organizationId, ruleResult.ruleId, newWeight);
    }
  }
}
```

## Re-entrenamiento Programado

```sql
-- Batch job semanal
-- 1. Re-generar embeddings para todos los clientes
-- 2. Re-indexar en Qdrant
-- 3. Re-calibrar modelo de confianza
-- 4. Actualizar estadísticas de precisión

CREATE OR REPLACE FUNCTION weekly_retrain() RETURNS void AS $$
BEGIN
  -- Solo si hay nuevos datos desde el último entrenamiento
  IF EXISTS (
    SELECT 1 FROM learning_logs
    WHERE created_at > (
      SELECT COALESCE(MAX(created_at), '1970-01-01')
      FROM training_log
    )
  ) THEN
    INSERT INTO training_log (status, started_at) VALUES ('running', NOW());
    -- Los servicios externos (Python) detectan este registro y ejecutan el re-entrenamiento
  END IF;
END;
$$ LANGUAGE plpgsql;
```

## Dashboard de Aprendizaje

| Métrica | Descripción |
|---------|-------------|
| Patrones Activos | Número de SimilarityPattern activos |
| Correcciones Hoy | LearningLogs de hoy |
| Tasa de Aprendizaje | % de movimientos que mejoraron por aprendizaje |
| Precisión del Modelo | % de aciertos del motor de IA |
| Reglas más Efectivas | Ranking de reglas por precisión histórica |
| Tiempo de Mejora | Cómo ha mejorado la tasa de auto-identificación en el tiempo |
