import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# --- FIXED: Dynamically read from Docker environment or fallback to the correct container credentials ---
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:supersecretpassword@postgres_db:5432/forensic_db"
)

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBCaseFile(Base):
    """Case Management Relational Layer"""
    __tablename__ = "case_files"
    
    case_id = Column(String(100), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_examiner = Column(String(255), nullable=False, default="Lead Investigator")
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="OPEN_ACTIVE")

    # Relationships
    evidence_records = relationship("DBForensicReport", back_populates="case_file")

class DBVideoRecord(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String(64), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class DBForensicReport(Base):
    __tablename__ = "forensic_reports"

    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String(64), ForeignKey("videos.file_hash"), unique=True, index=True)
    case_id = Column(String(100), ForeignKey("case_files.case_id"), nullable=True) 
    verdict = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    device_type = Column(String(255))
    resolution = Column(String(50))
    fps = Column(Float)
    compression_profile = Column(String(100))
    blockchain_tx_hash = Column(String(66), nullable=True)
    block_number = Column(Integer, nullable=True)
    gas_used = Column(Integer, nullable=True)
    is_anchored = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Using JSONB for PostgreSQL stability
    timeline_json = Column(JSONB) 

    # Relationships
    case_file = relationship("DBCaseFile", back_populates="evidence_records")

class DBAuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables inside PostgreSQL."""
    Base.metadata.create_all(bind=engine)