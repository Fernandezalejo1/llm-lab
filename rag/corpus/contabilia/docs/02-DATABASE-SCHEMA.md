# CONTABILIA - Esquema de Base de Datos

## Diagrama de Entidades

```
Organization 1──N Customer 1──N Invoice 1──N InvoiceLine
                             1──N CustomerAttribute
                             1──N CustomerBalance

BankStatement 1──N BankMovement 1──1 PaymentMatch 1──N PaymentSuggestion
                                                   1──1 PaymentApplication 1──N AppliedInvoice

BankMovement 1──N MovementAnalysis

LearningLog N──1 Organization
SimilarityPattern N──1 Organization

PaymentApplication ──> Invoice (N:N via AppliedInvoice)

Reconciliation 1──N Organization
AuditLog N──1 Organization
```

## Tablas y Columnas

### Organization

```sql
CREATE TABLE organizations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    logo_url        TEXT,
    settings        JSONB NOT NULL DEFAULT '{}',
    -- settings: {auto_apply_threshold, currency, timezone, rules_config, notification_prefs}
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    -- trial, active, suspended, cancelled
    trial_ends_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_org_slug ON organizations(slug);
```

### Customer

```sql
CREATE TABLE customers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    legal_name      VARCHAR(500) NOT NULL,
    rfc             VARCHAR(20),
    alias           VARCHAR(255),
    email           VARCHAR(255),
    phone           VARCHAR(50),
    website         VARCHAR(500),
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    -- active, inactive, blocked
    notes           TEXT,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_customer_org ON customers(organization_id);
CREATE INDEX idx_customer_legal_name ON customers USING gin(legal_name gin_trgm_ops);
CREATE INDEX idx_customer_rfc ON customers(rfc);
CREATE UNIQUE INDEX idx_customer_org_rfc ON customers(organization_id, rfc) WHERE rfc IS NOT NULL;

COMMENT ON COLUMN customers.legal_name IS 'Razón social completa';
COMMENT ON COLUMN customers.alias IS 'Nombre corto o comercial';
```

### CustomerAttribute

```sql
CREATE TABLE customer_attributes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id     UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    attribute_type  VARCHAR(50) NOT NULL,
    -- legal_representative, owner, director, related_company,
    -- construction_site, address, site_address, phone, email,
    -- bank_account, clabe, known_alias, payment_method,
    -- payment_frequency, check_pattern, reference_code
    value           TEXT NOT NULL,
    source          VARCHAR(50) DEFAULT 'manual',
    -- manual, bank_statement, learning, import, system
    confidence      DECIMAL(5,2) DEFAULT 1.00,
    verified        BOOLEAN DEFAULT false,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cattr_customer ON customer_attributes(customer_id);
CREATE INDEX idx_cattr_type ON customer_attributes(attribute_type);
CREATE INDEX idx_cattr_value ON customer_attributes USING gin(value gin_trm_ops);

COMMENT ON COLUMN customer_attributes.attribute_type IS 'Tipo de atributo: representa la relación con el cliente';
COMMENT ON COLUMN customer_attributes.confidence IS 'Qué tan seguro estamos de que este atributo es correcto';
COMMENT ON COLUMN customer_attributes.source IS 'Origen del atributo: manual, learning, import, etc.';
```

### Invoice

```sql
CREATE TYPE invoice_type AS ENUM ('factura', 'credit_note', 'debit_note');
CREATE TYPE invoice_status AS ENUM ('issued', 'sent', 'partial', 'paid', 'overdue', 'cancelled');

CREATE TABLE invoices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    customer_id     UUID NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    invoice_type    invoice_type NOT NULL DEFAULT 'factura',
    invoice_number  VARCHAR(100) NOT NULL,
    invoice_serie   VARCHAR(50),
    rfc             VARCHAR(20),
    amount          DECIMAL(18,2) NOT NULL,
    tax             DECIMAL(18,2) DEFAULT 0,
    total           DECIMAL(18,2) NOT NULL,
    currency        VARCHAR(3) NOT NULL DEFAULT 'MXN',
    exchange_rate   DECIMAL(12,6) DEFAULT 1,
    issue_date      DATE NOT NULL,
    due_date        DATE NOT NULL,
    payment_date    DATE,
    status          invoice_status NOT NULL DEFAULT 'issued',
    balance         DECIMAL(18,2) NOT NULL, -- saldo pendiente
    notes           TEXT,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id, invoice_number)
);

CREATE INDEX idx_invoice_org ON invoices(organization_id);
CREATE INDEX idx_invoice_customer ON invoices(customer_id);
CREATE INDEX idx_invoice_status ON invoices(status);
CREATE INDEX idx_invoice_due_date ON invoices(due_date);
CREATE INDEX idx_invoice_balance ON invoices(balance) WHERE balance > 0;
```

