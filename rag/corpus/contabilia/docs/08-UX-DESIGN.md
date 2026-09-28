# CONTABILIA - Diseño UX/UI

## Filosofía de Diseño

- **Inspiración**: Stripe, Linear, Vercel, Notion, Arc Browser, Apple
- **Principio**: Nada debe parecer una plantilla. Todo debe sentirse premium.
- **Enfoque**: Densidad de información sin sacrificar claridad. Diseño orientado a datos.

## Design System

### Tokens de Diseño

```css
:root {
  /* Colores */
  --color-bg: #0a0a0b;           /* Fondo principal - oscuro */
  --color-surface: #141416;       /* Superficie de tarjetas */
  --color-surface-hover: #1c1c1f;
  --color-border: #232326;
  --color-border-hover: #2f2f34;

  /* Primario (verde - dinero, finanzas) */
  --color-primary: #22c55e;
  --color-primary-hover: #16a34a;
  --color-primary-soft: rgba(34, 197, 94, 0.1);
  --color-primary-text: #86efac;

  /* Semántica */
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* Texto */
  --color-text: #fafafa;
  --color-text-secondary: #a1a1aa;
  --color-text-tertiary: #71717a;

  /* Tipografía */
  --font-sans: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Espaciado */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  /* Sombras */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
}
```

### Componentes Base

- **Button**: Variantes primary, secondary, ghost, danger. Estados loading, disabled.
- **Input**: Base con label flotante, estados error, éxito. Variantes con icono.
- **Select**: Autocomplete con búsqueda, multi-select con tags.
- **Table**: Virtualizada, sortable, filterable, expandable rows.
- **Card**: Superficie elevada con hover sutil. Sin bordes.
- **Badge**: Estados (success, warning, error, info, neutral).
- **Modal**: Slide-in desde la derecha (drawer) para paneles detallados.
- **Dropdown**: Menú contextual, command palette (⌘K).
- **Toast**: Notificaciones no intrusivas, esquina inferior derecha.
- **Skeleton**: Loading states con shimmer animation.
- **Progress**: Barra de progreso, dona (circular) para porcentajes.
- **Tabs**: Navegación secundaria, animación de indicador.

## Layout Principal

```
┌──────────────────────────────────────────────────────────────────┐
│  LOGO      Buscar (⌘K)    Notif.   Perfil   [Usuario]   ▼      │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────┬──────────────────────────────────────────────────┐ │
│  │         │                                                   │ │
│  │  Dashboard │  [Contenido Principal]                         │ │
│  │  Movimientos│                                                │ │
│  │  Clientes  │                                                │ │
│  │  Facturas  │                                                │ │
│  │  Conciliac.│                                                │ │
│  │  Reportes  │                                                │ │
│  │  Settings  │                                                │ │
│  │         │                                                   │ │
│  │         │                                                   │ │
│  └─────────┴──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘

Sidebar (240px) colapsable a iconos (64px).
```

## Pantallas Clave

### 1. Dashboard Principal

