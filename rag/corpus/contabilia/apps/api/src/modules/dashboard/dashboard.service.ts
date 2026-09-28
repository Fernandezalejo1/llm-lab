import { Injectable } from '@nestjs/common';
import { PrismaService } from '@contabilia/database';

@Injectable()
export class DashboardService {
  constructor(private prisma: PrismaService) {}

  async getStats(orgId: string) {
    const [totalInvoices, paidInvoices, pendingInvoices, overdueInvoices, totalCustomers] = await Promise.all([
      this.prisma.invoice.count({ where: { organizationId: orgId } }),
      this.prisma.invoice.count({ where: { organizationId: orgId, status: 'paid' } }),
      this.prisma.invoice.count({ where: { organizationId: orgId, status: 'pending' } }),
      this.prisma.invoice.count({ where: { organizationId: orgId, status: 'overdue' } }),
      this.prisma.customer.count({ where: { organizationId: orgId } }),
    ]);

    const [invoicedAgg, paidAgg, pendingAgg] = await Promise.all([
      this.prisma.invoice.aggregate({ where: { organizationId: orgId }, _sum: { amount: true } }),
      this.prisma.invoice.aggregate({ where: { organizationId: orgId, status: 'paid' }, _sum: { amount: true } }),
      this.prisma.invoice.aggregate({ where: { organizationId: orgId, status: 'pending' }, _sum: { balance: true } }),
    ]);

    const totalMovements = await this.prisma.bankMovement.count({ where: { organizationId: orgId } });
    const identifiedMovements = await this.prisma.bankMovement.count({
      where: { organizationId: orgId, status: { in: ['identified', 'reconciled'] } },
    });
    const unmatchedMovements = await this.prisma.bankMovement.count({
      where: { organizationId: orgId, status: 'unidentified' },
    });

    return {
      totalInvoices,
      paidInvoices,
      pendingInvoices,
      overdueInvoices,
      totalInvoiced: invoicedAgg._sum.amount || 0,
      totalPaid: paidAgg._sum.amount || 0,
      totalPending: pendingAgg._sum.balance || 0,
      totalMovements,
      identifiedMovements,
      unmatchedMovements,
      totalCustomers,
      automationRate: totalMovements > 0 ? Math.round((identifiedMovements / totalMovements) * 100) : 0,
    };
  }

  async getWeeklyData(orgId: string) {
    const days = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'];
    const now = new Date();
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() - now.getDay() + 1);
    weekStart.setHours(0, 0, 0, 0);

    const weeklyData = [];
    for (let i = 0; i < 7; i++) {
      const dayStart = new Date(weekStart);
      dayStart.setDate(weekStart.getDate() + i);
      const dayEnd = new Date(dayStart);
      dayEnd.setDate(dayStart.getDate() + 1);

      const [reconciled, pending] = await Promise.all([
        this.prisma.bankMovement.count({
          where: { organizationId: orgId, status: 'reconciled', transactionDate: { gte: dayStart, lt: dayEnd } },
        }),
        this.prisma.bankMovement.count({
          where: { organizationId: orgId, status: { in: ['pending', 'unidentified'] }, transactionDate: { gte: dayStart, lt: dayEnd } },
        }),
      ]);

      weeklyData.push({ day: days[i], reconciled, pending });
    }

    return { weeklyData };
  }
}