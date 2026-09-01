# Hostinger VPS Deployment Runbook

## Target Host
- **Domain:** `tradiepulse.mainuddintalukdar.cloud`
- **Reverse Proxy:** Caddy v2 (automatic Let's Encrypt TLS)
- **Container Engine:** Docker & Docker Compose
- **Container Registry:** GitHub Container Registry (`ghcr.io/mainuddin-talukdar/*`)

---

## 1. Initial Host Provisioning

SSH into the Hostinger VPS:
```bash
ssh root@vps.mainuddintalukdar.cloud
```

Ensure Docker and Docker Compose plugin are installed:
```bash
apt-get update && apt-get install -y docker.io docker-compose-plugin git
```

Create production app directory:
```bash
mkdir -p /opt/tradiepulse/infra/caddy
cd /opt/tradiepulse
```

---

## 2. Secrets & Production Configuration

Create `/opt/tradiepulse/.env` (permissions `chmod 600 .env`):
```bash
DOMAIN_NAME=tradiepulse.mainuddintalukdar.cloud
ENVIRONMENT=production
NODE_ENV=production

JWT_SIGNING_KEY=<PRODUCTION_SECRET_KEY>
SUPERADMIN_EMAIL=admin@mainuddintalukdar.cloud
SUPERADMIN_PASSWORD=<PRODUCTION_SUPERADMIN_PASSWORD>

POSTGRES_DB=tradiepulse
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<STRONG_POSTGRES_PASSWORD>

REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

OPENROUTER_API_KEY=<PRODUCTION_OPENROUTER_KEY>
GROQ_API_KEY=<PRODUCTION_GROQ_KEY>
RESEND_API_KEY=<PRODUCTION_RESEND_KEY>
EMAIL_FROM_ADDRESS=noreply@mainuddintalukdar.cloud

GHCR_OWNER=mainuddin-talukdar
IMAGE_TAG=latest
```

Copy `docker-compose.yml` and `infra/caddy/Caddyfile` to `/opt/tradiepulse`.

---

## 3. Deployment Procedure

Authenticate Docker with GHCR:
```bash
echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_OWNER --password-stdin
```

Pull the latest published images and start:
```bash
docker compose pull
docker compose up -d --remove-orphans
```

Verify running health checks:
```bash
docker compose ps
curl -I https://tradiepulse.mainuddintalukdar.cloud/health
```

---

## 4. Rollback Procedure

If a deployed image fails health checks:
```bash
# Rollback to specific SHA or previous release tag
export IMAGE_TAG=<PREVIOUS_SHA>
docker compose pull
docker compose up -d
```
