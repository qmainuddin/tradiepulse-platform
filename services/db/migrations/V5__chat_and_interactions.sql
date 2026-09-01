-- V5__chat_and_interactions.sql
-- Chat Sessions, Messages, Image References, and Token Metrics

CREATE TYPE jobs.chat_status AS ENUM ('active', 'completed', 'archived');
CREATE TYPE jobs.message_type AS ENUM ('text', 'image', 'proposal', 'system');

CREATE TABLE jobs.chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES identity.users(id) ON DELETE CASCADE,
    tradie_id UUID REFERENCES catalog.tradie_profiles(id) ON DELETE SET NULL,
    job_id UUID REFERENCES jobs.jobs(id) ON DELETE SET NULL,
    status jobs.chat_status NOT NULL DEFAULT 'active',
    summary TEXT,
    classified_trade catalog.trade_type,
    extracted_location_name VARCHAR(255),
    extracted_coordinates GEOGRAPHY(Point, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_customer ON jobs.chat_sessions(customer_id);
CREATE INDEX idx_chat_status ON jobs.chat_sessions(status);

CREATE TABLE jobs.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES jobs.chat_sessions(id) ON DELETE CASCADE,
    sender_id UUID,
    sender_role VARCHAR(50) NOT NULL, -- 'customer', 'agent', 'tradesperson', 'system'
    msg_type jobs.message_type NOT NULL DEFAULT 'text',
    content TEXT NOT NULL,
    media_urls TEXT[], -- Storage paths for uploaded images
    token_count INT,
    latency_ms INT,
    cache_hit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_messages_session ON jobs.chat_messages(session_id, created_at);
