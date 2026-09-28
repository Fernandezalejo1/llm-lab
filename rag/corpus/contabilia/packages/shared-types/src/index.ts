// Organization
export interface Organization {
  id: string;
  name: string;
  slug: string;
  settings: OrganizationSettings;
  status: OrganizationStatus;
  createdAt: Date;
  updatedAt: Date;
}

export type OrganizationStatus = 'trial' | 'active' | 'suspended' | 'cancelled';

export interface OrganizationSettings {
  autoApplyThreshold: number;
  currency: string;
  timezone: string;
  rulesConfig: Record<string, RuleConfig>;
  notificationPrefs: NotificationPrefs;
}

export interface RuleConfig {
  enabled: boolean;
  weight: number;
}

export interface NotificationPrefs {
  email: boolean;
  inApp: boolean;
  onUnidentified: boolean;
  onError: boolean;
  onReconciliationReady: boolean;
}

// Customer
export interface Customer {
  id: string;
  organizationId: string;
  legalName: string;
  rut?: string;
  alias?: string;
  email?: string;
  phone?: string;
  status: CustomerStatus;
  attributes: CustomerAttribute[];
  createdAt: Date;
  updatedAt: Date;
}

export type CustomerStatus = 'active' | 'inactive' | 'blocked';

export interface CustomerAttribute {
  id: string;
  customerId: string;
  attributeType: CustomerAttributeType;
  value: string;
  source: AttributeSource;
  confidence: number;
  verified: boolean;
}

export type CustomerAttributeType =
  | 'legal_representative'
  | 'owner'
  | 'director'
  | 'related_company'
  | 'construction_site'
  | 'address'
  | 'site_address'
  | 'phone'
  | 'email'
  | 'bank_account'
  | 'cuenta_bancaria'
  | 'known_alias'
  | 'payment_method'
  | 'payment_frequency'
  | 'check_pattern'
  | 'reference_code';

export type AttributeSource = 'manual' | 'bank_statement' | 'learning' | 'import' | 'system';

// Invoice
export interface Invoice {
  id: string;
  organizationId: string;
  customerId: string;
  invoiceType: InvoiceType;
  invoiceNumber: string;
  invoiceSerie?: string;
  rut?: string;
  amount: number;
  tax: number;
  total: number;
  currency: string;
  exchangeRate?: number;
  issueDate: Date;
  dueDate: Date;
  paymentDate?: Date;
  status: InvoiceStatus;
  balance: number;
  lines: InvoiceLine[];
}

export type InvoiceType = 'factura' | 'credit_note' | 'debit_note';
export type InvoiceStatus = 'issued' | 'sent' | 'partial' | 'paid' | 'overdue' | 'cancelled';

export interface InvoiceLine {
  id: string;
  invoiceId: string;
  description: string;
  quantity: number;
  unitPrice: number;
  total: number;
}

export interface CustomerBalance {
  id: string;
  customerId: string;
  balanceType: 'credit' | 'advance';
  amount: number;
  currency: string;
}

// Bank Statement
export interface BankStatement {
  id: string;
  organizationId: string;
  accountNumber: string;
  accountName?: string;
  bankName?: string;
  periodStart: Date;
  periodEnd: Date;
  fileType: 'excel' | 'csv' | 'pdf';
  status: BankStatementStatus;
  movements: BankMovement[];
}

export type BankStatementStatus = 'pending' | 'processing' | 'processed' | 'completed' | 'error';

// Bank Movement
export interface BankMovement {
  id: string;
  bankStatementId: string;
  organizationId: string;
  transactionDate: Date;
  valueDate?: Date;
  description: string;
  reference?: string;
  checkNumber?: string;
  movementType: 'credit' | 'debit' | 'unknown';
  debitAmount: number;
  creditAmount: number;
  currency: string;
  balance?: number;
  status: MovementStatus;
  paymentMatch?: PaymentMatch;
}

export type MovementStatus =
  | 'pending'
  | 'identified'
  | 'applied'
  | 'reconciled'
  | 'error'
  | 'duplicate'
  | 'unidentified';

