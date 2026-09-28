# ── Contabilidad API ──────────────────────────────────────────────
FROM node:20-alpine AS base

# Instalar dependencias del sistema
RUN apk add --no-cache libc6-compat

# Working directory
WORKDIR /app

# ── Dependencies ──────────────────────────────────────────────────
COPY package.json package-lock.json ./
COPY apps/api/package.json ./apps/api/
COPY packages/database/package.json ./packages/database/
COPY packages/shared-types/package.json ./packages/shared-types/

RUN npm ci --workspace=@contabilia/api --workspace=@contabilia/database

# ── Build ─────────────────────────────────────────────────────────
COPY . .

RUN npx prisma generate --schema=packages/database/prisma/schema.prisma
RUN npm run build --workspace=@contabilia/api

# ── Production ────────────────────────────────────────────────────
FROM node:20-alpine AS production

WORKDIR /app

COPY --from=base /app/node_modules ./node_modules
COPY --from=base /app/apps/api/dist ./apps/api/dist
COPY --from=base /app/apps/api/package.json ./apps/api/
COPY --from=base /app/packages/database ./packages/database
COPY --from=base /app/packages/shared-types ./packages/shared-types

ENV NODE_ENV=production
ENV PORT=3001

EXPOSE 3001

CMD ["node", "apps/api/dist/main.js"]
