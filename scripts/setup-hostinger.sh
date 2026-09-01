#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# TradiePulse — Hostinger VPS Quick Provisioning & Deployment Script
# Domain: https://tradiepulse.mainuddintalukdar.cloud
# ==============================================================================

echo "==> Setting up TradiePulse on Hostinger VPS..."

# 1. Install Docker & Docker Compose Plugin if missing
if ! command -v docker &> /dev/null; then
    echo "==> Installing Docker Engine & Compose..."
    apt-get update
    apt-get install -y ca-certificates curl gnupg lsb-release
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# 2. Create production directories
mkdir -p /opt/tradiepulse/infra/caddy
mkdir -p /opt/tradiepulse/services/db/migrations
cd /opt/tradiepulse

echo "==> Preparing production environment file (.env)..."
if [ ! -f .env ]; then
    echo "Creating .env template in /opt/tradiepulse/.env. Please edit this file with your Supabase, Resend, and LLM credentials."
    cat << 'EOF' > .env
DOMAIN_NAME=tradiepulse.mainuddintalukdar.cloud
ENVIRONMENT=production
NODE_ENV=production

# JWT & Admin
JWT_SIGNING_KEY=your_generated_random_256bit_key_at_least_32_chars
SUPERADMIN_EMAIL=admin@mainuddintalukdar.cloud
SUPERADMIN_PASSWORD=change_this_to_a_secure_password_123!

# Supabase / Postgres Database
POSTGRES_DB=tradiepulse
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_secure_password
DATABASE_URL=postgresql://postgres:postgres_secure_password@postgres:5432/tradiepulse
SUPABASE_URL=https://your-supabase-id.supabase.co
SUPABASE_SERVICE_KEY=your-supabase-service-key
SUPABASE_ANON_KEY=your-supabase-anon-key

# Email (Resend)
RESEND_API_KEY=re_your_resend_api_key
EMAIL_FROM_ADDRESS=noreply@mainuddintalukdar.cloud

# AI Models (OpenRouter / Groq)
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_DEFAULT_MODEL=meta-llama/llama-3.3-70b-instruct:free
GROQ_API_KEY=gsk_your_key
GROQ_FALLBACK_MODEL=llama-3.3-70b-versatile

# Container Registry
GHCR_OWNER=mainuddin-talukdar
IMAGE_TAG=latest
EOF
    chmod 600 .env
fi

echo "==> Copying Caddyfile and Docker Compose..."
# If repository is cloned locally:
if [ -f "/tmp/tradiepulse/docker-compose.yml" ]; then
    cp /tmp/tradiepulse/docker-compose.yml /opt/tradiepulse/
    cp /tmp/tradiepulse/infra/caddy/Caddyfile /opt/tradiepulse/infra/caddy/
    cp -r /tmp/tradiepulse/services/db/migrations/* /opt/tradiepulse/services/db/migrations/
fi

echo "==> Pulling images and launching stack..."
docker compose pull || true
docker compose up -d --remove-orphans

echo "==> Checking status:"
docker compose ps

echo "==> Deployment initialized! Caddy is obtaining Let's Encrypt TLS for https://tradiepulse.mainuddintalukdar.cloud/"
