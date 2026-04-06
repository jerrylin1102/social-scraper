"""
Instagram scraper — curl_cffi (Chrome TLS) + i.instagram.com REST API
No login required for public profiles.
Pagination: /api/v1/feed/user/{user_id}/ (more stable than GraphQL doc_id)
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from curl_cffi.requests import AsyncSession

logger = logging.getLogger(__name__)

IG_APP_ID = "936619743392459"
PROFILE_URL = "https://i.instagram.com/api/v1/users/web_profile_info/"
FEED_URL = "https://i.instagram.com/api/v1/feed/user/{user_id}/"
AVATARS_DIR = Path(__file__).resolve().parent.parent / "static" / "avatars"

_BASE_HEADERS = {
    "x-ig-app-id": IG_APP_ID,
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.instagram.com/",
}


# ── Parsers ───────────────────────────────────────────────────────────────────

def _parse_profile(user: dict) -> dict:
    bio_links = user.get("bio_links") or []
    website = bio_links[0].get("url", "") if bio_links else user.get("external_url", "")
    return {
        "username":        user.get("username", ""),
        "full_name":       user.get("full_name") or "",
        "bio":             user.get("biography") or "",
        "followers_count": (user.get("edge_followed_by") or {}).get("count", 0),
        "following_count": (user.get("edge_follow") or {}).get("count", 0),
        "posts_count":     (user.get("edge_owner_to_timeline_media") or {}).get("count", 0),
        "is_verified":     bool(user.get("is_verified")),
        "profile_pic_url": user.get("profile_pic_url_hd") or user.get("profile_pic_url", ""),
        "website":         website or None,
        "user_id":         user.get("id", ""),
    }


def _parse_media_node(node: dict) -> Optional[dict]:
    """Parse a GraphQL media node (from web_profile_info edges)."""
    captions = (node.get("edge_media_to_caption") or {}).get("edges", [])
    text = captions[0].get("node", {}).get("text", "") if captions else ""
    shortcode = node.get("shortcode", "")
    ts = node.get("taken_at_timestamp")
    return {
        "external_id":  node.get("id", ""),
        "text":         text,
        "created_at":   datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None,
        "like_count":   (node.get("edge_liked_by") or {}).get("count", 0),
        "reply_count":  (node.get("edge_media_to_comment") or {}).get("count", 0),
        "repost_count": 0,
        "post_url":     f"https://www.instagram.com/p/{shortcode}/" if shortcode else None,
    }


def _parse_feed_item(item: dict) -> Optional[dict]:
    """Parse a mobile API feed item."""
    caption = item.get("caption") or {}
    text = caption.get("text", "") if isinstance(caption, dict) else ""
    ts = item.get("taken_at")
    code = item.get("code", "")
    return {
        "external_id":  str(item.get("pk", item.get("id", ""))),
        "text":         text,
        "created_at":   datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None,
        "like_count":   item.get("like_count", 0),
        "reply_count":  item.get("comment_count", 0),
        "repost_count": 0,
        "post_url":     f"https://www.instagram.com/p/{code}/" if code else None,
    }


# ── Avatar download ───────────────────────────────────────────────────────────

async def _download_avatar(url: str, username: str) -> Optional[str]:
    if not url:
        return None
    dest = AVATARS_DIR / f"instagram_{username}.jpg"
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.instagram.com/",
            })
            if resp.status_code == 200:
                dest.write_bytes(resp.content)
                return f"/static/avatars/instagram_{username}.jpg"
    except Exception as exc:
        logger.warning("Avatar download failed: %s", exc)
    return None


# ── Main scraper ──────────────────────────────────────────────────────────────

async def scrape_instagram(username: str) -> dict:
    async with AsyncSession(impersonate="chrome124") as session:
        # Step 1: profile + first 12 posts
        resp = await session.get(PROFILE_URL, params={"username": username},
                                 headers=_BASE_HEADERS)
        if resp.status_code == 404:
            raise ValueError(f"找不到帳號 @{username}。")
        if resp.status_code != 200:
            raise ValueError(f"Instagram 請求失敗 (HTTP {resp.status_code})，請稍後再試。")

        data = resp.json()
        user = (data.get("data") or {}).get("user")
        if not user:
            raise ValueError(f"找不到帳號 @{username}，可能是私人帳號或不存在。")

        profile_raw = _parse_profile(user)
        user_id: str = profile_raw.pop("user_id", "")

        media_edge = user.get("edge_owner_to_timeline_media") or {}
        posts: list[dict] = []
        for edge in media_edge.get("edges", []):
            post = _parse_media_node(edge.get("node", {}))
            if post:
                posts.append(post)

        # Step 2: paginate via mobile feed API
        more_available = True
        max_id: Optional[str] = None
        page = 0
        while more_available and user_id:
            await asyncio.sleep(2)
            params = {"count": 12}
            if max_id:
                params["max_id"] = max_id
            feed_resp = await session.get(
                FEED_URL.format(user_id=user_id),
                params=params, headers=_BASE_HEADERS,
            )
            if feed_resp.status_code != 200:
                break
            feed = feed_resp.json()
            for item in feed.get("items", []):
                post = _parse_feed_item(item)
                if post:
                    posts.append(post)
            more_available = bool(feed.get("more_available"))
            max_id = feed.get("next_max_id")
            page += 1
            if page >= 50:   # safety cap ~600 posts
                break

    # De-duplicate
    seen: set[str] = set()
    unique: list[dict] = []
    for p in posts:
        k = p.get("external_id", "")
        if k not in seen:
            seen.add(k)
            unique.append(p)

    pic_url: str = profile_raw.pop("profile_pic_url", "") or ""
    profile_raw["profile_pic_local"] = await _download_avatar(pic_url, username)

    return {"profile": profile_raw, "posts": unique}
