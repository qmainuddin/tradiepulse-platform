-- V2__identity_and_roles.sql
-- Enums, User Accounts, Security Questions, Activation & Refresh Token Families

CREATE TYPE identity.user_role AS ENUM ('super_admin', 'admin', 'customer', 'tradesperson');
CREATE TYPE identity.account_status AS ENUM ('pending_verification', 'active', 'suspended', 'deactivated');
CREATE TYPE identity.token_type AS ENUM ('email_activation', 'admin_invite', 'password_reset');

-- Primary users table
CREATE TABLE identity.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role identity.user_role NOT NULL,
    status identity.account_status NOT NULL DEFAULT 'pending_verification',
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    google_id VARCHAR(255) UNIQUE,
    failed_login_attempts INT NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON identity.users(email);
CREATE INDEX idx_users_role ON identity.users(role);

-- Security questions for Step-Up impersonation verification
CREATE TABLE identity.security_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id) ON DELETE CASCADE,
    question_key VARCHAR(100) NOT NULL, -- e.g. 'first_pet', 'mothers_maiden', 'first_car'
    hashed_answer VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_question UNIQUE(user_id, question_key)
);

-- Activation and Invitation Tokens (e.g. 48-hour customer verification, admin single-use invite)
CREATE TABLE identity.activation_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    token_type identity.token_type NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activation_token_hash ON identity.activation_tokens(token_hash);

-- Refresh Token Family with reuse detection
CREATE TABLE identity.refresh_token_families (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id) ON DELETE CASCADE,
    current_token_hash VARCHAR(255) NOT NULL UNIQUE,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_refresh_token_user ON identity.refresh_token_families(user_id);
