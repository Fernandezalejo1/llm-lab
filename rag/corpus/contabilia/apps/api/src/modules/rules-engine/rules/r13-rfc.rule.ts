import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R13RFCRule extends BaseRule {
  readonly id = 'R13';
  readonly name = 'RUT en Referencia';
  readonly description = 'Se encontro un RUT valido en la descripcion o referencia';
  readonly priority = 14;

  private readonly rutPattern = /\d{1,12}-[\dkK]/;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const searchText = [movement.description, movement.reference, movement.normalizedDescription]
      .filter(Boolean)
      .join(' ')
      .toUpperCase();

    const rutMatch = searchText.match(this.rutPattern);
    if (!rutMatch) return this.createNonMatch();

    const foundRUT = rutMatch[0];

    for (const customer of context.allCustomers) {
      if (!customer.rut) continue;
      const normalizedCustomerRUT = this.normalize(customer.rut);

      if (foundRUT === normalizedCustomerRUT) {
        return this.createMatch(customer.id, 0.92, [
          {
            type: 'rut_match',
            source: 'description/reference',
            value: foundRUT,
            matched: customer.rut,
            explanation: `RUT ${foundRUT} coincide con el RUT registrado de ${customer.legalName}`,
          },
        ]);
      }
    }

    for (const customer of context.allCustomers) {
      for (const attr of customer.attributes) {
        const normalizedAttr = this.normalize(attr.value);
        if (normalizedAttr === foundRUT) {
          return this.createMatch(customer.id, 0.85, [
            {
              type: 'rut_match_attribute',
              source: 'description/reference',
              value: foundRUT,
              matched: `${attr.attributeType}: ${attr.value}`,
              explanation: `RUT ${foundRUT} encontrado en atributo "${attr.attributeType}" de ${customer.legalName}`,
            },
          ]);
        }
      }
    }

    return this.createNonMatch();
  }
}

