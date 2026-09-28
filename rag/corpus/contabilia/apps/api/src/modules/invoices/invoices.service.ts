import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class InvoicesService {
  private prisma = new PrismaClient();

  async findAll(orgId: string) {
    return this.prisma.invoice.findMany({
      where: { organizationId: orgId },
      include: { customer: true },
      orderBy: { issueDate: 'desc' },
    });
  }
}