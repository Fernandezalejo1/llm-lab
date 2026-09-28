import { NormalizedMovement, RuleResult, RuleContext } from '@contabilia/shared-types';

export interface IRule {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly weight: number;
  readonly priority: number;
  enabled: boolean;

  evaluate(movement: NormalizedMovement, context: RuleContext): Promise<RuleResult>;
}
