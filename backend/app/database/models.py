from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Planet(Base):
    __tablename__ = "planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    host_star: Mapped[str] = mapped_column(String(160), default="Unknown")
    discovery_method: Mapped[str] = mapped_column(String(100), default="Unknown")
    discovery_year: Mapped[int | None] = mapped_column(nullable=True)
    radius_earth: Mapped[float | None] = mapped_column(Float, nullable=True)
    mass_earth: Mapped[float | None] = mapped_column(Float, nullable=True)
    orbital_period_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    semi_major_axis_au: Mapped[float | None] = mapped_column(Float, nullable=True)
    stellar_luminosity_solar: Mapped[float | None] = mapped_column(Float, nullable=True)
    stellar_temperature_k: Mapped[float | None] = mapped_column(Float, nullable=True)
    insolation_earth: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(40), default="demo")
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    planet_name: Mapped[str] = mapped_column(String(160))
    assessment: Mapped[str] = mapped_column(String(100))
    stellar_flux: Mapped[float | None] = mapped_column(Float, nullable=True)
    facts_json: Mapped[str] = mapped_column(Text)
    explanation_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
