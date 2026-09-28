# Contributing to Contabilia

Gracias por querer contribuir! Este documento explica cómo configurar el entorno de desarrollo y las guías de código.

## 🚀 Requisitos previos

- Node.js >= 20
- npm >= 11
- PostgreSQL (o SQLite para desarrollo local)

## 🔧 Setup de desarrollo

```bash
# Clonar el repo
git clone https://github.com/Fernandezalejo1/contabilia.git
cd contabilia

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Generar cliente Prisma
npm run db:generate

# Aplicar migraciones
npm run db:migrate

# Cargar datos de ejemplo
npm run db:seed

# Iniciar desarrollo
npm run dev
```

## 📁 Estructura del proyecto

```
contabilia/
├── apps/
│   ├── api/               # API NestJS (conciliación, ingesta, IA)
│   └── web/               # Frontend Next.js (dashboard, revisión)
├── packages/
│   ├── database/          # Prisma schema + client + seeds
│   └── shared-types/      # Tipos TypeScript compartidos
├── docs/                  # Documentos de diseño
└── turbo.json             # Orquestación de tareas
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
npm test

# Tests con cobertura
npm run test:cov

# Tests en watch mode
npm run test:watch
```

### Convenciones de tests

- Archivos de test: `*.spec.ts` junto al archivo fuente
- Usar `describe()` para agrupar tests relacionados
- Tests unitarios para servicios, tests de integración para controllers
- Mockear Prisma Client en tests unitarios

## 🎨 Código y estilo

- **TypeScript estricto** — Habilitado en tsconfig
- **Prettier** — Formateo automático con `npm run format`
- **Lint** — `npm run lint` antes de commitear
- **Commits** — [Conventional Commits](https://www.conventionalcommits.org/)

### Formato de commits

```
feat: agregar módulo de reportes
fix: corregir cálculo de saldo en conciliación
docs: actualizar README con badges
test: agregar tests para MatchingService
refactor: extraer lógica de parsing a utilidad
```

## 🏗️ Agregar un nuevo módulo

1. Crear directorio en `apps/api/src/modules/tu-modulo/`
2. Crear archivos: `*.module.ts`, `*.controller.ts`, `*.service.ts`
3. Agregar tests: `*.service.spec.ts`, `*.controller.spec.ts`
4. Importar el módulo en `app.module.ts`
5. Agregar tags en Swagger si es un endpoint público

## 🔒 Seguridad

- Nunca commitear `.env` o secrets
- Usar variables de entorno para toda configuración sensible
- Reportar vulnerabilidades a [SECURITY.md](SECURITY.md)

## 📝 Pull Requests

1. Crear branch desde `main`: `git checkout -b feat/nombre-feature`
2. Hacer cambios con commits descriptivos
3. Ejecutar `npm test` y `npm run lint`
4. Abrir PR con descripción clara del cambio
5. Esperar revisión y CI verde

## ❓ Preguntas?

Abrir un issue en GitHub con label `question`.
