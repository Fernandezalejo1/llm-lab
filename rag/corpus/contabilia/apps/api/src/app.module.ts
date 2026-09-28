import { Module } from '@nestjs/common';
import { PrismaModule } from '@contabilia/database';
import { HealthController } from './health.controller';
import { DashboardModule } from './modules/dashboard/dashboard.module';
import { CustomersModule } from './modules/customers/customers.module';
import { BankMovementsModule } from './modules/bank-movements/bank-movements.module';
import { InvoicesModule } from './modules/invoices/invoices.module';
import { IngestionModule } from './modules/ingestion/ingestion.module';
import { MatchingModule } from './modules/matching/matching.module';

@Module({
  imports: [
    PrismaModule,
    DashboardModule,
    CustomersModule,
    BankMovementsModule,
    InvoicesModule,
    IngestionModule,
    MatchingModule,
  ],
  controllers: [HealthController],
})
export class AppModule {}
