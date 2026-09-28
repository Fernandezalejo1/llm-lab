import { Controller, Get, Param } from '@nestjs/common';
import { InvoicesService } from './invoices.service';

@Controller('invoices')
export class InvoicesController {
  constructor(private readonly invoicesService: InvoicesService) {}

  @Get(':orgId')
  findAll(@Param('orgId') orgId: string) {
    return this.invoicesService.findAll(orgId);
  }
}