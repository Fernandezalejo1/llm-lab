import { Test, TestingModule } from '@nestjs/testing';
import { DashboardService } from './dashboard.service';
import { PrismaService } from '@contabilia/database';

describe('DashboardService', () => {
  let service: DashboardService;
  let prisma: {
    invoice: { count: jest.Mock; aggregate: jest.Mock };
    customer: { count: jest.Mock };
    bankMovement: { count: jest.Mock };
  };

  beforeEach(async () => {
    prisma = {
      invoice: { count: jest.fn(), aggregate: jest.fn() },
      customer: { count: jest.fn() },
      bankMovement: { count: jest.fn() },
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        DashboardService,
        { provide: PrismaService, useValue: prisma },
      ],
    }).compile();

    service = module.get<DashboardService>(DashboardService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('getStats', () => {
    it('should return dashboard statistics', async () => {
      prisma.invoice.count
        .mockResolvedValueOnce(50)   // totalInvoices
        .mockResolvedValueOnce(30)   // paidInvoices
        .mockResolvedValueOnce(15)   // pendingInvoices
        .mockResolvedValueOnce(5);   // overdueInvoices
      prisma.customer.count.mockResolvedValue(10);
      prisma.invoice.aggregate
        .mockResolvedValueOnce({ _sum: { amount: 100000 } })  // totalInvoiced
        .mockResolvedValueOnce({ _sum: { amount: 60000 } })   // totalPaid
        .mockResolvedValueOnce({ _sum: { balance: 25000 } }); // totalPending
      prisma.bankMovement.count
        .mockResolvedValueOnce(200)  // totalMovements
        .mockResolvedValueOnce(180)  // identifiedMovements
        .mockResolvedValueOnce(20);  // unmatchedMovements

      const result = await service.getStats('org-1');
      expect(result).toHaveProperty('totalInvoices', 50);
      expect(result).toHaveProperty('paidInvoices', 30);
      expect(result).toHaveProperty('automationRate');
      expect(typeof result.automationRate).toBe('number');
    });
  });

  describe('getWeeklyData', () => {
    it('should return weekly data structure', async () => {
      prisma.bankMovement.count.mockResolvedValue(5);

      const result = await service.getWeeklyData('org-1');
      expect(result).toHaveProperty('weeklyData');
      expect(Array.isArray(result.weeklyData)).toBe(true);
      expect(result.weeklyData.length).toBe(7);
    });
  });
});
