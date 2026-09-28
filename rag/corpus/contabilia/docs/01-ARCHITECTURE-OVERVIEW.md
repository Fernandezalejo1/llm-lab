# CONTABILIA - Arquitectura del Producto

## Visión General

Plataforma SaaS que automatiza la identificación de pagos, aplicación de cobros y conciliación bancaria. El sistema emula el razonamiento de un contador senior: analiza evidencia, justifica decisiones, calcula confianza y aprende de correcciones.

### Principios de Diseño

- **La confianza es un espectro**: toda decisión tiene un porcentaje de confianza (0-100%)
- **El monto es la última validación**: primero identificar quién, luego validar con monto
- **Evidencia sobre suposición**: toda decisión debe ser trazable a la evidencia que la sustentó
- **Aprendizaje continuo**: cada corrección del usuario retroalimenta el sistema
- **Reglas primero, IA después**: las reglas son determinísticas y rápidas; la IA es un refuerzo
- **Sin pérdida de trazabilidad**: cada movimiento mantiene su historia completa

### Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | Next.js 14+ (App Router), React 18+, TypeScript, Tailwind CSS, Radix UI, Framer Motion |
| Backend | Node.js + TypeScript (NestJS), arquitectura hexagonal |
| Base de Datos Principal | PostgreSQL |
| Cache / Colas | Redis + BullMQ |
| Vector DB | Qdrant (búsqueda semántica) |
| ML/IA | Python (FastAPI, microservicio independiente), scikit-learn, sentence-transformers |
| LLM | OpenAI API / Claude API (solo casos complejos) |
| Infraestructura | Docker, Kubernetes, AWS/GCP |
| Almacenamiento | S3/MinIO (documentos) |
| Monitoreo | OpenTelemetry, Sentry |
| API | REST + GraphQL (Apollo) |

---

## Arquitectura del Sistema

```
+-------------------------------------------------------------------+
|                        CLIENTE (Next.js)                           |
|  +-----------+ +------------+ +------------+ +-----------------+   |
|  | Dashboard | |Conciliación| | Clientes   | | Configuración   |   |
|  +-----+-----+ +-----+------+ +-----+------+ +--------+--------+   |
|        |             |              |                 |            |
|  +-----+-------------+--------------+-----------------+--------+   |
|  |                    API Gateway (GraphQL + REST)               |   |
|  +-------------------------------+-------------------------------+   |
+----------------------------------+----------------------------------+
                                   |
+----------------------------------+----------------------------------+
|                     BACKEND (NestJS - Hexagonal)                     |
|  +-------------------------------------------------------------+    |
|  |                     DOMAIN LAYER                             |    |
|  |  +----------------+ +---------------+ +----------------+    |    |
|  |  | Identification | | Cash App.     | | Reconciliation |    |    |
|  |  +-------+--------+ +-------+-------+ +-------+--------+    |    |
|  |  +-------+--------+ +-------+-------+ +-------+--------+    |    |
|  |  | Rules Engine    | | Learning      | | AI Engine      |    |    |
|  |  +----------------+ +---------------+ +----------------+    |    |
|  +-------------------------------------------------------------+    |
|  +-------------------------------------------------------------+    |
|  |                   INFRASTRUCTURE LAYER                        |    |
|  |  +----------+ +----------+ +----------+ +----------------+   |    |
|  |  |PostgreSQL | | Redis    | | Qdrant   | | S3/MinIO      |   |    |
|  |  +----------+ +----------+ +----------+ +----------------+   |    |
|  +-------------------------------------------------------------+    |
+----------------------------------+----------------------------------+
                                   |
+----------------------------------+----------------------------------+
|                     SERVICES EXTERNOS                               |
|  +------------------+ +------------------+ +---------------------+  |
|  | AI Engine (Py)   | | PDF Extractor    | | OpenAI / Claude     |  |
|  +------------------+ +------------------+ +---------------------+  |
+---------------------------------------------------------------------+
```

### Capas Hexagonales (Backend)

