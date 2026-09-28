import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R08ObraRule extends BaseRule {
  readonly id = 'R08';
  readonly name = 'Obra Conocida';
  readonly description = 'La descripción menciona una obra registrada del cliente';
  readonly priority = 30;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const normalizedDesc = this.normalize(movement.normalizedDescription);

    for (const customer of context.allCustomers) {
      for (const attr of customer.attributes) {
        if (attr.attributeType !== 'construction_site' && attr.attributeType !== 'site_address') continue;

        const normalizedAttr = this.normalize(attr.value);
        if (normalizedDesc.includes(normalizedAttr) || normalizedAttr.includes(normalizedDesc)) {
          return this.createMatch(customer.id, 0.75, [
            {
              type: 'obra_match',
              source: 'description',
              value: movement.description,
              matched: attr.value,
              explanation: `La obra "${attr.value}" pertenece a ${customer.legalName}`,
            },
          ]);
        }
      }
    }

    return this.createNonMatch();
  }
}
