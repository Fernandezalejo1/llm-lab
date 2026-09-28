import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R05RepresentativeRule extends BaseRule {
  readonly id = 'R05';
  readonly name = 'Representante / Dueño / Director';
  readonly description = 'El nombre del pago coincide con un representante legal, dueño o director';
  readonly priority = 18;

  private readonly personTypes = ['legal_representative', 'owner', 'director'] as const;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const normalizedDesc = this.normalize(movement.normalizedDescription);
    const descTokens = this.tokenize(movement.normalizedDescription);

    for (const customer of context.allCustomers) {
      for (const attr of customer.attributes) {
        if (!this.personTypes.includes(attr.attributeType as any)) continue;

        const normalizedAttr = this.normalize(attr.value);
        const attrTokens = this.tokenize(attr.value);

        const isExact = normalizedDesc === normalizedAttr;
        const isContained = normalizedDesc.includes(normalizedAttr) || normalizedAttr.includes(normalizedDesc);
        const tokenOverlap = attrTokens.filter((t) => descTokens.includes(t)).length;
        const hasNameMatch = tokenOverlap >= Math.min(2, attrTokens.length);

        if (isExact || isContained || hasNameMatch) {
          const confidence = isExact ? 0.85 : isContained ? 0.8 : 0.7;

          return this.createMatch(customer.id, confidence, [
            {
              type: 'representative_match',
              source: 'description',
              value: movement.description,
              matched: `${attr.attributeType}: ${attr.value}`,
              explanation: `"${attr.value}" es ${this.getTypeLabel(attr.attributeType)} de ${customer.legalName}`,
            },
          ]);
        }
      }
    }

    return this.createNonMatch();
  }

  private getTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      legal_representative: 'representante legal',
      owner: 'dueño',
      director: 'director',
    };
    return labels[type] || type;
  }
}
