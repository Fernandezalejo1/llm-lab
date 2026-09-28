# CONTABILIA - PRD Completo, Arquitectura y Plan de Negocio

## Indice

1. Vision del Producto
2. Problemas que Resuelve
3. Caso de Uso: Flujo Completo
4. Arquitectura Completa del Sistema
5. Modelo de Datos Extendido
6. Base de Datos: Tablas Nuevas
7. Motor de Conciliacion Hibrido
8. Motor de IA
9. Motor de Reglas
10. Portal del Cliente (B2B)
11. Panel Administrativo
12. APIs e Integraciones
13. Seguridad
14. Escalabilidad
15. Roadmap de Desarrollo
16. MVP
17. Versiones Futuras
18. Modelo SaaS
19. Estrategia Comercial
20. Riesgos Tecnicos y de Negocio
21. Comparacion con Soluciones Existentes
22. Funcionalidades Innovadoras
23. Estrategia para Ser el Estandar
24. Critica al Diseno y Alternativas
25. Decisiones de Diseno Criticas

---

## 1. Vision del Producto

### 1.1 Declaracion de Vision

**Contabilia** es la plataforma de gestion inteligente de cobros B2B que elimina la conciliacion bancaria manual. No es un conciliador: es el sistema donde los clientes pagan correctamente desde el origen, haciendo que la conciliacion sea una consecuencia automatica, no un proceso posterior.

### 1.2 El Cambio de Paradigma

```
MODELO ACTUAL (Reactor):

Cliente paga -> Dinero llega -> Administrativo busca -> Concilia

Problema: todo ocurre DESPUES del pago.
Resultado: horas de trabajo manual, errores, demoras.


CONTABILIA (Predictor):

Cliente entra al portal -> Selecciona facturas -> El sistema
genera Orden de Pago con referencia unica -> Cliente paga
con esa referencia -> El banco recibe -> Conciliacion
automatica por referencia exacta.

Resultado: 95%+ de conciliacion automatica desde el dia 1.
```

### 1.3 Principios Fundamentales

| # | Principio | Descripcion |
|---|-----------|-------------|
| 1 | **Captura antes del cobro** | La informacion se obtiene ANTES de que el dinero llegue al banco |
| 2 | **Referencia unica** | Cada pago tiene un ID unico (ej: PAGO-58412) que el cliente usa como referencia |
| 3 | **El cliente se auto-sirve** | El portal reduce al minimo la intervencion del cobrador |
| 4 | **Confianza como espectro** | Toda decision tiene un % de confianza, nunca binaria |
| 5 | **Aprendizaje continuo** | Cada correccion humana alimenta el sistema |
| 6 | **IA como asistente, no juez** | La IA sugiere, el humano confirma en casos criticos |
| 7 | **Multi-tenant estricto** | Cada organizacion esta completamente aislada |
| 8 | **Trazabilidad total** | Cada accion tiene un audit trail completo |

### 1.4 Propuesta de Valor

**Para el distribuidor** (nuestro cliente):
- Reduce el tiempo de conciliacion de horas diarias a minutos
- Elimina errores de imputacion de pagos
- Mejora la relacion con sus clientes (portal self-service)
- Visibilidad en tiempo real del estado de cobros
- Aprendizaje automatico que mejora con cada mes

**Para el cliente del distribuidor** (quien paga):
- Ve todas sus facturas pendientes en un solo lugar
- Paga exactamente lo que debe, sin errores de referencia
- Genera ordenes de pago con un clic
- Usa creditos existentes automaticamente
- Historial completo de pagos

---

## 2. Problemas que Resuelve

### 2.1 Problema Core: La Convergencia de Datos

```
                    +------------------+
                    |   DATOS BANCARIOS |
                    |  (lo que el banco |
                    |   nos dice)       |
                    +--------+---------+
                             |
    +------------------------+------------------------+
    |                        |                        |
    v                        v                        v
+----------+          +-----------+          +------------+
|Nombre    |          |Referencia |          |Monto       |
|"Jose"    |          |"PAGO"     |          |$6,000      |
|          |          |"GRACIAS"  |          |            |
|(generico)|          |"12345"    |          |(a que      |
|          |          |(inutil)   |          | factura?)  |
+----------+          +-----------+          +------------+

                             +

                    +------------------+
                    |   DATOS INTERNOS  |
                    |  (lo que nosotros |
                    |   sabemos)        |
                    +--------+---------+
                             |
    +------------------------+------------------------+
    |                        |                        |
    v                        v                        v
+----------+          +-----------+          +------------+
|Clientes  |          |Facturas   |          |Saldos      |
|con       |          |pendientes |          |a favor     |
|alias     |          |con        |          |y           |
|varios    |          |montos     |          |anticipos   |
+----------+          +-----------+          +------------+

    EL PROBLEMA:
    La union de estos dos conjuntos de datos
    requiere juicio humano -> Horas de trabajo.
```

