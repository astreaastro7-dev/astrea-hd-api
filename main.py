from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chart import calculate_chart, CHANNELS, GATE_NAMES
from tzfpy import get_tz
from geopy.geocoders import Nominatim
import pytz
from datetime import datetime
import time

app = FastAPI(title="Astraea HD API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STRATEGY_MAP = {
    "Generator": "Respond",
    "Manifesting Generator": "Respond and Inform",
    "Manifestor": "Inform",
    "Projector": "Wait for Invitation",
    "Reflector": "Wait a Lunar Cycle"
}

CHANNEL_NAMES = {
    frozenset({1, 8}): "Inspiration",
    frozenset({2, 14}): "The Beat",
    frozenset({3, 60}): "Mutation",
    frozenset({4, 63}): "Logic",
    frozenset({5, 15}): "Rhythm",
    frozenset({6, 59}): "Mating",
    frozenset({7, 31}): "The Alpha",
    frozenset({9, 52}): "Concentration",
    frozenset({10, 20}): "Awakening",
    frozenset({11, 56}): "Curiosity",
    frozenset({12, 22}): "Openness",
    frozenset({13, 33}): "The Prodigal",
    frozenset({16, 48}): "The Wavelength",
    frozenset({17, 62}): "Acceptance",
    frozenset({18, 58}): "Judgment",
    frozenset({19, 49}): "Synthesis",
    frozenset({20, 34}): "Charisma",
    frozenset({20, 57}): "The Brainwave",
    frozenset({21, 45}): "Money",
    frozenset({23, 43}): "Structuring",
    frozenset({24, 61}): "Awareness",
    frozenset({25, 51}): "Initiation",
    frozenset({26, 44}): "Surrender",
    frozenset({27, 50}): "Preservation",
    frozenset({28, 38}): "Struggle",
    frozenset({29, 46}): "Discovery",
    frozenset({30, 41}): "Recognition",
    frozenset({32, 54}): "Transformation",
    frozenset({34, 57}): "Power",
    frozenset({35, 36}): "Transitoriness",
    frozenset({37, 40}): "Community",
    frozenset({39, 55}): "Emoting",
    frozenset({42, 53}): "Maturation",
    frozenset({47, 64}): "Abstraction"
}


class ChartRequest(BaseModel):
    date: str
    time: str
    city: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "Astraea HD API"}


@app.post("/bodygraph")
def get_bodygraph(req: ChartRequest):
    geolocator = Nominatim(user_agent="astraea-hd-v1")
    time.sleep(1)

    location = geolocator.geocode(req.city)
    if not location:
        raise HTTPException(status_code=400, detail=f"Ville non trouvee: {req.city}")

    tz_name = get_tz(location.longitude, location.latitude)
    if not tz_name:
        raise HTTPException(status_code=400, detail="Fuseau horaire introuvable.")

    tz = pytz.timezone(tz_name)

    try:
        dt_naive = datetime.strptime(f"{req.date} {req.time}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format invalide. Attendu: YYYY-MM-DD et HH:MM")

    dt_local = tz.localize(dt_naive)
    utc_offset = dt_local.utcoffset().total_seconds() / 3600

    year, month, day = map(int, req.date.split('-'))
    hour, minute = map(int, req.time.split(':'))

    try:
        result = calculate_chart(year, month, day, hour, minute, utc_offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur calcul HD: {str(e)}")

    gate_set = set(result["all_active_gates"])
    defined_channels = []
    for g1, g2 in CHANNELS:
        if g1 in gate_set and g2 in gate_set:
            channel_name = CHANNEL_NAMES.get(frozenset({g1, g2}), f"Channel {g1}-{g2}")
            defined_channels.append({
                "name": channel_name,
                "gates": [g1, g2]
            })

    p_sun = result["personality"]["Sun"]
    p_earth = result["personality"]["Earth"]
    d_sun = result["design"]["Sun"]
    d_earth = result["design"]["Earth"]

    p_line = p_sun["line"]
    if p_line in [1, 2, 3, 4]:
        cross_family = "Right Angle Cross"
    else:
        cross_family = "Left Angle Cross"

    incarnation_cross = {
        "family": cross_family,
        "personality_sun_gate": p_sun["gate"],
        "personality_earth_gate": p_earth["gate"],
        "design_sun_gate": d_sun["gate"],
        "design_earth_gate": d_earth["gate"],
        "label": f"{cross_family} — Porte {p_sun['gate']} / Porte {p_earth['gate']} (Personnalite) — Porte {d_sun['gate']} / Porte {d_earth['gate']} (Design)"
    }

    return {
        "type": result["type"],
        "strategy": STRATEGY_MAP.get(result["type"], result["type"]),
        "authority": result["authority"],
        "profile": result["profile"],
        "centers_defined": result["defined_centers"],
        "centers_open": result["undefined_centers"],
        "channels": defined_channels,
        "incarnation_cross": incarnation_cross,
        "active_gates": result["all_active_gates"],
        "meta": {
            "city_resolved": location.address,
            "timezone": tz_name,
            "utc_offset": utc_offset
        }
    }
