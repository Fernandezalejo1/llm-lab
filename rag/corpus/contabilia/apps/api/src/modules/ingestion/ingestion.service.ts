import { Injectable } from '@nestjs/common';
import { PrismaService } from '@contabilia/database';
import * as XLSX from 'xlsx';
import { parse } from 'csv-parse/sync';

@Injectable()
export class IngestionService {
  constructor(private prisma: PrismaService) {}

  private readonly invoiceColumnMap: Record<string, string> = {
    'cliente': 'customerName',
    'nombre': 'customerName',
    'rut': 'rut',
    'numero': 'number',
    'factura': 'number',
    'numero de factura': 'number',
    'importe': 'amount',
    'monto': 'amount',
    'total': 'amount',
    'fecha': 'issueDate',
    'fecha de factura': 'issueDate',
    'vencimiento': 'dueDate',
    'fecha vencimiento': 'dueDate',
    'saldo': 'balance',
    'saldo pendiente': 'balance',
    'pendiente': 'balance',
  };

  private readonly bankColumnMap: Record<string, string> = {
    'fecha': 'date',
    'descripcion': 'description',
    'detalle': 'description',
    'referencia': 'reference',
    'ref': 'reference',
    'cargo': 'amount',
    'abono': 'amount',
    'monto': 'amount',
    'importe': 'amount',
    'debito': 'amount',
    'credito': 'amount',
  };

  async processInvoices(fileBuffer: Buffer, filename: string, orgId: string) {
    const records = this.parseFile(fileBuffer, filename);
    const mapped = records.map((r) => this.mapColumns(r, this.invoiceColumnMap));

    let created = 0;
    for (const row of mapped) {
      try {
        const amount = parseFloat(String(row.amount || 0));
        const balance = parseFloat(String(row.balance || row.amount || 0));
        if (isNaN(amount) || amount === 0) continue;

        let customerId = '';
        if (row.customerName) {
          const name = String(row.customerName).trim();
          let customer = await this.prisma.customer.findFirst({
            where: { organizationId: orgId, legalName: name },
          });
          if (!customer) {
            customer = await this.prisma.customer.create({
              data: { organizationId: orgId, legalName: name },
            });
          }
          customerId = customer.id;
        }

        await this.prisma.invoice.create({
          data: {
            organizationId: orgId,
            invoiceNumber: String(row.number || `INV-${Date.now()}-${created}`),
            customerId,
            amount,
            total: amount,
            balance: isNaN(balance) ? amount : balance,
            issueDate: this.parseDate(row.issueDate) || new Date(),
            dueDate: this.parseDate(row.dueDate) || new Date(),
            status: 'pending',
          },
        });
        created++;
      } catch { continue; }
    }

    return { totalRows: mapped.length, created, data: mapped.slice(0, 50) };
  }

  async processBankStatements(fileBuffer: Buffer, filename: string, orgId: string) {
    const records = this.parseFile(fileBuffer, filename);
    const mapped = records.map((r) => this.mapColumns(r, this.bankColumnMap));

    if (mapped.length === 0) return { totalRows: 0, created: 0, data: [] };

    const bankStatement = await this.prisma.bankStatement.create({
      data: {
        organizationId: orgId,
        accountNumber: 'imported',
        periodStart: new Date(),
        periodEnd: new Date(),
        fileType: 'excel',
        status: 'processing',
      },
    });

    let created = 0;
    const maxSeq = await this.prisma.bankMovement.aggregate({
      where: { organizationId: orgId },
      _max: { sequence: true },
    });
    let seq = (maxSeq._max.sequence || 0) + 1;

    for (const row of mapped) {
      try {
        const amount = parseFloat(String(row.amount || 0));
        if (isNaN(amount) || amount === 0) continue;

        const date = this.parseDate(row.date) || new Date();
        const movementType = amount >= 0 ? 'credit' : 'debit';
        const description = String(row.description || row.detalle || 'Sin descripcion');

        await this.prisma.bankMovement.create({
          data: {
            bankStatementId: bankStatement.id,
            organizationId: orgId,
            transactionDate: date,
            description,
            reference: row.reference ? String(row.reference) : null,
            debitAmount: movementType === 'debit' ? Math.abs(amount) : 0,
            creditAmount: movementType === 'credit' ? Math.abs(amount) : 0,
            movementType,
            status: 'unidentified',
            sequence: seq++,
          },
        });
        created++;
      } catch { continue; }
    }

    await this.prisma.bankStatement.update({
      where: { id: bankStatement.id },
      data: { status: 'processed' },
    });

    return { totalRows: mapped.length, created, data: mapped.slice(0, 50) };
  }

  private parseFile(buffer: Buffer, filename: string): Record<string, unknown>[] {
    const ext = filename.toLowerCase().split('.').pop();
    if (ext === 'csv') {
      const content = buffer.toString('utf-8').replace(/^\uFEFF/, '');
      return parse(content, { columns: true, skip_empty_lines: true, trim: true });
    }
    const workbook = XLSX.read(buffer, { type: 'buffer' });
    const sheetName = workbook.SheetNames[0];
    return XLSX.utils.sheet_to_json(workbook.Sheets[sheetName]);
  }

  private mapColumns(row: Record<string, unknown>, columnMap: Record<string, string>): Record<string, unknown> {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(row)) {
      const normalizedKey = key.toLowerCase().trim();
      const mappedKey = columnMap[normalizedKey] || normalizedKey;
      result[mappedKey] = value;
    }
    return result;
  }

  private parseDate(value: unknown): Date | null {
    if (!value) return null;
    if (value instanceof Date) return value;
    const str = String(value).trim();
    if (!str) return null;

    // Try ISO format
    const isoDate = new Date(str);
    if (!isNaN(isoDate.getTime())) return isoDate;

    // Try DD/MM/YYYY (Uruguayan format)
    const parts = str.split(/[\/\-\.]/);
    if (parts.length === 3) {
      const [day, month, year] = parts.map(Number);
      const fullYear = year < 100 ? 2000 + year : year;
      const d = new Date(fullYear, month - 1, day);
      if (!isNaN(d.getTime())) return d;
    }

    return null;
  }
}