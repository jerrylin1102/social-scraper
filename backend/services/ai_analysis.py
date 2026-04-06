from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_POSTS_FOR_ANALYSIS = 40
MAX_CHARS_PER_POST = 500
MIN_DATETIME = datetime.min.replace(tzinfo=timezone.utc)
CONFIDENCE_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}

ANALYSIS_SCHEMA: dict[str, Any] = {
    "name": "social_profile_analysis",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "personality": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "headline": {"type": "string"},
                    "summary": {"type": "string"},
                    "traits": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["headline", "summary", "traits"],
            },
            "interests": {
                "type": "array",
                "items": {"type": "string"},
            },
            "key_events": {
                "type": "array",
                "items": {"type": "string"},
            },
            "mbti": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string"},
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                    "reason": {"type": "string"},
                },
                "required": ["type", "confidence", "reason"],
            },
            "chat_topics": {
                "type": "array",
                "items": {"type": "string"},
            },
            "inferred_facts": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "age": {"$ref": "#/$defs/fact"},
                    "birthday": {"$ref": "#/$defs/birthday_fact"},
                    "height": {"$ref": "#/$defs/fact"},
                    "location": {"$ref": "#/$defs/fact"},
                    "school_or_company": {"$ref": "#/$defs/fact"},
                    "zodiac": {"$ref": "#/$defs/fact"},
                },
                "required": [
                    "age",
                    "birthday",
                    "height",
                    "location",
                    "school_or_company",
                    "zodiac",
                ],
            },
        },
        "required": [
            "personality",
            "interests",
            "key_events",
            "mbti",
            "chat_topics",
            "inferred_facts",
        ],
        "$defs": {
            "fact": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "value": {"type": ["string", "null"]},
                    "evidence": {"type": ["string", "null"]},
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low", "none"],
                    },
                },
                "required": ["value", "evidence", "confidence"],
            },
            "birthday_fact": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "value": {"type": ["string", "null"]},
                    "iso_date": {
                        "type": ["string", "null"],
                        "description": "生日請盡量用 YYYY-MM-DD",
                    },
                    "evidence": {"type": ["string", "null"]},
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low", "none"],
                    },
                },
                "required": ["value", "iso_date", "evidence", "confidence"],
            },
        },
    },
}


def _default_fact() -> dict[str, Any]:
    return {"value": None, "evidence": None, "confidence": "none"}


def _default_birthday_fact() -> dict[str, Any]:
    return {"value": None, "iso_date": None, "evidence": None, "confidence": "none"}


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        text = _clean_text(item)
        if text:
            cleaned.append(text)
    return cleaned


def _normalize_fact(value: Any) -> dict[str, Any]:
    fact = _default_fact()
    if not isinstance(value, dict):
        return fact

    fact["value"] = _clean_text(value.get("value"))
    fact["evidence"] = _clean_text(value.get("evidence"))
    confidence = str(value.get("confidence", "none")).lower()
    fact["confidence"] = confidence if confidence in CONFIDENCE_ORDER else "none"
    return fact


def _normalize_birthday_fact(value: Any) -> dict[str, Any]:
    fact = _default_birthday_fact()
    if not isinstance(value, dict):
        return fact

    fact["value"] = _clean_text(value.get("value"))
    fact["iso_date"] = _clean_text(value.get("iso_date"))
    fact["evidence"] = _clean_text(value.get("evidence"))
    confidence = str(value.get("confidence", "none")).lower()
    fact["confidence"] = confidence if confidence in CONFIDENCE_ORDER else "none"
    return fact


def _normalize_analysis_result(result: Any) -> dict[str, Any]:
    raw = result if isinstance(result, dict) else {}
    personality_raw = raw.get("personality") if isinstance(raw.get("personality"), dict) else {}
    mbti_raw = raw.get("mbti") if isinstance(raw.get("mbti"), dict) else {}
    facts_raw = raw.get("inferred_facts") if isinstance(raw.get("inferred_facts"), dict) else {}

    personality_headline = _clean_text(personality_raw.get("headline")) or "公開資料人格分析"
    personality_summary = _clean_text(personality_raw.get("summary")) or "根據公開資料整理出的性格與互動線索。"

    mbti_confidence = str(mbti_raw.get("confidence", "low")).lower()
    if mbti_confidence not in {"high", "medium", "low"}:
        mbti_confidence = "low"

    normalized = {
        "personality": {
            "headline": personality_headline,
            "summary": personality_summary,
            "traits": _clean_list(personality_raw.get("traits")),
        },
        "interests": _clean_list(raw.get("interests")),
        "key_events": _clean_list(raw.get("key_events")),
        "mbti": {
            "type": _clean_text(mbti_raw.get("type")) or "未明確",
            "confidence": mbti_confidence,
            "reason": _clean_text(mbti_raw.get("reason")) or "公開資料不足，僅能做低信心推測。",
        },
        "chat_topics": _clean_list(raw.get("chat_topics")),
        "inferred_facts": {
            "age": _normalize_fact(facts_raw.get("age")),
            "birthday": _normalize_birthday_fact(facts_raw.get("birthday")),
            "height": _normalize_fact(facts_raw.get("height")),
            "location": _normalize_fact(facts_raw.get("location")),
            "school_or_company": _normalize_fact(facts_raw.get("school_or_company")),
            "zodiac": _normalize_fact(facts_raw.get("zodiac")),
        },
    }
    return normalized


