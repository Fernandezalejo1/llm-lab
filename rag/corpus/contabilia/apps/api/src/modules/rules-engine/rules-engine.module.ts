import { Module } from '@nestjs/common';
import { RulesEngineService } from './rules-engine.service';
import { RULES_REGISTRY } from './rules.registry';

@Module({
  providers: [
    RulesEngineService,
    ...RULES_REGISTRY,
  ],
  exports: [RulesEngineService],
})
export class RulesEngineModule {}
