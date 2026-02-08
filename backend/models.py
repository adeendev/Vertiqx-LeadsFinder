from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    business_name: str
    domain: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    email_quality: Optional[str] = None
    builder: Optional[str] = None
    builder_type: Optional[str] = None
    technical_score: int = Field(default=0)
    ux_score: int = Field(default=0)
    business_score: int = Field(default=0)
    final_priority: float = Field(default=0.0)
    tier: str = Field(default="Ignore")
    city: str
    keyword: str
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    screenshot_path: Optional[str] = None
    contacted: bool = Field(default=False)
    notes: Optional[str] = None
    project_name: str = Field(default="Default Project")
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    linkedin: Optional[str] = None
    pain_points: Optional[str] = None
    email_sent: bool = Field(default=False)
    email_sent_at: Optional[datetime] = None
    email_status: Optional[str] = None

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SystemLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: str
    message: str
    type: str = Field(default="info")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Deduplication hash (domain + phone) - logically handled, but we can add a unique constraint if needed.
    # For simplicity, we'll check logic in code or add a computed field. 
    # Let's add a unique constraint on domain if it exists, or handle in application logic.

class Settings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    value: str
    description: Optional[str] = None
