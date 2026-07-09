import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dateutil import parser as date_parser

try:
    from backend.database import (
        delete_interaction,
        get_interaction,
        insert_interaction,
        list_interactions,
        update_interaction,
    )
except ImportError:  # pragma: no cover
    from database import delete_interaction, get_interaction, insert_interaction, list_interactions, update_interaction

try:
    from langchain_groq import ChatGroq
except ImportError:  # pragma: no cover
    ChatGroq = None


EXPECTED_FIELDS = {
    "hcpName": "",
    "interactionType": "",
    "date": "",
    "time": "",
    "attendees": [],
    "topicsDiscussed": "",
    "voiceNoteSummary": False,
    "materialsShared": [],
    "samplesDistributed": [],
    "hcpSentiment": "",
    "outcomes": "",
    "followUpActions": "",
    "aiSuggestedFollowUps": [],
}

INTERACTION_TYPES = {"Meeting", "Call", "Email", "Virtual Meeting"}
SENTIMENTS = {"Positive", "Neutral", "Negative"}


def get_reference_now() -> datetime:
    timezone_name = os.getenv("APP_TIMEZONE", "Asia/Kolkata")
    try:
        return datetime.now(ZoneInfo(timezone_name))
    except ZoneInfoNotFoundError:
        return datetime.now()


def get_groq_model():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or ChatGroq is None:
        raise ValueError("GROQ_API_KEY is missing or ChatGroq is not available.")
    return ChatGroq(model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), api_key=api_key, temperature=0)


def parse_relative_day(value: str) -> str:
    lowered = value.lower()
    now = get_reference_now()

    if re.search(r"\byesterday\b", lowered):
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    if re.search(r"\btoday\b", lowered):
        return now.strftime("%Y-%m-%d")
    if re.search(r"\btomorrow\b", lowered):
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    return ""


def normalize_date(value: str) -> str:
    if not value:
        return ""

    relative_day = parse_relative_day(value)
    if relative_day:
        return relative_day

    relative_weekday = parse_relative_weekday(value)
    if relative_weekday:
        return relative_weekday

    try:
        return date_parser.parse(value, fuzzy=True).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return ""


def normalize_time(value: str) -> str:
    if not value:
        return ""
    try:
        return date_parser.parse(value, fuzzy=True).strftime("%H:%M")
    except (ValueError, TypeError, OverflowError):
        return ""


def parse_relative_weekday(value: str) -> str:
    match = re.search(
        r"\b(this|next|last)\s+"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        value,
        re.IGNORECASE,
    )
    if not match:
        return ""

    modifier = match.group(1).lower()
    weekday_name = match.group(2).lower()
    weekday_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    today = get_reference_now()
    current_weekday = today.weekday()
    target_weekday = weekday_map[weekday_name]

    if modifier == "this":
        start_of_week = today - timedelta(days=current_weekday)
        target_date = start_of_week + timedelta(days=target_weekday)
    elif modifier == "next":
        days_ahead = (target_weekday - current_weekday) % 7
        days_ahead = 7 if days_ahead == 0 else days_ahead
        target_date = today + timedelta(days=days_ahead)
    else:
        days_back = (current_weekday - target_weekday) % 7
        days_back = 7 if days_back == 0 else days_back
        target_date = today - timedelta(days=days_back)

    return target_date.strftime("%Y-%m-%d")


def parse_iso_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


def normalize_hcp_name(value: str) -> str:
    if not value:
        return ""
    cleaned = re.sub(r"\s+", " ", value).strip()
    cleaned = re.sub(r"^(doctor|dr\.?)\s+", "Dr ", cleaned, flags=re.IGNORECASE)
    parts = []
    for part in cleaned.split():
        if part.lower() == "dr":
            parts.append("Dr")
        else:
            parts.append(part.capitalize())
    res = " ".join(parts)
    if not res.lower().startswith("dr "):
        res = "Dr " + res
    return res


