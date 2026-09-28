import { Injectable } from '@nestjs/common';
import {
  ApplicationDecision,
  ApplicationType,
} from '@contabilia/shared-types';

interface OpenInvoiceData {
  id: string;
  invoiceNumber: string;
  customerId: string;
  balance: number;
  total: number;
  issueDate: Date;
  dueDate: Date;
  isOverdue: boolean;
  currency: string;
}

interface CreditNoteData {
  id: string;
  availableAmount: number;
}

@Injectable()
export class CashApplicationService {
  async determineApplication(
    customerId: string,
    amount: number,
    currency: string,
    openInvoices: OpenInvoiceData[],
    creditNotes: CreditNoteData[],
    existingBalance: number = 0,
  ): Promise<ApplicationDecision> {
    const effectiveAmount = amount + existingBalance;

    if (openInvoices.length === 0) {
      return this.createAdvanceDecision(amount, effectiveAmount);
    }

    // Intentar combinaciones exactas
    const exactMatch = openInvoices.find((inv) => Math.abs(inv.balance - effectiveAmount) < 0.01);
    if (exactMatch) {
      return this.createFullPaymentDecision(exactMatch, amount, effectiveAmount);
    }

    // Combinación exacta múltiple
    const multiMatch = this.findSubsetSum(openInvoices, effectiveAmount);
    if (multiMatch) {
      return this.createMultiplePaymentDecision(multiMatch, amount, effectiveAmount);
    }

    // Combinación con notas de crédito
    if (creditNotes.length > 0) {
      const totalCN = creditNotes.reduce((sum, cn) => sum + cn.availableAmount, 0);
      const adjustedAmount = effectiveAmount + totalCN;
      const cnMatch = this.findSubsetSum(openInvoices, adjustedAmount);
      if (cnMatch) {
        return this.createMultiplePaymentDecision(cnMatch, amount, effectiveAmount, creditNotes);
      }
    }

    // FIFO parcial por defecto
    return this.applyFIFOPartial(openInvoices, effectiveAmount, amount);
  }

  private findSubsetSum(invoices: OpenInvoiceData[], target: number): OpenInvoiceData[] | null {
    const sorted = [...invoices].sort((a, b) => b.balance - a.balance);

    // Greedy first
    const greedy = this.tryGreedy(sorted, target);
    if (greedy) return greedy;

    // DP for small sets
    if (invoices.length <= 20) {
      return this.subsetSumDP(invoices, target);
    }

    return null;
  }

  private tryGreedy(invoices: OpenInvoiceData[], target: number): OpenInvoiceData[] | null {
    let sum = 0;
    const selected: OpenInvoiceData[] = [];

    for (const inv of invoices) {
      if (sum + inv.balance <= target + 0.01) {
        selected.push(inv);
        sum += inv.balance;
      }
      if (Math.abs(sum - target) < 0.01) return selected;
    }

    return null;
  }

  private subsetSumDP(invoices: OpenInvoiceData[], target: number): OpenInvoiceData[] | null {
    const n = invoices.length;
    const dp: boolean[][] = Array.from({ length: n + 1 }, () => Array(Math.floor(target) + 1).fill(false));
    dp[0][0] = true;

    for (let i = 1; i <= n; i++) {
      const amount = Math.floor(invoices[i - 1].balance);
      for (let w = 0; w <= Math.floor(target); w++) {
        dp[i][w] = dp[i - 1][w];
        if (w >= amount && dp[i - 1][w - amount]) {
          dp[i][w] = true;
        }
      }
    }

    if (!dp[n][Math.floor(target)]) return null;

    const result: OpenInvoiceData[] = [];
    let w = Math.floor(target);
    for (let i = n; i > 0 && w > 0; i--) {
      if (!dp[i - 1][w]) {
        result.push(invoices[i - 1]);
        w -= Math.floor(invoices[i - 1].balance);
      }
    }

    return result;
  }

  private applyFIFOPartial(
    invoices: OpenInvoiceData[],
    effectiveAmount: number,
    originalAmount: number,
  ): ApplicationDecision {
    const sorted = [...invoices].sort((a, b) => {
      if (a.isOverdue && !b.isOverdue) return -1;
      if (!a.isOverdue && b.isOverdue) return 1;
      return a.issueDate.getTime() - b.issueDate.getTime();
    });

    let remaining = effectiveAmount;
    const invoiceApps: Array<{
      invoiceId: string;
      amountApplied: number;
      previousBalance: number;
      newBalance: number;
      isPartial: boolean;
    }> = [];
    let totalApplied = 0;

    for (const inv of sorted) {
      if (remaining <= 0) break;
      const amountToApply = Math.min(remaining, inv.balance);
      invoiceApps.push({
        invoiceId: inv.id,
        amountApplied: amountToApply,
        previousBalance: inv.balance,
        newBalance: inv.balance - amountToApply,
        isPartial: amountToApply < inv.balance,
      });
      totalApplied += amountToApply;
      remaining -= amountToApply;
    }

    const finalRemaining = originalAmount - totalApplied;
    const type: ApplicationType = remaining > 0 && invoiceApps.length > 1
      ? 'partial'
      : invoiceApps.length > 1 ? 'multiple' : 'partial';

    return {
      type,
      totalAmount: originalAmount,
      totalApplied,
      remaining: Math.max(0, finalRemaining),
      invoiceApplications: invoiceApps,
      details: finalRemaining > 0
        ? `Aplicado $${totalApplied.toFixed(2)}. Sobrante: $${finalRemaining.toFixed(2)} registrado como saldo a favor`
        : `Aplicación completa de $${totalApplied.toFixed(2)}`,
    };
  }

  private createFullPaymentDecision(
    invoice: OpenInvoiceData,
    originalAmount: number,
    effectiveAmount: number,
  ): ApplicationDecision {
    return {
      type: 'full',
      totalAmount: originalAmount,
      totalApplied: invoice.balance,
      remaining: Math.max(0, originalAmount - invoice.balance),
      invoiceApplications: [{
        invoiceId: invoice.id,
        amountApplied: invoice.balance,
        previousBalance: invoice.balance,
        newBalance: 0,
        isPartial: false,
      }],
      details: `Pago exacto de factura ${invoice.invoiceNumber}`,
    };
  }

  private createMultiplePaymentDecision(
    invoices: OpenInvoiceData[],
    originalAmount: number,
    effectiveAmount: number,
    creditNotes?: CreditNoteData[],
  ): ApplicationDecision {
    const totalApplied = invoices.reduce((s, inv) => s + inv.balance, 0);
    return {
      type: 'multiple',
      totalAmount: originalAmount,
      totalApplied,
      remaining: Math.max(0, originalAmount - totalApplied),
      invoiceApplications: invoices.map((inv) => ({
        invoiceId: inv.id,
        amountApplied: inv.balance,
        previousBalance: inv.balance,
        newBalance: 0,
        isPartial: false,
      })),
      details: `Combinación de ${invoices.length} facturas${creditNotes ? ' con notas de crédito' : ''}`,
    };
  }

  private createAdvanceDecision(
    originalAmount: number,
    effectiveAmount: number,
  ): ApplicationDecision {
    return {
      type: 'advance',
      totalAmount: originalAmount,
      totalApplied: 0,
      remaining: originalAmount,
      invoiceApplications: [],
      details: `No hay facturas abiertas. Monto registrado como anticipo: $${originalAmount.toFixed(2)}`,
    };
  }
}
