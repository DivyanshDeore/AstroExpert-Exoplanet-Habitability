import json
import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.database.db import Base, engine, get_db
from app.database.models import Planet, Assessment
from app.engine.calculations import stellar_flux, relative_density, simplified_hz
from app.engine.inference_engine import run_rules

Base.metadata.create_all(bind=engine)
RULES = json.loads((Path(__file__).parent / "knowledge_base" / "rules.json").read_text(encoding="utf-8"))

app = FastAPI(title="AstroExpert", version="1.1.0", description="Offline exoplanet catalogue and explainable habitability screening tool.")
cors_origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

CATALOGUE_PATH = Path(__file__).parent / "data" / "exoplanets.json"

class AssessmentInput(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    stellar_luminosity_solar: float = Field(gt=0)
    semi_major_axis_au: float = Field(gt=0)
    radius_earth: float | None = Field(default=None, gt=0)
    mass_earth: float | None = Field(default=None, gt=0)

def planet_dict(p: Planet) -> dict:
    return {k: getattr(p, k) for k in [
        "id","name","host_star","discovery_method","discovery_year","radius_earth",
        "mass_earth","orbital_period_days","semi_major_axis_au","stellar_luminosity_solar",
        "stellar_temperature_k","insolation_earth","source","source_url","is_favorite"
    ]}

@app.on_event("startup")
def seed_catalogue():
    """Merge bundled records into SQLite without deleting favourites or assessment history."""
    payload = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    with Session(engine) as db:
        for item in payload["records"]:
            existing = db.scalar(select(Planet).where(Planet.name == item["name"]))
            if existing is None:
                db.add(Planet(**item))
            else:
                for key, value in item.items():
                    if key not in {"name", "is_favorite"} and value is not None:
                        setattr(existing, key, value)
        db.commit()

@app.get("/")
def home():
    return {"app":"AstroExpert","status":"running","version":app.version}

@app.get("/api/dataset/metadata")
def dataset_metadata():
    payload = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    return {
        "source": payload.get("source"),
        "table": payload.get("table"),
        "snapshot_date": payload.get("snapshot_date"),
        "planet_count": payload.get("source_row_count"),
        "source_column_count": payload.get("source_column_count"),
        "source_columns": payload.get("source_columns", [])
    }

@app.get("/api/overview")
def overview(db: Session = Depends(get_db)):
    planets = db.scalars(select(Planet)).all()
    assessments = db.scalars(select(Assessment)).all()
    return {
        "planet_count": len(planets),
        "favorite_count": sum(1 for p in planets if p.is_favorite),
        "assessment_count": len(assessments),
        "recent_assessments": [
            {"id": a.id, "planet_name": a.planet_name, "assessment": a.assessment, "created_at": a.created_at.isoformat()}
            for a in sorted(assessments, key=lambda x:x.created_at, reverse=True)[:5]
        ]
    }

@app.get("/api/planets")
def list_planets(q: str = "", db: Session = Depends(get_db)):
    stmt = select(Planet)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Planet.name.ilike(like), Planet.host_star.ilike(like)))
    return [planet_dict(p) for p in db.scalars(stmt.order_by(Planet.name)).all()]

