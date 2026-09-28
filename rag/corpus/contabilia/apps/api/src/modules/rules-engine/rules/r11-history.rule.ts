import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';
import { PrismaClient } from '@contabilia/database';

@Injectable()
export class R11HistoryRule extends BaseRule {
  readonly id = 'R11';
  readonly name = 'Historial de Pagos';
  readonly description = 'Descripción similar a movimientos previamente identificados';
  readonly priority = 28;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const tokens = this.tokenize(movement.normalizedDescription);
    if (tokens.length === 0) return this.createNonMatch();

    const recentMatches = context.recentMatches.filter((m) => m.customerId && m.matchedRules.length > 0);

    const candidates = new Map<string, { count: number; totalConfidence: number; bestMatch: string }>();

    for (const match of recentMatches) {
      const matchMovement = match as any;
      const matchDesc = matchMovement.description || '';
      const matchTokens = this.tokenize(matchDesc);

      if (matchTokens.length === 0) continue;

      const overlap = tokens.filter((t) => matchTokens.includes(t)).length;
      const jaccard = overlap / Math.max(tokens.length + matchTokens.length - overlap, 1);

      if (jaccard >= 0.5) {
        const existing = candidates.get(match.customerId!) || { count: 0, totalConfidence: 0, bestMatch: '' };
        existing.count++;
        existing.totalConfidence += match.confidence;
        if (jaccard > 0.7) {
          existing.bestMatch = matchDesc;
        }
        candidates.set(match.customerId!, existing);
      }
    }

    if (candidates.size === 0) return this.createNonMatch();

    const sorted = Array.from(candidates.entries())
      .map(([customerId, data]) => ({
        customerId,
        avgConfidence: data.totalConfidence / data.count,
        count: data.count,
        bestMatch: data.bestMatch,
      }))
      .sort((a, b) => b.avgConfidence - a.avgConfidence);

    const best = sorted[0];
    const confidence = Math.min(0.8 + best.count * 0.02, 0.92);

    return this.createMatch(best.customerId, confidence, [
      {
        type: 'history_match',
        source: 'description',
        value: movement.description,
        matched: best.bestMatch || `Historial: ${best.count} coincidencias`,
        explanation: `${best.count} movimiento(s) previo(s) con descripción similar para este cliente`,
      },
    ]);
  }
}
