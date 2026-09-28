# Deploy Guide — Contabilia

## Opción 1: Docker (Local/Server)

```bash
# Clonar y configurar
git clone https://github.com/Fernandezalejo1/contabilia.git
cd contabilia
cp .env.example .env

# Editar .env con tu DATABASE_URL de PostgreSQL
# DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Ejecutar
docker compose up -d --build

# API: http://localhost:3001
# Web: http://localhost:3000
# Docs: http://localhost:3001/docs
```

## Opción 2: Railway (Recomendado para Demo)

### Deploy API (Backend)
1. Ir a [railway.app](https://railway.app)
2. Nuevo proyecto → "Deploy from GitHub repo"
3. Seleccionar `Fernandezalejo1/contabilia`
4. Configurar variables de entorno:
   - `DATABASE_URL` → PostgreSQL de Railway (plugin)
   - `PORT` → 3001
   - `NODE_ENV` → production
5. Deploy automático

### Deploy Web (Frontend)
1. Ir a [vercel.com](https://vercel.com)
2. Importar proyecto → `Fernandezalejo1/contabilia`
3. Framework: Next.js
4. Root Directory: `apps/web`
5. Variable: `NEXT_PUBLIC_API_URL` → URL de la API en Railway
6. Deploy

## Opción 3: Render

1. Ir a [render.com](https://render.com)
2. Nuevo Web Service → GitHub repo
3. Runtime: Node
4. Build: `npm install && npm run build`
5. Start: `npm run start`
6. Env vars: `DATABASE_URL`, `PORT`

## Variables de Entorno Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `PORT` | Puerto del servidor | `3001` |
| `NODE_ENV` | Entorno | `production` |
| `CORS_ORIGINS` | Orígenes permitidos | `https://tu-app.vercel.app` |

## Verificar Deploy

```bash
# Health check
curl https://tu-api.railway.app/health

# Swagger docs
curl https://tu-api.railway.app/docs

# API test
curl https://tu-api.railway.app/api/v1/dashboard/stats/org-1
```