def _trim_text(text: str | None, limit: int = MAX_CHARS_PER_POST) -> str:
    return (text or "").strip().replace("\u0000", "")[:limit]


def _sort_posts(posts: list[dict]) -> list[dict]:
    return sorted(posts, key=lambda post: post.get("created_at") or MIN_DATETIME, reverse=True)


def _serialize_sources(scraped_sources: list[dict]) -> list[dict]:
    serialized: list[dict] = []
    seen_posts: set[str] = set()

    for source in scraped_sources:
        profile = source["profile"]
        selected_posts: list[dict] = []
        for post in _sort_posts(source["posts"]):
            text = _trim_text(post.get("text"))
            if not text:
                continue

            dedupe_key = text.lower()
            if dedupe_key in seen_posts:
                continue
            seen_posts.add(dedupe_key)

            selected_posts.append(
                {
                    "created_at": post.get("created_at").isoformat() if post.get("created_at") else None,
                    "text": text,
                    "like_count": post.get("like_count", 0),
                    "reply_count": post.get("reply_count", 0),
                    "repost_count": post.get("repost_count", 0),
                    "post_url": post.get("post_url"),
                }
            )
            if len(selected_posts) >= MAX_POSTS_FOR_ANALYSIS:
                break

        serialized.append(
            {
                "platform": profile["platform"],
                "username": profile["username"],
                "full_name": profile.get("full_name") or None,
                "bio": profile.get("bio") or None,
                "website": profile.get("website") or None,
                "followers_count": profile.get("followers_count", 0),
                "following_count": profile.get("following_count", 0),
                "posts_count": profile.get("posts_count", 0),
                "is_verified": bool(profile.get("is_verified")),
                "posts": selected_posts,
            }
        )

    return serialized


def _build_initial_messages(username: str, scraped_sources: list[dict]) -> list[dict[str, str]]:
    serialized_sources = _serialize_sources(scraped_sources)

    instructions = """
你是一位給社群用戶使用的平台分析助手。請根據提供的公開個人資料與貼文內容，用繁體中文做簡潔、可讀性高的使用者分析。

規則：
1. 一定要分析：個性、興趣、重要事件或活動、MBTI、適合聊天的話題。
2. 若有線索，請推測並填寫：年齡、生日、身高、居住區域、學校或公司、星座。
3. 某些資訊即使沒有明講，只要線索很明顯也可以推測，例如帳號中的生日數字、常見學校英文縮寫、工作或地區關鍵字。
4. 不能胡亂編造；若線索不足就回傳 null，confidence 請填 none。
5. MBTI 一定要給最佳推測，並清楚說明原因與信心。
6. personality.headline 請短一點，適合做結果頁標題。
7. key_events 請只放明顯出現過的重要事、活動、旅行、比賽、合作、畢業、工作變動等；若不足可回空陣列。
8. chat_topics 請給 3 到 6 個可以直接拿來聊天的主題，只要資料中存在可聊線索，就不要留空。
9. birthday.value 可保留原始推測寫法，例如 92/11/02；birthday.iso_date 盡量轉成西元 YYYY-MM-DD。
10. 若已知生日，就應盡量補上年齡與星座。
11. inferred_facts 一定要包含 age、birthday、height、location、school_or_company、zodiac 六個欄位。
12. 若無法判斷某個 fact，仍然要輸出該欄位，格式如下：
    - 一般 fact: {"value": null, "evidence": null, "confidence": "none"}
    - birthday: {"value": null, "iso_date": null, "evidence": null, "confidence": "none"}
""".strip()

    payload = {
        "target_username": username,
        "today": datetime.now(timezone.utc).date().isoformat(),
        "sources": serialized_sources,
    }

    return [
        {"role": "system", "content": instructions},
        {
            "role": "user",
            "content": (
                "以下是公開社群資料，請依照指定 JSON schema 產出分析結果。\n"
                f"{json.dumps(payload, ensure_ascii=False)}"
            ),
        },
    ]


