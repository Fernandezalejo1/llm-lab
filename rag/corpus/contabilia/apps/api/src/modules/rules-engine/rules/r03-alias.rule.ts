import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R03AliasRule extends BaseRule {
  readonly id = 'R03';
  readonly name = 'Alias Conocido';
  readonly description = 'Busca coincidencia con alias conocidos o patrones aprendidos';
  readonly priority = 15;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const normalizedDesc = this.normalize(movement.normalizedDescription);

    for (const pattern of context.similarityPatterns) {
      if (!pattern.isActive) continue;
      const normalizedPattern = this.normalize(pattern.sourceText);

      const isExact = normalizedDesc === normalizedPattern;
      const isContained = normalizedDesc.includes(normalizedPattern) || normalizedPattern.includes(normalizedDesc);

      if (isExact || isContained) {
        const baseConfidence = isExact ? 0.95 : 0.85;
        const occurrenceBoost = Math.min(pattern.occurrences * 0.01, 0.05);
        const confidence = Math.min(baseConfidence + occurrenceBoost, 0.98);

        return this.createMatch(pattern.targetCustomerId, confidence, [
          {
            type: 'learning_pattern',
            source: 'description',
            value: movement.description,
            matched: pattern.sourceText,
            explanation: `Patrón aprendido: "${pattern.sourceText}" → cliente (usado ${pattern.occurrences} veces)`,
          },
        ]);
      }
    }

    for (const customer of context.allCustomers) {
      for (const attr of customer.attributes) {
        if (attr.attributeType === 'known_alias') {
          const normalizedAlias = this.normalize(attr.value);
          if (normalizedDesc === normalizedAlias || normalizedDesc.includes(normalizedAlias)) {
            return this.createMatch(customer.id, 0.9, [
              {
                type: 'alias_match',
                source: 'description',
                value: movement.description,
                matched: attr.value,
                explanation: `Alias conocido "${attr.value}" para ${customer.legalName}`,
              },
            ]);
          }
        }
      }
    }

    return this.createNonMatch();
  }
}
