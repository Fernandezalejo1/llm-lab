import { Injectable } from '@nestjs/common';
import { NormalizedMovement, RuleContext } from '@contabilia/shared-types';
import { BaseRule } from './base.rule';

@Injectable()
export class R10FrequencyRule extends BaseRule {
  readonly id = 'R10';
  readonly name = 'Frecuencia / Fecha Cercana';
  readonly description = 'El pago coincide con la frecuencia o patrón de fechas del cliente';
  readonly priority = 40;

  async evaluate(movement: NormalizedMovement, context: RuleContext) {
    const movementDate = new Date(movement.transactionDate);
    const movementDay = movementDate.getDate();
    const movementMonth = movementDate.getMonth();
    const amount = movement.amount;

    if (context.recentMatches.length === 0) return this.createNonMatch();

    const frequencyByCustomer = new Map<string, { dates: Date[]; amounts: number[]; dayOfMonth: number[] }>();

    for (const match of context.recentMatches) {
      if (!match.customerId) continue;
      if (!frequencyByCustomer.has(match.customerId)) {
        frequencyByCustomer.set(match.customerId, { dates: [], amounts: [], dayOfMonth: [] });
      }
      const entry = frequencyByCustomer.get(match.customerId)!;
      entry.dates.push(new Date(match.createdAt));
      entry.amounts.push(0);
      entry.dayOfMonth.push(movementDay);
    }

    for (const [customerId, freq] of frequencyByCustomer) {
      if (freq.dayOfMonth.length < 3) continue;

      const avgDay = freq.dayOfMonth.reduce((a, b) => a + b, 0) / freq.dayOfMonth.length;
      const stdDev = Math.sqrt(freq.dayOfMonth.reduce((sq, d) => sq + (d - avgDay) ** 2, 0) / freq.dayOfMonth.length);

      if (stdDev <= 3 && Math.abs(movementDay - avgDay) <= 3) {
        return this.createMatch(customerId, 0.65, [
          {
            type: 'frequency_match',
            source: 'transaction_date',
            value: movementDate.toISOString(),
            matched: `Día ${Math.round(avgDay)} (desv: ${stdDev.toFixed(1)})`,
            explanation: `El cliente suele pagar los días ${Math.round(avgDay)} (±${Math.round(stdDev)} días)`,
          },
        ]);
      }
    }

    return this.createNonMatch();
  }
}
