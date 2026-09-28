import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R12ReferenceRule extends BaseRule {
  readonly id = 'R12';
  readonly name = 'Referencia Numérica';
  readonly description = 'La referencia contiene número de factura, contrato o expediente';
  readonly priority = 32;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const searchText = [movement.reference, movement.description, movement.normalizedDescription]
      .filter(Boolean)
      .join(' ')
      .toUpperCase();

    const invoicePatterns = [
      /FAC[-\s]?(\d{3,10})/i,
      /FACTURA[-\s]?(\d{3,10})/i,
      /FOLIO[-\s]?(\d{3,10})/i,
      /(\d{3,10})/,
    ];

    for (const pattern of invoicePatterns) {
      const match = searchText.match(pattern);
      if (!match) continue;

      const refNumber = match[1] || match[0];

      for (const customer of context.allCustomers) {
        const customerInvoices = context.allCustomers
          .filter((c) => c.id === customer.id)
          .flatMap((c) => []);

        for (const attr of customer.attributes) {
          if (attr.attributeType !== 'reference_code') continue;
          if (this.normalize(attr.value).includes(refNumber)) {
            return this.createMatch(customer.id, 0.7, [
              {
                type: 'reference_match',
                source: 'reference',
                value: refNumber,
                matched: attr.value,
                explanation: `Referencia #${refNumber} coincide con código registrado de ${customer.legalName}`,
              },
            ]);
          }
        }
      }
    }

    return this.createNonMatch();
  }
}
