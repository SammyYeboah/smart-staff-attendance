from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    role: str

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    role: str = Field(..., pattern="^(admin|staff)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)

class UserOut(BaseModel):
    id: int
    name: str
    username: str
    role: str

class UserList(BaseModel):
    items: List[UserOut]

class ClockInRequest(BaseModel):
    user_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ClockOutRequest(BaseModel):
    user_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AttendanceOut(BaseModel):
    attendance_id: int
    user_id: int
    clock_in: datetime
    clock_out: Optional[datetime] = None
    latitude_in: Optional[float] = None
    longitude_in: Optional[float] = None
    latitude_out: Optional[float] = None
    longitude_out: Optional[float] = None

class AttendanceLogList(BaseModel):
    items: List[AttendanceOut]

class DailySummaryFilter(BaseModel):
    date: str  # "YYYY-MM-DD"

class UserLogsFilter(BaseModel):
    user_id: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
