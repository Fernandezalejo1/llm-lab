import { Controller, Get, Param } from '@nestjs/common';
import { DashboardService } from './dashboard.service';

@Controller('dashboard')
export class DashboardController {
  constructor(private readonly dashboardService: DashboardService) {}

  @Get('stats/:orgId')
  getStats(@Param('orgId') orgId: string) {
    return this.dashboardService.getStats(orgId);
  }

  @Get('weekly/:orgId')
  getWeekly(@Param('orgId') orgId: string) {
    return this.dashboardService.getWeeklyData(orgId);
  }
}