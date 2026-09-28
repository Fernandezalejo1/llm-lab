import { Controller, Get, Param } from '@nestjs/common';
import { CustomersService } from './customers.service';

@Controller('customers')
export class CustomersController {
  constructor(private readonly customersService: CustomersService) {}

  @Get(':orgId')
  findAll(@Param('orgId') orgId: string) {
    return this.customersService.findAll(orgId);
  }

  @Get(':orgId/:customerId/invoices')
  getInvoices(@Param('orgId') orgId: string, @Param('customerId') customerId: string) {
    return this.customersService.getInvoices(orgId, customerId);
  }
}