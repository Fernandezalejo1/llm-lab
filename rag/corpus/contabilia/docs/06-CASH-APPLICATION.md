# CONTABILIA - Motor de Aplicación de Pagos

## Filosofía

Una vez identificado el cliente, el sistema debe determinar automáticamente qué facturas aplicar. Debe considerar todas las combinaciones posibles, anticipos, saldos a favor, notas de crédito/débito, y diferencias.

## Pipeline de Aplicación

```
Cliente Identificado + Monto del Pago
        │
        ▼
┌────────────────────────────────────┐
│ 1. Obtener Facturas Abiertas       │
│    - Status != paid, not cancelled  │
│    - Balance > 0                    │
│    - Orden: vencimiento DESC,       │
│      fecha ASC (FIFO)              │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 2. Verificar Saldos a Favor        │
│    - Existe balance previo?         │
│    - Aplicar saldo si existe        │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 3. Verificar Anticipos             │
│    - Tiene anticipos registrados?   │
│    - Compensar si aplica           │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 4. Buscar Combinaciones            │
│    - Combinación exacta            │
│    - Combinación parcial           │
│    - FIFO por defecto              │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 5. Notas de Crédito/Débito         │
│    - NC disponibles?               │
│    - ND pendientes?                │
│    - Compensar                     │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 6. Determinar Tipo de Aplicación   │
│    - full, partial, multiple,      │
│      advance, balance_forward      │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 7. Ejecutar Aplicación             │
│    - Actualizar balances           │
│    - Crear PaymentApplication      │
│    - Crear AppliedInvoice(s)       │
│    - Actualizar estado movimiento  │
└───────────┬────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│ 8. Notificar Resultado             │
│    - Dashboard actualizado         │
│    - Alertas si hay diferencias    │
└────────────────────────────────────┘
```

## Algoritmo Principal

```typescript
async function determineApplication(
  customerId: string,
  amount: number,
  currency: string,
  context: ApplicationContext
): Promise<ApplicationDecision> {
  // 1. Obtener facturas abiertas
  const openInvoices = await getOpenInvoices(customerId, currency);

  // 2. Verificar saldo a favor
  const balance = await getCustomerBalance(customerId, currency);
  const effectiveAmount = amount + (balance?.amount ?? 0);

  // 3. Verificar anticipos
  const advances = await getCustomerAdvances(customerId, currency);
  const advanceAmount = advances.reduce((sum, a) => sum + a.amount, 0);

  // 4. Obtener notas de crédito disponibles
  const creditNotes = await getAvailableCreditNotes(customerId);

  // Si no hay facturas abiertas
  if (openInvoices.length === 0) {
    if (balance && balance.amount > 0) {
      return {
        type: 'balance_forward',
        totalAmount: amount,
        appliedAmount: amount,
        difference: 0,
        details: `Saldo a favor actualizado: $${(balance.amount + amount).toFixed(2)}`
      };
    }
    return {
      type: 'advance',
      totalAmount: amount,
      appliedAmount: 0,
      difference: amount,
      details: 'No hay facturas abiertas. Registrado como anticipo.'
    };
  }

  // 5. Intentar combinaciones (exactas y parciales)
  const combination = await findInvoiceCombination(
    openInvoices,
    effectiveAmount,
    creditNotes
  );

  if (combination.type !== 'no_match') {
    return combination;
  }

  // 6. Si no hay combinación, aplicar FIFO parcial
  return applyFIFOPartial(openInvoices, effectiveAmount);
}
```

## Búsqueda de Combinaciones