### InvoiceLine

```sql
CREATE TABLE invoice_lines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id      UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    description     TEXT NOT NULL,
    quantity        DECIMAL(18,4) NOT NULL DEFAULT 1,
    unit_price      DECIMAL(18,4) NOT NULL,
    discount        DECIMAL(18,2) DEFAULT 0,
    total           DECIMAL(18,2) NOT NULL,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_iline_invoice ON invoice_lines(invoice_id);
```

### CustomerBalance

```sql
CREATE TABLE customer_balances (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id     UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    balance_type    VARCHAR(20) NOT NULL DEFAULT 'credit',
    -- credit (saldo a favor), advance (anticipo)
    amount          DECIMAL(18,2) NOT NULL DEFAULT 0,
    currency        VARCHAR(3) NOT NULL DEFAULT 'MXN',
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(customer_id, balance_type, currency)
);

CREATE INDEX idx_cbal_customer ON customer_balances(customer_id);
```

### BankStatement

```sql
CREATE TABLE bank_statements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    account_number  VARCHAR(100) NOT NULL,
    account_name    VARCHAR(255),
    bank_name       VARCHAR(255),
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    file_type       VARCHAR(20) NOT NULL, -- excel, csv, pdf
    file_path       TEXT,
    file_hash       VARCHAR(64), -- SHA-256
    original_name   VARCHAR(500),
    file_size       BIGINT,
    total_movements INTEGER DEFAULT 0,
    total_credits   DECIMAL(18,2) DEFAULT 0,
    total_debits    DECIMAL(18,2) DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- pending, processing, processed, completed, error
    error_message   TEXT,
    uploaded_by     UUID,
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ,
    metadata        JSONB DEFAULT '{}'
);

CREATE INDEX idx_bs_org ON bank_statements(organization_id);
CREATE INDEX idx_bs_status ON bank_statements(status);
CREATE INDEX idx_bs_period ON bank_statements(period_start, period_end);
```

### BankMovement

```sql
CREATE TYPE movement_type AS ENUM ('credit', 'debit', 'unknown');
CREATE TYPE movement_status AS ENUM (
    'pending', 'identified', 'applied', 'reconciled',
    'error', 'duplicate', 'unidentified'
);

CREATE TABLE bank_movements (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_statement_id UUID NOT NULL REFERENCES bank_statements(id) ON DELETE CASCADE,
    organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    transaction_date  DATE NOT NULL,
    value_date        DATE,
    description       TEXT NOT NULL,
    reference         VARCHAR(255),
    check_number      VARCHAR(50),
    movement_type     movement_type NOT NULL,
    debit_amount      DECIMAL(18,2) DEFAULT 0,
    credit_amount     DECIMAL(18,2) DEFAULT 0,
    currency          VARCHAR(3) NOT NULL DEFAULT 'MXN',
    exchange_rate     DECIMAL(12,6) DEFAULT 1,
    raw_data          JSONB, -- datos originales del archivo
    balance           DECIMAL(18,2),
    status            movement_status NOT NULL DEFAULT 'pending',
    sequence          INTEGER, -- orden dentro del estado de cuenta
    hash              VARCHAR(64), -- para detectar duplicados
    metadata          JSONB DEFAULT '{}',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bm_statement ON bank_movements(bank_statement_id);
CREATE INDEX idx_bm_org ON bank_movements(organization_id);
CREATE INDEX idx_bm_status ON bank_movements(status);
CREATE INDEX idx_bm_date ON bank_movements(transaction_date);
CREATE INDEX idx_bm_hash ON bank_movements(hash);
CREATE INDEX idx_bm_desc ON bank_movements USING gin(description gin_trm_ops);
CREATE INDEX idx_bm_reference ON bank_movements(reference);

COMMENT ON COLUMN bank_movements.hash IS 'Hash de (fecha, monto, descripcion, referencia) para detectar duplicados';
```

### PaymentMatch