def normalize_person_name(title: str, name: str) -> str:
    normalized_name = " ".join(part.capitalize() for part in name.split() if part)
    normalized_title = title.strip().lower().rstrip(".")

    if normalized_title in {"dr", "doctor"}:
        return normalize_hcp_name(f"Dr {normalized_name}")
    if normalized_title == "mr":
        return f"Mr {normalized_name}"
    if normalized_title == "mrs":
        return f"Mrs {normalized_name}"
    if normalized_title == "ms":
        return f"Ms {normalized_name}"
    return f"{normalized_title.capitalize()} {normalized_name}".strip()


def normalize_plain_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split() if part).strip()


def extract_people(text: str) -> list[str]:
    matches = re.finditer(
        r"\b(dr\.?|doctor|nurse|mr\.?|mrs\.?|ms\.?)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
        text,
        re.IGNORECASE,
    )
    stopwords = {
        "this", "next", "last", "i", "and", "at", "on", "by", "with",
        "today", "yesterday", "tomorrow", "regarding", "about",
        "discussed", "shared", "called", "met", "attended", "present",
        "meeting", "call", "visit",
    }
    people = []
    seen = set()
    for match in matches:
        title = match.group(1)
        tokens = re.findall(r"[a-zA-Z]+", match.group(2))
        name_parts = []
        for token in tokens:
            if token.lower() in stopwords:
                break
            name_parts.append(token)
            if len(name_parts) == 2:
                break
        if not name_parts:
            continue
        person = normalize_person_name(title, " ".join(name_parts))
        key = person.lower()
        if key not in seen:
            people.append(person)
            seen.add(key)
    return people


def extract_attendee_mentions(text: str, current_state: dict[str, Any]) -> list[str]:
    attendees = extract_people(text)
    current_hcp = current_state.get("hcpName", "").strip().lower()
    filtered = [person for person in attendees if person.strip().lower() != current_hcp]
    if filtered:
        return filtered

    bare_name_match = re.search(
        r"\b(also|add|include|and)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+"
        r"(attended|was present|present|joined|came)\b",
        text,
        re.IGNORECASE,
    )
    if bare_name_match:
        plain_name = normalize_plain_name(bare_name_match.group(2))
        if plain_name and plain_name.lower() != current_hcp:
            return [plain_name]
    return []


def to_list(val: Any) -> list[str]:
    if isinstance(val, list):
        return [str(v).strip() for v in val if str(v).strip()]
    if not val:
        return []
    if isinstance(val, str):
        return [item.strip() for item in re.split(r",|;|\band\b", val, flags=re.IGNORECASE) if item.strip()]
    return [str(val).strip()]


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = EXPECTED_FIELDS.copy()
    
    # Map old keys if present for backward compatibility
    legacy_mappings = {
        "hcp_name": "hcpName",
        "interaction_type": "interactionType",
        "topics": "topicsDiscussed",
        "materials": "materialsShared",
        "sentiment": "hcpSentiment",
        "follow_up_actions": "followUpActions",
    }
    for old, new in legacy_mappings.items():
        if old in payload and new not in payload:
            payload[new] = payload[old]

    normalized["hcpName"] = normalize_hcp_name(payload.get("hcpName", ""))
    normalized["interactionType"] = str(payload.get("interactionType", "")).strip()
    if normalized["interactionType"] not in INTERACTION_TYPES:
        normalized["interactionType"] = ""
    normalized["date"] = normalize_date(payload.get("date", ""))
    normalized["time"] = normalize_time(payload.get("time", ""))
    normalized["attendees"] = to_list(payload.get("attendees", []))
    normalized["topicsDiscussed"] = str(payload.get("topicsDiscussed", "")).strip()
    normalized["voiceNoteSummary"] = bool(payload.get("voiceNoteSummary", False))
    normalized["materialsShared"] = to_list(payload.get("materialsShared", []))
    normalized["samplesDistributed"] = to_list(payload.get("samplesDistributed", []))
    normalized["hcpSentiment"] = str(payload.get("hcpSentiment", "")).strip()
    if normalized["hcpSentiment"] not in SENTIMENTS:
        normalized["hcpSentiment"] = ""
    normalized["outcomes"] = str(payload.get("outcomes", "")).strip()
    normalized["followUpActions"] = str(payload.get("followUpActions", "")).strip()
    normalized["aiSuggestedFollowUps"] = to_list(payload.get("aiSuggestedFollowUps", []))
    return normalized