```
┌──────────────────────────────────────────────────────────────────────┐
│  Dashboard                                            Ene 2026  ▼   │
├──────────────────────────────────────────────────────────────────────┤
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐             │
│  │$458K  │ │$23K   │ │  12   │ │  3    │ │ 92%  │ │ 15h  │             │
│  │Cobros │ │Pend.  │ │Sin Id.│ │Errors │ │Auto. │ │Ahorro│             │
│  │ ▲12%  │ │       │ │       │ │       │ │      │ │      │             │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Cobros Semanales                                   ▼ Exportar │   │
│  │  ┌────────────────────────────────────────────────────────┐   │   │
│  │  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░  │   │   │
│  │  │  Lun Mar Mié Jue Vie Sáb Dom                          │   │   │
│  │  │  ● Conciliado  ● Pendiente  ● Sin identificar         │   │   │
│  │  └────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────┐  ┌────────────────────┐  ┌────────────────────┐   │
│  │ Pendientes    │  │ Sin Identificar    │  │ Precisión Sistema  │   │
│  │ Factura 001   │  │ $5,000 - TRANSF    │  │ ○○○○○○○○○○ 92%    │   │
│  │ Factura 002   │  │ $3,200 - CHEQUE    │  │ Mejora vs mes ant │   │
│  │ Factura 003   │  │ $1,000 - SPEI      │  │ ▲ +5%             │   │
│  └──────────────┘  └────────────────────┘  └────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### 2. Lista de Movimientos Bancarios

```
┌──────────────────────────────────────────────────────────────────────┐
│  Movimientos Bancarios                    + Importar    ▼ Filtros   │
├──────────────────────────────────────────────────────────────────────┤
│  ┌────┬──────────┬──────────────┬────────┬────────┬────────┬──────┐│
│  │    │ Fecha    │ Descripción  │ Monto  │ Cliente│ Conf.  │Status││
│  ├────┼──────────┼──────────────┼────────┼────────┼────────┼──────┤│
│  │ ●  │ 15/01    │ TRANSF SPEI  │ $10K   │ ABC SA │ 97%    │ ✓    ││
│  │    │          │ JUAN PEREZ   │        │        │        │      ││
│  │ ●  │ 14/01    │ CHEQUE 45012 │ $5K    │ —      │ —      │ ⚠    ││
│  │ ●  │ 14/01    │ SPEI         │ $20K   │ XYZ    │ 85%    │ ◐    ││
│  │ ✕  │ 13/01    │ DEPOSITO     │ $3K    │ —      │ —      │ ●    ││
│  │ ●  │ 13/01    │ TRANSF       │ $15K   │ LMN    │ 92%    │ ✓    ││
│  └────┴──────────┴──────────────┴────────┴────────┴────────┴──────┘│
│                                                                      │
│  Estados: ● Identificado  ◐ Pendiente Revisión  ✓ Conciliado         │
│           ⚠ Sin Identificar  ✕ Error                                │
└──────────────────────────────────────────────────────────────────────┘
```

### 3. Detalle de Movimiento (Drawer lateral)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Volver                              Movimiento: MOV-2026-00142  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  DATOS DEL MOVIMIENTO                                      │     │
│  │                                                           │     │
│  │  Fecha:      15 de enero, 2026                            │     │
│  │  Descripción: TRANSFERENCIA SPEI JUAN PEREZ               │     │
│  │  Referencia: SPEI-1234567890                              │     │
│  │  Monto:      $10,000.00 MXN                               │     │
│  │  Tipo:       Abono (Crédito)                              │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  IDENTIFICACIÓN                                              │     │
│  │                                                           │     │
│  │  Cliente:  CONSTRUCTORA ABC SA DE CV           [Cambiar]  │     │
│  │  Confianza: 97% ●●●●●●●●●○                                │     │
│  │                                                           │     │
│  │  EVIDENCIA:                                                │     │
│  │  ✓ R05 - Representante: JUAN PEREZ es representante       │     │
│  │         legal de CONSTRUCTORA ABC (confianza: 80%)        │     │
│  │  ✓ R03 - Alias conocido en patrón de aprendizaje          │     │
│  │         (confianza: 90%)                                  │     │
│  │  ✓ Validación con monto: Factura FAC-2026-001             │     │
│  │         de $10,000.00 coincide exactamente (+5%)          │     │
│  │                                                           │     │
│  │  OTROS CANDIDATOS:                                         │     │
│  │  ○ CONSTRUCTORA XYZ SA (confianza: 45%) - Solo            │     │
│  │    coincidencia parcial de nombre                          │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  APLICACIÓN                                                 │     │
│  │                                                           │     │
│  │  Tipo: Pago completo de factura                           │     │
│  │                                                           │     │
│  │  ┌──────┬────────────┬────────┬────────┬──────────┐      │     │
│  │  │Sel.  │ Factura    │ Monto  │ Aplicar│ Nuevo    │      │     │
│  │  ├──────┼────────────┼────────┼────────┼──────────┤      │     │
│  │  │ ✓    │ FAC-2026-001│ $10K   │ $10K   │ $0       │      │     │
│  │  │ ☐    │ FAC-2026-002│ $5K    │ —      │ $5K      │      │     │
│  │  └──────┴────────────┴────────┴────────┴──────────┘      │     │
│  │                                                           │     │
│  │  [✓] Auto-aplicar  [Confirmar]  [Corregir Identificación] │     │
│  └────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4. Perfil de Cliente

```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Clientes                     CONSTRUCTORA ABC SA DE CV        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┬────────────────────────────────────────────────┐ │
│  │              │  Razón Social: CONSTRUCTORA ABC SA DE CV       │ │
│  │   [Logo]     │  RFC: ABC121212XXX                             │ │
│  │              │  Alias: Constructora ABC, ABC                  │ │
│  │              │  Status: ● Activo                              │ │
│  └──────────────┴────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Información     Atributos     Obras     Facturas    Historial │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │  ATRIBUTOS DEL CLIENTE                          + Agregar     │ │
│  │                                                               │ │
│  │  Representantes Legales:                                       │ │
│  │  • Juan Pérez (confianza: 95% - manual)        [✕]            │ │
│  │  • María García (confianza: 80% - aprendido)   [✕]            │ │
│  │                                                               │ │
│  │  Empresas Relacionadas:                                        │ │
│  │  • EMPRESA MADRE SA (confianza: 100% - manual)  [✕]           │ │
│  │                                                               │ │
│  │  Cuentas Bancarias:                                            │ │
│  │  • 0121 8001 5798 3456 78 (BBVA)               [✕]            │ │
│  │                                                               │ │
│  │  Obras:                                                        │ │
│  │  • EDIFICIO CORPORATIVO ZONA SUR                [✕]            │ │
│  │  • CONDOMINIO RESIDENCIAL LAS PALMAS            [✕]            │ │
│  │                                                               │ │
│  │  PATRONES APRENDIDOS:                                          │ │
│  │  • "JUAN PEREZ" → CONSTRUCTORA ABC (usado 5 veces)            │ │
│  │  • "CHEQUE 45***" → CONSTRUCTORA ABC (usado 3 veces)          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Saldo Actual: $25,000.00    |    Anticipos: $10,000.00        │ │
│  │  Facturas Pendientes: 3     |    Último Pago: 15/01/2026      │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 5. Pantalla de Importación