def _build_review_messages(
    username: str,
    scraped_sources: list[dict],
    draft_analysis_text: str,
) -> list[dict[str, str]]:
    serialized_sources = _serialize_sources(scraped_sources)

    instructions = """
你現在要複核並修正一份社群人物分析草稿。請以原始公開資料為唯一依據，重新產出最終版本。

規則：
1. 只能保留原始資料支持的內容，不要補寫沒有依據的敘述。
2. 如果草稿遺漏了原始資料中已經很明顯的線索，請補上。
3. chat_topics 只要原始資料裡存在興趣、事件、生活風格、喜歡的事物，就應該整理出 3 到 6 個自然、具體、可直接開聊的主題。
4. inferred_facts 六個欄位都必須存在；若無法判斷就填 null 與 confidence="none"。
5. birthday、age、zodiac、school_or_company、location 等欄位，只有在原始資料能支持時才可填入。
6. key_events 只保留明確發生過的重要事或活動，不要塞太泛的描述。
7. 回傳內容必須符合指定 JSON schema。
""".strip()

    payload = {
        "target_username": username,
        "today": datetime.now(timezone.utc).date().isoformat(),
        "sources": serialized_sources,
        "draft_analysis": draft_analysis_text,
    }

    return [
        {"role": "system", "content": instructions},
        {
            "role": "user",
            "content": (
                "以下是原始公開資料與先前草稿，請重新輸出最終 JSON。\n"
                f"{json.dumps(payload, ensure_ascii=False)}"
            ),
        },
    ]


def _finalize_analysis_result(result: dict[str, Any]) -> dict[str, Any]:
    facts = result.get("inferred_facts", {})
    facts.setdefault("age", _default_fact())
    facts.setdefault("birthday", _default_birthday_fact())
    facts.setdefault("height", _default_fact())
    facts.setdefault("location", _default_fact())
    facts.setdefault("school_or_company", _default_fact())
    facts.setdefault("zodiac", _default_fact())

    result["inferred_facts"] = facts
    return result


def _build_payload(messages: list[dict[str, str]], response_format: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": GROQ_MODEL,
        "temperature": 0.2,
        "max_completion_tokens": 1400,
        "response_format": response_format,
        "messages": messages,
    }


def _extract_message_content(data: dict[str, Any]) -> str:
    content = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
    if isinstance(content, list):
        text_chunks = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_chunks.append(item.get("text", ""))
        return "".join(text_chunks).strip()
    return str(content).strip()


def _parse_analysis_json(raw_text: str, source: str) -> dict[str, Any]:
    if not raw_text:
        raise RuntimeError(f"{source} 沒有回傳分析內容。")

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{source} 回傳格式無法解析：{exc}") from exc

    normalized = _normalize_analysis_result(parsed)
    return _finalize_analysis_result(normalized)


async def analyze_social_profile(username: str, scraped_sources: list[dict]) -> dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("尚未設定 GROQ_API_KEY，無法進行 AI 分析。")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    initial_result: dict[str, Any] | None = None
    draft_text: str | None = None

    async with httpx.AsyncClient(timeout=90) as client:
        strict_response = await client.post(
            f"{GROQ_BASE_URL}/chat/completions",
            headers=headers,
            json=_build_payload(
                _build_initial_messages(username, scraped_sources),
                {
                    "type": "json_schema",
                    "json_schema": {
                        "name": ANALYSIS_SCHEMA["name"],
                        "schema": ANALYSIS_SCHEMA["schema"],
                        "strict": True,
                    },
                },
            ),
        )

        try:
            strict_data = strict_response.json()
        except Exception:
            strict_data = None

        if strict_response.status_code < 400:
            draft_text = _extract_message_content(strict_data or {})
            initial_result = _parse_analysis_json(draft_text, "Groq")
        else:
            error_detail = strict_data if strict_data is not None else strict_response.text
            error_payload = (strict_data or {}).get("error") if isinstance(strict_data, dict) else {}

            if error_payload.get("code") == "json_validate_failed":
                draft_text = error_payload.get("failed_generation")
                if draft_text:
                    initial_result = _parse_analysis_json(draft_text, "Groq failed_generation")
                else:
                    raise RuntimeError(f"Groq 分析失敗：{error_detail}")
            else:
                raise RuntimeError(f"Groq 分析失敗：{error_detail}")

        review_response = await client.post(
            f"{GROQ_BASE_URL}/chat/completions",
            headers=headers,
            json=_build_payload(
                _build_review_messages(username, scraped_sources, draft_text or ""),
                {
                    "type": "json_schema",
                    "json_schema": {
                        "name": ANALYSIS_SCHEMA["name"],
                        "schema": ANALYSIS_SCHEMA["schema"],
                        "strict": True,
                    },
                },
            ),
        )

        try:
            review_data = review_response.json()
        except Exception:
            review_data = None

        if review_response.status_code < 400:
            return _parse_analysis_json(_extract_message_content(review_data or {}), "Groq review")

        review_detail = review_data if review_data is not None else review_response.text
        review_error_payload = (review_data or {}).get("error") if isinstance(review_data, dict) else {}

        if review_error_payload.get("code") == "json_validate_failed":
            failed_generation = review_error_payload.get("failed_generation")
            if failed_generation:
                return _parse_analysis_json(failed_generation, "Groq review failed_generation")

        if initial_result is not None:
            return initial_result

        raise RuntimeError(f"Groq 分析失敗：{review_detail}")
