from typing import List, Dict
from datetime import datetime
from sqlmodel import Session, select, desc
from database import engine
from models import SystemLog

class StatusManager:
    def __init__(self):
        pass

    def add_log(self, message: str, type: str = "info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        try:
            with Session(engine) as session:
                log = SystemLog(
                    timestamp=timestamp,
                    message=message,
                    type=type
                )
                session.add(log)
                session.commit()
        except Exception as e:
            print(f"Failed to save log: {e}")

    @property
    def logs(self):
        try:
            with Session(engine) as session:
                # Get last 50 logs
                statement = select(SystemLog).order_by(desc(SystemLog.id)).limit(50)
                results = session.exec(statement).all()
                # Convert to dict list for API
                return [
                    {"timestamp": l.timestamp, "message": l.message, "type": l.type}
                    for l in results
                ]
        except:
            return []

status_manager = StatusManager()
