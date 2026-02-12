import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID

# Base CLass
Base = declarative_base()

class WorkSession(Base):
    __tablename__ = "work_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)  
    
    # Relationships
    blink_logs = relationship("BlinkLog", back_populates="session", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkSession(id={self.id}, start={self.start_time})>"


class BlinkLog(Base):                             #Avg Blink per minute
    __tablename__ = "blink_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("work_sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    blink_rate = Column(Integer, nullable=False)  # Blinks per minute
    avg_ear = Column(Float, nullable=False)       # Average Eye Aspect Ratio 

    # Relationships
    session = relationship("WorkSession", back_populates="blink_logs")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("work_sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String, nullable=False)   
    action_taken = Column(String, nullable=True)  

    # Relationships
    session = relationship("WorkSession", back_populates="events")