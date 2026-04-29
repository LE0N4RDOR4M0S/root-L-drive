from pydantic import BaseModel, Field
from typing import List, Optional


class CreateMachineRequest(BaseModel):
    name: str = Field(..., max_length=120)
    allowed_paths: List[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = None


class MachineListItemResponse(BaseModel):
    id: str
    name: str
    allowed_paths: List[str]
    created_at: str
    last_seen: Optional[str] = None
    is_active: bool


class MachineCreateResponse(MachineListItemResponse):
    token: str
    installer_script: Optional[str] = None