def normalize_text_for_match(value: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", value.lower()).strip()


def similarity_score(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, normalize_text_for_match(left), normalize_text_for_match(right)).ratio()


def topic_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    left_tokens = {t for t in normalize_text_for_match(left).split() if t}
    right_tokens = {t for t in normalize_text_for_match(right).split() if t}
    if not left_tokens or not right_tokens:
        return similarity_score(left, right)
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    overlap = intersection / union if union else 0.0
    return max(overlap, similarity_score(left, right))


def time_difference_minutes(left: str, right: str) -> int | None:
    if not left or not right:
        return None
    try:
        left_time = date_parser.parse(left)
        right_time = date_parser.parse(right)
    except (ValueError, TypeError, OverflowError):
        return None
    return abs(int((left_time - right_time).total_seconds() // 60))


def heuristic_duplicate_check(new_entry: dict[str, Any], existing_entries: list[dict[str, Any]]) -> dict[str, Any]:
    best_index = None
    best_score = -1
    best_reason = "No close interaction found."

    for index, entry in enumerate(existing_entries):
        normalized_existing = normalize_payload(entry)
        score = 0
        reasons = []
        hcp_similarity = similarity_score(new_entry["hcpName"], normalized_existing["hcpName"])
        if hcp_similarity >= 0.9:
            score += 40
            reasons.append("doctor name is almost identical")
        elif hcp_similarity >= 0.75:
            score += 30
            reasons.append("doctor name is similar")

        if new_entry["date"] and normalized_existing["date"] and new_entry["date"] == normalized_existing["date"]:
            score += 25
            reasons.append("interaction date matches")

        minutes_apart = time_difference_minutes(new_entry["time"], normalized_existing["time"])
        if minutes_apart is not None:
            if minutes_apart <= 10:
                score += 20
                reasons.append("interaction time is very close")
            elif minutes_apart <= 30:
                score += 15
                reasons.append("interaction time is somewhat close")

        topics_score = topic_similarity(new_entry["topicsDiscussed"], normalized_existing["topicsDiscussed"])
        if topics_score >= 0.65:
            score += 15
            reasons.append("topics are similar")
        elif topics_score >= 0.4:
            score += 8
            reasons.append("topics overlap")

        if score > best_score:
            best_score = score
            best_index = index
            best_reason = ", ".join(reasons) if reasons else "No close interaction found."

    if best_index is None:
        return {"is_duplicate": False, "confidence": 0, "matched_record": None, "reason": "No saved interactions found."}

    matched_record = normalize_payload(existing_entries[best_index])
    matched_record["id"] = existing_entries[best_index].get("id")
    confidence = max(0, min(100, best_score))
    name_anchor = similarity_score(new_entry["hcpName"], matched_record["hcpName"]) >= 0.75
    date_anchor = bool(new_entry["date"] and matched_record["date"] and new_entry["date"] == matched_record["date"])
    topics_anchor = topic_similarity(new_entry["topicsDiscussed"], matched_record["topicsDiscussed"]) >= 0.4
    time_anchor = (
        (time_difference_minutes(new_entry["time"], matched_record["time"]) or 10**9) <= 30
        if new_entry["time"] and matched_record["time"]
        else False
    )
    is_duplicate = name_anchor and date_anchor and (time_anchor or topics_anchor)
    if is_duplicate and confidence < 60:
        confidence = 60
    return {
        "is_duplicate": is_duplicate,
        "confidence": confidence,
        "matched_record": matched_record if is_duplicate else None,
        "reason": best_reason,
    }


def combine_field_values(existing_value: str, new_value: str) -> str:
    existing_value = (existing_value or "").strip()
    new_value = (new_value or "").strip()
    if not existing_value:
        return new_value
    if not new_value:
        return existing_value
    if existing_value.lower() == new_value.lower():
        return existing_value
    return new_value if len(new_value) > len(existing_value) else existing_value


def combine_list_values(existing_list: list[str], new_list: list[str]) -> list[str]:
    combined = list(existing_list)
    seen = {item.lower() for item in combined}
    for item in new_list:
        if item.lower() not in seen:
            combined.append(item)
            seen.add(item.lower())
    return combined


def determine_follow_up_date(meeting_date: str, sentiment: str) -> str:
    parsed_meeting_date = parse_iso_date(meeting_date)
    if not parsed_meeting_date:
        return ""

    days_by_sentiment = {
        "positive": 2,
        "neutral": 4,
        "negative": 1,
    }
    days_to_add = days_by_sentiment.get((sentiment or "").strip().lower(), 2)
    follow_up_date = parsed_meeting_date + timedelta(days=days_to_add)
    return follow_up_date.strftime("%Y-%m-%d")


def heuristic_merge_records(existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    existing_payload = normalize_payload(existing)
    new_payload = normalize_payload(new)
    merged = {
        "id": existing.get("id"),
        "hcpName": existing_payload["hcpName"] or new_payload["hcpName"],
        "interactionType": new_payload["interactionType"] or existing_payload["interactionType"],
        "date": new_payload["date"] or existing_payload["date"],
        "time": max(existing_payload["time"], new_payload["time"]) if existing_payload["time"] and new_payload["time"] else existing_payload["time"] or new_payload["time"],
        "attendees": combine_list_values(existing_payload["attendees"], new_payload["attendees"]),
        "topicsDiscussed": combine_field_values(existing_payload["topicsDiscussed"], new_payload["topicsDiscussed"]),
        "voiceNoteSummary": existing_payload["voiceNoteSummary"] or new_payload["voiceNoteSummary"],
        "materialsShared": combine_list_values(existing_payload["materialsShared"], new_payload["materialsShared"]),
        "samplesDistributed": combine_list_values(existing_payload["samplesDistributed"], new_payload["samplesDistributed"]),
        "hcpSentiment": new_payload["hcpSentiment"] or existing_payload["hcpSentiment"],
        "outcomes": combine_field_values(existing_payload["outcomes"], new_payload["outcomes"]),
        "followUpActions": combine_field_values(existing_payload["followUpActions"], new_payload["followUpActions"]),
        "aiSuggestedFollowUps": combine_list_values(existing_payload["aiSuggestedFollowUps"], new_payload["aiSuggestedFollowUps"]),
    }
    return merged


def heuristic_follow_up(entry: dict[str, Any]) -> dict[str, Any]:
    topics = str(entry.get("topicsDiscussed", "") or "").strip()
    interaction_type = str(entry.get("interactionType", "") or "").strip()
    hcp_name = str(entry.get("hcpName", "") or "").strip()
    date = str(entry.get("date", "") or "").strip()
    time = str(entry.get("time", "") or "").strip()
    lowered = topics.lower()

    has_context = any([topics, interaction_type, hcp_name, date, time])
    if not has_context:
        return {
            "hcpSentiment": "",
            "outcomes": "",
            "followUpActions": "",
            "aiSuggestedFollowUps": [],
            "message": "Insufficient data to suggest follow-up.",
        }

    detected_sentiment = ""
    sentiment = "Neutral"
    if any(token in lowered for token in ["positive", "interested", "good", "strong", "supportive"]):
        sentiment = "Positive"
        detected_sentiment = sentiment
    elif any(token in lowered for token in ["concern", "risk", "issue", "negative", "problem"]):
        sentiment = "Negative"
        detected_sentiment = sentiment

    follow_up_steps = [
        "Send a follow-up summary and confirm next steps.",
        "Schedule the next touchpoint and confirm availability.",
    ]
    outcomes = "Follow-up pending."
    if "pricing" in lowered:
        follow_up_steps = [
            "Share a pricing summary tailored to the discussion.",
            "Confirm any budget questions or approval blockers.",
            "Schedule a short follow-up call to review pricing options.",
        ]
        outcomes = "Pricing discussion captured."
    elif "efficacy" in lowered or "clinical" in lowered:
        follow_up_steps = [
            "Send the most relevant clinical evidence discussed.",
            "Offer a scientific follow-up meeting for deeper review.",
            "Capture any unanswered efficacy questions for the next call.",
        ]
        outcomes = "Clinical discussion captured."
    elif topics:
        follow_up_steps = [
            f"Send a recap covering {topics}.",
            "Confirm whether any supporting material should be shared next.",
            "Set a follow-up check-in to continue the discussion.",
        ]
        outcomes = f"Discussed {topics}."

    follow_up_date = determine_follow_up_date(date, detected_sentiment or "Positive")
    scheduled_date_note = ""
    if follow_up_date:
        follow_up_steps = [
            f"Reach out on {follow_up_date} with a concise follow-up summary.",
            *follow_up_steps,
        ]
        outcomes = f"{outcomes.rstrip('.')} Follow-up planned for {follow_up_date}."
        scheduled_date_note = f" on {follow_up_date}"

    context_bits = [bit for bit in [hcp_name, interaction_type, date] if bit]
    context_line = f" for {', '.join(context_bits)}" if context_bits else ""
    if time:
        context_line = f"{context_line} at {time}" if context_line else f" at {time}"
    message = "\n".join(f"- {step}" for step in follow_up_steps[:3])

    if follow_up_date and follow_up_date == date:
        # avoid validation crash, adjust slightly
        follow_up_date = (parse_iso_date(date) + timedelta(days=1)).strftime("%Y-%m-%d")

    return {
        "hcpSentiment": sentiment,
        "outcomes": outcomes,
        "followUpActions": "; ".join(follow_up_steps[:3]),
        "aiSuggestedFollowUps": follow_up_steps[:3],
        "message": f"Suggested follow-up{context_line}{scheduled_date_note}:\n{message}",
    }


def llm_extract(text: str) -> dict[str, Any] | None:
    try:
        model = get_groq_model()
        system_prompt = (
            "Extract structured CRM interaction data from the input text. Return only valid JSON. "
            "If the user input contains ONLY a single name or word (e.g., 'RAM' or 'Sharma'), "
            "extract it directly into the 'hcpName' field and leave others blank/empty.\n"
            "JSON structure must use the following keys:\n"
            "- hcpName (string, e.g. Dr. Name)\n"
            "- interactionType (string, must be one of: 'Meeting', 'Call', 'Email', 'Virtual Meeting')\n"
            "- date (string, YYYY-MM-DD)\n"
            "- time (string, HH:MM)\n"
            "- attendees (JSON array of strings)\n"
            "- topicsDiscussed (string)\n"
            "- voiceNoteSummary (boolean)\n"
            "- materialsShared (JSON array of strings)\n"
            "- samplesDistributed (JSON array of strings)\n"
            "- hcpSentiment (string, must be one of: 'Positive', 'Neutral', 'Negative')\n"
            "- outcomes (string)\n"
            "- followUpActions (string)\n"
            "- aiSuggestedFollowUps (JSON array of strings)"
        )
        response = model.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ])
        content = getattr(response, "content", "") or "{}"
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            return parsed
        return None
    except Exception as e:
        print(f"Error in llm_extract: {e}")
        return None


def llm_edit(instruction: str, current_state: dict[str, Any]) -> dict[str, Any] | None:
    try:
        model = get_groq_model()
        system_prompt = (
            "You are an editor for a CRM interaction form. Apply the user's conversational instructions "
            "to modify the current state. Return only the updated state as a single JSON object. "
            "If the instruction contains ONLY a single name or word (e.g., 'RAM' or 'Sharma'), "
            "set the 'hcpName' field directly to this name, keeping other fields unchanged.\n"
            "Maintain existing values for fields that are not mentioned or modified. For array fields (attendees, materialsShared, samplesDistributed), "
            "if the instruction adds an item (e.g. 'Add Sarah as attendee'), append it to the existing array. "
            "If it removes an item (e.g. 'Remove sample X'), filter it out of the array.\n"
            "Form keys:\n"
            "- hcpName (string)\n"
            "- interactionType (string, must be 'Meeting', 'Call', 'Email', 'Virtual Meeting')\n"
            "- date (string, YYYY-MM-DD)\n"
            "- time (string, HH:MM)\n"
            "- attendees (array of strings)\n"
            "- topicsDiscussed (string)\n"
            "- voiceNoteSummary (boolean)\n"
            "- materialsShared (array of strings)\n"
            "- samplesDistributed (array of strings)\n"
            "- hcpSentiment (string, 'Positive', 'Neutral', 'Negative')\n"
            "- outcomes (string)\n"
            "- followUpActions (string)\n"
            "- aiSuggestedFollowUps (array of strings)\n"
        )
        response = model.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps({"current_state": current_state, "instruction": instruction})}
        ])
        content = getattr(response, "content", "") or "{}"
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            return parsed
        return None
    except Exception as e:
        print(f"Error in llm_edit: {e}")
        return None