```
┌────────────────────────────────────────────┐
│         INTERFACES / ADAPTERS               │
│  (REST Controllers, GraphQL Resolvers,      │
│   WebSocket Gateways, CLI)                  │
├────────────────────────────────────────────┤
│         APPLICATION                          │
│  (Use Cases, DTOs, Ports)                    │
├────────────────────────────────────────────┤
│         DOMAIN                               │
│  (Entities, Value Objects, Events,           │
│   Domain Services, Repository Interfaces)    │
├────────────────────────────────────────────┤
│         INFRASTRUCTURE                       │
│  (PostgreSQL Repositories, Redis Cache,      │
│   Queue Producers/Consumers, External APIs)  │
└────────────────────────────────────────────┘
```

---

## Módulos del Sistema

### 1. Módulo de Ingesta (Data Ingestion)
Importar datos desde múltiples fuentes y formatos.

- **BankStatementIngestor**: Estados bancarios (Excel, CSV, PDF)
- **InvoiceIngestor**: Facturas (Excel, CSV, XML)
- **CustomerIngestor**: Clientes (masivo o manual)
- **ManualEntryIngestor**: Pagos manuales, cheques, transferencias, NC/ND
- **PDFExtractor**: Extracción con OCR si es necesario

### 2. Módulo de Identificación (Identification Engine)
Corazón del sistema. Determina quién realizó un pago usando múltiples estrategias.

### 3. Módulo de Reglas (Rules Engine)
Ejecuta reglas determinísticas para identificación. 13+ reglas configurables.

### 4. Módulo de IA (AI Engine)
Interviene cuando las reglas no alcanzan suficiente confianza. Usa embeddings + LLM.

### 5. Módulo de Aprendizaje (Learning Engine)
Aprende de cada corrección del usuario.

### 6. Módulo de Aplicación de Pagos (Cash Application)
Aplica pagos identificados a facturas.

### 7. Módulo de Conciliación (Reconciliation)
Genera conciliación bancaria automática.

### 8. Módulo de Dashboard y Reportes
Visualiza métricas, estado y rendimiento.

### 9. Módulo de Administración de Clientes
Gestión completa del perfil de cada cliente.

### 10. Módulo de Notificaciones
Alertas sobre movimientos sin identificar, errores, conciliaciones listas.

---

## Pipeline de Identificación Completo

```
Movimiento Bancario
       │
       ▼
┌───────────────────────────────┐
│ 1. PRE-PROCESAMIENTO           │
│ - Normalizar texto             │
│ - Extraer campos útiles        │
│ - Detectar tipo (cheque, SPEI, │
│   transferencia, etc.)         │
│ - Extraer referencia, CLABE,   │
│   RFC si existe                │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ 2. MOTOR DE REGLAS             │  ← Intenta resolver sin IA
│ - Ejecuta R01 a R13            │
│ - Cada regla produce:          │
│   * customer_id candidato      │
│   * puntaje de confianza       │
│   * evidencia                  │
└───────────┬───────────────────┘
            │
        ┌─────┐
        │≥90% │ ──────────────────→ AUTO-ACEPTAR
        └─────┘                          │
            │ <90%                       │
            ▼                            ▼
┌───────────────────────────────┐   ┌──────────────────┐
│ 3. MOTOR DE IA                │   │ PaymentMatch     │
│ - Solo si confianza < umbral  │   │ Confidence: ≥90%  │
│ - Búsqueda semántica (Qdrant) │   │ Status: auto      │
│ - Clasificación difusa        │   └──────────────────┘
│ - LLM (casos complejos)       │
│ - Genera candidatos           │
│ - Explica evidencia           │
└───────────┬───────────────────┘
            │
            ▼
        ┌─────┐
        │≥90% │ ──────────────────→ AUTO-ACEPTAR
        └─────┘
            │ <90%
            ▼
┌───────────────────────────────┐
│ 4. MÚLTIPLES CANDIDATOS       │
│ - Si hay 2+ candidatos        │
│   con > 50% confianza         │
│ - VALIDAR CON MONTO            │
│ - El que tenga factura         │
│   compatible → gana puntos     │
│ - Si persiste empate:          │
│   solicitar revisión manual    │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ 5. REVISIÓN MANUAL             │
│ - UI muestra candidatos        │
│ - Muestra evidencia            │
│ - Usuario selecciona           │
│ - O crea nuevo cliente         │
│ - Se registra en LearningLog   │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ 6. APRENDIZAJE                 │
│ - Se genera SimilarityPattern  │
│ - Se actualizan pesos          │
│ - El sistema mejora            │
└───────────────────────────────┘
```
