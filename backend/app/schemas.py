from datetime import datetime
from enum import Enum
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator


class PlatformEnum(str, Enum):
    threads = "threads"
    instagram = "instagram"


def _parse_social_input(value: str) -> tuple[str, Optional[PlatformEnum]]:
    raw = value.strip()
    if not raw:
        raise ValueError("username 不能為空")

    original = raw
    inferred_platform: Optional[PlatformEnum] = None
    if "instagram.com" in raw or "threads.net" in raw:
        parsed = urlparse(raw if raw.startswith("http") else f"https://{raw}")
        parts = [part for part in parsed.path.split("/") if part]
        if "threads.net" in parsed.netloc:
            inferred_platform = PlatformEnum.threads
            if parts and parts[0].startswith("@"):
                raw = parts[0][1:]
            elif parts:
                raw = parts[0]
        elif "instagram.com" in parsed.netloc:
            inferred_platform = PlatformEnum.instagram
            reserved_paths = {"p", "reel", "reels", "stories", "explore", "accounts", "direct"}
            if parts:
                candidate = parts[0]
                if candidate.startswith("@"):
                    candidate = candidate[1:]
                if candidate.lower() not in reserved_paths:
                    raw = candidate
                else:
                    raw = ""

    raw = raw.strip().strip("/")
    if raw.startswith("@"):
        raw = raw[1:]

    if not raw:
        if "instagram.com" in original or "threads.net" in original:
            raise ValueError("請輸入 IG 或 Threads 的用戶個人頁網址。")
        raise ValueError("username 不能為空")

    return raw, inferred_platform


def _sanitize_username(value: str) -> str:
    username, _ = _parse_social_input(value)
    return username


class PostOut(BaseModel):
    external_id: Optional[str] = None
    text: Optional[str] = None
    created_at: Optional[datetime] = None
    like_count: int = 0
    reply_count: int = 0
    repost_count: int = 0
    post_url: Optional[str] = None


class ScrapedProfileOut(BaseModel):
    platform: PlatformEnum
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    is_verified: bool = False
    profile_pic_local: Optional[str] = None
    profile_pic_url: Optional[str] = None
    website: Optional[str] = None
    scraped_at: datetime
    analyzed_post_count: int = 0
    posts: List[PostOut] = Field(default_factory=list)


class PlatformAnalysisResult(BaseModel):
    platform: PlatformEnum
    success: bool
    error: Optional[str] = None
    profile: Optional[ScrapedProfileOut] = None


class AnalysisFact(BaseModel):
    value: Optional[str] = None
    evidence: Optional[str] = None
    confidence: str = "none"


class BirthdayFact(AnalysisFact):
    iso_date: Optional[str] = None


class PersonalityInsight(BaseModel):
    headline: str
    summary: str
    traits: List[str] = Field(default_factory=list)


class MbtiInsight(BaseModel):
    type: str
    confidence: str
    reason: str


class InferredFacts(BaseModel):
    age: AnalysisFact
    birthday: BirthdayFact
    height: AnalysisFact
    location: AnalysisFact
    school_or_company: AnalysisFact
    zodiac: AnalysisFact


class UserAnalysis(BaseModel):
    personality: PersonalityInsight
    interests: List[str] = Field(default_factory=list)
    key_events: List[str] = Field(default_factory=list)
    mbti: MbtiInsight
    chat_topics: List[str] = Field(default_factory=list)
    inferred_facts: InferredFacts


class AnalyzeRequest(BaseModel):
    username: str
    platforms: List[PlatformEnum]

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return _sanitize_username(value)

    @field_validator("platforms", mode="before")
    @classmethod
    def normalize_platforms(cls, value):
        if isinstance(value, str):
            if value.lower().strip() == "both":
                return [PlatformEnum.threads.value, PlatformEnum.instagram.value]
            return [value]
        return value

    @model_validator(mode="before")
    @classmethod
    def preprocess_input(cls, data):
        if not isinstance(data, dict):
            return data

        username = data.get("username")
        if not isinstance(username, str):
            return data

        try:
            normalized_username, inferred_platform = _parse_social_input(username)
        except ValueError:
            return data

        payload = dict(data)
        payload["username"] = normalized_username
        if inferred_platform is not None:
            payload["platforms"] = [inferred_platform.value]
        return payload

    @field_validator("platforms")
    @classmethod
    def validate_platforms(cls, values: List[PlatformEnum]) -> List[PlatformEnum]:
        cleaned: List[PlatformEnum] = []
        seen = set()
        for value in values:
            platform = PlatformEnum(value)
            if platform not in seen:
                cleaned.append(platform)
                seen.add(platform)
        if not cleaned:
            raise ValueError("platforms 至少要選擇一個平台")
        return cleaned


class AnalyzeResponse(BaseModel):
    success: bool
    message: str
    username: str
    requested_platforms: List[PlatformEnum]
    completed_platforms: List[PlatformEnum]
    failed_platforms: List[PlatformEnum]
    analyzed_at: datetime
    results: List[PlatformAnalysisResult]
    analysis: UserAnalysis
