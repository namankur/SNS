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
    phone_number: str
    timestamp: datetime
    screen_active_last_mins: int
    movement_type: str = "STILL"
    last_interaction_time: str = ""
    battery_level: int = 100
    is_charging: bool = False
    is_wifi: bool = True
    network_type: str = "WIFI"
    dnd_active: bool = False
    ringer_mode: str = "NORMAL"
    ringer_volume: int = 50
    is_headphone_plugged: bool = False
    ambient_light: str = "NORMAL" # DARK, NORMAL, BRIGHT
    phone_orientation: str = "FLAT" # FLAT, TILTED
    proximity: str = "FAR" # NEAR, FAR
    last_app_used: str = ""

class LinkFamilyRequest(BaseModel):
    dear_one_phone: str
    nickname: str

class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp: str
