from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime

class Subscriber(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    tier: str = "free"
    is_active: bool = True
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    tags: Optional[str] = None

class MessageLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subscriber_id: int = Field(foreign_key="subscriber.id")
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    message: str

def segment_subscribers(session: Session, tag: str) -> List[Subscriber]:
    stmt = select(Subscriber).where(Subscriber.tags.contains(tag))
    return session.exec(stmt).all()
