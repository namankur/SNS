from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    DEAR_ONE = "dear_one"
    CALLER = "caller"

class UserCreate(BaseModel):
    name: str
    phone_number: str
    role: UserRole

class UserResponse(BaseModel):
    user_id: str
    name: str
    phone_number: str
    role: UserRole
    family_group_id: Optional[str]
    created_at: datetime
    is_active: bool

class SignalCreate(BaseModel):
    timestamp: datetime
    screen_active_last_mins: int
    movement_type: str
    last_interaction_time: str
    battery_level: int
    is_charging: bool
    network_type: str
    dnd_active: bool

class LinkFamilyRequest(BaseModel):
    dear_one_phone: str
    nickname: str

class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp: str