### 2.2 Desglose de Dolor Economico

| Aspecto | Impacto | Costo Anual Estimado (empresa 50 empleados) |
|---------|---------|----------------------------------------------|
| Tiempo administrativo en conciliacion | 2-4 horas diarias por contador | $15,000 - $30,000 USD |
| Errores de imputacion | 3-5% de pagos mal aplicados | $5,000 - $20,000 USD |
| Pagos no identificados | 5-15% de movimientos sin ID | Capital de trabajo inmovilizado |
| Clientes que no pagan a tiempo | 10-20% de facturas vencidas | $20,000 - $100,000 USD |
| Sanciones por mora/error | Variable | $1,000 - $10,000 USD |
| **Total estimado** | | **$41,000 - $160,000 USD/ano** |

### 2.3 Los 7 Casos que Matan la Productividad

| Caso | Descripcion | Solucion Contabilia |
|------|-------------|---------------------|
| **1. Pago parcial** | Cliente debe $28K, paga $6K | Portal muestra facturas, cliente selecciona cuales pagar |
| **2. Pago excedente** | Cliente debe $50K, paga $80K | Portal genera orden por $50K, sobrante -> credito automatico |
| **3. Multi-empresa** | Jose tiene 3 empresas | Portal: Jose selecciona empresa -> paga facturas de esa empresa |
| **4. Sin referencia** | Cliente escribe "Jose" o nada | Referencia unica PAGO-XXXXX resuelve esto |
| **5. Pagos multiples** | Varios pagos pequenos en el mes | Cada pago tiene su orden -> conciliacion automatica |
| **6. Una transferencia, varias facturas** | Pago cubre 3 facturas | Portal permite seleccionar multiples facturas |
| **7. Pago parcial de multiples facturas** | Pago cubre parcialmente 3 facturas | Portal calcula distribucion optima |

---

## 3. Caso de Uso: Flujo Completo

### 3.1 Flujo Principal (Happy Path)

```
DIA 1 - CLIENTE
===============

1. Distribuidor envia link al cliente:
   "Accede a tu portal en portal.contabilia.app"
   "Usuario: jose@constructora.com"

2. Jose entra al portal.

3. Jose tiene 3 empresas registradas:
   +---------------------------+
   | Selecciona tu empresa:    |
   |  Constructora Norte SA    | <- Jose selecciona
   |  Constructora Sur SA      |
   |  Hormigones SA            |
   +---------------------------+

4. Ve las facturas pendientes de Constructora Norte:
   +----------------------------------------------+
   |  Factura    | Monto    | Vence    | Estado   |
   |-------------|----------|----------|----------|
   |  FAC-001    | $5,000   | 15/01   | Pend.    |
   |  FAC-002    | $8,000   | 20/01   | Pend.    |
   |  FAC-003    | $15,000  | 25/01   | Pend.    |
   |-------------|----------|----------|----------|
   |  Total pendiente:           $28,000          |
   |  Credito disponible:        $3,000           |
   +----------------------------------------------+

5. Jose selecciona FAC-001 ($5,000) y parte de FAC-002 ($1,000).

6. El sistema genera ORDEN DE PAGO: PAGO-58412

7. Jose transfiere $6,000 con referencia: PAGO-58412

DIA 2 - SISTEMA
===============

8. Movimiento bancario llega: TRANSF SPEI PAGO-58412, $6,000

9. MOTOR DE REGLAS detecta referencia PAGO-58412 -> match 99.9%

10. APLICACION AUTOMATICA:
    FAC-001: $5,000 -> pagada
    FAC-002: $1,000 -> parcial (pendiente $7,000)

11. Jose recibe notificacion: "Tu pago fue aplicado correctamente"

TOTAL TIEMPO HUMANO: 2 minutos
DECISIONES MANUALES: 0
```

### 3.2 Flujo Fallback (Sin Portal)

