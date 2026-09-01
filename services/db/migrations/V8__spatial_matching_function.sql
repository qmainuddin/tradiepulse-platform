-- V8__spatial_matching_function.sql
-- High-performance PostGIS Spatial Matching Engine
-- Matches nearest verified, active tradesperson based on distance, service radius, and availability

CREATE OR REPLACE FUNCTION catalog.nearest_available_qualified(
    p_trade catalog.trade_type,
    p_lat NUMERIC,
    p_lng NUMERIC,
    p_radius_meters INT DEFAULT 25000,
    p_day_of_week INT DEFAULT NULL,
    p_limit INT DEFAULT 5
)
RETURNS TABLE (
    tradie_id UUID,
    user_id UUID,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    business_name VARCHAR(255),
    trade catalog.trade_type,
    distance_meters DOUBLE PRECISION,
    service_radius_km INT,
    rating_avg NUMERIC(3,2),
    rating_count INT,
    hourly_rate_nzd NUMERIC(10,2),
    phone VARCHAR(50)
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_customer_point GEOGRAPHY;
BEGIN
    -- Construct customer geography point (Longitude, Latitude in SRID 4326)
    v_customer_point := ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography;

    RETURN QUERY
    SELECT 
        tp.id AS tradie_id,
        u.id AS user_id,
        u.first_name,
        u.last_name,
        tp.business_name,
        tp.trade,
        ST_Distance(tp.location, v_customer_point) AS distance_meters,
        tp.service_radius_km,
        tp.rating_avg,
        tp.rating_count,
        tp.hourly_rate_nzd,
        tp.phone
    FROM catalog.tradie_profiles tp
    INNER JOIN identity.users u ON tp.user_id = u.id
    WHERE tp.trade = p_trade
      AND tp.verification_status = 'verified'
      AND tp.is_active = TRUE
      AND u.status = 'active'
      -- Distance must be within both the customer requested search radius and the tradie's own service radius
      AND ST_DWithin(tp.location, v_customer_point, p_radius_meters)
      AND ST_DWithin(tp.location, v_customer_point, tp.service_radius_km * 1000)
      -- Optional availability filter
      AND (
          p_day_of_week IS NULL
          OR EXISTS (
              SELECT 1 FROM catalog.availability_slots av
              WHERE av.tradie_id = tp.id
                AND av.day_of_week = p_day_of_week
                AND av.is_available = TRUE
          )
      )
    ORDER BY 
        distance_meters ASC,
        tp.rating_avg DESC,
        tp.rating_count DESC
    LIMIT p_limit;
END;
$$;