// Payment Match
export interface PaymentMatch {
  id: string;
  bankMovementId: string;
  organizationId: string;
  customerId?: string;
  customer?: Customer;
  engineVersion: string;
  matchStrategy: MatchStrategy;
  confidence: number;
  status: MatchStatus;
  executedRules: RuleExecution[];
  matchedRules: RuleExecution[];
  evidence: EvidenceData;
  aiAnalysis?: AIAnalysis;
  description?: string;
  suggestions: PaymentSuggestion[];
  application?: PaymentApplication;
  createdAt: Date;
}

export type MatchStrategy =
  | 'rule_exact_name'
  | 'rule_partial_name'
  | 'rule_alias'
  | 'rule_related_company'
  | 'rule_representative'
  | 'rule_bank_account'
  | 'rule_check'
  | 'rule_obra'
  | 'rule_address'
  | 'rule_frequency'
  | 'rule_history'
  | 'rule_reference'
  | 'rule_rut'
  | 'ai_semantic'
  | 'ai_fuzzy'
  | 'ai_llm'
  | 'learning_pattern'
  | 'manual'
  | 'combined';

export type MatchStatus =
  | 'auto_accepted'
  | 'pending_review'
  | 'manual_confirmed'
  | 'manual_rejected'
  | 'learning';

export interface RuleExecution {
  ruleId: string;
  ruleName: string;
  matched: boolean;
  confidence: number;
  evidence: EvidenceItem[];
}

export interface EvidenceItem {
  type: string;
  source: string;
  value: string;
  matched: string;
  explanation: string;
}

export interface EvidenceData {
  summary: string;
  items: EvidenceItem[];
}

export interface AIAnalysis {
  used: boolean;
  reason?: string;
  model?: string;
  semanticSearch?: SemanticSearchResult;
  fuzzySearch?: FuzzySearchResult;
  llmAnalysis?: LLMAnalysis;
  finalConfidence: number;
}

export interface SemanticSearchResult {
  queryNormalized: string;
  topCandidates: SemanticCandidate[];
}

export interface SemanticCandidate {
  customerId: string;
  score: number;
  matchedOn: string;
  matchedText: string;
}

export interface FuzzySearchResult {
  query: string;
  candidates: FuzzyCandidate[];
}

export interface FuzzyCandidate {
  target: string;
  combinedScore: number;
  levenshtein: number;
  tokenOverlap: number;
  substring: number;
  trigram: number;
}

export interface LLMAnalysis {
  prompt: string;
  response: string;
  candidates: LLMCandidate[];
}

export interface LLMCandidate {
  customerId: string;
  confidence: number;
  evidence: string[];
  explanation: string;
}

// Payment Suggestion
export interface PaymentSuggestion {
  id: string;
  paymentMatchId: string;
  customerId: string;
  confidence: number;
  strategyUsed: MatchStrategy;
  evidenceSummary: string;
  suggestedInvoices: SuggestedInvoice[];
  selected: boolean;
}

export interface SuggestedInvoice {
  invoiceId: string;
  amount: number;
  reason: string;
}

// Payment Application
export interface PaymentApplication {
  id: string;
  paymentMatchId: string;
  organizationId: string;
  applicationType: ApplicationType;
  totalAmount: number;
  appliedAmount: number;
  difference: number;
  differenceReason?: string;
  appliedInvoices: AppliedInvoice[];
  status: 'completed' | 'pending_approval' | 'error';
}

export type ApplicationType =
  | 'full'
  | 'partial'
  | 'multiple'
  | 'advance'
  | 'credit_note'
  | 'debit_note'
  | 'balance_forward';

export interface AppliedInvoice {
  id: string;
  applicationId: string;
  invoiceId: string;
  invoiceNumber: string;
  amountApplied: number;
  previousBalance: number;
  newBalance: number;
  isPartial: boolean;
}

// Reconciliation
export interface Reconciliation {
  id: string;
  organizationId: string;
  periodStart: Date;
  periodEnd: Date;
  totalMovements: number;
  conciliatedCount: number;
  pendingCount: number;
  unidentifiedCount: number;
  errorCount: number;
  duplicateCount: number;
  advanceCount: number;
  balanceForwardCount: number;
  status: 'draft' | 'completed' | 'verified';
  details: ReconciliationDetail[];
}

export interface ReconciliationDetail {
  movementId: string;
  date: Date;
  description: string;
  amount: number;
  type: 'credit' | 'debit';
  status: string;
  customer?: { id: string; name: string };
  confidence?: number;
  application?: string;
}

