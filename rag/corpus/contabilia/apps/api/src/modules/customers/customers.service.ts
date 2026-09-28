import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class CustomersService {
  private prisma = new PrismaClient();

  async findAll(orgId: string) {
    const customers = await this.prisma.customer.findMany({
      where: { organizationId: orgId },
      include: {
        invoices: { select: { amount: true, balance: true, status: true } },
      },
    });

    return customers.map((c) => {
      const totalPending = c.invoices.filter((i) => i.status !== 'paid').reduce((sum, i) => sum + i.balance, 0);
      const totalInvoiced = c.invoices.reduce((sum, i) => sum + i.amount, 0);
      const pendingInvoices = c.invoices.filter((i) => i.status !== 'paid').length;
      return {
        id: c.id,
        legalName: c.legalName,
        rut: c.rut,
        email: c.email,
        totalPending,
        totalInvoiced,
        pendingInvoices,
        lastPayment: null,
      };
    });
  }

  async getInvoices(orgId: string, customerId: string) {
    return this.prisma.invoice.findMany({
      where: { organizationId: orgId, customerId },
      orderBy: { issueDate: 'desc' },
    });
  }
}