def fallback_parse(text: str) -> dict[str, Any]:
    normalized = EXPECTED_FIELDS.copy()
    people = extract_people(text)
    if people:
        normalized["hcpName"] = people[0]
        additional_people = [person for person in people if person != normalized["hcpName"]]
        if additional_people:
            normalized["attendees"] = additional_people
    else:
        cleaned = text.strip()
        if cleaned and len(cleaned.split()) <= 2 and not any(k in cleaned.lower() for k in ["meeting", "call", "email", "validate", "change", "update", "add", "remove"]):
            normalized["hcpName"] = normalize_hcp_name(cleaned)

    lowered = text.lower()
    if "call" in lowered or "called" in lowered:
        normalized["interactionType"] = "Call"
    elif "email" in lowered:
        normalized["interactionType"] = "Email"
    elif "virtual" in lowered:
        normalized["interactionType"] = "Virtual Meeting"
    else:
        normalized["interactionType"] = "Meeting"

    relative_day = parse_relative_day(text)
    relative_weekday = parse_relative_weekday(text)
    if relative_day:
        normalized["date"] = relative_day
        normalized["time"] = normalize_time(text)
    elif relative_weekday:
        normalized["date"] = relative_weekday
        normalized["time"] = normalize_time(text)
    else:
        try:
            parsed = date_parser.parse(text, fuzzy=True)
            normalized["date"] = parsed.strftime("%Y-%m-%d")
            if re.search(r"\b\d{1,2}(:\d{2})?\s*(am|pm)\b", lowered) or re.search(r"\b\d{1,2}:\d{2}\b", lowered):
                normalized["time"] = parsed.strftime("%H:%M")
        except (ValueError, TypeError, OverflowError):
            pass

    return normalized


