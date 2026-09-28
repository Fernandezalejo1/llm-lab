import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class BankMovementsService {
  private prisma = new PrismaClient();

  async findAll(orgId: string) {
    return this.prisma.bankMovement.findMany({
      where: { organizationId: orgId },
      orderBy: { transactionDate: 'desc' },
    });
  }

  async getStats(orgId: string) {
    const [total, identified, reconciled, pending, unidentified] = await Promise.all([
      this.prisma.bankMovement.count({ where: { organizationId: orgId } }),
      this.prisma.bankMovement.count({ where: { organizationId: orgId, status: 'identified' } }),
      this.prisma.bankMovement.count({ where: { organizationId: orgId, status: 'reconciled' } }),
      this.prisma.bankMovement.count({ where: { organizationId: orgId, status: 'pending' } }),
      this.prisma.bankMovement.count({ where: { organizationId: orgId, status: 'unidentified' } }),
    ]);

    return { total, identified, reconciled, pending, unidentified };
  }
}