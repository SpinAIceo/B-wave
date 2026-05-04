from __future__ import annotations

import random
from app.models import Vessel, FleetResponse

random.seed(42)

_VESSEL_NAMES = [
    "Pacific Horizon", "Atlantic Star", "Nordic Wave", "Ocean Pioneer",
    "Sea Eagle", "Harbor Master", "Blue Meridian", "Iron Crusader",
    "Coral Voyager", "Arctic Falcon", "Silver Stream", "Golden Gate",
    "Thunder Bay", "Crystal Seas", "Nova Spirit", "Crimson Tide",
    "Emerald Isle", "Solar Wind", "Black Pearl", "Titan Express",
    "Sea Monarch", "Delta Force", "Zephyr Wind", "Pacific Queen",
    "Orient Star", "Nordic Storm", "Bering Strait", "Cape Victory",
    "Rio Grande", "Adriatic Sun", "Baltic Pride", "Caribbean Dream",
    "Mediterranean Blue", "Red Sea Runner", "Indian Ocean", "Caspian Sea",
    "South China Sea", "Tasman Spirit", "Coral Princess", "Jade Dragon",
    "Silver Knight", "Golden Eagle", "Iron Horse", "Steel Tiger",
    "Ocean Thunder", "Sea Breeze", "Wind Rider", "Wave Master",
    "Tide Turner", "Storm Chaser",
]

_FLAGS = ["🇰🇷 KOR", "🇯🇵 JPN", "🇨🇳 CHN", "🇵🇦 PAN", "🇲🇭 MHL", "🇬🇧 GBR", "🇬🇷 GRC", "🇳🇴 NOR", "🇩🇪 DEU", "🇸🇬 SGP"]
_TYPES = ["Bulk Carrier", "Container", "Tanker", "General Cargo", "Ro-Ro", "Gas Carrier"]
_DEFECT_POOL = ["rust", "damage", "leak"]
_NEXT_PORTS = [
    "Shanghai", "Rotterdam", "Singapore", "Busan", "Hamburg",
    "Los Angeles", "Tokyo", "Antwerp", "New York", "Dubai",
]

# Realistic vessel positions (lat, lon) across major shipping lanes
_POSITIONS = [
    (31.2, 121.5), (51.9, 4.5), (1.3, 103.8), (35.1, 129.0), (53.5, 9.9),
    (33.7, -118.2), (35.7, 139.7), (51.2, 4.4), (40.7, -74.0), (25.2, 55.3),
    (22.3, 114.2), (-33.8, 151.2), (48.9, 2.4), (55.6, 12.6), (60.4, 5.3),
    (38.7, -9.1), (43.3, 5.4), (37.9, 23.7), (41.0, 28.9), (-34.6, -58.4),
    (10.5, 107.2), (18.9, 72.8), (22.5, 88.3), (13.1, 80.3), (6.8, 79.9),
    (29.9, 32.6), (37.5, 126.9), (24.5, 118.1), (21.3, 158.1), (64.1, -21.9),
    (36.7, 3.2), (-25.9, 32.6), (-33.9, 18.4), (6.3, 2.4), (4.0, 9.7),
    (14.7, -17.4), (15.6, 32.5), (11.8, 43.1), (-4.3, 15.3), (-25.7, -43.2),
    (45.0, -73.5), (43.7, -79.4), (49.2, -123.1), (47.6, -122.3), (37.8, -122.4),
    (29.7, -95.4), (25.8, -80.2), (30.4, -88.9), (21.3, -157.8), (57.9, -152.4),
]


def generate_fleet() -> FleetResponse:
    vessels: list[Vessel] = []
    counts = {"green": 0, "yellow": 0, "red": 0}

    for i in range(50):
        name = _VESSEL_NAMES[i]
        flag = _FLAGS[i % len(_FLAGS)]
        v_type = _TYPES[i % len(_TYPES)]
        imo = f"IMO{9000000 + i * 7 + 13}"
        lat, lon = _POSITIONS[i]

        # Generate defects with realistic distribution
        n_defects = random.choices([0, 1, 2, 3], weights=[45, 30, 15, 10])[0]
        defects = random.sample(_DEFECT_POOL, min(n_defects, len(_DEFECT_POOL)))

        if len(defects) == 0:
            risk = "low"
            status = "green"
        elif "leak" in defects or len(defects) >= 2:
            risk = "high"
            status = "red"
        else:
            risk = "medium"
            status = "yellow"

        counts[status] += 1

        days_since = random.randint(3, 180)
        year = 2026 if days_since < 30 else 2025
        month = max(1, (4 - days_since // 30) % 12 + 1)
        day = random.randint(1, 28)
        last_inspection = f"{year}-{month:02d}-{day:02d}"

        vessels.append(Vessel(
            id=f"v{i+1:03d}",
            name=name,
            flag=flag,
            type=v_type,
            imo=imo,
            lat=round(lat + random.uniform(-2, 2), 3),
            lon=round(lon + random.uniform(-2, 2), 3),
            status=status,
            risk_level=risk,
            defects=defects,
            last_inspection=last_inspection,
            next_port=_NEXT_PORTS[i % len(_NEXT_PORTS)],
        ))

    return FleetResponse(
        vessels=vessels,
        summary={"total": 50, "green": counts["green"], "yellow": counts["yellow"], "red": counts["red"]},
    )