@dataclass
class LogInteractionTool:
    name: str = "LogInteractionTool"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        operation = payload.get("operation", "extract")
        if operation == "list":
            return {"entries": list_interactions()}

        if operation == "load":
            entry_id = payload.get("entry_id")
            if entry_id in (None, ""):
                raise ValueError("Entry ID is required.")
            entry = get_interaction(entry_id)
            if entry is None:
                raise ValueError("Saved interaction not found.")
            return {"entry": entry}

        if operation == "save":
            entry = normalize_payload(payload.get("entry", {}))
            saved_entry = insert_interaction(entry)
            return {"entry": saved_entry, "entries": list_interactions()}

        if operation == "update":
            entry_id = payload.get("entry_id")
            if entry_id in (None, ""):
                raise ValueError("Entry ID is required.")
            entry = normalize_payload(payload.get("entry", {}))
            updated_entry = update_interaction(entry_id, entry)
            return {"entry": updated_entry, "entries": list_interactions()}

        if operation == "delete":
            entry_id = payload.get("entry_id")
            if entry_id in (None, ""):
                raise ValueError("Entry ID is required.")
            was_deleted = delete_interaction(entry_id)
            if not was_deleted:
                raise ValueError("Saved interaction not found.")
            return {"deleted": True, "entries": list_interactions()}

        text = str(payload.get("text", "") or "")
        extracted = llm_extract(text)
        if extracted is None:
            extracted = fallback_parse(text)
        return {"form_data": normalize_payload(extracted)}


