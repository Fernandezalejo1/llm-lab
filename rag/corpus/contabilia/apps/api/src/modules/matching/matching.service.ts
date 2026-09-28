import { Injectable } from '@nestjs/common';
import { PrismaService } from '@contabilia/database';

@Injectable()
export class MatchingService {
  constructor(private prisma: PrismaService) {}

  async confirmMatch(movementId: string, customerId: string) {
    const movement = await this.prisma.bankMovement.findUnique({ where: { id: movementId } });
    if (!movement) throw new Error('Movement not found');

    const invoices = await this.prisma.invoice.findMany({
      where: { customerId, status: 'pending', organizationId: movement.organizationId },
    });

    const amount = movement.creditAmount || movement.debitAmount;

    let matchedInvoice = null;
    for (const inv of invoices) {
      if (Math.abs(inv.balance - amount) < 0.01) {
        matchedInvoice = inv;
        break;
      }
    }

    if (!matchedInvoice && invoices.length > 0) {
      matchedInvoice = invoices[0];
    }

    const match = await this.prisma.paymentMatch.create({
      data: {
        bankMovementId: movementId,
        organizationId: movement.organizationId,
        customerId,
        engineVersion: '1.0',
        matchStrategy: 'manual',
        confidence: matchedInvoice ? 1.0 : 0.5,
        status: 'manual_confirmed',
        executedRules: [],
        matchedRules: [],
        evidence: {},
      },
    });

    await this.prisma.bankMovement.update({
      where: { id: movementId },
      data: { status: 'reconciled' },
    });

    if (matchedInvoice) {
      const newBalance = matchedInvoice.balance - amount;
      await this.prisma.invoice.update({
        where: { id: matchedInvoice.id },
        data: {
          balance: Math.max(0, newBalance),
          status: newBalance <= 0 ? 'paid' : 'pending',
        },
      });
    }

    return match;
  }

  async getStatus(orgId: string) {
    const [totalMatches, confirmedMatches, pendingMatches] = await Promise.all([
      this.prisma.paymentMatch.count({
        where: { bankMovement: { organizationId: orgId } },
      }),
      this.prisma.paymentMatch.count({
        where: { bankMovement: { organizationId: orgId }, status: 'manual_confirmed' },
      }),
      this.prisma.paymentMatch.count({
        where: { bankMovement: { organizationId: orgId }, status: 'pending_review' },
      }),
    ]);

    return { totalMatches, confirmed: confirmedMatches, pending: pendingMatches };
  }
}