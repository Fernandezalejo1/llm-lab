import { Module } from '@nestjs/common';
import { BankMovementsController } from './bank-movements.controller';
import { BankMovementsService } from './bank-movements.service';

@Module({
  controllers: [BankMovementsController],
  providers: [BankMovementsService],
})
export class BankMovementsModule {}