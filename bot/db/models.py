from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Lead:
    id: Optional[int]
    tg_user_id: int
    tg_username: Optional[str]
    parent_name: str
    child_name: str
    child_age: int
    course: str
    phone: str
    preferred_time: Optional[str]
    status: str  # new / in_progress / done / cancelled
    created_at: datetime
    updated_at: datetime