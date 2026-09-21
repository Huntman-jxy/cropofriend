from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    crop = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)

    disease = Column(String(200))
    disease_confidence = Column(Float)
    pest = Column(String(200))
    pest_confidence = Column(Float)

    severity = Column(String(50))
    risk_score = Column(Float)
    risk_level = Column(String(50))

    temperature = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    weather_code = Column(Integer)

    raw_result = Column(JSON)


Base.metadata.create_all(bind=engine)
