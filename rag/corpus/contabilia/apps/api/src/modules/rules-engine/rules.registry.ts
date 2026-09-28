import { Provider } from '@nestjs/common';
import { R01ExactNameRule } from './rules/r01-exact-name.rule';
import { R02PartialNameRule } from './rules/r02-partial-name.rule';
import { R03AliasRule } from './rules/r03-alias.rule';
import { R04RelatedCompanyRule } from './rules/r04-related-company.rule';
import { R05RepresentativeRule } from './rules/r05-representative.rule';
import { R06BankAccountRule } from './rules/r06-bank-account.rule';
import { R07CheckRule } from './rules/r07-check.rule';
import { R08ObraRule } from './rules/r08-obra.rule';
import { R09AddressRule } from './rules/r09-address.rule';
import { R10FrequencyRule } from './rules/r10-frequency.rule';
import { R11HistoryRule } from './rules/r11-history.rule';
import { R12ReferenceRule } from './rules/r12-reference.rule';
import { R13RFCRule } from './rules/r13-rfc.rule';

export const RULES_REGISTRY: Provider[] = [
  { provide: 'RULES', useFactory: (...rules) => rules, inject: [
    R01ExactNameRule,
    R02PartialNameRule,
    R03AliasRule,
    R04RelatedCompanyRule,
    R05RepresentativeRule,
    R06BankAccountRule,
    R07CheckRule,
    R08ObraRule,
    R09AddressRule,
    R10FrequencyRule,
    R11HistoryRule,
    R12ReferenceRule,
    R13RFCRule,
  ]},
  R01ExactNameRule,
  R02PartialNameRule,
  R03AliasRule,
  R04RelatedCompanyRule,
  R05RepresentativeRule,
  R06BankAccountRule,
  R07CheckRule,
  R08ObraRule,
  R09AddressRule,
  R10FrequencyRule,
  R11HistoryRule,
  R12ReferenceRule,
  R13RFCRule,
];
