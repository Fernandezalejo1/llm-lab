import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R07CheckRule extends BaseRule {
  readonly id = 'R07';
  readonly name = 'Cheque Conocido';
  readonly description = 'El número de cheque coincide con patrones conocidos del cliente';
  readonly priority = 22;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const checkNumber = movement.checkNumber || movement.rawData?.check_number as string;
    if (!checkNumber) return this.createNonMatch();

    const normalizedCheck = checkNumber.trim();

    for (const pattern of context.similarityPatterns) {
      if (pattern.patternType !== 'check_to_client' || !pattern.isActive) continue;

      const patternText = pattern.sourceText.trim();
      if (normalizedCheck === patternText) {
        return this.createMatch(pattern.targetCustomerId, 0.9, [
          {
            type: 'check_match',
            source: 'check_number',
            value: checkNumber,
            matched: patternText,
            explanation: `Cheque #${checkNumber} previamente asociado al cliente (${pattern.occurrences} ocurrencias)`,
          },
        ]);
      }
    }

    for (const customer of context.allCustomers) {
      for (const attr of customer.attributes) {
        if (attr.attributeType !== 'check_pattern') continue;
        if (this.matchesCheckPattern(normalizedCheck, attr.value)) {
          return this.createMatch(customer.id, 0.8, [
            {
              type: 'check_pattern',
              source: 'check_number',
              value: checkNumber,
              matched: attr.value,
              explanation: `Cheque #${checkNumber} coincide con patrón "${attr.value}" de ${customer.legalName}`,
            },
          ]);
        }
      }
    }

    return this.createNonMatch();
  }

  private matchesCheckPattern(checkNumber: string, pattern: string): boolean {
    if (pattern.includes('*')) {
      const regex = new RegExp('^' + pattern.replace(/\*/g, '\\d+') + '$');
      return regex.test(checkNumber);
    }
    const prefix = pattern.replace(/X/g, '').replace(/\*/g, '');
    return checkNumber.startsWith(prefix);
  }
}
