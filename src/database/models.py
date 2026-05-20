import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import TypeDecorator, CHAR


Base = declarative_base()


# ── SQLite-compatible UUID column type ───────────────────────────────────────
# PostgreSQL has a native UUID type; SQLite stores it as a 36-char string.
# This decorator handles conversion transparently so the rest of the code
# (and any future migration back to Postgres) stays unchanged.
class UUID(TypeDecorator):
    """Platform-independent UUID type stored as CHAR(36)."""
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(str(value))


# ── Models ────────────────────────────────────────────────────────────────────

class WorkSession(Base):
    __tablename__ = "work_sessions"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    blink_logs = relationship("BlinkLog", back_populates="session",
                              cascade="all, delete-orphan")
    events = relationship("Event", back_populates="session",
                          cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkSession(id={self.id}, start={self.start_time})>"


class BlinkLog(Base):
    __tablename__ = "blink_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(), ForeignKey("work_sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    blink_rate = Column(Integer, nullable=False)   # Blinks per minute
    avg_ear = Column(Float, nullable=False)        # Average Eye Aspect Ratio

    session = relationship("WorkSession", back_populates="blink_logs")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(), ForeignKey("work_sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String, nullable=False)
    action_taken = Column(String, nullable=True)

    session = relationship("WorkSession", back_populates="events")
