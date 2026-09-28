# Política de Seguridad

## Reportar Vulnerabilidades

Si descubres una vulnerabilidad de seguridad, por favor **no** la reportes en un issue público. En su lugar:

1. Envía un email a **[tu-email@ejemplo.com]** con:
   - Descripción de la vulnerabilidad
   - Pasos para reproducir
   - Impacto potencial
   - Sugiere una corrección (opcional)

2. Respuesta esperada:
   - Confirmación de recepción en 48 horas
   - Evaluación en 5 días hábiles
   - Corrección o mitigación según prioridad

## Medidas de seguridad implementadas

### Autenticación
- JWT tokens con expiración configurable
- Password hashing con PBKDF2 (120,000 iteraciones + salt único)
- Tokens de refresh (próximamente)

### Autorización
- Multi-tenant: aislamiento completo por organización
- Roles: admin, member, viewer
- Validación de tenant en cada request

### Input Validation
- Whitelist de parámetros permitidos
- Transformación y sanitización automática
- Rechazo de parámetros no esperados

### CORS
- Orígenes configurados via `CORS_ORIGINS`
- Credentials habilitados solo para orígenes permitidos

### Base de datos
- Prisma Client con query raw parameterizado
- Migraciones versionadas
- Audit logs para trazabilidad

### Infraestructura
- Secrets en variables de entorno (nunca en código)
- `.gitignore` excluye `.env`, bases de datos, uploads
- Docker multi-stage builds para minimizar superficie de ataque

## Dependencias

Usamos [Dependabot](https://docs.github.com/en/code-security/dependabot) para mantener las dependencias actualizadas y alertar sobre vulnerabilidades conocidas.

## Actualizaciones de seguridad

Las actualizaciones de seguridad se publicarán como patch versions (ej: `0.1.1`).