```sql
CREATE TYPE match_status AS ENUM (
    'auto_accepted', 'pending_review', 'manual_confirmed',
    'manual_rejected', 'learning'
);

CREATE TYPE match_strategy AS ENUM (
    'rule_exact_name', 'rule_partial_name', 'rule_alias',
    'rule_related_company', 'rule_representative', 'rule_bank_account',
    'rule_check', 'rule_obra', 'rule_address', 'rule_frequency',
    'rule_history', 'rule_reference', 'rule_rfc',
    'ai_semantic', 'ai_fuzzy', 'ai_llm', 'learning_pattern',
    'manual', 'combined'
);

CREATE TABLE payment_matches (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_movement_id  UUID NOT NULL REFERENCES bank_movements(id) ON DELETE CASCADE,
    organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    customer_id       UUID REFERENCES customers(id) ON DELETE RESTRICT,
    engine_version    VARCHAR(20) NOT NULL,
    match_strategy    match_strategy NOT NULL,
    confidence        DECIMAL(5,2) NOT NULL, -- 0.00 - 100.00
    status            match_status NOT NULL DEFAULT 'pending_review',
    executed_rules    JSONB, -- [lista de reglas ejecutadas con resultados]
    matched_rules     JSONB, -- [reglas que hicieron match]
    evidence          JSONB, -- {detalle de evidencia encontrada}
    ai_analysis       JSONB, -- {resultado del análisis de IA si se usó}
    reviewed_by       UUID,
    reviewed_at       TIMESTAMPTZ,
    reviewed_notes    TEXT,
    is_correction     BOOLEAN DEFAULT false,
    correction_of_id  UUID REFERENCES payment_matches(id),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pm_movement ON payment_matches(bank_movement_id);
CREATE INDEX idx_pm_customer ON payment_matches(customer_id);
CREATE INDEX idx_pm_status ON payment_matches(status);
CREATE INDEX idx_pm_confidence ON payment_matches(confidence);
```

### PaymentSuggestion

```sql
CREATE TABLE payment_suggestions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_match_id  UUID NOT NULL REFERENCES payment_matches(id) ON DELETE CASCADE,
    customer_id       UUID NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    confidence        DECIMAL(5,2) NOT NULL,
    strategy_used     match_strategy NOT NULL,
    evidence_summary  TEXT,
    suggested_invoices JSONB, -- [{invoice_id, amount, reason}]
    selected          BOOLEAN DEFAULT false,
    reason            TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ps_match ON payment_suggestions(payment_match_id);
```

### PaymentApplication

```sql
CREATE TYPE application_type AS ENUM (
    'full', 'partial', 'multiple', 'advance',
    'credit_note', 'debit_note', 'balance_forward'
);

CREATE TABLE payment_applications (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_match_id  UUID NOT NULL REFERENCES payment_matches(id) ON DELETE CASCADE,
    organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    application_type  application_type NOT NULL,
    total_amount      DECIMAL(18,2) NOT NULL,
    applied_amount    DECIMAL(18,2) NOT NULL,
    difference        DECIMAL(18,2) DEFAULT 0,
    difference_reason VARCHAR(100),
    -- overpayment, underpayment, exchange_rate, discount, other
    notes             TEXT,
    status            VARCHAR(20) NOT NULL DEFAULT 'completed',
    -- completed, pending_approval, error
    created_by        UUID,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pa_match ON payment_applications(payment_match_id);
CREATE INDEX idx_pa_org ON payment_applications(organization_id);
```

### AppliedInvoice

```sql
CREATE TABLE applied_invoices (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id    UUID NOT NULL REFERENCES payment_applications(id) ON DELETE CASCADE,
    invoice_id        UUID NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    amount_applied    DECIMAL(18,2) NOT NULL,
    previous_balance  DECIMAL(18,2) NOT NULL,
    new_balance       DECIMAL(18,2) NOT NULL,
    is_partial        BOOLEAN DEFAULT false,
    notes             TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_application ON applied_invoices(application_id);
CREATE INDEX idx_ai_invoice ON applied_invoices(invoice_id);
```

### MovementAnalysis

```sql
CREATE TABLE movement_analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    movement_id     UUID NOT NULL REFERENCES bank_movements(id) ON DELETE CASCADE,
    analysis_type   VARCHAR(50) NOT NULL,
    -- preprocessing, rule_evaluation, ai_evaluation, combined
    result          JSONB NOT NULL,
    confidence      DECIMAL(5,2),
    details         TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ma_movement ON movement_analyses(movement_id);
```

### LearningLog

