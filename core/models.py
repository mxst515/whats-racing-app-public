from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Session:
    type: str
    date: str # Format: YYYY-MM-DD
    time: str # Format: HH:MM

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "date": self.date,
            "time": self.time
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Session':
        return Session(
            type = data.get("type", ""),
            date = data.get("date", ""),
            time = data.get("time", "")
        )
    
@dataclass
class Race:
    series: str
    round: int
    name: str
    country: str
    sessions: List[Session] = field(default_factory=list)
    id: Optional[str] = None # document id from firestore

    def to_dict(self) -> dict:
        return{
            "series": self.series,
            "round": self.round,
            "name": self.name,
            "country": self.country,
            "sessions": [session.to_dict() for session in self.sessions]
        }
    
    @staticmethod
    def from_dict(data: dict, doc_id: str = None) -> 'Race':
        sessions_data = data.get("sessions", [])
        sessions_list = [Session.from_dict(s) for s in sessions_data]

        return Race(
            id=doc_id,
            series=data.get("series", ""),
            round=data.get("round", 0),
            name=data.get("name", ""),
            country=data.get("country", ""),
            sessions=sessions_list
        )
