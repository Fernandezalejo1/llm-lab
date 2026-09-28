import { Module } from '@nestjs/common';
import { IdentificationService } from './identification.service';
import { RulesEngineModule } from '../rules-engine/rules-engine.module';
import { LearningModule } from '../learning/learning.module';

@Module({
  imports: [RulesEngineModule, LearningModule],
  providers: [IdentificationService],
  exports: [IdentificationService],
})
export class IdentificationModule {}
