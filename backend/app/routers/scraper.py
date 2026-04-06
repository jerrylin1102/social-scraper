import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..schemas import AnalyzeRequest, AnalyzeResponse, PlatformAnalysisResult, PlatformEnum
from services.ai_analysis import analyze_social_profile
from services.threads_scraper import scrape_threads
from services.instagram_scraper import scrape_instagram

router = APIRouter()

MAX_POSTS_IN_RESPONSE = 12
MIN_DATETIME = datetime.min.replace(tzinfo=timezone.utc)

def _select_posts(posts: list[dict]) -> list[dict]:
    sorted_posts = sorted(posts, key=lambda post: post.get("created_at") or MIN_DATETIME, reverse=True)
    selected: list[dict] = []
    for post in sorted_posts:
        selected.append(
            {
                "external_id": post.get("external_id"),
                "text": (post.get("text") or "").strip()[:280] or None,
                "created_at": post.get("created_at"),
                "like_count": post.get("like_count", 0),
                "reply_count": post.get("reply_count", 0),
                "repost_count": post.get("repost_count", 0),
                "post_url": post.get("post_url"),
            }
        )
        if len(selected) >= MAX_POSTS_IN_RESPONSE:
            break
    return selected


async def _scrape_platform(platform: PlatformEnum, username: str) -> dict:
    scraper = scrape_threads if platform == PlatformEnum.threads else scrape_instagram
    scraped_at = datetime.now(timezone.utc)

    try:
        result = await scraper(username)
    except ValueError as exc:
        return {
            "response": PlatformAnalysisResult(platform=platform, success=False, error=str(exc)),
            "analysis_source": None,
        }
    except Exception as exc:
        return {
            "response": PlatformAnalysisResult(platform=platform, success=False, error=f"爬取失敗：{exc}"),
            "analysis_source": None,
        }

    profile = {
        "platform": platform,
        "username": result["profile"]["username"],
        "full_name": result["profile"].get("full_name"),
        "bio": result["profile"].get("bio"),
        "followers_count": result["profile"].get("followers_count", 0),
        "following_count": result["profile"].get("following_count", 0),
        "posts_count": result["profile"].get("posts_count", 0),
        "is_verified": bool(result["profile"].get("is_verified")),
        "profile_pic_local": result["profile"].get("profile_pic_local"),
        "profile_pic_url": result["profile"].get("profile_pic_url"),
        "website": result["profile"].get("website"),
        "scraped_at": scraped_at,
        "analyzed_post_count": len([post for post in result["posts"] if (post.get("text") or "").strip()]),
        "posts": _select_posts(result["posts"]),
    }
    return {
        "response": PlatformAnalysisResult(
            platform=platform,
            success=True,
            profile=profile,
        ),
        "analysis_source": {
            "profile": {
                "platform": platform.value,
                "username": result["profile"]["username"],
                "full_name": result["profile"].get("full_name"),
                "bio": result["profile"].get("bio"),
                "followers_count": result["profile"].get("followers_count", 0),
                "following_count": result["profile"].get("following_count", 0),
                "posts_count": result["profile"].get("posts_count", 0),
                "is_verified": bool(result["profile"].get("is_verified")),
                "website": result["profile"].get("website"),
            },
            "posts": result["posts"],
        },
    }


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    payloads = await asyncio.gather(*[_scrape_platform(platform, req.username) for platform in req.platforms])
    results = [payload["response"] for payload in payloads]

    successful_profiles = [payload["analysis_source"] for payload in payloads if payload["analysis_source"]]
    completed_platforms = [result.platform for result in results if result.success]
    failed_platforms = [result.platform for result in results if not result.success]

    if not successful_profiles:
        detail = "、".join(filter(None, [result.error for result in results])) or "找不到可分析的公開資料。"
        raise HTTPException(status_code=502, detail=detail)

    analysis_time = datetime.now(timezone.utc)
    try:
        analysis_result = await analyze_social_profile(req.username, successful_profiles)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI 分析失敗：{exc}")

    message = f"完成 @{req.username} 的 AI 分析"
    if failed_platforms:
        failed_label = "、".join(platform.value for platform in failed_platforms)
        message = f"{message}，但 {failed_label} 未成功取得資料"

    return AnalyzeResponse(
        success=True,
        message=message,
        username=req.username,
        requested_platforms=req.platforms,
        completed_platforms=completed_platforms,
        failed_platforms=failed_platforms,
        analyzed_at=analysis_time,
        results=results,
        analysis=analysis_result,
    )
