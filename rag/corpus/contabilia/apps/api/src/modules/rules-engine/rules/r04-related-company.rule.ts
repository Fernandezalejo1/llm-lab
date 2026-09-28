import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R04RelatedCompanyRule extends BaseRule {
  readonly id = 'R04';
  readonly name = 'Empresa Relacionada';
  readonly description = 'El pago proviene de una empresa relacionada al cliente';
  readonly priority = 25;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const normalizedDesc = this.normalize(movement.normalizedDescription);

    for (const customer of context.allCustomers) {
      for (const attr of customer.attributes) {
        if (attr.attributeType === 'related_company') {
          const normalizedRelated = this.normalize(attr.value);
          if (
            normalizedDesc === normalizedRelated ||
            normalizedDesc.includes(normalizedRelated) ||
            normalizedRelated.includes(normalizedDesc)
          ) {
            return this.createMatch(customer.id, 0.85, [
              {
                type: 'related_company',
                source: 'description',
                value: movement.description,
                matched: attr.value,
                explanation: `Empresa relacionada "${attr.value}" pagó para ${customer.legalName}`,
              },
            ]);
          }
        }
      }
    }

    return this.createNonMatch();
  }
}
