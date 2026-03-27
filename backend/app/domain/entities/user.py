from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class User:
    id: str
    email: str
    password_hash: str
    full_name: str | None
    role: str | None
    department: str | None
    phone: str | None
    avatar_url: str | None
    updated_at: datetime | None
    last_login_at: datetime | None
    created_at: datetime
