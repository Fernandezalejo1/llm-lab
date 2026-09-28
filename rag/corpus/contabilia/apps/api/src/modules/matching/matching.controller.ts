import { Controller, Post, Get, Param, Body } from '@nestjs/common';
import { MatchingService } from './matching.service';

@Controller('matching')
export class MatchingController {
  constructor(private readonly matchingService: MatchingService) {}

  @Post('confirm/:movementId')
  confirmMatch(
    @Param('movementId') movementId: string,
    @Body('customerId') customerId: string,
  ) {
    return this.matchingService.confirmMatch(movementId, customerId);
  }

  @Get('status/:orgId')
  getStatus(@Param('orgId') orgId: string) {
    return this.matchingService.getStatus(orgId);
  }
}