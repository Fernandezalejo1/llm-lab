import { Test, TestingModule } from '@nestjs/testing';
import { MatchingService } from './matching.service';
import { PrismaService } from '@contabilia/database';

describe('MatchingService', () => {
  let service: MatchingService;
  let prisma: {
    bankMovement: { findUnique: jest.Mock };
    invoice: { findMany: jest.Mock; update: jest.Mock };
    paymentMatch: { create: jest.Mock; count: jest.Mock };
  };

  beforeEach(async () => {
    prisma = {
      bankMovement: { findUnique: jest.fn() },
      invoice: { findMany: jest.fn(), update: jest.fn() },
      paymentMatch: { create: jest.fn(), count: jest.fn() },
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        MatchingService,
        { provide: PrismaService, useValue: prisma },
      ],
    }).compile();

    service = module.get<MatchingService>(MatchingService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('confirmMatch', () => {
    it('should throw when movement not found', async () => {
      prisma.bankMovement.findUnique.mockResolvedValue(null);
      await expect(
        service.confirmMatch('non-existent', 'customer-1'),
      ).rejects.toThrow('Movement not found');
    });

    it('should create a payment match when movement exists', async () => {
      prisma.bankMovement.findUnique.mockResolvedValue({
        id: 'mov-1',
        organizationId: 'org-1',
        creditAmount: 1000,
        debitAmount: 0,
      });
      prisma.invoice.findMany.mockResolvedValue([]);
      prisma.paymentMatch.create.mockResolvedValue({ id: 'match-1' });
      prisma.bankMovement.update = jest.fn();

      const result = await service.confirmMatch('mov-1', 'customer-1');
      expect(result).toHaveProperty('id', 'match-1');
      expect(prisma.paymentMatch.create).toHaveBeenCalled();
    });
  });

  describe('getStatus', () => {
    it('should return match statistics', async () => {
      prisma.paymentMatch.count
        .mockResolvedValueOnce(100)  // totalMatches
        .mockResolvedValueOnce(80)   // confirmed
        .mockResolvedValueOnce(20);  // pending

      const result = await service.getStatus('org-1');
      expect(result).toEqual({
        totalMatches: 100,
        confirmed: 80,
        pending: 20,
      });
    });
  });
});
