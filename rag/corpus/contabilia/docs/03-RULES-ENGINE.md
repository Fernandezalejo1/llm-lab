# CONTABILIA - Motor de Reglas

## Filosofía

El motor de reglas es el primer respondedor del sistema. Es determinístico, rápido y transparente. Cada regla produce un resultado con evidencia y confianza. El motor consolida los resultados de todas las reglas para producir un ranking de candidatos.

## Arquitectura del Motor

```
┌─────────────────────────────────────────────┐
│           RulesEngineService                  │
│                                              │
│  ┌─────────┐ ┌─────────┐ ┌───────────────┐  │
│  │ Registry│ │ Executor│ │ Consolidator   │  │
│  │ (carga  │ │ (ejecuta│ │ (agrupa por    │  │
│  │  reglas)│ │  reglas)│ │  customer_id)  │  │
│  └─────────┘ └────┬────┘ └───────┬───────┘  │
│                   │              │           │
│  ┌────────────────┴──────────────┴───────┐   │
│  │        RuleInterface                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌───────┐  │   │
│  │  │ R01      │ │ R02      │ │ ...   │  │   │
│  │  │ ExactName│ │ PartName │ │ R13   │  │   │
│  │  └──────────┘ └──────────┘ └───────┘  │   │
│  └────────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Interface de una Regla

```typescript
interface Rule {
  id: string;
  name: string;
  description: string;
  weight: number;        // peso en la confianza final (0.0 - 1.0)
  priority: number;      // orden de ejecución (menor = primero)
  enabled: boolean;
  config: Record<string, any>;

  evaluate(
    movement: NormalizedMovement,
    context: RuleContext
  ): Promise<RuleResult>;
}

interface RuleResult {
  matched: boolean;
  customerId?: string;
  confidence: number;        // 0.0 - 1.0
  evidence: EvidenceItem[];  // qué se encontró
  debug?: Record<string, any>;
}

interface EvidenceItem {
  type: string;              // 'exact_match', 'partial_match', 'semantic', etc.
  source: string;            // qué campo se usó (description, reference, etc.)
  value: string;             // valor encontrado
  matched: string;           // con qué coincidió
  explanation: string;       // explicación en lenguaje natural
}
```

## Procesador de Confianza Compuesto

```
Confianza_Final = Σ(Peso_Regla × Confianza_Regla) / Σ(Peso_Regla)

Donde:
- Peso_Regla: importancia relativa (configurable por organización)
- Confianza_Regla: 0.0 - 1.0 según qué tan bien coincidió

