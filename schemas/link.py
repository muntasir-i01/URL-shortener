from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, Field


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_code: Optional[str] = Field(default=None, min_length=3, max_length=16)
    expires_at: Optional[datetime] = None


class LinkResponse(BaseModel):
    code: str
    short_url: str


class LinkMetadata(BaseModel):
    code: str
    original_url: HttpUrl
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
