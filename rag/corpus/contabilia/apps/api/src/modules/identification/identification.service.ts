import { Injectable } from '@nestjs/common';
import {
  NormalizedMovement,
  RuleContext,
  ConsolidatedCandidate,
  Customer,
  SimilarityPattern,
  PaymentMatch,
  CustomerBalance,
  EvidenceItem,
} from '@contabilia/shared-types';
import { RulesEngineService } from '../rules-engine/rules-engine.service';

@Injectable()
export class IdentificationService {
  private readonly AUTO_ACCEPT_THRESHOLD = 0.90;
  private readonly SUGGESTION_THRESHOLD = 0.70;
  private readonly CANDIDATE_THRESHOLD = 0.50;

  constructor(private readonly rulesEngine: RulesEngineService) {}

  async identifyMovement(
    movement: NormalizedMovement,
    customers: Customer[],
    patterns: SimilarityPattern[],
    recentMatches: PaymentMatch[],
    balances: CustomerBalance[],
  ): Promise<IdentificationResult> {
    const context: RuleContext = {
      organizationId: movement.organizationId,
      allCustomers: customers,
      similarityPatterns: patterns,
      recentMatches,
      customerBalances: balances,
      transactionDate: movement.transactionDate,
    };

    // Fase 1: Motor de Reglas
    const candidates = await this.rulesEngine.executeRules(movement, context);

    // Fase 2: Evaluar resultados
    if (candidates.length === 0) {
      return {
        status: 'unidentified',
        candidates: [],
        primaryCandidate: null,
        needsReview: false,
        needsAI: true,
        explanation: 'No se encontraron candidatos mediante reglas',
      };
    }

    const primary = candidates[0];

    // Fase 3: Validación final con monto si hay múltiples candidatos
    if (candidates.length >= 2 && candidates[1].confidence >= this.CANDIDATE_THRESHOLD) {
      this.validateWithAmount(movement, customers, candidates);
    }

    // Nueva ordenación después de validación con monto
    candidates.sort((a, b) => b.confidence - a.confidence);
    const updatedPrimary = candidates[0];

    // Decisión basada en confianza
    if (updatedPrimary.confidence >= this.AUTO_ACCEPT_THRESHOLD) {
      return {
        status: 'auto_accepted',
        candidates,
        primaryCandidate: updatedPrimary,
        needsReview: false,
        needsAI: false,
        explanation: this.buildExplanation(updatedPrimary),
      };
    }

    if (updatedPrimary.confidence >= this.SUGGESTION_THRESHOLD) {
      return {
        status: 'suggested',
        candidates,
        primaryCandidate: updatedPrimary,
        needsReview: true,
        needsAI: false,
        explanation: this.buildExplanation(updatedPrimary),
      };
    }

    // Baja confianza - necesita IA
    return {
      status: 'low_confidence',
      candidates,
      primaryCandidate: updatedPrimary,
      needsReview: true,
      needsAI: true,
      explanation: `Confianza baja (${(updatedPrimary.confidence * 100).toFixed(0)}%). Se recomienda intervención de IA`,
    };
  }

  private validateWithAmount(
    movement: NormalizedMovement,
    customers: Customer[],
    candidates: ConsolidatedCandidate[],
  ): void {
    const amount = movement.amount;

    for (const candidate of candidates) {
      const customer = customers.find((c) => c.id === candidate.customerId);
      if (!customer) continue;

      const hasMatchingAmount = candidate.evidence.some(
        (e) => e.type === 'amount_match',
      );

      if (!hasMatchingAmount) {
        candidate.confidence += 0.05;
        candidate.evidence.push({
          type: 'amount_match',
          source: 'amount',
          value: String(amount),
          matched: `Monto $${amount.toFixed(2)}`,
          explanation: `Monto registrado para posible validación con facturas de ${customer.legalName}`,
        });
      }
    }
  }

  private buildExplanation(candidate: ConsolidatedCandidate): string {
    const confidence = (candidate.confidence * 100).toFixed(0);
    const evidenceList = candidate.evidence.map((e) => e.explanation).join('; ');

    return `Confianza: ${confidence}%. Evidencia: ${evidenceList}`;
  }
}

export interface IdentificationResult {
  status: 'auto_accepted' | 'suggested' | 'low_confidence' | 'unidentified';
  candidates: ConsolidatedCandidate[];
  primaryCandidate: ConsolidatedCandidate | null;
  needsReview: boolean;
  needsAI: boolean;
  explanation: string;
}
