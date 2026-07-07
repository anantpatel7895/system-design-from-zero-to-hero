from pydantic import BaseModel
from pydantic import HttpUrl
from pydantic import Field
from datetime import datetime


class URLCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = Field(default=None, min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_-]+$")


class URLResponse(BaseModel):
    id: int
    short_url: str


class URLStatsResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    click_count: int
    created_at: datetime