```typescript
async function findInvoiceCombination(
  invoices: OpenInvoice[],
  amount: number,
  creditNotes: CreditNote[]
): Promise<CombinationResult> {
  // Fase 1: Combinación exacta (una factura)
  const exactMatch = invoices.find(inv => inv.balance === amount);
  if (exactMatch) {
    return {
      type: 'full',
      invoiceId: exactMatch.id,
      amountApplied: amount,
      remaining: 0,
      details: `Pago exacto de factura ${exactMatch.invoiceNumber}`
    };
  }

  // Fase 2: Combinación exacta (múltiples facturas)
  const multiMatch = findSubsetSum(invoices, amount);
  if (multiMatch) {
    return {
      type: 'multiple',
      invoices: multiMatch,
      amountApplied: amount,
      remaining: 0,
      details: `Combinación de ${multiMatch.length} facturas`
    };
  }

  // Fase 3: Combinación con notas de crédito
  if (creditNotes.length > 0) {
    const totalCN = creditNotes.reduce((s, cn) => s + cn.availableAmount, 0);
    const adjustedAmount = amount + totalCN;
    const cnMatch = findSubsetSum(invoices, adjustedAmount);
    if (cnMatch) {
      return {
        type: 'multiple',
        invoices: cnMatch,
        creditNotes: creditNotes,
        amountApplied: amount,
        remaining: 0,
        details: `Combinación con notas de crédito`
      };
    }
  }

  // Fase 4: Pago parcial
  const partialMatch = invoices.find(inv => amount < inv.balance);
  if (partialMatch) {
    return {
      type: 'partial',
      invoiceId: partialMatch.id,
      amountApplied: amount,
      remaining: partialMatch.balance - amount,
      details: `Pago parcial de factura ${partialMatch.invoiceNumber}. Pendiente: $${(partialMatch.balance - amount).toFixed(2)}`
    };
  }

  // Fase 5: Pago mayor (sobrante)
  const smallestInvoice = invoices[invoices.length - 1]; // la más reciente
  if (amount > smallestInvoice.balance) {
    return {
      type: 'full_with_balance',
      invoiceId: smallestInvoice.id,
      amountApplied: smallestInvoice.balance,
      overpayment: amount - smallestInvoice.balance,
      details: `Pago completo con saldo a favor de $${(amount - smallestInvoice.balance).toFixed(2)}`
    };
  }

  return { type: 'no_match' };
}
```

## Subset Sum (Combinación de Facturas)

Para pagos que cubren múltiples facturas. Se usa un algoritmo de subset sum optimizado:

```typescript
function findSubsetSum(
  invoices: OpenInvoice[],
  target: number
): OpenInvoice[] | null {
  // Ordenar por monto descendente para priorizar facturas grandes
  const sorted = [...invoices].sort((a, b) => b.balance - a.balance);

  // Intentar primero con facturas grandes (caso común)
  const result = tryGreedy(sorted, target);
  if (result) return result;

  // Si falla, usar DP para subsets exactos (limitado a N facturas)
  if (invoices.length <= 20) {
    return subsetSumDP(invoices, target);
  }

  // Para muchos invoices, usar aproximación greedy
  return greedyApproximation(sorted, target);
}

function tryGreedy(invoices: OpenInvoice[], target: number): OpenInvoice[] | null {
  let sum = 0;
  const selected: OpenInvoice[] = [];

  for (const inv of invoices) {
    if (sum + inv.balance <= target) {
      selected.push(inv);
      sum += inv.balance;
    }
    if (sum === target) return selected;
  }

  return null;
}
```

## FIFO por Defecto

Cuando no hay combinación exacta, se aplica FIFO (First In, First Out):

```typescript
async function applyFIFOPartial(
  invoices: OpenInvoice[],
  amount: number
): Promise<ApplicationDecision> {
  // Ordenar: vencidas primero, luego por fecha de emisión ASC
  const sorted = [...invoices].sort((a, b) => {
    if (a.isOverdue && !b.isOverdue) return -1;
    if (!a.isOverdue && b.isOverdue) return 1;
    return a.issueDate.getTime() - b.issueDate.getTime();
  });

  let remaining = amount;
  const applied: AppliedInvoice[] = [];

  for (const inv of sorted) {
    if (remaining <= 0) break;

    const amountToApply = Math.min(remaining, inv.balance);
    applied.push({
      invoiceId: inv.id,
      amountApplied: amountToApply,
      previousBalance: inv.balance,
      newBalance: inv.balance - amountToApply,
      isPartial: amountToApply < inv.balance
    });

    remaining -= amountToApply;
  }

  return {
    type: remaining === 0 ? 'full_multiple' : 'partial_multiple',
    invoiceApplications: applied,
    totalApplied: amount - remaining,
    remaining: remaining,
    details: remaining > 0
      ? `Sobrante de $${remaining.toFixed(2)} registrado como saldo a favor`
      : 'Aplicación completa'
  };
}
```

