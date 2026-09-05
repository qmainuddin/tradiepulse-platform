"""
Tests for PostGIS Spatial Matching Engine (V8__spatial_matching_function.sql)
Validates distance calculations, radius filters, status filters, availability, and rating tie-breakers.
Supports both unittest and pytest.
"""
import math
import unittest

def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Calculate distance on sphere in meters for test baseline verification."""
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

# Christchurch Test Geographies
CHRISTCHURCH_CATHEDRAL_SQUARE = (-43.530955, 172.636806)
RICCARTON_CHRISTCHURCH = (-43.531000, 172.597000)
PAPANUI_CHRISTCHURCH = (-43.498000, 172.605000)
RANGIORA_CANTERBURY = (-43.303100, 172.595400)
DUNEDIN_NZ = (-45.878800, 170.502800)

class MockTradieProfile:
    def __init__(self, tradie_id, name, trade, lat, lon, radius_km, verified=True, active=True, slots=None, rating=5.0):
        self.tradie_id = tradie_id
        self.name = name
        self.trade = trade
        self.lat = lat
        self.lon = lon
        self.radius_km = radius_km
        self.verified = verified
        self.active = active
        self.slots = slots or [0, 1, 2, 3, 4, 5, 6]  # default all days available
        self.rating = rating

def simulate_nearest_available_qualified(candidates, trade, customer_lat, customer_lon, radius_meters=25000, day_of_week=None, limit=5):
    """Simulation matching the SQL stored procedure logic in V8__spatial_matching_function.sql"""
    matched = []
    for c in candidates:
        if c.trade != trade or not c.verified or not c.active:
            continue
        dist = haversine_distance_meters(customer_lat, customer_lon, c.lat, c.lon)
        if dist > radius_meters or dist > (c.radius_km * 1000):
            continue
        if day_of_week is not None and day_of_week not in c.slots:
            continue
        matched.append({
            "tradie_id": c.tradie_id,
            "name": c.name,
            "distance_meters": dist,
            "rating": c.rating
        })
    # Sort by distance ASC, rating DESC
    matched.sort(key=lambda x: (x["distance_meters"], -x["rating"]))
    return matched[:limit]


class TestSpatialMatching(unittest.TestCase):
    def test_nearest_tradie_ordering(self):
        """Verify that the nearest tradie is ranked first."""
        plumber_riccarton = MockTradieProfile("t1", "Dave Riccarton Plumbing", "plumber", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 20)
        plumber_papanui = MockTradieProfile("t2", "Sarah Papanui Pipes", "plumber", PAPANUI_CHRISTCHURCH[0], PAPANUI_CHRISTCHURCH[1], 20)
        
        results = simulate_nearest_available_qualified(
            [plumber_papanui, plumber_riccarton],
            trade="plumber",
            customer_lat=CHRISTCHURCH_CATHEDRAL_SQUARE[0],
            customer_lon=CHRISTCHURCH_CATHEDRAL_SQUARE[1],
            radius_meters=15000
        )
        self.assertEqual(len(results), 2)
        # Riccarton (~3.2km) is closer to Cathedral Square than Papanui (~4.4km)
        self.assertEqual(results[0]["name"], "Dave Riccarton Plumbing")
        self.assertLess(results[0]["distance_meters"], results[1]["distance_meters"])

    def test_rating_tie_breaker_for_equal_distance(self):
        """Verify that when distance is equal, higher rated tradie ranks higher."""
        tradie_high_rating = MockTradieProfile("t1", "Top Rated Plumber", "plumber", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 20, rating=4.95)
        tradie_lower_rating = MockTradieProfile("t2", "Good Plumber", "plumber", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 20, rating=4.50)

        results = simulate_nearest_available_qualified(
            [tradie_lower_rating, tradie_high_rating],
            trade="plumber",
            customer_lat=CHRISTCHURCH_CATHEDRAL_SQUARE[0],
            customer_lon=CHRISTCHURCH_CATHEDRAL_SQUARE[1],
            radius_meters=15000
        )
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "Top Rated Plumber")
        self.assertEqual(results[1]["name"], "Good Plumber")

    def test_limit_truncation(self):
        """Verify that the limit parameter strictly limits the number of returned results."""
        candidates = [
            MockTradieProfile(f"t{i}", f"Tradie {i}", "electrician", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 25, rating=4.0 + (i * 0.1))
            for i in range(10)
        ]
        results = simulate_nearest_available_qualified(
            candidates,
            trade="electrician",
            customer_lat=CHRISTCHURCH_CATHEDRAL_SQUARE[0],
            customer_lon=CHRISTCHURCH_CATHEDRAL_SQUARE[1],
            limit=3
        )
        self.assertEqual(len(results), 3)

    def test_radius_cutoff(self):
        """Verify that tradies outside the search radius or outside their own service radius are excluded."""
        local_plumber = MockTradieProfile("t1", "Central Plumber", "plumber", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 15)
        rangiora_plumber = MockTradieProfile("t2", "North Canterbury Plumber", "plumber", RANGIORA_CANTERBURY[0], RANGIORA_CANTERBURY[1], 10)
        dunedin_plumber = MockTradieProfile("t3", "Dunedin Plumber", "plumber", DUNEDIN_NZ[0], DUNEDIN_NZ[1], 50)
        
        results = simulate_nearest_available_qualified(
            [local_plumber, rangiora_plumber, dunedin_plumber],
            trade="plumber",
            customer_lat=CHRISTCHURCH_CATHEDRAL_SQUARE[0],
            customer_lon=CHRISTCHURCH_CATHEDRAL_SQUARE[1],
            radius_meters=15000 # 15km cut off excludes Rangiora (~25km) and Dunedin (~360km)
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Central Plumber")

    def test_unverified_tradies_excluded(self):
        """Verify that unverified or inactive tradies are never returned."""
        unverified_plumber = MockTradieProfile("t1", "Unverified Dave", "plumber", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 20, verified=False)
        inactive_plumber = MockTradieProfile("t2", "Inactive Sarah", "plumber", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 20, verified=True, active=False)
        verified_plumber = MockTradieProfile("t3", "Verified Bob", "plumber", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 20, verified=True, active=True)
        
        results = simulate_nearest_available_qualified(
            [unverified_plumber, inactive_plumber, verified_plumber],
            trade="plumber",
            customer_lat=CHRISTCHURCH_CATHEDRAL_SQUARE[0],
            customer_lon=CHRISTCHURCH_CATHEDRAL_SQUARE[1]
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Verified Bob")

    def test_availability_filter(self):
        """Verify that tradies unavailable on a given day are excluded."""
        monday_only_electrician = MockTradieProfile("t1", "Monday Spark", "electrician", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 20, slots=[1])
        tuesday_only_electrician = MockTradieProfile("t2", "Tuesday Spark", "electrician", RICCARTON_CHRISTCHURCH[0], RICCARTON_CHRISTCHURCH[1], 20, slots=[2])
        
        # Query for Monday (day 1)
        results_monday = simulate_nearest_available_qualified(
            [monday_only_electrician, tuesday_only_electrician],
            trade="electrician",
            customer_lat=CHRISTCHURCH_CATHEDRAL_SQUARE[0],
            customer_lon=CHRISTCHURCH_CATHEDRAL_SQUARE[1],
            day_of_week=1
        )
        self.assertEqual(len(results_monday), 1)
        self.assertEqual(results_monday[0]["name"], "Monday Spark")

    def test_empty_candidates_returns_empty(self):
        """Verify that an empty pool returns an empty list without error."""
        results = simulate_nearest_available_qualified(
            [],
            trade="mechanic",
            customer_lat=CHRISTCHURCH_CATHEDRAL_SQUARE[0],
            customer_lon=CHRISTCHURCH_CATHEDRAL_SQUARE[1]
        )
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