// Learning
export interface LearningLog {
  id: string;
  organizationId: string;
  inputText: string;
  suggestedCustomerId?: string;
  selectedCustomerId?: string;
  confidence?: number;
  correctionType: CorrectionType;
  createdAt: Date;
}

export type CorrectionType =
  | 'manual_match'
  | 'manual_reject'
  | 'manual_create'
  | 'confirm_suggestion';

export interface SimilarityPattern {
  id: string;
  organizationId: string;
  patternType: PatternType;
  sourceText: string;
  normalizedText: string;
  targetCustomerId: string;
  similarityScore: number;
  occurrences: number;
  isActive: boolean;
}

export type PatternType =
  | 'name_alias'
  | 'name_similarity'
  | 'bank_ref_client'
  | 'check_to_client'
  | 'obra_to_client'
  | 'address_to_client'
  | 'rut_in_ref'
  | 'representative_payment'
  | 'generic';

// Dashboard
export interface DashboardMetrics {
  todayCollections: number;
  pendingCollections: number;
  unidentifiedMovements: number;
  errors: number;
  automationRate: number;
  precision: number;
  timeSaved: number;
  periodComparison: number;
  dailyCollections: DailyCollection[];
  pendingInvoices: PendingInvoice[];
  unidentifiedMovementsList: UnidentifiedMovement[];
}

export interface DailyCollection {
  date: string;
  conciliated: number;
  pending: number;
  unidentified: number;
}

export interface PendingInvoice {
  invoiceNumber: string;
  customerName: string;
  amount: number;
  dueDate: Date;
  daysOverdue: number;
}

export interface UnidentifiedMovement {
  id: string;
  date: Date;
  description: string;
  amount: number;
  type: 'credit' | 'debit';
}

// Normalized Movement (input for rules engine)
export interface NormalizedMovement {
  id: string;
  organizationId: string;
  transactionDate: Date;
  description: string;
  normalizedDescription: string;
  reference?: string;
  checkNumber?: string;
  movementType: 'credit' | 'debit';
  amount: number;
  currency: string;
  sourceAccount?: string;
  rawData: Record<string, unknown>;
}

// Rule Engine
export interface Rule {
  id: string;
  name: string;
  description: string;
  weight: number;
  priority: number;
  enabled: boolean;
  config: Record<string, unknown>;
  evaluate(movement: NormalizedMovement, context: RuleContext): Promise<RuleResult>;
}

export interface RuleContext {
  organizationId: string;
  allCustomers: Customer[];
  similarityPatterns: SimilarityPattern[];
  recentMatches: PaymentMatch[];
  customerBalances: CustomerBalance[];
  transactionDate: Date;
}

export interface RuleResult {
  matched: boolean;
  customerId?: string;
  confidence: number;
  evidence: EvidenceItem[];
  debug?: Record<string, unknown>;
}

export interface ConsolidatedCandidate {
  customerId: string;
  confidence: number;
  matchedRules: RuleResult[];
  evidence: EvidenceItem[];
  customer?: Customer;
}

// Application Decision
export interface ApplicationDecision {
  type: ApplicationType;
  totalAmount: number;
  totalApplied: number;
  remaining: number;
  invoiceApplications: Array<{
    invoiceId: string;
    amountApplied: number;
    previousBalance: number;
    newBalance: number;
    isPartial: boolean;
  }>;
  details: string;
  creditNotes?: Array<{ id: string; amount: number }>;
}

export interface OpenInvoice {
  id: string;
  invoiceNumber: string;
  customerId: string;
  balance: number;
  total: number;
  issueDate: Date;
  dueDate: Date;
  isOverdue: boolean;
  currency: string;
}

export interface UploadedFile {
  id: string;
  originalName: string;
  mimeType: string;
  size: number;
  path: string;
  uploadedAt: Date;
}

export interface ParsedInvoiceRow {
  customerName: string;
  invoiceNumber: string;
  amount: number;
  total: number;
  issueDate: string;
  dueDate: string;
  balance: number;
  rut?: string;
}

export interface ParsedBankMovementRow {
  date: string;
  description: string;
  reference?: string;
  checkNumber?: string;
  debitAmount: number;
  creditAmount: number;
  balance?: number;
}

