-- V4__jobs_and_ratings.sql
-- Jobs state machine, assignment, spatial customer locations, and ratings

CREATE TYPE jobs.job_status AS ENUM (
    'draft',
    'matched',
    'assigned',
    'in_progress',
    'completed',
    'cancelled'
);

CREATE TABLE jobs.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES identity.users(id) ON DELETE RESTRICT,
    assigned_tradie_id UUID REFERENCES catalog.tradie_profiles(id) ON DELETE SET NULL,
    trade catalog.trade_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status jobs.job_status NOT NULL DEFAULT 'draft',
    site_location GEOGRAPHY(Point, 4326) NOT NULL,
    street_address TEXT NOT NULL,
    suburb VARCHAR(100),
    city VARCHAR(100) NOT NULL DEFAULT 'Christchurch',
    postal_code VARCHAR(20),
    estimated_cost_nzd NUMERIC(10,2),
    final_cost_nzd NUMERIC(10,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jobs_location ON jobs.jobs USING GIST (site_location);
CREATE INDEX idx_jobs_customer ON jobs.jobs(customer_id);
CREATE INDEX idx_jobs_tradie ON jobs.jobs(assigned_tradie_id);
CREATE INDEX idx_jobs_status ON jobs.jobs(status);

-- Job State Transition Audit Trail
CREATE TABLE jobs.job_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs.jobs(id) ON DELETE CASCADE,
    from_status jobs.job_status,
    to_status jobs.job_status NOT NULL,
    actor_id UUID NOT NULL,
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_job_events_job ON jobs.job_events(job_id);

-- Ratings and Customer Feedback
CREATE TABLE jobs.ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL UNIQUE REFERENCES jobs.jobs(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES identity.users(id) ON DELETE RESTRICT,
    tradie_id UUID NOT NULL REFERENCES catalog.tradie_profiles(id) ON DELETE RESTRICT,
    score INT NOT NULL CHECK (score BETWEEN 1 AND 5),
    feedback_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ratings_tradie ON jobs.ratings(tradie_id);
