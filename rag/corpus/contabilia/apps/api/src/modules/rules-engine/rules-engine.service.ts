import { Inject, Injectable } from '@nestjs/common';
import {
  NormalizedMovement,
  RuleContext,
  RuleResult,
  ConsolidatedCandidate,
  EvidenceItem,
} from '@contabilia/shared-types';
import { IRule } from './rules/rule.interface';

interface ConsolidatingEntry {
  customerId: string;
  matchedRules: RuleResult[];
  totalWeight: number;
  weightedConfidence: number;
  allEvidence: EvidenceItem[];
}

@Injectable()
export class RulesEngineService {
  constructor(@Inject('RULES') private readonly rules: IRule[]) {}

  async executeRules(
    movement: NormalizedMovement,
    context: RuleContext,
  ): Promise<ConsolidatedCandidate[]> {
    const results: RuleResult[] = [];

    const sortedRules = [...this.rules]
      .filter((r) => r.enabled)
      .sort((a, b) => a.priority - b.priority);

    for (const rule of sortedRules) {
      try {
        const result = await rule.evaluate(movement, context);
        results.push(result);
      } catch (error) {
        results.push({
          matched: false,
          confidence: 0,
          evidence: [],
          debug: { error: error instanceof Error ? error.message : 'Unknown error' },
        });
      }
    }

    return this.consolidate(results);
  }

  private consolidate(results: RuleResult[]): ConsolidatedCandidate[] {
    const grouped = new Map<string, ConsolidatingEntry>();

    for (const result of results) {
      if (!result.matched || !result.customerId) continue;

      const key = result.customerId;
      if (!grouped.has(key)) {
        grouped.set(key, {
          customerId: key,
          matchedRules: [],
          totalWeight: 0,
          weightedConfidence: 0,
          allEvidence: [],
        });
      }

      const entry = grouped.get(key)!;
      entry.matchedRules.push(result);
      entry.totalWeight += result.confidence > 0 ? 1 : 0.1;
      entry.weightedConfidence += result.confidence;
      entry.allEvidence.push(...result.evidence);
    }

    const candidates: ConsolidatedCandidate[] = [];
    for (const [, entry] of grouped) {
      const avgConfidence = entry.totalWeight > 0
        ? entry.weightedConfidence / entry.matchedRules.length
        : 0;

      candidates.push({
        customerId: entry.customerId,
        confidence: Math.min(avgConfidence, 1.0),
        matchedRules: entry.matchedRules,
        evidence: entry.allEvidence,
      });
    }

    return candidates.sort((a, b) => b.confidence - a.confidence);
  }
}
