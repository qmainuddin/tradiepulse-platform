-- V7__audit_log.sql
-- Append-only tamper-evident audit log for privileged actions, step-up impersonation, and verification changes

CREATE TABLE audit.audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID NOT NULL,
    actor_email VARCHAR(255) NOT NULL,
    actor_role identity.user_role NOT NULL,
    action VARCHAR(100) NOT NULL, -- e.g. 'IMPERSONATION_STARTED', 'JOB_ASSIGNED', 'TRADIE_VERIFIED'
    target_type VARCHAR(100) NOT NULL, -- 'user', 'job', 'verification_case'
    target_id UUID,
    correlation_id VARCHAR(255) NOT NULL,
    impersonated_user_id UUID,
    client_ip VARCHAR(50),
    user_agent TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_actor ON audit.audit_log(actor_id);
CREATE INDEX idx_audit_correlation ON audit.audit_log(correlation_id);
CREATE INDEX idx_audit_impersonation ON audit.audit_log(impersonated_user_id) WHERE impersonated_user_id IS NOT NULL;
CREATE INDEX idx_audit_action ON audit.audit_log(action, created_at);