@dataclass
class EditInteractionTool:
    name: str = "EditInteractionTool"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        instruction = str(payload.get("instruction", "") or "")
        current_state = normalize_payload(payload.get("current_state", {}) or {})
        extracted = llm_edit(instruction, current_state)
        if extracted is None:
            # Fallback edit
            extracted = current_state
        return {"form_data": normalize_payload(extracted)}


@dataclass
class VoiceAssistantTool:
    name: str = "VoiceAssistantTool"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        voice_text = str(payload.get("voice_text", "") or "")
        current_state = normalize_payload(payload.get("current_state", {}) or {})
        
        extracted = llm_edit(voice_text, current_state)
        if extracted is None:
            extracted = llm_extract(voice_text)
            if extracted is not None:
                extracted = {**current_state, **extracted}
            else:
                extracted = current_state

        updated = normalize_payload(extracted)
        updated["voiceNoteSummary"] = True
        return {"form_data": updated, "message": "Voice note processed. Summarized from transcription (consent noted)."}


@dataclass
class ModificationTool:
    name: str = "ModificationTool"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        instruction = str(payload.get("instruction", "") or "")
        current_state = normalize_payload(payload.get("current_state", {}) or {})
        
        extracted = llm_edit(instruction, current_state)
        if extracted is None:
            extracted = current_state
            
        return {"form_data": normalize_payload(extracted), "message": "Conversational modification applied successfully."}