```
┌─────────────────────────────────────────────────────────────────────┐
│  Importar Estado de Cuenta                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Arrastra tu archivo aquí o haz clic para buscar              │ │
│  │                                                               │ │
│  │  Formatos soportados: Excel (.xlsx, .xls), CSV, PDF           │ │
│  │  Tamaño máximo: 50MB                                          │ │
│  │  ┌────────────────────────────────────────────────────────┐   │ │
│  │  │  [📎] estado_cuenta_ene2026.xlsx   3.2MB  ✓ Validado  │   │ │
│  │  └────────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  CONFIGURACIÓN DE IMPORTACIÓN                                  │ │
│  │                                                               │ │
│  │  Banco:        [BBVA ▼]                    + Nuevo banco      │ │
│  │  Cuenta:       [0121 8001 5798 3456 78 ▼]                     │ │
│  │  Delimitador:  [Coma ▼]  (solo para CSV)                     │ │
│  │                                                               │ │
│  │  MAPEO DE COLUMNAS:                                            │ │
│  │  ┌───────────────┬────────────────────────────────────────┐   │ │
│  │  │ Columna Archivo│ Campo del Sistema                     │   │ │
│  │  ├───────────────┼────────────────────────────────────────┤   │ │
│  │  │ Fecha         │ Fecha de Transacción ✓                 │   │ │
│  │  │ Descripción   │ Descripción ✓                          │   │ │
│  │  │ Referencia    │ Referencia ✓                           │   │ │
│  │  │ Cargos        │ Débito ✓                              │   │ │
│  │  │ Abonos        │ Crédito ✓                             │   │ │
│  │  └───────────────┴────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  [Cancelar]                              [Importar (45 movimientos)]│
└─────────────────────────────────────────────────────────────────────┘
```

### 6. Pantalla de Reportes

```
┌─────────────────────────────────────────────────────────────────────┐
│  Reportes                                        Ene 2026  ▼     │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Conciliación Bancaria - Enero 2026                 Exportar ▼│ │
│  │  Cuenta: 0121 8001 5798 3456 78 - BBVA                       │ │
│  │                                                             │ │
│  │  Resumen:                                                    │ │
│  │  45 movimientos | $458,230.00 créditos | $12,450.00 débitos │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 78%            │   │ │
│  │  │  ▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░            │   │ │
│  │  │  ● Conciliado (35)  ● Sin Identificar (5)            │   │ │
│  │  │  ● Pendiente (3)    ● Error/Duplicado (2)            │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  [Descargar Excel] [Descargar PDF] [Descargar CSV]                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Animaciones y Micro-interacciones

- **Transiciones de página**: Slide suave (200ms ease-out)
- **Hover en cards**: Elevación sutil (+2px shadow, -1px translateY)
- **Loading states**: Skeleton shimmer con gradient animation
- **Notificaciones**: Toast con slide-in desde abajo-derecha
- **Drawer**: Slide desde la derecha (300ms), overlay con blur
- **Badges de estado**: Pulse animation para estados "en proceso"
- **Gráficas**: Transiciones animadas al cambiar período
- **Command palette (⌘K)**: Overlay con búsqueda instantánea

## Responsive

- **Desktop (>1024px)**: Layout completo con sidebar expandida
- **Tablet (768-1024px)**: Sidebar colapsada (iconos), layout adaptativo
- **Mobile (<768px)**: Bottom navigation, cards en una columna

## Estados de Vacío

Cada lista/pantalla debe tener un estado vacío informativo:

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│                    📄                                           │
│              No hay movimientos                                  │
│         Sube tu primer estado de cuenta para                      │
│         empezar a conciliar automáticamente.                      │
│                                                                    │
│              [Subir Estado de Cuenta]                             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```
