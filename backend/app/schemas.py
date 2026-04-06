from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List


class PostOut(BaseModel):
    id: int
    external_id: Optional[str] = None
    text: Optional[str] = None
    created_at: Optional[datetime] = None
    like_count: int = 0
    reply_count: int = 0
    repost_count: int = 0
    post_url: Optional[str] = None
    scraped_at: datetime

    model_config = {"from_attributes": True}


class ProfileOut(BaseModel):
    id: int
    platform: str
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    is_verified: bool = False
    profile_pic_local: Optional[str] = None
    website: Optional[str] = None
    scraped_at: datetime

    model_config = {"from_attributes": True}


class ProfileWithPostsOut(ProfileOut):
    posts: List[PostOut] = []
    total_posts: int = 0

    @field_validator("total_posts", mode="before")
    @classmethod
    def compute_total(cls, v, info):
        return v


class ScrapeRequest(BaseModel):
    platform: str   # 'threads' or 'instagram'
    username: str

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ("threads", "instagram"):
            raise ValueError("platform 必須是 'threads' 或 'instagram'")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip().lstrip("@")
        if not v:
            raise ValueError("username 不能為空")
        return v


class ScrapeResponse(BaseModel):
    success: bool
    message: str
    profile: Optional[ProfileWithPostsOut] = None
