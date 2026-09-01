-- V3__catalog_and_tradies.sql
-- Tradesperson profiles with PostGIS coordinates, service radii, and availability slots

CREATE TYPE catalog.trade_type AS ENUM ('plumber', 'electrician', 'mechanic');
CREATE TYPE catalog.verification_status AS ENUM ('unverified', 'pending', 'verified', 'rejected');

CREATE TABLE catalog.tradie_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES identity.users(id) ON DELETE CASCADE,
    trade catalog.trade_type NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    bio TEXT,
    location GEOGRAPHY(Point, 4326) NOT NULL, -- Longitude, Latitude (WGS 84)
    service_radius_km INT NOT NULL DEFAULT 25,
    hourly_rate_nzd NUMERIC(10,2),
    verification_status catalog.verification_status NOT NULL DEFAULT 'unverified',
    rating_avg NUMERIC(3,2) NOT NULL DEFAULT 5.00,
    rating_count INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Spatial index for sub-millisecond distance querying
CREATE INDEX idx_tradie_location ON catalog.tradie_profiles USING GIST (location);
CREATE INDEX idx_tradie_trade ON catalog.tradie_profiles(trade);
CREATE INDEX idx_tradie_status ON catalog.tradie_profiles(verification_status, is_active);

-- Day-of-week availability schedules (0 = Sunday, 1 = Monday, ... 6 = Saturday)
CREATE TABLE catalog.availability_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tradie_id UUID NOT NULL REFERENCES catalog.tradie_profiles(id) ON DELETE CASCADE,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_slot_time CHECK (start_time < end_time)
);

CREATE INDEX idx_availability_tradie ON catalog.availability_slots(tradie_id, day_of_week);