Si el cliente NO usa el portal y transfiere directamente:
1. Movimiento llega sin referencia de Orden de Pago
2. Pipeline de identificacion clasico se activa:
   - Reglas deterministicas (R01-R13)
   - Motor heuristico (fuzzy matching)
   - IA (embeddings + LLM)
3. Se muestra al administrador con % de confianza
4. El administrador confirma o corrige
5. El sistema aprende de la decision

---

## 4. Arquitectura Completa del Sistema

### 4.1 Arquitectura de Alto Nivel

```
+---------------------------------------------------------------------+
|                        CAPA DE PRESENTACION                          |
|  +---------------+  +---------------+  +------------------------+   |
|  | Portal        |  | Panel Admin   |  | Landing Page           |   |
|  | Cliente (B2B) |  | (Dashboard)   |  | marketing.contabilia |   |
|  +-------+-------+  +-------+-------+  +----------+-------------+   |
|          +-------------------+---------------------+                 |
|                    +-------v--------+                               |
|                    |   API GATEWAY   |                               |
|                    |  (GraphQL+REST) |                               |
|                    +-------+--------+                               |
+----------------------------+----------------------------------------+
                             |
+----------------------------+----------------------------------------+
|                    CAPA DE APLICACION (NestJS - Modular)             |
|  Auth | Organizations | Customers | Invoices | BankMovements        |
|  PaymentOrders (NUEVO) | Identification | CashApp | Reconciliation  |
|  Rules | Learning | Notifications | Reports | Audit | Integrations  |
+----------------------------+----------------------------------------+
                             |
+----------------------------+----------------------------------------+
|                    CAPA DE INFRAESTRUCTURA                          |
|  PostgreSQL | Redis+BullMQ | Qdrant | S3/MinIO                    |
+----------------------------------------------------------------------+
                             |
+----------------------------+----------------------------------------+
|                    SERVICIOS EXTERNOS                                |
|  AI Service (Python) | Open Banking | ERP Integrations              |
|  Email (SendGrid) | WhatsApp | OCR (Textract)                      |
+----------------------------------------------------------------------+
```

### 4.2 Flujo de Datos: Referencia Unica

```
1. Cliente selecciona facturas en el portal
2. Sistema genera PaymentOrder con reference = "PAGO-58412"
3. Cliente transfiere $6,000 con referencia "PAGO-58412"
4. Movimiento bancario llega con referencia "PAGO-58412"
5. Lookup en payment_orders -> match encontrado -> confianza 99.9%
6. Aplicacion automatica segun la orden
7. Conciliacion completada sin intervencion humana
```

---

## 5. Modelo de Datos Extendido

### 5.1 Diagrama de Entidades

```
Organization
+-- Users (via OrganizationMember)
+-- Customers
|   +-- CustomerAttributes
|   +-- Invoices
|   |   +-- InvoiceLines
|   +-- CustomerBalances
|   +-- SimilarityPatterns (target)
+-- PaymentOrders (NUEVO - Referencia Unica)
|   +-- PaymentOrderItems (NUEVO)
+-- BankStatements
|   +-- BankMovements
|       +-- PaymentMatches
|       |   +-- PaymentSuggestions
|       |   +-- PaymentApplications
|       |       +-- AppliedInvoices
|       +-- MovementAnalyses
+-- Reconciliations
+-- LearningLogs
+-- AuditLogs
+-- NotificationQueues (NUEVO)
+-- IntegrationConfigs (NUEVO)
+-- PortalUsers (NUEVO)
|   +-- PortalUserOrganizations (NUEVO)
|   +-- PortalUserCustomers (NUEVO)
+-- CustomerPortalInvitations (NUEVO)
```

---

## 6. Base de Datos: Tablas Nuevas

### 6.1 PaymentOrder

