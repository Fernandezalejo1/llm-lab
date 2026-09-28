import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R09AddressRule extends BaseRule {
  readonly id = 'R09';
  readonly name = 'Dirección Conocida';
  readonly description = 'La descripción contiene una dirección registrada del cliente';
  readonly priority = 35;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const normalizedDesc = this.normalize(movement.normalizedDescription);
    const descTokens = this.tokenize(movement.normalizedDescription);

    for (const customer of context.allCustomers) {
      for (const attr of customer.attributes) {
        if (attr.attributeType !== 'address' && attr.attributeType !== 'site_address') continue;

        const attrTokens = this.tokenize(attr.value);
        const overlap = attrTokens.filter((t) => descTokens.includes(t)).length;
        const overlapRatio = overlap / Math.max(attrTokens.length, 1);

        if (overlapRatio >= 0.6 || normalizedDesc.includes(this.normalize(attr.value))) {
          return this.createMatch(customer.id, 0.65, [
            {
              type: 'address_match',
              source: 'description',
              value: movement.description,
              matched: attr.value,
              explanation: `Dirección "${attr.value}" registrada para ${customer.legalName}`,
            },
          ]);
        }
      }
    }

    return this.createNonMatch();
  }
}
