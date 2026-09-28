import { Controller, Get, Param } from '@nestjs/common';
import { BankMovementsService } from './bank-movements.service';

@Controller('bank-movements')
export class BankMovementsController {
  constructor(private readonly bankMovementsService: BankMovementsService) {}

  @Get(':orgId')
  findAll(@Param('orgId') orgId: string) {
    return this.bankMovementsService.findAll(orgId);
  }

  @Get(':orgId/stats')
  getStats(@Param('orgId') orgId: string) {
    return this.bankMovementsService.getStats(orgId);
  }
}