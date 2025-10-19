from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    avatar_type = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

class Schedule(Base):
    __tablename__ = 'schedules'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    scheduled_datetime = Column(DateTime, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    completed = Column(Integer, default=0)  # 0: not completed, 1: completed

class UsageLog(Base):
    __tablename__ = 'usage_logs'
    
    id = Column(Integer, primary_key=True)
    avatar_type = Column(String(50), nullable=False)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

# DB の設定
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///llm_app.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def add_conversation(avatar_type: str, role: str, content: str):
    """Add conversation to database"""
    db = SessionLocal()
    conversation = Conversation(
        avatar_type=avatar_type,
        role=role,
        content=content
    )
    db.add(conversation)
    db.commit()
    db.close()

def get_conversations(avatar_type: str, limit: int = 50):
    """Get conversation history for specific avatar"""
    db = SessionLocal()
    conversations = db.query(Conversation)\
        .filter(Conversation.avatar_type == avatar_type)\
        .order_by(Conversation.timestamp.desc())\
        .limit(limit)\
        .all()
    db.close()
    return list(reversed(conversations))

def add_usage_log(avatar_type: str, input_tokens: int, output_tokens: int, cost: float):
    """Add API usage log"""
    db = SessionLocal()
    usage = UsageLog(
        avatar_type=avatar_type,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost
    )
    db.add(usage)
    db.commit()
    db.close()

def get_total_usage():
    """Get total usage statistics"""
    db = SessionLocal()
    total = db.query(
        sqlalchemy.func.sum(UsageLog.input_tokens).label('total_input'),
        sqlalchemy.func.sum(UsageLog.output_tokens).label('total_output'),
        sqlalchemy.func.sum(UsageLog.cost).label('total_cost')
    ).first()
    db.close()
    return total

def add_schedule(title: str, scheduled_datetime: datetime, description: str = ""):
    """Add schedule to database"""
    db = SessionLocal()
    schedule = Schedule(
        title=title,
        scheduled_datetime=scheduled_datetime,
        description=description
    )
    db.add(schedule)
    db.commit()
    db.close()

def get_schedules(limit: int = 20):
    """Get upcoming schedules"""
    db = SessionLocal()
    schedules = db.query(Schedule)\
        .filter(Schedule.completed == 0)\
        .order_by(Schedule.scheduled_datetime)\
        .limit(limit)\
        .all()
    db.close()
    return schedules

import sqlalchemy