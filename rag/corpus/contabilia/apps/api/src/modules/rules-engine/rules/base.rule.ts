import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext, RuleResult, EvidenceItem } from '@contabilia/shared-types';
import { IRule } from './rule.interface';

@Injectable()
export abstract class BaseRule implements IRule {
  abstract readonly id: string;
  abstract readonly name: string;
  abstract readonly description: string;
  readonly weight: number = 1.0;
  readonly priority: number = 100;
  enabled: boolean = true;

  abstract evaluate(movement: NormalizedMovement, context: RuleContext): Promise<RuleResult>;

  protected createMatch(
    customerId: string,
    confidence: number,
    evidence: EvidenceItem[],
  ): RuleResult {
    return {
      matched: true,
      customerId,
      confidence,
      evidence,
    };
  }

  protected createNonMatch(debug?: Record<string, unknown>): RuleResult {
    return {
      matched: false,
      confidence: 0,
      evidence: [],
      debug,
    };
  }

  protected normalize(text: string): string {
    return text
      .toUpperCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^\w\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  protected tokenize(text: string): string[] {
    return this.normalize(text).split(/\s+/).filter(Boolean);
  }
}
