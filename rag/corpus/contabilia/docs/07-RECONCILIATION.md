# CONTABILIA - Motor de Conciliación

## Estados de Conciliación

| Estado | Color | Descripción |
|--------|-------|-------------|
| `Conciliado` | Verde | Movimiento bancario = factura aplicada, todo en orden |
| `Pendiente` | Amarillo | Identificado pero pendiente de aplicar |
| `Sin Identificar` | Rojo | No se pudo determinar el cliente |
| `Error` | Rojo oscuro | Error en procesamiento (dato inválido, factura cancelada) |
| `Duplicado` | Naranja | Posible duplicado de otro movimiento |
| `Anticipo` | Azul | Identificado como anticipo de cliente |
| `Saldo a Favor` | Celeste | Aplicado con saldo sobrante |
| `Saldo Pendiente` | Naranja | Aplicado parcialmente, queda saldo |

## Generación Automática

```typescript
async function generateReconciliation(params: {
  organizationId: string;
  bankStatementId?: string;
  periodStart: Date;
  periodEnd: Date;
}): Promise<Reconciliation> {
  const movements = await getMovementsInPeriod(
    params.organizationId,
    params.periodStart,
    params.periodEnd
  );

  const summary = {
    totalMovements: movements.length,
    totalCredits: 0,
    totalDebits: 0,
    conciliatedCount: 0,
    pendingCount: 0,
    unidentifiedCount: 0,
    errorCount: 0,
    duplicateCount: 0,
    advanceCount: 0,
    balanceForwardCount: 0,
    details: []
  };

  for (const movement of movements) {
    const status = reconcileStatus(movement);
    summary[`${status}Count`]++;
    if (movement.creditAmount) summary.totalCredits += movement.creditAmount;
    if (movement.debitAmount) summary.totalDebits += movement.debitAmount;

    summary.details.push({
      movementId: movement.id,
      date: movement.transactionDate,
      description: movement.description,
      amount: movement.creditAmount || movement.debitAmount,
      type: movement.creditAmount ? 'credit' : 'debit',
      status,
      customer: movement.paymentMatch?.customer
        ? { id: movement.paymentMatch.customer.id, name: movement.paymentMatch.customer.legalName }
        : null,
      confidence: movement.paymentMatch?.confidence,
      application: movement.paymentMatch?.application
        ? formatApplication(movement.paymentMatch.application)
        : null
    });
  }

  return await db.reconciliation.create({
    data: {
      organizationId: params.organizationId,
      bankStatementId: params.bankStatementId,
      periodStart: params.periodStart,
      periodEnd: params.periodEnd,
      ...summary,
      generatedAt: new Date()
    }
  });
}

function reconcileStatus(movement: BankMovement): string {
  switch (movement.status) {
    case 'reconciled': return 'conciliated';
    case 'applied': return 'conciliated';
    case 'identified': return 'pending';
    case 'pending': return 'unidentified';
    case 'unidentified': return 'unidentified';
    case 'error': return 'error';
    case 'duplicate': return 'duplicate';
    default: return 'unidentified';
  }
}
```

## Detección de Duplicados

```typescript
async function detectDuplicates(
  movement: BankMovement,
  periodMovements: BankMovement[]
): Promise<DuplicateInfo | null> {
  for (const other of periodMovements) {
    if (other.id === movement.id) continue;

    // Criterio 1: Mismo monto
    const sameAmount = Math.abs(
      (movement.creditAmount || movement.debitAmount) -
      (other.creditAmount || other.debitAmount)
    ) < 0.01;

    if (!sameAmount) continue;

    // Criterio 2: Referencia similar o misma descripción
    const sameRef = movement.reference &&
      other.reference &&
      movement.reference === other.reference;

    const similarDesc = movement.description &&
      other.description &&
      trigramSimilarity(movement.description, other.description) > 0.8;

    if (!sameRef && !similarDesc) continue;

    // Criterio 3: Fecha cercana (≤ 3 días hábiles)
    const daysDiff = Math.abs(
      dayjs(movement.transactionDate).diff(dayjs(other.transactionDate), 'day')
    );

    if (daysDiff <= 3) {
      return {
        isDuplicate: true,
        originalMovementId: other.id,
        confidence: sameRef ? 0.95 : 0.85,
        reason: sameRef
          ? `Misma referencia y monto que movimiento del ${other.transactionDate}`
          : `Descripción y monto similares a movimiento del ${other.transactionDate}`
      };
    }
  }

  return null;
}
```

## Exportación de Conciliación

```typescript
// Excel / CSV
async function exportReconciliation(
  reconciliationId: string,
  format: 'excel' | 'csv'
): Promise<Buffer> {
  const reconciliation = await getReconciliationDetail(reconciliationId);

  const rows = reconciliation.details.map(d => ({
    Fecha: formatDate(d.date),
    Descripción: d.description,
    Monto: d.amount,
    Tipo: d.type === 'credit' ? 'Abono' : 'Cargo',
    Estado: translateStatus(d.status),
    Cliente: d.customer?.name ?? '',
    Confianza: d.confidence ? `${d.confidence}%` : '',
    Aplicación: d.application ?? '',
    Diferencia: d.difference ?? ''
  }));

  if (format === 'csv') {
    return generateCSV(rows);
  }
  return generateExcel(rows, {
    title: `Conciliación ${formatDateRange(reconciliation.periodStart, reconciliation.periodEnd)}`
  });
}

// PDF (resumen ejecutivo)
async function exportReconciliationPDF(id: string): Promise<Buffer> {
  const reconciliation = await getReconciliationDetail(id);

  return generatePDF({
    template: 'reconciliation',
    data: {
      period: reconciliation.period,
      summary: {
        totalMovements: reconciliation.totalMovements,
        conciliated: reconciliation.conciliatedCount,
        unidentified: reconciliation.unidentifiedCount,
        errors: reconciliation.errorCount,
        duplicates: reconciliation.duplicateCount
      },
      movements: reconciliation.details
    }
  });
}
```
