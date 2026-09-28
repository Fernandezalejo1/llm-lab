# Changelog

Todos los cambios notables en Contabilia serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/),
y el proyecto adherido a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added
- Swagger/OpenAPI documentation (`/docs`)
- CORS configurado con orígenes permitidos
- Validación global de inputs (whitelist + transform)
- Docker setup (api + web Dockerfiles + docker-compose)
- GitHub Actions CI/CD (lint, typecheck, test, build)
- Tests unitarios para MatchingService, IngestionService, DashboardService
- CONTRIBUTING.md con guías de desarrollo
- SECURITY.md con política de reporte de vulnerabilidades
- README mejorado con badges y documentación completa

### Changed
- `main.ts` refactorizado con middleware de seguridad
- CORS ya no es abierto por defecto

### Security
- CORS restringido a orígenes configurados via env
- Input validation con `forbidNonWhitelisted: true`

## [0.1.0] - 2026-08-17

### Added
- Monorepo con Turborepo
- API NestJS con 12 módulos
- Frontend Next.js con Radix UI + Tailwind
- Prisma schema con 17+ modelos
- Motor de conciliación con reglas + embeddings
- Cash application con pagos parciales
- Motor de aprendizaje continuo
- Dashboard con métricas en tiempo real
- 9 documentos de diseño (arquitectura → PRD)
- Licencia MIT
