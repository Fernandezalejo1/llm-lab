import { Injectable } from '@nestjs/common';
import { SimilarityPattern, PatternType } from '@contabilia/shared-types';

interface LearningInput {
  organizationId: string;
  inputText: string;
  suggestedCustomerId?: string;
  selectedCustomerId: string;
  confidence?: number;
  correctionType: 'manual_match' | 'manual_reject' | 'manual_create' | 'confirm_suggestion';
  userId?: string;
}

@Injectable()
export class LearningService {
  async processCorrection(input: LearningInput): Promise<void> {
    const normalizedText = this.normalizeText(input.inputText);
    const patternType = this.determinePatternType(input.inputText);

    switch (input.correctionType) {
      case 'manual_match':
      case 'confirm_suggestion':
        await this.upsertPattern({
          organizationId: input.organizationId,
          sourceText: input.inputText,
          normalizedText,
          targetCustomerId: input.selectedCustomerId,
          patternType,
          createdBy: 'user_correction',
        });
        break;

      case 'manual_create':
        await this.createNewCustomerPattern({
          organizationId: input.organizationId,
          sourceText: input.inputText,
          normalizedText,
          targetCustomerId: input.selectedCustomerId,
          patternType,
        });
        break;

      case 'manual_reject':
        await this.demotePattern({
          organizationId: input.organizationId,
          customerId: input.selectedCustomerId,
          sourceText: input.inputText,
        });
        break;
    }

    await this.learnAttributes(input);
  }

  private async upsertPattern(params: {
    organizationId: string;
    sourceText: string;
    normalizedText: string;
    targetCustomerId: string;
    patternType: PatternType;
    createdBy: string;
  }): Promise<void> {
    // Buscar si ya existe un patrÃ³n similar
    const existing = await this.findExistingPattern(
      params.organizationId,
      params.normalizedText,
      params.targetCustomerId,
    );

    if (existing) {
      // Reforzar patrÃ³n existente
      await this.reinforcePattern(existing.id);
    }
  }

  private async reinforcePattern(patternId: string): Promise<void> {
    // Incrementar ocurrencias y restaurar score
    // (en producciÃ³n: db.similarityPattern.update)
  }

  private async demotePattern(params: {
    organizationId: string;
    customerId: string;
    sourceText: string;
  }): Promise<void> {
    const normalizedText = this.normalizeText(params.sourceText);
    const existing = await this.findExistingPattern(
      params.organizationId,
      normalizedText,
      params.customerId,
    );

    if (existing && existing.occurrences <= 1) {
      // Desactivar patrÃ³n si solo tiene 1 ocurrencia
      // (en producciÃ³n: db.similarityPattern.update)
    }
  }

  private async createNewCustomerPattern(params: {
    organizationId: string;
    sourceText: string;
    normalizedText: string;
    targetCustomerId: string;
    patternType: PatternType;
  }): Promise<void> {
    // Crear nuevo patrÃ³n y aprender atributos
    // (en producciÃ³n: db.similarityPattern.create)
  }

  private async learnAttributes(input: LearningInput): Promise<void> {
    const namePattern = /^[A-ZÃÃ‰ÃÃ“ÃšÃ‘\s]+$/i;
    const words = input.inputText.split(/\s+/);

    const personName = words
      .filter((w) => w.length > 2 && namePattern.test(w) && !w.includes('SA') && !w.includes('DE'))
      .join(' ');

    if (personName && personName.length >= 6) {
      // Aprender como posible representante
      // (en producciÃ³n: crear/actualizar CustomerAttribute)
    }
  }

  private determinePatternType(text: string): PatternType {
    const upper = text.toUpperCase();
    if (/CHEQUE|CH|CHQ/i.test(upper)) return 'check_to_client';
    if (/RFC|R\.F\.C/i.test(upper) || /[A-Z]{3,4}\d{6}[A-Z0-9]{3}/.test(upper)) return 'rut_in_ref';
    if (/OBRA|CONSTRUCCION|EDIFICIO/i.test(upper)) return 'obra_to_client';
    if (/CALLE|AV\.|AVENIDA|REFORMA|INSURGENTES/i.test(upper)) return 'address_to_client';
    if (/SPEI|TRANSF|TRANSFERENCIA|REF/i.test(upper)) return 'bank_ref_client';
    return 'name_similarity';
  }

  private normalizeText(text: string): string {
    return text
      .toUpperCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^\w\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  private async findExistingPattern(
    organizationId: string,
    normalizedText: string,
    customerId: string,
  ): Promise<{ id: string; occurrences: number } | null> {
    // (en producciÃ³n: db.similarityPattern.findFirst)
    return null;
  }
}

