-- V6__verification_and_compliance.sql
-- Pluggable Tradesperson Verification State Machine & Stored Evidence

CREATE TYPE verification.stage_enum AS ENUM (
    'email_verified',
    'docs_submitted',
    'identity_checked',
    'licence_checked',
    'tax_checked',
    'references_checked',
    'approved',
    'rejected',
    'needs_info'
);

CREATE TYPE verification.provider_type AS ENUM (
    'mock_ird',
    'ird_official',
    'ewrb_nz',
    'pgdb_nz',
    'mechanic_registry',
    'realme_identity',
    'manual_review'
);

CREATE TABLE verification.verification_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tradie_id UUID NOT NULL UNIQUE REFERENCES catalog.tradie_profiles(id) ON DELETE CASCADE,
    current_stage verification.stage_enum NOT NULL DEFAULT 'email_verified',
    ird_number_encrypted TEXT,
    licence_number VARCHAR(100),
    licence_board VARCHAR(50), -- 'EWRB', 'PGDB', etc.
    insurance_policy_number VARCHAR(100),
    insurance_expiry_date DATE,
    regional_consent_verified BOOLEAN DEFAULT FALSE,
    reviewer_id UUID REFERENCES identity.users(id) ON DELETE SET NULL,
    reviewer_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_verification_tradie ON verification.verification_cases(tradie_id);
CREATE INDEX idx_verification_stage ON verification.verification_cases(current_stage);

CREATE TABLE verification.verification_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES verification.verification_cases(id) ON DELETE CASCADE,
    doc_type VARCHAR(100) NOT NULL, -- 'id_photo', 'trade_cert', 'insurance_cert', 'reference_letter'
    file_path TEXT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    provider verification.provider_type NOT NULL DEFAULT 'manual_review',
    provider_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    provider_raw_response JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMPTZ
);

CREATE INDEX idx_verif_docs_case ON verification.verification_documents(case_id);
