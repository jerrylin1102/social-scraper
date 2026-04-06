from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from ..database import get_db
from ..models import Profile, Post
from ..schemas import ScrapeRequest, ScrapeResponse, ProfileOut, ProfileWithPostsOut, PostOut
from services.threads_scraper import scrape_threads
from services.instagram_scraper import scrape_instagram

router = APIRouter()


# ── helpers ───────────────────────────────────────────────────────────────────

def _upsert_profile(db: Session, platform: str, data: dict) -> Profile:
    profile = db.query(Profile).filter_by(platform=platform, username=data["username"]).first()
    fields = ["full_name", "bio", "followers_count", "following_count",
              "posts_count", "is_verified", "profile_pic_local", "website"]
    if profile:
        for f in fields:
            setattr(profile, f, data.get(f))
        profile.scraped_at = datetime.now(timezone.utc)
        # Remove old posts
        db.query(Post).filter_by(profile_id=profile.id).delete()
    else:
        profile = Profile(platform=platform, username=data["username"],
                          **{f: data.get(f) for f in fields})
        db.add(profile)
    db.flush()
    return profile


def _insert_posts(db: Session, profile_id: int, posts: list[dict]) -> None:
    for p in posts:
        db.add(Post(profile_id=profile_id, **p))


def _profile_with_posts(profile: Profile) -> ProfileWithPostsOut:
    sorted_posts = sorted(profile.posts, key=lambda p: p.created_at or datetime.min, reverse=True)
    posts_out = [PostOut.model_validate(p) for p in sorted_posts]
    return ProfileWithPostsOut(
        **ProfileOut.model_validate(profile).model_dump(),
        posts=posts_out,
        total_posts=len(posts_out),
    )


# ── POST /api/scrape ──────────────────────────────────────────────────────────

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape(req: ScrapeRequest, db: Session = Depends(get_db)):
    try:
        if req.platform == "threads":
            result = await scrape_threads(req.username)
        else:
            result = await scrape_instagram(req.username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"爬取失敗：{e}")

    profile = _upsert_profile(db, req.platform, result["profile"])
    _insert_posts(db, profile.id, result["posts"])
    db.commit()
    db.refresh(profile)

    return ScrapeResponse(
        success=True,
        message=f"成功爬取 @{req.username}，共 {len(result['posts'])} 篇貼文。",
        profile=_profile_with_posts(profile),
    )


# ── GET /api/profiles ─────────────────────────────────────────────────────────

@router.get("/profiles", response_model=List[ProfileOut])
def list_profiles(db: Session = Depends(get_db)):
    return db.query(Profile).order_by(Profile.scraped_at.desc()).all()


# ── GET /api/profiles/{platform}/{username} ───────────────────────────────────

@router.get("/profiles/{platform}/{username}", response_model=ProfileWithPostsOut)
def get_profile(platform: str, username: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter_by(platform=platform, username=username).first()
    if not profile:
        raise HTTPException(status_code=404, detail="找不到該帳號，請先進行爬取。")
    return _profile_with_posts(profile)


# ── DELETE /api/profiles/{platform}/{username} ────────────────────────────────

@router.delete("/profiles/{platform}/{username}")
def delete_profile(platform: str, username: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter_by(platform=platform, username=username).first()
    if not profile:
        raise HTTPException(status_code=404, detail="找不到該帳號。")
    db.delete(profile)
    db.commit()
    return {"success": True, "message": f"已刪除 @{username}"}
