import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str | None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class IncidentOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RunbookDocumentOut(BaseModel):
    id: uuid.UUID
    title: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class RunbookSearchResultOut(BaseModel):
    document_title: str
    start_line: int
    end_line: int
    content: str
    distance: float
