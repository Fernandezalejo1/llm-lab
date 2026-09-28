# ── Contabilidad Web ──────────────────────────────────────────────
FROM node:20-alpine AS base

# ── Dependencies ──────────────────────────────────────────────────
WORKDIR /app

COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/
COPY packages/shared-types/package.json ./packages/shared-types/

RUN npm ci --workspace=@contabilia/web

# ── Build ─────────────────────────────────────────────────────────
COPY . .

ARG NEXT_PUBLIC_API_URL=http://localhost:3001
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build --workspace=@contabilia/web

# ── Production ────────────────────────────────────────────────────
FROM node:20-alpine AS production

WORKDIR /app

ENV NODE_ENV=production

COPY --from=base /app/apps/web/.next ./.next
COPY --from=base /app/apps/web/public ./public
COPY --from=base /app/apps/web/package.json ./
COPY --from=base /app/node_modules ./node_modules

EXPOSE 3000

CMD ["npx", "next", "start"]
