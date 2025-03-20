from pydantic import BaseModel, EmailStr
from typing import Optional

class URLCreate(BaseModel):
    url: str
    custom_alias: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True