from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timezone
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

COMMON_SCHOOL_ABBREVIATIONS = {
    "mcu": "銘傳大學",
    "nttu": "國立臺東大學",
    "ntu": "國立臺灣大學",
    "nccu": "國立政治大學",
    "nthu": "國立清華大學",
    "nycu": "國立陽明交通大學",
    "ncku": "國立成功大學",
    "nsysu": "國立中山大學",
    "fju": "輔仁大學",
    "tku": "淡江大學",
    "scu": "東吳大學",
    "thu": "東海大學",
    "cgu": "長庚大學",
    "cmu": "中國醫藥大學",
}

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


def _infer_birthday_from_digits(digits: str) -> str | None:
    if len(digits) == 6:
        year = 1911 + int(digits[:2])
        month = int(digits[2:4])
        day = int(digits[4:6])
    elif len(digits) == 8:
        year = int(digits[:4])
        month = int(digits[4:6])
        day = int(digits[6:8])
    else:
        return None

    try:
        inferred = date(year, month, day)
    except ValueError:
        return None

    if inferred > date.today() or inferred.year < 1970:
        return None

    return inferred.isoformat()


def _collect_derived_clues(username: str, sources: list[dict]) -> list[str]:
    pool = [username]
    for source in sources:
        profile = source["profile"]
        pool.extend([profile.get("username", ""), profile.get("bio", ""), profile.get("full_name", "")])

    lower_pool = " ".join(pool).lower()
    clues: list[str] = []

    digit_matches = re.findall(r"(?<!\d)(\d{6}|\d{8})(?!\d)", lower_pool)
    for digits in digit_matches[:3]:
        iso = _infer_birthday_from_digits(digits)
        if iso:
            clues.append(
                f"發現數字片段 {digits}，看起來像生日。若無衝突，可推測為 {iso}，"
                "並進一步推算年齡與星座。"
            )

    for abbr, school_name in COMMON_SCHOOL_ABBREVIATIONS.items():
        if re.search(rf"(?<![a-z]){abbr}(?![a-z])", lower_pool):
            clues.append(f"發現常見學校縮寫 {abbr.upper()}，可能對應 {school_name}。")

    return clues


def _build_messages(username: str, scraped_sources: list[dict]) -> list[dict[str, str]]:
    serialized_sources = _serialize_sources(scraped_sources)
    derived_clues = _collect_derived_clues(username, scraped_sources)

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
8. chat_topics 請給可以直接拿來聊天的主題，不要太空泛。
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
        "derived_clues": derived_clues,
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


def _build_json_object_messages(username: str, scraped_sources: list[dict]) -> list[dict[str, str]]:
    messages = _build_messages(username, scraped_sources)
    messages[-1]["content"] += (
        "\n請只輸出單一 JSON object，不要加上 markdown code fence。"
        "\n再次確認：所有頂層欄位與 inferred_facts 底下六個欄位都必須存在，"
        "不確定就填 null 與 confidence=\"none\"。"
    )
    return messages


def _compute_age(iso_date: str) -> str | None:
    try:
        birth = datetime.strptime(iso_date, "%Y-%m-%d").date()
    except ValueError:
        return None

    today = datetime.now(timezone.utc).date()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    if age < 0 or age > 100:
        return None
    return str(age)


def _compute_zodiac(iso_date: str) -> str | None:
    try:
        birth = datetime.strptime(iso_date, "%Y-%m-%d").date()
    except ValueError:
        return None

    month_day = (birth.month, birth.day)
    zodiac_ranges = [
        ((1, 20), "摩羯座"),
        ((2, 19), "水瓶座"),
        ((3, 21), "雙魚座"),
        ((4, 20), "牡羊座"),
        ((5, 21), "金牛座"),
        ((6, 22), "雙子座"),
        ((7, 23), "巨蟹座"),
        ((8, 23), "獅子座"),
        ((9, 23), "處女座"),
        ((10, 24), "天秤座"),
        ((11, 23), "天蠍座"),
        ((12, 22), "射手座"),
        ((12, 32), "摩羯座"),
    ]
    for boundary, zodiac in zodiac_ranges:
        if month_day < boundary:
            return zodiac
    return "摩羯座"


def _backfill_inferred_facts(result: dict[str, Any]) -> dict[str, Any]:
    facts = result.get("inferred_facts", {})
    facts.setdefault("age", _default_fact())
    facts.setdefault("birthday", _default_birthday_fact())
    facts.setdefault("height", _default_fact())
    facts.setdefault("location", _default_fact())
    facts.setdefault("school_or_company", _default_fact())
    facts.setdefault("zodiac", _default_fact())
    birthday = facts.get("birthday") or {}
    iso_date = birthday.get("iso_date") or None

    if not iso_date and birthday.get("value"):
        digits = re.sub(r"\D", "", birthday["value"])
        if len(digits) in {6, 8}:
            iso_date = _infer_birthday_from_digits(digits)
            if iso_date:
                birthday["iso_date"] = iso_date
    if iso_date:
        birthday.setdefault("confidence", "low")
        if not facts.get("age", {}).get("value"):
            age = _compute_age(iso_date)
            if age:
                facts["age"]["value"] = age
                facts["age"]["evidence"] = facts["age"].get("evidence") or "依生日推算"
                if CONFIDENCE_ORDER.get(facts["age"].get("confidence", "none"), 0) < CONFIDENCE_ORDER["low"]:
                    facts["age"]["confidence"] = "low"
        if not facts.get("zodiac", {}).get("value"):
            zodiac = _compute_zodiac(iso_date)
            if zodiac:
                facts["zodiac"]["value"] = zodiac
                facts["zodiac"]["evidence"] = facts["zodiac"].get("evidence") or "依生日推算"
                if CONFIDENCE_ORDER.get(facts["zodiac"].get("confidence", "none"), 0) < CONFIDENCE_ORDER["low"]:
                    facts["zodiac"]["confidence"] = "low"

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
    return _backfill_inferred_facts(normalized)


async def analyze_social_profile(username: str, scraped_sources: list[dict]) -> dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("尚未設定 GROQ_API_KEY，無法進行 AI 分析。")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=90) as client:
        strict_response = await client.post(
            f"{GROQ_BASE_URL}/chat/completions",
            headers=headers,
            json=_build_payload(
                _build_messages(username, scraped_sources),
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
            return _parse_analysis_json(_extract_message_content(strict_data or {}), "Groq")

        error_detail = strict_data if strict_data is not None else strict_response.text
        error_payload = (strict_data or {}).get("error") if isinstance(strict_data, dict) else {}

        if error_payload.get("code") == "json_validate_failed":
            failed_generation = error_payload.get("failed_generation")
            if failed_generation:
                try:
                    return _parse_analysis_json(failed_generation, "Groq failed_generation")
                except RuntimeError:
                    pass

            fallback_response = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers=headers,
                json=_build_payload(
                    _build_json_object_messages(username, scraped_sources),
                    {"type": "json_object"},
                ),
            )
            if fallback_response.status_code >= 400:
                try:
                    fallback_detail = fallback_response.json()
                except Exception:
                    fallback_detail = fallback_response.text
                raise RuntimeError(f"Groq 分析失敗：{fallback_detail}")

            try:
                fallback_data = fallback_response.json()
            except Exception:
                raise RuntimeError("Groq fallback 沒有回傳可解析的 JSON。")
            return _parse_analysis_json(_extract_message_content(fallback_data), "Groq fallback")

        raise RuntimeError(f"Groq 分析失敗：{error_detail}")
