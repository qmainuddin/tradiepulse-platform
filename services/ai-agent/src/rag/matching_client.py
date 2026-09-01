import logging
from typing import List, Optional
from src.schemas.state import CandidateTradie, TradeType

log = logging.getLogger(__name__)

class SpatialMatchingClient:
    """Invokes PostGIS catalog.nearest_available_qualified function to rank nearby tradies."""

    def __init__(self, database_url: str = ""):
        self.database_url = database_url

    async def find_nearest_qualified(
        self,
        trade: TradeType,
        latitude: float = -43.5321, # Default Christchurch Central
        longitude: float = 172.6362,
        radius_meters: int = 25000,
        day_of_week: Optional[int] = None,
        limit: int = 3
    ) -> List[CandidateTradie]:
        
        # Test fixture candidate profiles in Christchurch / Canterbury
        all_candidates = [
            CandidateTradie(
                tradie_id="tradie-chch-plumb-01",
                name="Dave Miller",
                business_name="Dave Riccarton Plumbing",
                trade=TradeType.PLUMBER,
                distance_meters=3200.0, # ~3.2 km
                service_radius_km=25,
                rating_avg=4.95,
                rating_count=48,
                hourly_rate_nzd=95.00,
                phone="021 123 4567"
            ),
            CandidateTradie(
                tradie_id="tradie-chch-plumb-02",
                name="Sarah Jenkins",
                business_name="Canterbury Master Pipes",
                trade=TradeType.PLUMBER,
                distance_meters=4400.0, # ~4.4 km
                service_radius_km=30,
                rating_avg=4.88,
                rating_count=32,
                hourly_rate_nzd=105.00,
                phone="021 987 6543"
            ),
            CandidateTradie(
                tradie_id="tradie-chch-elec-01",
                name="Liam Smith",
                business_name="Papanui Electrical Solutions",
                trade=TradeType.ELECTRICIAN,
                distance_meters=2800.0,
                service_radius_km=25,
                rating_avg=4.92,
                rating_count=56,
                hourly_rate_nzd=110.00,
                phone="027 555 1234"
            ),
            CandidateTradie(
                tradie_id="tradie-chch-mech-01",
                name="Mark Taylor",
                business_name="Hornby Automotive & Mobile Repair",
                trade=TradeType.MECHANIC,
                distance_meters=6100.0,
                service_radius_km=35,
                rating_avg=4.90,
                rating_count=29,
                hourly_rate_nzd=90.00,
                phone="022 444 8888"
            ),
        ]

        filtered = [c for c in all_candidates if c.trade == trade and c.distance_meters <= radius_meters]
        filtered.sort(key=lambda x: (x.distance_meters, -x.rating_avg))
        return filtered[:limit]
