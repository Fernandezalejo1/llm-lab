import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R06BankAccountRule extends BaseRule {
  readonly id = 'R06';
  readonly name = 'Cuenta Bancaria / CLABE Conocida';
  readonly description = 'La cuenta origen o CLABE coincide con una conocida del cliente';
  readonly priority = 12;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const sourceText = [
      movement.sourceAccount,
      movement.reference,
      movement.rawData?.cuenta_origen,
      movement.rawData?.clabe,
    ].filter(Boolean).map((s) => String(s));

    if (sourceText.length === 0) return this.createNonMatch();

    for (const customer of context.allCustomers) {
      for (const attr of customer.attributes) {
        if (attr.attributeType !== 'bank_account' && attr.attributeType !== 'cuenta_bancaria') continue;

        const normalizedAttr = this.normalize(attr.value);

        for (const source of sourceText) {
          const normalizedSource = this.normalize(source);
          if (normalizedSource.includes(normalizedAttr) || normalizedAttr.includes(normalizedSource)) {
            return this.createMatch(customer.id, 0.95, [
              {
                type: 'bank_account_match',
                source: 'reference/raw_data',
                value: source,
                matched: attr.value,
                explanation: `Cuenta bancaria "${attr.value}" registrada para ${customer.legalName}`,
              },
            ]);
          }
        }
      }
    }

    return this.createNonMatch();
  }
}