```sql
CREATE TABLE learning_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    input_text          TEXT NOT NULL, -- texto original del banco
    normalized_text     TEXT,
    suggested_customer  UUID REFERENCES customers(id),
    selected_customer   UUID REFERENCES customers(id),
    confidence          DECIMAL(5,2),
    correction_type     VARCHAR(50) NOT NULL,
    -- manual_match, manual_reject, manual_create, confirm_suggestion
    user_id             UUID,
    feedback            JSONB, -- {reason, notes, attributes_learned}
    match_strategy      match_strategy,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ll_org ON learning_logs(organization_id);
CREATE INDEX idx_ll_input ON learning_logs USING gin(input_text gin_trm_ops);
CREATE INDEX idx_ll_created ON learning_logs(created_at);
```

### SimilarityPattern

```sql
CREATE TYPE pattern_type AS ENUM (
    'name_alias', 'name_similarity', 'bank_ref_client',
    'check_to_client', 'obra_to_client', 'address_to_client',
    'rfc_in_ref', 'representative_payment', 'generic'
);

CREATE TABLE similarity_patterns (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    pattern_type        pattern_type NOT NULL,
    source_text         TEXT NOT NULL, -- texto original
    normalized_text     TEXT NOT NULL, -- texto normalizado para búsqueda
    target_customer_id  UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    similarity_score    DECIMAL(5,2) DEFAULT 0.00,
    occurrences         INTEGER NOT NULL DEFAULT 1,
    last_used_at        TIMESTAMPTZ,
    is_active           BOOLEAN DEFAULT true,
    created_by          VARCHAR(50) NOT NULL DEFAULT 'system',
    -- system, user_correction, manual, learning
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sp_org ON similarity_patterns(organization_id);
CREATE INDEX idx_sp_norm ON similarity_patterns USING gin(normalized_text gin_trm_ops);
CREATE INDEX idx_sp_type ON similarity_patterns(pattern_type);
CREATE INDEX idx_sp_customer ON similarity_patterns(target_customer_id);
CREATE INDEX idx_sp_active ON similarity_patterns(is_active) WHERE is_active = true;
```

### Reconciliation

```sql
CREATE TABLE reconciliations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    bank_statement_id   UUID REFERENCES bank_statements(id),
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    total_movements     INTEGER NOT NULL DEFAULT 0,
    total_credits       DECIMAL(18,2) DEFAULT 0,
    total_debits        DECIMAL(18,2) DEFAULT 0,
    conciliated_count   INTEGER DEFAULT 0,
    pending_count       INTEGER DEFAULT 0,
    unidentified_count  INTEGER DEFAULT 0,
    error_count         INTEGER DEFAULT 0,
    duplicate_count     INTEGER DEFAULT 0,
    advance_count       INTEGER DEFAULT 0,
    balance_forward_count INTEGER DEFAULT 0,
    status              VARCHAR(20) NOT NULL DEFAULT 'draft',
    -- draft, completed, verified
    notes               TEXT,
    generated_by        UUID,
    generated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verified_at         TIMESTAMPTZ,
    metadata            JSONB DEFAULT '{}'
);

CREATE INDEX idx_rec_org ON reconciliations(organization_id);
CREATE INDEX idx_rec_period ON reconciliations(period_start, period_end);
```

### AuditLog

```sql
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    entity_type     VARCHAR(50) NOT NULL,
    -- bank_movement, payment_match, payment_application,
    -- customer, invoice, reconciliation, etc.
    entity_id       UUID NOT NULL,
    action          VARCHAR(50) NOT NULL,
    -- created, updated, deleted, identified, applied,
    -- reconciled, corrected, reviewed, imported, exported
    previous_state  JSONB,
    new_state       JSONB,
    user_id         UUID,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_al_org ON audit_logs(organization_id);
CREATE INDEX idx_al_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_al_action ON audit_logs(action);
CREATE INDEX idx_al_created ON audit_logs(created_at);
```

### Users (para el SaaS)

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    avatar_url      TEXT,
    role            VARCHAR(20) NOT NULL DEFAULT 'member',
    -- admin, member, viewer
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE organization_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL DEFAULT 'member',
    -- owner, admin, member, viewer
    joined_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id, user_id)
);
```

## Diagrama de Relaciones (Resumen)

```
organizations
  ├── users (N:N via organization_members)
  ├── customers
  │     ├── customer_attributes
  │     ├── invoices
  │     │     └── invoice_lines
  │     ├── customer_balances
  │     └── similarity_patterns (target)
  ├── bank_statements
  │     └── bank_movements
  │           ├── payment_matches
  │           │     ├── payment_suggestions
  │           │     └── payment_applications
  │           │           └── applied_invoices
  │           └── movement_analyses
  ├── reconciliations
  ├── learning_logs
  ├── similarity_patterns
  └── audit_logs
```
