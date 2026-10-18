"""Shared config: stations, entrances, features. Station data is illustrative."""
HOURS = list(range(5, 24))  # metro operating hours

_RAW = [
    ("RC", "Rajiv Chowk", 28.6328, 77.2197, "mixed", 9000),
    ("KG", "Kashmere Gate", 28.6675, 77.2284, "mixed", 8000),
    ("ND", "New Delhi", 28.6431, 77.2219, "mixed", 7500),
    ("HK", "Hauz Khas", 28.5433, 77.2066, "residential", 5000),
    ("HC", "Huda City Centre", 28.4595, 77.0727, "residential", 6500),
    ("N18", "Noida Sector 18", 28.5708, 77.3260, "business", 5500),
    ("DW", "Dwarka Sector 21", 28.5524, 77.0581, "residential", 5200),
    ("VV", "Vishwavidyalaya", 28.6945, 77.2146, "residential", 4500),
    ("NP", "Nehru Place", 28.5491, 77.2518, "business", 5000),
    ("LN", "Lajpat Nagar", 28.5700, 77.2373, "mixed", 4800),
    ("SK", "Saket", 28.5206, 77.2012, "mixed", 4200),
    ("CC", "Chandni Chowk", 28.6580, 77.2300, "mixed", 4600),
]

STATIONS = []
for i, (code, name, lat, lon, kind, peak) in enumerate(_RAW):
    cap = int(peak * 1.2)
    STATIONS.append(dict(
        id=i, code=code, name=name, lat=lat, lon=lon, kind=kind, peak=peak,
        capacity=cap,  # max comfortable entries/hour
        # SIMULATED entrance split (replace with surveyed data if you have it)
        entrances=[
            dict(name="Gate 1 (Main)", share=0.50, cap_share=0.38),
            dict(name="Gate 2", share=0.30, cap_share=0.34),
            dict(name="Gate 3", share=0.20, cap_share=0.28),
        ],
    ))
STATION = {s["code"]: s for s in STATIONS}

FEATURES = ["station_id", "hour", "dow", "month", "is_weekend",
            "is_holiday", "event", "rain", "temp", "how_mean"]