@app.get("/api/planets/compare")
def compare_planets(ids: str, db: Session = Depends(get_db)):
    try:
        selected = [int(x) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(400, "ids must be comma-separated planet IDs")
    if not 1 <= len(selected) <= 3:
        raise HTTPException(400, "Select between one and three planets")
    rows = db.scalars(select(Planet).where(Planet.id.in_(selected))).all()
    by_id = {p.id: p for p in rows}
    missing = [x for x in selected if x not in by_id]
    if missing:
        raise HTTPException(404, f"Planet IDs not found: {missing}")
    return [planet_dict(by_id[x]) for x in selected]


@app.get("/api/planets/{planet_id}")
def get_planet(planet_id: int, db: Session = Depends(get_db)):
    p = db.get(Planet, planet_id)
    if not p:
        raise HTTPException(404, "Planet not found")
    return planet_dict(p)

@app.post("/api/planets/{planet_id}/favorite")
def toggle_favorite(planet_id: int, db: Session = Depends(get_db)):
    p = db.get(Planet, planet_id)
    if not p:
        raise HTTPException(404, "Planet not found")
    p.is_favorite = not p.is_favorite
    db.commit()
    db.refresh(p)
    return {"id": p.id, "is_favorite": p.is_favorite}

@app.get("/api/favorites")
def favorites(db: Session = Depends(get_db)):
    return [planet_dict(p) for p in db.scalars(select(Planet).where(Planet.is_favorite == True).order_by(Planet.name)).all()]



@app.post("/api/assess")
def assess(payload: AssessmentInput, db: Session = Depends(get_db)):
    flux = stellar_flux(payload.stellar_luminosity_solar, payload.semi_major_axis_au)
    hz = simplified_hz(payload.stellar_luminosity_solar)
    facts = set()
    if hz["inner_au"] <= payload.semi_major_axis_au <= hz["outer_au"]:
        facts.add("inside_simplified_hz")
    if payload.radius_earth is not None and 0.8 <= payload.radius_earth <= 1.4:
        facts.add("earth_size_radius")
    density = None
    if payload.mass_earth is not None and payload.radius_earth is not None:
        density = relative_density(payload.mass_earth, payload.radius_earth)
        facts.add("density_calculated")
    inference = run_rules(facts, RULES)
    assessment = "Multiple screening indicators" if "multiple_screening_indicators" in inference["facts"] else ("Some indicators met" if facts else "Insufficient data")
    record = Assessment(
        planet_name=payload.name, assessment=assessment, stellar_flux=flux,
        facts_json=json.dumps(sorted(facts)), explanation_json=json.dumps(inference["fired_rules"])
    )
    db.add(record)
    db.commit()
    return {
        "planet_name": payload.name, "assessment": assessment,
        "stellar_flux_earth_units": round(flux, 4),
        "simplified_hz_au": {k: round(v, 5) for k,v in hz.items()},
        "relative_density_earth_units": round(density, 4) if density is not None else None,
        "facts": sorted(facts), "fired_rules": inference["fired_rules"],
        "limitations": [
            "Simplified luminosity-scaled HZ approximation only; not temperature-dependent.",
            "Earth-size and HZ indicators do not establish atmosphere, surface water, or life.",
            "Density is not a definitive composition classifier.",
            "Missing measurements remain unknown."
        ],
        "saved": True
    }

@app.get("/api/assessments")
def assessment_history(db: Session = Depends(get_db)):
    rows = db.scalars(select(Assessment).order_by(Assessment.created_at.desc()).limit(50)).all()
    return [{
        "id": r.id, "planet_name": r.planet_name, "assessment": r.assessment,
        "stellar_flux": r.stellar_flux, "created_at": r.created_at.isoformat(),
        "facts": json.loads(r.facts_json), "explanations": json.loads(r.explanation_json)
    } for r in rows]


@app.get("/api/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    """Dataset-backed dashboard summary."""
    rows = db.scalars(select(Planet)).all()
    methods = {}
    years = {}
    missing = {"radius": 0, "mass": 0, "insolation": 0, "semi_major_axis": 0}
    for p in rows:
        methods[p.discovery_method or "Unknown"] = methods.get(p.discovery_method or "Unknown", 0) + 1
        years[str(p.discovery_year) if p.discovery_year is not None else "Unknown"] = years.get(str(p.discovery_year) if p.discovery_year is not None else "Unknown", 0) + 1
        missing["radius"] += p.radius_earth is None
        missing["mass"] += p.mass_earth is None
        missing["insolation"] += p.insolation_earth is None
        missing["semi_major_axis"] += p.semi_major_axis_au is None
    return {"planet_count": len(rows), "host_star_count": len({p.host_star for p in rows if p.host_star}),
            "discovery_methods": methods, "discovery_years": years, "missing_measurements": missing}

@app.get("/api/planets/search")
def search_planets(q: str = "", limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 250))
    stmt = select(Planet)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Planet.name.ilike(like), Planet.host_star.ilike(like)))
    rows = db.scalars(stmt.order_by(Planet.name).offset(max(0, offset)).limit(limit)).all()
    return {"items": [planet_dict(p) for p in rows], "limit": limit, "offset": max(0, offset)}


@app.get("/api/rules")
def get_rules():
    return RULES

@app.get("/api/dataset/health")
def dataset_health():
    payload = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    raw_path = Path(__file__).parent / "data" / "nasa_pscomppars_full.csv"
    return {"raw_csv_present": raw_path.exists(), "raw_csv_bytes": raw_path.stat().st_size if raw_path.exists() else 0,
            "catalogue_records": len(payload.get("records", [])),
            "source_rows": payload.get("source_row_count"), "source_columns": payload.get("source_column_count"),
            "healthy": raw_path.exists() and len(payload.get("records", [])) == payload.get("source_row_count")}

@app.get("/api/assessments/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    row = db.get(Assessment, assessment_id)
    if not row:
        raise HTTPException(404, "Assessment not found")
    return {"id": row.id, "planet_name": row.planet_name, "assessment": row.assessment,
            "stellar_flux": row.stellar_flux, "created_at": row.created_at.isoformat(),
            "facts": json.loads(row.facts_json), "explanations": json.loads(row.explanation_json)}
