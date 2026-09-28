import { Injectable } from '@nestjs/common';
import { DashboardMetrics, DailyCollection, PendingInvoice, UnidentifiedMovement } from '@contabilia/shared-types';

@Injectable()
export class ReportsService {
  async getDashboardMetrics(organizationId: string): Promise<DashboardMetrics> {
    return {
      todayCollections: 0,
      pendingCollections: 0,
      unidentifiedMovements: 0,
      errors: 0,
      automationRate: 0,
      precision: 0,
      timeSaved: 0,
      periodComparison: 0,
      dailyCollections: [],
      pendingInvoices: [],
      unidentifiedMovementsList: [],
    };
  }

  async getReconciliationReport(organizationId: string, periodStart: Date, periodEnd: Date): Promise<any> {
    return null;
  }
}