Los pesos se ajustan automáticamente según precisión histórica:
- Si una regla acierta frecuentemente → su peso aumenta
- Si falla frecuentemente → su peso disminuye
- Recalibración semanal vía batch job
```

## Umbrales de Decisión

| Confianza | Acción |
|-----------|--------|
| ≥ 95% | Auto-aplicar, no requiere revisión |
| ≥ 85% | Auto-aplicar, marcar para revisión opcional |
| ≥ 70% | Sugerir, requiere confirmación del usuario |
| ≥ 50% | Mostrar como candidato secundario |
| < 50% | Descartar |

## Catálogo de Reglas

### R01: Coincidencia Exacta de Razón Social
- **Input**: `description`, `reference`
- **Proceso**: Comparación exacta (case-insensitive, sin acentos) contra `customers.legal_name`
- **Confianza**: 0.95
- **Peso**: 1.0
- **Ejemplo**: "CONSTRUCCIONES ABC SA DE CV" → match exacto

### R02: Coincidencia Parcial de Razón Social
- **Input**: `description`
- **Proceso**: Token matching. Divide el texto en tokens, busca clientes que contengan ≥60% de los tokens
- **Confianza**: 0.60 - 0.85 (según % de tokens matching)
- **Peso**: 0.9
- **Ejemplo**: "ABC CONSTRUCCIONES" → match parcial con "CONSTRUCCIONES ABC SA DE CV"

### R03: Alias Conocido
- **Input**: `description`, `reference`
- **Proceso**: Busca en `customer_attributes` donde `attribute_type = 'known_alias'` y en `similarity_patterns` donde `pattern_type = 'name_alias'`
- **Confianza**: 0.90
- **Peso**: 0.95
- **Ejemplo**: "JUAN PEREZ" → en similarity_patterns está asociado a "CONSTRUCTORA ABC"

### R04: Empresa Relacionada
- **Input**: `description`
- **Proceso**: Busca en `customer_attributes` donde `attribute_type = 'related_company'`
- **Confianza**: 0.85
- **Peso**: 0.85
- **Ejemplo**: "EMPRESA MADRE SA" → related_company de "FILIAL ABC"

### R05: Representante / Dueño / Director
- **Input**: `description`, `reference`
- **Proceso**: Busca en `customer_attributes` donde `attribute_type IN ('legal_representative', 'owner', 'director')`
- **Confianza**: 0.80
- **Peso**: 0.85
- **Ejemplo**: "LIC. JUAN PEREZ" → legal_representative de "CONSTRUCTORA ABC"

### R06: Cuenta Bancaria / CLABE Conocida
- **Input**: `reference`, `raw_data`
- **Proceso**: Busca en `customer_attributes` donde `attribute_type IN ('bank_account', 'clabe')`
- **Confianza**: 0.95
- **Peso**: 1.0
- **Ejemplo**: CLABE 012180015798345678 → cliente CONSTRUCTORA ABC

### R07: Cheque Conocido
- **Input**: `check_number`, `description`
- **Proceso**: Busca en `similarity_patterns` donde `pattern_type = 'check_to_client'` o en `customer_attributes` con `attribute_type = 'check_pattern'`
- **Confianza**: 0.85
- **Peso**: 0.8
- **Ejemplo**: CHEQUE 45012 → previamente asociado a CONSTRUCTORA ABC

### R08: Obra Conocida
- **Input**: `description`
- **Proceso**: Busca en `customer_attributes` donde `attribute_type IN ('construction_site', 'site_address')`
- **Confianza**: 0.75
- **Peso**: 0.75
- **Ejemplo**: "EDIFICIO CORPORATIVO ZONA SUR" → construction_site de "DESARROLLADORA XYZ"

### R09: Dirección Conocida
- **Input**: `description`
- **Proceso**: Busca en `customer_attributes` donde `attribute_type IN ('address', 'site_address')`
- **Confianza**: 0.65
- **Peso**: 0.7
- **Ejemplo**: "AV REFORMA 123 CDMX" → address de "CLIENTE ABC"

### R10: Frecuencia de Pago / Fecha Cercana
- **Input**: `transaction_date`, historial del cliente
- **Proceso**: Calcula qué clientes tienen patrón de pago en fechas similares (ej: todos los días 15)
- **Confianza**: 0.60 - 0.70
- **Peso**: 0.6
- **Ejemplo**: Hoy es 15 de enero y el cliente X siempre paga los días 15

### R11: Historial de Pagos (Descripción Similar)
- **Input**: `description` completa
- **Proceso**: Busca movimientos previos con descripción similar (usando trigramas) que ya fueron identificados
- **Confianza**: 0.80 - 0.90
- **Peso**: 0.9
- **Ejemplo**: "TRANSFERENCIA SPEI JUAN PEREZ CONSTRUCCIONES" → match con movimiento previo

### R12: Referencia Numérica (Factura, Contrato)
- **Input**: `reference`, `description`
- **Proceso**: Extrae números que parecen facturas (ej: FAC-1234, 1234) y busca en invoices
- **Confianza**: 0.70
- **Peso**: 0.75
- **Ejemplo**: "PAGO FACTURA 1234" → busca invoice 1234 y asigna al customer de esa factura

### R13: RFC en Referencia
- **Input**: `description`, `reference`
- **Proceso**: Extrae potenciales RFCs (formato: XXXX-XXXXXX-XXX) y busca en customers
- **Confianza**: 0.90
- **Peso**: 0.95
- **Ejemplo**: "ABC121212XXX" → RFC de CONSTRUCTORA ABC

## Pseudocódigo del Motor

```typescript
async function executeRules(
  movement: NormalizedMovement,
  context: RuleContext
): Promise<ConsolidatedCandidate[]> {
  const results: RuleResult[] = [];

  // 1. Ejecutar todas las reglas activas en orden de prioridad
  for (const rule of rulesRegistry.getActiveRules()) {
    const result = await rule.evaluate(movement, context);
    results.push(result);

    // Guardar análisis individual
    await saveMovementAnalysis({
      movementId: movement.id,
      analysisType: 'rule_evaluation',
      result: {
        ruleId: rule.id,
        ruleName: rule.name,
        matched: result.matched,
        confidence: result.confidence,
        customerId: result.customerId,
        evidence: result.evidence
      }
    });
  }

  // 2. Consolidar resultados por customerId
  const grouped = new Map<string, ConsolidatingCandidate>();

  for (const result of results.filter(r => r.matched)) {
    const key = result.customerId!;
    if (!grouped.has(key)) {
      grouped.set(key, {
        customerId: key,
        matchedRules: [],
        totalWeight: 0,
        weightedConfidence: 0,
        allEvidence: []
      });
    }
    const entry = grouped.get(key)!;
    entry.matchedRules.push(result);
    entry.totalWeight += ruleWeights.get(result.ruleId) ?? 1;
    entry.weightedConfidence += result.confidence * (ruleWeights.get(result.ruleId) ?? 1);
    entry.allEvidence.push(...result.evidence);
  }

  // 3. Calcular confianza consolidada
  const candidates: ConsolidatedCandidate[] = [];
  for (const [, entry] of grouped) {
    candidates.push({
      customerId: entry.customerId,
      confidence: entry.totalWeight > 0
        ? entry.weightedConfidence / entry.totalWeight
        : 0,
      matchedRules: entry.matchedRules,
      evidence: entry.allEvidence
    });
  }

  // 4. Ordenar por confianza descendente
  return candidates.sort((a, b) => b.confidence - a.confidence);
}
```

## Configuración por Organización

Cada organización puede:
- Activar/desactivar reglas individualmente
- Ajustar pesos de reglas
- Configurar umbrales de auto-aplicación
- Agregar reglas personalizadas

```json
{
  "rules_config": {
    "R01": { "enabled": true, "weight": 1.0 },
    "R02": { "enabled": true, "weight": 0.9 },
    "R03": { "enabled": true, "weight": 0.95 },
    "R04": { "enabled": true, "weight": 0.85 },
    "R05": { "enabled": true, "weight": 0.85 },
    "R06": { "enabled": true, "weight": 1.0 },
    "R07": { "enabled": true, "weight": 0.8 },
    "R08": { "enabled": true, "weight": 0.75 },
    "R09": { "enabled": true, "weight": 0.7 },
    "R10": { "enabled": true, "weight": 0.6 },
    "R11": { "enabled": true, "weight": 0.9 },
    "R12": { "enabled": true, "weight": 0.75 },
    "R13": { "enabled": true, "weight": 0.95 }
  },
  "thresholds": {
    "auto_accept": 0.95,
    "auto_accept_with_review": 0.85,
    "suggestion": 0.70,
    "candidate": 0.50
  }
}
```
