import { Module } from '@nestjs/common';
import { CashApplicationService } from './cash-application.service';

@Module({
  providers: [CashApplicationService],
  exports: [CashApplicationService],
})
export class CashApplicationModule {}
