import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R02PartialNameRule extends BaseRule {
  readonly id = 'R02';
  readonly name = 'Coincidencia Parcial de Razón Social';
  readonly description = 'Token matching parcial contra el nombre legal del cliente';
  readonly priority = 20;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const descTokens = this.tokenize(movement.normalizedDescription);
    if (descTokens.length === 0) return this.createNonMatch();

    const candidates: Array<{ customerId: string; score: number; matchedTokens: string[] }> = [];

    for (const customer of context.allCustomers) {
      const nameTokens = this.tokenize(customer.legalName);
      const matchedTokens = descTokens.filter((t) => nameTokens.includes(t));

      if (matchedTokens.length === 0) continue;

      const score = matchedTokens.length / Math.max(descTokens.length, nameTokens.length);

      if (score >= 0.4) {
        candidates.push({ customerId: customer.id, score, matchedTokens });
      }
    }

    if (candidates.length === 0) return this.createNonMatch();

    const best = candidates.sort((a, b) => b.score - a.score)[0];
    const confidence = 0.6 + best.score * 0.25;

    return this.createMatch(best.customerId, Math.min(confidence, 0.85), [
      {
        type: 'partial_match',
        source: 'description',
        value: movement.description,
        matched: best.matchedTokens.join(', '),
        explanation: `Coincidencia parcial: ${best.matchedTokens.length} tokens en común`,
      },
    ]);
  }
}
