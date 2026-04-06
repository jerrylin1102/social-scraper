"""
Threads scraper — Playwright + hidden JSON extraction
No login required for public profiles.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
import jmespath
from nested_lookup import nested_lookup
from parsel import Selector
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

AVATARS_DIR = Path(__file__).resolve().parent.parent / "static" / "avatars"


# ── Profile parser ────────────────────────────────────────────────────────────

def _parse_profile(user_obj: dict) -> dict:
    r = jmespath.search("""{
        username:       username,
        full_name:      full_name,
        bio:            biography,
        bio_links:      bio_links[].url,
        followers:      follower_count,
        following:      following_count,
        posts_count:    media_count,
        is_verified:    is_verified,
        profile_pic:    hd_profile_pic_versions[-1].url
    }""", user_obj) or {}

    bio_links = r.get("bio_links") or []
    return {
        "username":        r.get("username", ""),
        "full_name":       r.get("full_name") or "",
        "bio":             r.get("bio") or "",
        "followers_count": r.get("followers") or 0,
        "following_count": r.get("following") or 0,
        "posts_count":     r.get("posts_count") or 0,
        "is_verified":     bool(r.get("is_verified")),
        "profile_pic_url": r.get("profile_pic") or "",
        "website":         bio_links[0] if bio_links else None,
    }


# ── Post parser ───────────────────────────────────────────────────────────────

def _parse_post(thread_item: dict) -> Optional[dict]:
    try:
        r = jmespath.search("""{
            text:         post.caption.text,
            taken_at:     post.taken_at,
            external_id:  post.id,
            code:         post.code,
            username:     post.user.username,
            like_count:   post.like_count,
            reply_count:  post.text_post_app_info.direct_reply_count,
            repost_count: post.text_post_app_info.repost_count
        }""", thread_item) or {}

        username = r.get("username", "")
        code = r.get("code", "")
        taken_at = r.get("taken_at")

        return {
            "external_id":  str(r.get("external_id", "")),
            "text":         r.get("text") or "",
            "created_at":   datetime.fromtimestamp(taken_at, tz=timezone.utc) if taken_at else None,
            "like_count":   r.get("like_count") or 0,
            "reply_count":  r.get("reply_count") or 0,
            "repost_count": r.get("repost_count") or 0,
            "post_url":     f"https://www.threads.net/@{username}/post/{code}" if code else None,
        }
    except Exception:
        return None


# ── Avatar download ───────────────────────────────────────────────────────────

async def _download_avatar(url: str, username: str) -> Optional[str]:
    if not url:
        return None
    dest = AVATARS_DIR / f"threads_{username}.jpg"
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.threads.net/",
            })
            if resp.status_code == 200:
                dest.write_bytes(resp.content)
                return f"/static/avatars/threads_{username}.jpg"
    except Exception as exc:
        logger.warning("Avatar download failed: %s", exc)
    return None


# ── Main scraper ──────────────────────────────────────────────────────────────

async def scrape_threads(username: str) -> dict:
    """Return {"profile": {...}, "posts": [...]} or raise on failure."""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await ctx.new_page()
        try:
            await page.goto(f"https://www.threads.net/@{username}",
                            wait_until="networkidle", timeout=30_000)
            await page.wait_for_timeout(2_000)
            html = await page.content()
        finally:
            await browser.close()

    sel = Selector(html)
    datasets = sel.css('script[type="application/json"][data-sjs]::text').getall()

    profile_data: dict = {}
    posts: list[dict] = []

    for raw in datasets:
        if '"ScheduledServerJS"' not in raw:
            continue
        blob = json.loads(raw)

        if "follower_count" in raw and not profile_data:
            for user_obj in nested_lookup("user", blob):
                if isinstance(user_obj, dict) and "follower_count" in user_obj:
                    profile_data = _parse_profile(user_obj)
                    break

        if "thread_items" in raw:
            for thread_list in nested_lookup("thread_items", blob):
                for item in (thread_list or []):
                    post = _parse_post(item)
                    if post:
                        posts.append(post)

    if not profile_data:
        raise ValueError(f"找不到帳號 @{username}，可能是私人帳號或不存在。")

    # De-duplicate posts by external_id
    seen: set[str] = set()
    unique_posts: list[dict] = []
    for p in posts:
        key = p.get("external_id", "")
        if key and key not in seen:
            seen.add(key)
            unique_posts.append(p)

    pic_url: str = profile_data.pop("profile_pic_url", "") or ""
    local_pic = await _download_avatar(pic_url, username)
    profile_data["profile_pic_local"] = local_pic

    return {"profile": profile_data, "posts": unique_posts}
