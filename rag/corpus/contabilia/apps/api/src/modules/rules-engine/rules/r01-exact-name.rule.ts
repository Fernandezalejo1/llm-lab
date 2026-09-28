import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R01ExactNameRule extends BaseRule {
  readonly id = 'R01';
  readonly name = 'Coincidencia Exacta de Razón Social';
  readonly description = 'Comparación exacta contra el nombre legal del cliente';
  readonly priority = 10;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const normalizedDesc = this.normalize(movement.normalizedDescription);

    for (const customer of context.allCustomers) {
      const normalizedName = this.normalize(customer.legalName);

      if (normalizedDesc === normalizedName) {
        return this.createMatch(customer.id, 0.95, [
          {
            type: 'exact_match',
            source: 'description',
            value: movement.description,
            matched: customer.legalName,
            explanation: `La descripción coincide exactamente con la razón social de ${customer.legalName}`,
          },
        ]);
      }

      if (customer.alias) {
        const normalizedAlias = this.normalize(customer.alias);
        if (normalizedDesc === normalizedAlias) {
          return this.createMatch(customer.id, 0.92, [
            {
              type: 'exact_match',
              source: 'description',
              value: movement.description,
              matched: customer.alias,
              explanation: `La descripción coincide exactamente con el alias de ${customer.legalName}`,
            },
          ]);
        }
      }
    }

    return this.createNonMatch();
  }
}
