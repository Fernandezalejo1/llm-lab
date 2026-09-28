import { Injectable } from '@nestjs/common';

interface BankMovementData {
  id: string;
  transactionDate: Date;
  description: string;
  creditAmount: number;
  debitAmount: number;
  status: string;
  customerName?: string;
  confidence?: number;
}

interface ReconciliationSummary {
  periodStart: Date;
  periodEnd: Date;
  totalMovements: number;
  totalCredits: number;
  totalDebits: number;
  conciliatedCount: number;
  pendingCount: number;
  unidentifiedCount: number;
  errorCount: number;
  duplicateCount: number;
  advanceCount: number;
  balanceForwardCount: number;
  details: Array<{
    movementId: string;
    date: Date;
    description: string;
    amount: number;
    type: 'credit' | 'debit';
    status: string;
    customer?: { id?: string; name: string };
    confidence?: number;
    application?: string;
  }>;
}

@Injectable()
export class ReconciliationService {
  async generateReconciliation(params: {
    organizationId: string;
    periodStart: Date;
    periodEnd: Date;
  }): Promise<ReconciliationSummary> {
    const movements = await this.getMovements(params);

    const summary: ReconciliationSummary = {
      periodStart: params.periodStart,
      periodEnd: params.periodEnd,
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
      details: [],
    };

    for (const mov of movements) {
      const status = this.mapStatus(mov.status);
      if (status === 'conciliated') summary.conciliatedCount++;
      else if (status === 'pending') summary.pendingCount++;
      else if (status === 'unidentified') summary.unidentifiedCount++;
      else if (status === 'error') summary.errorCount++;
      else if (status === 'duplicate') summary.duplicateCount++;
      else if (status === 'advance') summary.advanceCount++;
      else if (status === 'balance_forward') summary.balanceForwardCount++;

      summary.totalCredits += mov.creditAmount;
      summary.totalDebits += mov.debitAmount;

      summary.details.push({
        movementId: mov.id,
        date: mov.transactionDate,
        description: mov.description,
        amount: mov.creditAmount || mov.debitAmount,
        type: mov.creditAmount > 0 ? 'credit' : 'debit',
        status,
        customer: mov.customerName ? { name: mov.customerName } : undefined,
        confidence: mov.confidence,
      });
    }

    return summary;
  }

  private mapStatus(dbStatus: string): string {
    const map: Record<string, string> = {
      reconciled: 'conciliated',
      applied: 'conciliated',
      identified: 'pending',
      pending: 'unidentified',
      unidentified: 'unidentified',
      error: 'error',
      duplicate: 'duplicate',
    };
    return map[dbStatus] || 'unidentified';
  }

  private async getMovements(params: {
    organizationId: string;
    periodStart: Date;
    periodEnd: Date;
  }): Promise<BankMovementData[]> {
    return [];
  }
}