## Tipos de Aplicación

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `full` | Pago exacto de una factura | Paga $10,000 = factura de $10,000 |
| `partial` | Pago menor a una factura | Paga $5,000 de factura $10,000 |
| `multiple` | Pago exacto de varias facturas | Paga $15,000 = $10,000 + $5,000 |
| `advance` | Pago sin factura asociada | Anticipo de $20,000 |
| `credit_note` | Nota de crédito aplicada | NC de $2,000 + pago de $8,000 = factura $10,000 |
| `debit_note` | Nota de débito aplicada | ND de $500 adicional |
| `balance_forward` | Saldo a favor existente | Saldo previo $3,000 + pago $7,000 = factura $10,000 |

## Manejo de Diferencias

```typescript
// Después de aplicar, determinar el estado de la diferencia
function classifyDifference(applied: number, total: number): {
  type: 'none' | 'overpayment' | 'underpayment' | 'exchange_diff' | 'discount';
  amount: number;
  reason: string;
} {
  const diff = total - applied;

  if (Math.abs(diff) < 0.01) {
    return { type: 'none', amount: 0, reason: 'Pago exacto' };
  }

  if (diff > 0) {
    return {
      type: 'underpayment',
      amount: diff,
      reason: `Pago incompleto: faltan $${diff.toFixed(2)}`
    };
  }

  return {
    type: 'overpayment',
    amount: Math.abs(diff),
    reason: `Pago en exceso: sobran $${Math.abs(diff).toFixed(2)} registrado como saldo a favor`
  };
}
```

## Ejecución de la Aplicación (Transaccional)

```typescript
async function executeApplication(
  paymentMatchId: string,
  decision: ApplicationDecision
): Promise<PaymentApplication> {
  return await db.$transaction(async (tx) => {
    // 1. Crear PaymentApplication
    const application = await tx.paymentApplication.create({
      data: {
        paymentMatchId,
        applicationType: decision.type,
        totalAmount: decision.totalAmount,
        appliedAmount: decision.totalApplied,
        difference: decision.remaining,
        differenceReason: decision.remaining > 0 ? 'overpayment' : null
      }
    });

    // 2. Crear AppliedInvoices y actualizar balances
    for (const applied of decision.invoiceApplications) {
      await tx.appliedInvoice.create({
        data: {
          applicationId: application.id,
          invoiceId: applied.invoiceId,
          amountApplied: applied.amountApplied,
          previousBalance: applied.previousBalance,
          newBalance: applied.newBalance,
          isPartial: applied.isPartial
        }
      });

      // Actualizar balance de la factura
      await tx.invoice.update({
        where: { id: applied.invoiceId },
        data: {
          balance: applied.newBalance,
          status: applied.newBalance === 0 ? 'paid' : 'partial',
          paymentDate: new Date()
        }
      });
    }

    // 3. Actualizar saldo a favor si aplica
    if (decision.remaining > 0) {
      await upsertCustomerBalance({
        customerId,
        balanceType: 'credit',
        amount: decision.remaining,
        operation: 'increment'
      });
    }

    // 4. Actualizar estado del movimiento
    await tx.bankMovement.update({
      where: { id: movementId },
      data: { status: 'applied' }
    });

    // 5. Audit log
    await tx.auditLog.create({
      data: {
        entityType: 'payment_application',
        entityId: application.id,
        action: 'created',
        newState: decision as any
      }
    });

    return application;
  });
}
```