```sql
CREATE TABLE payment_orders (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    customer_id       UUID NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    reference         VARCHAR(50) UNIQUE NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_amount      DECIMAL(18,2) NOT NULL,
    paid_amount       DECIMAL(18,2) DEFAULT 0,
    remaining_amount  DECIMAL(18,2) NOT NULL,
    currency          VARCHAR(3) NOT NULL DEFAULT 'MXN',
    description       TEXT,
    expires_at        TIMESTAMPTZ NOT NULL,
    paid_at           TIMESTAMPTZ,
    metadata          JSONB DEFAULT '{}',
    created_by        UUID,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 6.2 PaymentOrderItem

```sql
CREATE TABLE payment_order_items (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_order_id  UUID NOT NULL REFERENCES payment_orders(id) ON DELETE CASCADE,
    invoice_id        UUID NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    amount            DECIMAL(18,2) NOT NULL,
    is_partial        BOOLEAN DEFAULT false,
    previous_balance  DECIMAL(18,2) NOT NULL,
    new_balance       DECIMAL(18,2) NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 6.3 PortalUser

```sql
CREATE TABLE portal_users (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email             VARCHAR(255) UNIQUE NOT NULL,
    password_hash     VARCHAR(255) NOT NULL,
    first_name        VARCHAR(100),
    last_name         VARCHAR(100),
    phone             VARCHAR(50),
    status            VARCHAR(20) NOT NULL DEFAULT 'active',
    last_login_at     TIMESTAMPTZ,
    email_verified    BOOLEAN DEFAULT false,
    mfa_enabled       BOOLEAN DEFAULT false,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 6.4 PortalUserOrganization

```sql
CREATE TABLE portal_user_organizations (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portal_user_id    UUID NOT NULL REFERENCES portal_users(id) ON DELETE CASCADE,
    organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role              VARCHAR(20) NOT NULL DEFAULT 'viewer',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(portal_user_id, organization_id)
);
```

### 6.5 PortalUserCustomer

```sql
CREATE TABLE portal_user_customers (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portal_user_id    UUID NOT NULL REFERENCES portal_users(id) ON DELETE CASCADE,
    customer_id       UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    is_default        BOOLEAN DEFAULT false,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(portal_user_id, customer_id)
);
```

### 6.6 NotificationQueue

```sql
CREATE TABLE notification_queue (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    recipient_type    VARCHAR(20) NOT NULL,
    recipient_id      UUID NOT NULL,
    channel           VARCHAR(20) NOT NULL,
    template          VARCHAR(100) NOT NULL,
    subject           VARCHAR(500),
    body              TEXT NOT NULL,
    metadata          JSONB DEFAULT '{}',
    status            VARCHAR(20) NOT NULL DEFAULT 'pending',
    sent_at           TIMESTAMPTZ,
    read_at           TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 6.7 IntegrationConfig

```sql
CREATE TABLE integration_configs (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    integration_type  VARCHAR(50) NOT NULL,
    config            JSONB NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'inactive',
    last_sync_at      TIMESTAMPTZ,
    error_message     TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 6.8 CustomerPortalInvitation

```sql
CREATE TABLE customer_portal_invitations (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    customer_id       UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    email             VARCHAR(255) NOT NULL,
    token             VARCHAR(255) UNIQUE NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'pending',
    invited_by        UUID,
    expires_at        TIMESTAMPTZ NOT NULL,
    accepted_at       TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 7. Motor de Conciliacion Hibrido

### 7.1 Pipeline de 5 Etapas

```
ETAPA 0: REFERENCIA UNICA (NUEVO)
==================================
Input: BankMovement.reference
Output: PaymentOrder match -> confianza 99.9%
Si hay match -> Conciliacion AUTOMATICA. Sin intervencion.
Este es el 95% de los casos si se adopta el portal.

ETAPA 1: REGLAS DETERMINISTICAS
=================================
Reglas R01-R13
Si confianza >= 90% -> AUTO-ACEPTAR
Si confianza 70-89% -> ETAPA 2

ETAPA 2: MOTOR HEURISTICO
===========================
Fuzzy matching + embeddings + patrones aprendidos
Si score >= 80% -> ETAPA 3 (validacion por monto)

ETAPA 3: VALIDACION POR MONTO
===============================
Verificar si el monto coincide con facturas del candidato
Si confianza ajustada >= 90% -> AUTO-ACEPTAR

ETAPA 4: MOTOR IA COMPLETO
============================
Embeddings + Clasificador + LLM reasoning
Si confianza >= 85% -> Sugerir

ETAPA 5: REVISION HUMANA
==========================
El operador confirma, corrige o rechaza.
Cada decision -> Learning Log -> El sistema aprende.
```

### 7.2 Estados de Conciliacion

| Estado | Color | Confianza | Origen |
|--------|-------|-----------|--------|
| CONCILIADO AUTOMATICAMENTE | Verde solido | >= 95% | Referencia Unica / Regla exacta |
| CONCILIADO CON ALTA CONFIANZA | Verde claro | 85-94% | Reglas + Validacion monto |
| REQUIERE REVISION | Amarillo | 60-84% | Heuristico + IA |
| NO IDENTIFICADO | Rojo claro | < 60% | Sin candidato encontrado |
| ERROR / DUPLICADO | Rojo solido | N/A | Duplicado o inconsistente |

---

## 8. Motor de IA

### 8.1 Arquitectura

```
MOTOR DE IA (Python Microservice)
FastAPI + scikit-learn + sentence-transformers

EMBEDDINGS SERVICE:
  all-MiniLM-L6-v2 (384 dims)
  Qdrant por organizacion

CLASSIFIER SERVICE:
  Gradient Boosting (sklearn)
  Features: levenshtein, token_overlap, trigram,
            amount_match, frequency, recency, embedding_sim

LLM REASONING:
  GPT-4o-mini / Claude 3.5 Sonnet
  Solo para casos no resueltos por reglas + fuzzy
  Costo: $0.001-0.01 por analisis

PLATT SCALING:
  Calibracion de probabilidades para scores confiables
```

### 8.2 Flujo de Decision

```
Movimiento -> Normalizar texto -> Generar embedding
-> Buscar en Qdrant (top-10) -> Calcular fuzzy scores
-> Clasificador Gradient Boosting -> Probabilidad calibrada
-> >= 85%? SI: Auto-sugerir / NO: LLM reasoning
```

---

## 9. Motor de Reglas

### 9.1 Reglas (15)

| ID | Regla | Peso |
|----|-------|------|
| R00 | **PaymentOrder Match** | 99.9% |
| R01 | Referencia exacta de factura | 95% |
| R02 | Numero de factura en descripcion | 90% |
| R03 | RFC del cliente | 85% |
| R04 | CLABE bancaria conocida | 80% |
| R05 | Representante legal | 75% |
| R06 | Empresa relacionada | 70% |
| R07 | Nombre exacto del cliente | 80% |
| R08 | Alias conocido | 85% |
| R09 | Numero de cheque | 90% |
| R10 | Direccion/obra | 60% |
| R11 | Frecuencia de pago habitual | 50% |
| R12 | Cuenta bancaria conocida | 85% |
| R13 | Monto exacto de factura | 60% |
| R14 | **Learning Pattern** | Variable |

### 9.2 Regla R00: PaymentOrder Match

La regla mas importante: busca en `payment_orders` por `reference`. Si encuentra match con monto compatible, confianza 99.9%.

---

## 10. Portal del Cliente (B2B)

### 10.1 Pantallas

**Login + Seleccion de Empresa:**
- Email + password
- Si multiples empresas: pantalla de seleccion
- Cada empresa muestra: facturas pendientes y saldo total

**Dashboard:**
- Resumen: total pendiente, credito disponible, cobrado mes, facturas pendientes
- Lista de facturas con checkbox para seleccionar
- Selector de credito existente
- Boton "Crear Orden de Pago"
- Historial de pagos recientes

**Crear Orden de Pago:**
- Facturas seleccionadas con montos editables (parcial/ completo)
- Resumen: subtotal, credito, total a transferir
- Instruccion con referencia unica PAGO-XXXXX
- Boton copiar referencia
- Descargar instrucciones PDF
- Fecha de expiracion

**Subir Comprobante:**
- Drag & drop de imagen/PDF
- Asociacion automatica a orden de pago
- Notificacion al administrador

### 10.2 API del Portal

```
POST   /auth/login
POST   /auth/logout
GET    /auth/me
GET    /organizations
POST   /organizations/:id/switch
GET    /invoices
GET    /invoices/:id/pdf
POST   /payment-orders
GET    /payment-orders/:id
POST   /payment-orders/:id/cancel
GET    /payments
GET    /balances
POST   /payment-proofs
GET    /notifications
```

---

## 11. Panel Administrativo

### 11.1 Modulos

- **Dashboard**: Metricas generales, conciliacion por estado, ordenes de pago, alertas IA
- **Conciliacion**: Movimientos pendientes, automatica, requieren revision, no identificados
- **Facturas**: Lista, importar, estados
- **Clientes**: Directorio, atributos, patrones, portal
- **Movimientos Bancarios**: Importar estados, lista, duplicados
- **Ordenes de Pago**: Pendientes, pagadas, expiradas, configuracion
- **Creditos y Anticipos**: Saldos, anticipos, movimientos
- **IA y Aprendizaje**: Sugerencias, patrones, historial correcciones, precision
- **Reportes**: Conciliacion, cobros, antiguedad, rendimiento IA, exportar
- **Configuracion**: Organizacion, usuarios, reglas, integraciones, notificaciones
- **Auditoria**: Log de acciones, cambios, historial

---

## 12. APIs e Integraciones

### 12.1 API REST

```
Base: https://api.contabilia.app/v1
Auth: Bearer Token (JWT)
Rate: 1000 req/min por tenant

# Clientes, Facturas, Movimientos, Ordenes de Pago,
# Conciliacion, Identificacion, Creditos, Reportes,
# Configuracion, Auditoria
```

### 12.2 ERPs

- **SAP**: RFC/JCo import, payment export
- **Oracle NetSuite**: REST API
- **Odoo**: XML-RPC/JSON-RPC + Webhooks
- **QuickBooks/Xero**: OAuth 2.0
- **Holded**: REST API + Webhooks
- **Dynamics 365**: Dataverse/OData

### 12.3 Bancos

- **NIVEL 1 (MVP)**: Excel, CSV, PDF import
- **NIVEL 2**: Open Banking APIs (Mexico, Colombia, Chile, Espana)
- **NIVEL 3**: Webhooks bancarios, polling, SFTP

### 12.4 Comunicacion

- Email (SendGrid/AWS SES)
- WhatsApp Business API
- Webhooks para ERPs

---

## 13. Seguridad

### 13.1 Capas

1. **Autenticacion**: JWT (15min/7d admin, 30min/30d portal), bcrypt, MFA (TOTP), SSO (SAML 2.0)
2. **RBAC**: owner, admin, member, viewer (admin y portal)
3. **Multi-Tenant**: TenantGuard + Row-Level Security en PostgreSQL
4. **Cifrado**: TLS 1.3 en transito, AES-256 en reposo, bcrypt passwords
5. **Auditoria**: AuditLog en cada accion, retencion 7 anos

### 13.2 Backups

- PostgreSQL: WAL archiving, full diario, incremental 6h, RPO 6h, RTO 30min
- Redis: RDB cada 15min + AOF
- SLA: 99.9% uptime

---

## 14. Escalabilidad

### 14.1 Niveles

| Nivel | Empresas | Movimientos/dia | Stack | Costo |
|-------|----------|-----------------|-------|-------|
| 1 | 0-1,000 | ~100K | Monolito NestJS, PG, Redis, Qdrant | $500-1K/mes |
| 2 | 1K-10K | ~1M | Microservicios, sharding, clusters | $3-8K/mes |
| 3 | 10K+ | ~10M | Multi-region, multi-AZ | $15-40K/mes |

### 14.2 Optimizaciones

- **DB**: Partitioning por mes, indices parciales, materialized views, PgBouncer
- **Cache**: Redis TTL por tipo (5min clientes, 1min facturas, 30s dashboard)
- **Colas**: BullMQ workers dedicados, batch processing, circuit breaker
- **Busqueda**: Qdrant HNSW, GIN indexes PostgreSQL

---

## 15. Roadmap

| Fase | Semanas | Descripcion |
|------|---------|-------------|
| **FASE 0** | 1-4 | Foundation: lo que existe + limpieza, CI/CD, tests, RLS |
| **FASE 1** | 5-10 | Core Engine: PaymentOrder, Portal, Reglas R00-R13, Cash App |
| **FASE 2** | 11-16 | AI + Learning: Embeddings, Fuzzy, LLM, Learning Engine |
| **FASE 3** | 17-24 | Integraciones: SAP, Odoo, QuickBooks, Open Banking, WhatsApp |
| **FASE 4** | 25-32 | Growth: SSO, API publica, Webhooks, i18n, Billing |

---

## 16. MVP

### Definicion

```
6 semanas de desarrollo

INCLUYE:
  Portal del cliente (login, facturas, crear orden)
  Referencia unica (PAGO-XXXXX)
  Importacion estados de cuenta (Excel, CSV)
  Conciliacion por referencia exacta (R00)
  Reglas basicas (R01, R02, R07, R08, R13)
  Cash application (FIFO + subset sum simple)
  Dashboard, CRUD clientes/facturas
  JWT auth, Multi-tenant basico

NO INCLUYE:
  IA/ML, ERPs, WhatsApp, Open Banking, OCR,
  Reportes avanzados, SSO, MFA

TARGET: 1-3 empresas piloto, 50-200 clientes portal
EXITO: >= 70% conciliacion automatica, reduccion >= 60% tiempo
```

---

## 17. Versiones Futuras

**v1.0**: IA basica, learning engine, 1 ERP integration, reportes, email notifications
**v2.0**: LLM reasoning, SAP/Oracle/Dynamics, Open Banking, WhatsApp, OCR, multi-idioma
**v3.0**: Predictive analytics, cash flow forecasting, credit scoring, multi-moneda, white-label

---

## 18. Modelo SaaS

### Pricing

| Plan | Precio | Clientes | Movimientos/mes | IA | Integraciones |
|------|--------|----------|-----------------|-----|---------------|
| **Starter** | $99/mes | 100 | 500 | Reglas | No |
| **Professional** | $299/mes | 500 | 2,000 | IA basica | 1 ERP |
| **Enterprise** | $799/mes | Ilimitado | 10,000 | IA completa+LLM | Ilimitadas |

**Add-ons**: Movimientos extra $0.05, portal users $2/usuario, LLM $0.001/analisis, integracion $49/mes

### Unit Economics

- CAC: $500-1,500
- ARPU: $250/mes
- LTV: $6,000-9,000
- LTV/CAC: 4-6x
- Churn: < 5% mensual
- Gross Margin: 80-85%

---

## 19. Estrategia Comercial

### Target Market (ICP)

**Industrias**: Distribucion mayorista, constructoras, manufactura, servicios profesionales, import/export
**Tamano**: 10-500 empleados, $1M-$50M facturacion, 50-5,000 facturas pendientes
**Dolor**: >= 2 personas en conciliacion, >= 2 horas diarias, ERP que no resuelve
**Decisor**: Director Financiero, Controller, Gerente Cobranza, Dueno, Estudio Contable

### Canales

1. **Inbound**: Blog, guias, webinars, case studies
2. **Partnerships**: Estudios contables, consultores ERPs, camaras empresariales
3. **Outbound**: LinkedIn, email, llamadas, demos
4. **PLG**: Free trial 14d, portal como viral loop, referral $100
5. **Eventos**: Ferias fintech, meetups, conferencias

### Ventajas Sostenibles

1. **Portal B2B**: Network effect, switching cost enorme
2. **Learning Engine**: Moat de datos por organizacion
3. **Enfoque "antes del cobro"**: Diferenciador radical (80-95% menos trabajo)

---

## 20. Riesgos

### Tecnicos

| Riesgo | Prob. | Impacto | Mitigacion |
|--------|-------|---------|------------|
| Baja adopcion del portal | Alta | Alto | Onboarding guiado, simplicidad, fallback reglas+IA |
| Precision IA insuficiente | Media | Alto | Empezar con reglas, IA como complemento |
| Escalabilidad subset sum | Baja | Medio | Limite 50 facturas, greedy, portal reduce busqueda |
| Dependencia LLM | Media | Medio | Fallback reglas, cache, multi-provider |

### Negocio

| Riesgo | Prob. | Impacto | Mitigacion |
|--------|-------|---------|------------|
| Clientes niegan portal | Alta | Critico | Valor inmediato, UX simple, WhatsApp como canal |
| Competidores copian | Media | Alto | Speed, network effects, moat datos |
| Churn alto | Media | Alto | Customer success, onboarding 30 dias |

---

## 21. Comparacion

| Feature | Excel | QuickBooks | SAP | HighRadius | **Contabilia** |
|---------|-------|------------|-----|------------|----------------|
| Conciliacion auto | No | Basica | Si | Si | **Si** |
| IA/ML | No | No | Basica | Si | **Si** |
| Portal B2B | No | No | No | No | **Si** |
| Referencia Unica | No | No | No | No | **Si** |
| Learning Engine | No | No | No | Parcial | **Si** |
| Precio PYMEs | Gratis | $30/mes | $10K+/ano | $50K+/ano | **$99-799/mes** |
| Implementacion | 0 | 1 dia | 3-12 meses | 3-6 meses | **1-2 semanas** |
| Sin consultoria | Si | Si | No | No | **Si** |

---

## 22. Funcionalidades Innovadoras

1. **Portal B2B con Referencia Unica**: Ningun otro sistema genera una referencia (PAGO-XXXXX) que el cliente usa para pagar, haciendo la conciliacion automatica desde el origen.

2. **Learning Engine por Organizacion**: Cada empresa tiene su propio "cerebro" que aprende de sus correcciones. Modelo personalizado, no generico.

3. **Grafo de Relaciones Empresa-Persona**: El sistema mantiene relaciones entre personas y multiples empresas para deducir a que empresa pertenece un pago.

4. **Deteccion Inteligente de Duplicados**: Detecta pagos repetidos, montos ligeramente diferentes, y transferencias parecidas con diferentes referencias.

5. **Score de Salud del Cobro**: Metrica 0-100 que indica que tan saludable es el proceso de cobro (auto-conciliacion, tiempo, errores, antiguedad).

6. **Notificaciones Contextuales**: No solo "pagaste", sino "tu pago cubrio FAC-001 completo y FAC-002 parcialmente, queda pendiente $7,000".

---

## 23. Estrategia para Ser el Estandar

### Plan 3 Anos

**Ano 1 (Validar)**: 20-50 clientes, MVP + portal, case studies, comunidad
**Ano 2 (Escalar)**: 200-500 clientes, partnerships, ERPs, expansion Latam, ARR > $500K
**Ano 3 (Dominar)**: 1,000-5,000 clientes, API publica, marketplace, white-label, ARR > $5M

### Network Effects

1. **Within Tenant**: Mas clientes portal -> mas conciliacion auto -> mas valor
2. **Cross-Tenant**: Benchmarking anonimo entre empresas similares
3. **Ecosystem**: Partners -> mas clientes -> mas datos -> mejor IA -> mas partners
4. **Platform**: API publica -> integraciones -> mas ERPs/bancos -> mas valor

### Como Ser Estandar

1. Hacer el portal adictivo (switching cost)
2. La referencia unica se vuelve expectativa del mercado
3. Crear datos unicos (benchmarks, patrones por industria)
4. Implementacion trivial (15 min -> 1 dia -> 1 semana)
5. Convertir contadores en ambassadors (partnership program)

---

## 24. Critica al Diseno

### Puntos Debiles

1. **¿Y si no usan el portal?**: El sistema DEBE funcionar sin portal. El portal es un acelerador (10x mas eficiente), no requisito. Fallback: reglas + IA.

2. **Subset sum es NP-C Completo**: Limite 50 facturas, greedy approximation, el portal YA selecciona las facturas (no hay que buscar combinaciones).

3. **Falta multi-moneda real**: MVP limita a moneda local. v2.0 agrega conversion con API de tipos de cambio.

4. **Invitaciones y onboarding**: Ya resuelto con `customer_portal_invitations` + flow de onboarding en portal.

5. **Fraude/abuso**: Un empleado podria crear ordenes falsas. Mitigacion: RBAC estricto, auditoria, alertas de patrones anomales.

---

## 25. Decisiones de Diseno Criticas

### 25.1 Monolito Modular vs Microservicios

**Decision**: Empezar como monolito modular (NestJS), separar solo cuando sea necesario.

**Razon**: Para < 100 organizaciones, un monolito bien estructurado es mas rapido de desarrollar y depurar. La separacion en microservicios viene en FASE 3 cuando la carga lo justifique.

### 25.2 Portal Separado vs Integrado

**Decision**: Portal como Next.js separado (apps/portal), compartiendo packages/ shared-types.

**Razon**: Independencia de deploy, escalabilidad separada, seguridad (el portal nunca toca la DB directamente).

### 25.3 IA en Python vs Node.js

**Decision**: IA como microservicio Python (FastAPI), separado del NestJS principal.

**Razon**: scikit-learn, sentence-transformers, y los LLM clients son nativos en Python. NestJS se comunica via HTTP/gRPC.

### 25.4 SQLite vs PostgreSQL

**Decision**: Desarrollo local con SQLite (ya configurado), produccion con PostgreSQL.

**Razon**: El schema Prisma ya soporta ambos. Para el MVP, SQLite es suficiente para pruebas. PostgreSQL para produccion con RLS.

### 25.5 Moneda por Defecto

**Decision**: MXN para MVP. El schema ya tiene `currency` y `exchange_rate` para soporte futuro multi-moneda.

**Razon**: El mercado target inicial es Mexico/Latam. Multi-moneda es feature de v2.0.

---

*Documento generado para Contabilia. Ultima actualizacion: Julio 2026.*
