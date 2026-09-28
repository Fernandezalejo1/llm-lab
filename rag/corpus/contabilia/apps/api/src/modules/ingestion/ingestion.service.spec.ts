import { Test, TestingModule } from '@nestjs/testing';
import { IngestionService } from './ingestion.service';
import { PrismaService } from '@contabilia/database';

describe('IngestionService', () => {
  let service: IngestionService;
  let prisma: {
    customer: { findFirst: jest.Mock; create: jest.Mock };
    invoice: { create: jest.Mock };
    bankStatement: { create: jest.Mock; update: jest.Mock };
    bankMovement: { create: jest.Mock; aggregate: jest.Mock };
  };

  beforeEach(async () => {
    prisma = {
      customer: { findFirst: jest.fn(), create: jest.fn() },
      invoice: { create: jest.fn() },
      bankStatement: { create: jest.fn(), update: jest.fn() },
      bankMovement: { create: jest.fn(), aggregate: jest.fn() },
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        IngestionService,
        { provide: PrismaService, useValue: prisma },
      ],
    }).compile();

    service = module.get<IngestionService>(IngestionService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('processInvoices', () => {
    it('should handle empty CSV buffer', async () => {
      const emptyCsv = Buffer.from('cliente,numero,importe,fecha\n');
      const result = await service.processInvoices(emptyCsv, 'test.csv', 'org-1');
      expect(result).toHaveProperty('totalRows', 0);
      expect(result).toHaveProperty('created', 0);
    });

    it('should parse CSV with data and create invoices', async () => {
      const csv = Buffer.from('cliente,numero,importe,fecha\nTest Client,INV-001,1000,2026-01-01\n');
      prisma.customer.findFirst.mockResolvedValue(null);
      prisma.customer.create.mockResolvedValue({ id: 'cust-1' });
      prisma.invoice.create.mockResolvedValue({});

      const result = await service.processInvoices(csv, 'test.csv', 'org-1');
      expect(result.totalRows).toBe(1);
      expect(result.created).toBe(1);
      expect(prisma.invoice.create).toHaveBeenCalled();
    });
  });

  describe('processBankStatements', () => {
    it('should handle empty CSV buffer', async () => {
      const emptyCsv = Buffer.from('fecha,descripcion,monto\n');
      const result = await service.processBankStatements(emptyCsv, 'test.csv', 'org-1');
      expect(result).toHaveProperty('totalRows', 0);
      expect(result).toHaveProperty('created', 0);
    });
  });
});