@dataclass
class InteractionValidationTool:
    name: str = "InteractionValidationTool"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        entry = normalize_payload(payload.get("entry", {}) or {})
        errors = []
        warnings = []
        
        if not entry.get("hcpName"):
            errors.append("HCP Name is a required field.")
        if not entry.get("interactionType"):
            errors.append("Interaction Type is a required field.")
        if not entry.get("date"):
            errors.append("Interaction Date is a required field.")
        if not entry.get("time"):
            errors.append("Interaction Time is a required field.")
            
        if entry.get("interactionType") and entry.get("interactionType") not in INTERACTION_TYPES:
            errors.append(f"Invalid interaction type. Must be one of: {', '.join(INTERACTION_TYPES)}")
            
        if entry.get("hcpSentiment") and entry.get("hcpSentiment") not in SENTIMENTS:
            errors.append(f"Invalid HCP sentiment. Must be one of: {', '.join(SENTIMENTS)}")
            
        if not entry.get("topicsDiscussed"):
            warnings.append("Topics discussed section is empty.")
        if not entry.get("outcomes"):
            warnings.append("Discussion outcomes are empty.")
        if not entry.get("followUpActions"):
            warnings.append("Follow-up actions are empty.")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


@dataclass
class DuplicateCheckTool:
    name: str = "DuplicateCheckTool"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        entry = normalize_payload(payload.get("entry", {}) or {})
        existing_entries = list_interactions()
        return heuristic_duplicate_check(entry, existing_entries)


@dataclass
class MergeInteractionTool:
    name: str = "MergeInteractionTool"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        existing_id = payload.get("existing_id")
        if existing_id in (None, ""):
            raise ValueError("Existing interaction ID is required.")
        existing = get_interaction(existing_id)
        if existing is None:
            raise ValueError("Existing interaction not found.")
        merged = heuristic_merge_records(existing, payload.get("new_entry", {}) or {})
        updated = update_interaction(existing_id, merged)
        return {"entry": updated, "entries": list_interactions()}


@dataclass
class FollowUpSuggestionTool:
    name: str = "FollowUpSuggestionTool"

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        entry = payload.get("entry", {}) or {}
        return heuristic_follow_up(entry)


def build_tool_registry() -> dict[str, Any]:
    tools = [
        LogInteractionTool(),
        EditInteractionTool(),
        VoiceAssistantTool(),
        ModificationTool(),
        InteractionValidationTool(),
        DuplicateCheckTool(),
        MergeInteractionTool(),
        FollowUpSuggestionTool(),
    ]
    return {tool.name: tool for tool in tools}
