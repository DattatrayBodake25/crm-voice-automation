"""
NLU module for Voice-Style Bot Service:
Handles intent classification, entity extraction, and optional LLM-based fallback
for unrecognized transcripts. Supports LEAD_CREATE, VISIT_SCHEDULE, LEAD_UPDATE intents.
"""

#imports
import re
import json
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
import dateparser
from openai import OpenAI
from bot import settings
from bot.settings import logger


# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# Constants
INTENT_KEYWORDS = {
    "LEAD_CREATE": ["add", "create", "new lead"],
    "VISIT_SCHEDULE": ["schedule", "fix", "visit"],
    "LEAD_UPDATE": ["update", "mark"]
}

PHONE_REGEX = r"(\+91[\-\s]?)?\d{10}"
UUID_REGEX = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"

CITIES = ["Mumbai", "Delhi", "Gurgaon", "Bangalore", "Chennai", "Kolkata", "Pune"]
STATUS_OPTIONS = ["NEW", "IN_PROGRESS", "FOLLOW_UP", "WON", "LOST"]


# Intent Classification
def classify_intent(transcript: str) -> Tuple[str, float]:
    """
    Classify the transcript into an intent based on keyword matches.
    Args:
        transcript (str): User input text.
    Returns:
        Tuple[str, float]: Detected intent and confidence score (0-1).
    """
    transcript_lower = transcript.lower()
    best_intent = "UNKNOWN"
    best_conf = 0.3  # default low confidence

    for intent, keywords in INTENT_KEYWORDS.items():
        matches = sum(1 for k in keywords if k in transcript_lower)
        if matches > 0:
            conf = min(1.0, 0.5 + 0.2 * matches)
            if conf > best_conf:
                best_conf = conf
                best_intent = intent

    return best_intent, best_conf


# Casual datetime parsing
def parse_casual_datetime(text: str) -> Optional[str]:
    """
    Parse casual date/time expressions like 'tomorrow 5pm'.
    Args:
        text (str): Text containing date/time reference.
    Returns:
        Optional[str]: ISO formatted datetime if recognized, else None.
    """
    text_lower = text.lower()
    now = datetime.now()

    if "tomorrow" in text_lower:
        dt = now + timedelta(days=1)
        time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            if time_match.group(3) == "pm" and hour < 12:
                hour += 12
            dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return dt.isoformat()

    if "day after tomorrow" in text_lower:
        dt = now + timedelta(days=2)
        return dt.isoformat()

    return None


# Entity Extraction
def extract_entities(transcript: str, intent: str) -> Tuple[Dict[str, Optional[str]], Optional[Dict]]:
    """
    Extract entities from transcript based on intent.
    Args:
        transcript (str): User input text.
        intent (str): Detected intent.
    Returns:
        Tuple[Dict[str, Optional[str]], Optional[Dict]]: Extracted entities and error info.
    """
    entities: Dict[str, Optional[str]] = {
        "name": None,
        "phone": None,
        "city": None,
        "lead_id": None,
        "visit_time": None,
        "status": None,
        "source": None,
        "notes": None
    }
    error_fields = []

    # Extract phone
    phone_match = re.search(PHONE_REGEX, transcript)
    if phone_match:
        entities["phone"] = phone_match.group()
    elif intent == "LEAD_CREATE":
        error_fields.append("phone")

    # Extract lead_id
    lead_id_match = re.search(UUID_REGEX, transcript)
    if lead_id_match:
        entities["lead_id"] = lead_id_match.group()
    elif intent in ["VISIT_SCHEDULE", "LEAD_UPDATE"]:
        error_fields.append("lead_id")

    # VISIT_SCHEDULE: extract visit_time and notes
    if intent == "VISIT_SCHEDULE":
        time_match = re.search(r"at (.+?)(?:\.|$)", transcript, re.IGNORECASE)
        if time_match:
            dt_str = time_match.group(1).strip()
            dt = parse_casual_datetime(dt_str)
            if not dt:
                parsed = dateparser.parse(
                    dt_str,
                    settings={
                        "RETURN_AS_TIMEZONE_AWARE": True,
                        "PREFER_DATES_FROM": "future"
                    }
                )
                if parsed:
                    dt = parsed.isoformat()
            if dt:
                entities["visit_time"] = dt
            else:
                error_fields.append("visit_time")
        else:
            error_fields.append("visit_time")

        notes_match = re.search(r"notes[:\-]?\s*(.*)", transcript, re.IGNORECASE)
        if notes_match:
            entities["notes"] = notes_match.group(1).strip()

    # LEAD_UPDATE: extract status and notes
    if intent == "LEAD_UPDATE":
        for s in STATUS_OPTIONS:
            if s.lower() in transcript.lower():
                entities["status"] = s
                break
        if not entities["status"]:
            error_fields.append("status")

        notes_match = re.search(r"notes[:\-]?\s*(.*)", transcript, re.IGNORECASE)
        if notes_match:
            entities["notes"] = notes_match.group(1).strip()

    # LEAD_CREATE: extract name, city, source
    if intent == "LEAD_CREATE":
        name_match = re.search(r"(?:name\s)?([A-Z][a-z]+\s[A-Z][a-z]+)", transcript)
        if name_match:
            entities["name"] = name_match.group(1)
        else:
            error_fields.append("name")

        for city in CITIES:
            if city.lower() in transcript.lower():
                entities["city"] = city
                break
        else:
            error_fields.append("city")

        source_match = re.search(r"source\s+(\w+)", transcript, re.IGNORECASE)
        if source_match:
            entities["source"] = source_match.group(1)

    error = {"type": "VALIDATION_ERROR", "missing_fields": error_fields} if error_fields else None
    return entities, error


# LLM-based Extraction Fallback
def extract_with_llm(transcript: str) -> Dict:
    """
    Use OpenAI LLM to extract intent and entities as a fallback.
    Args:
        transcript (str): User input text.
    Returns:
        Dict: Extracted intent and entities.
    """
    prompt = f"""
    You are an intent and entity extraction engine for a CRM bot.
    Extract intent (LEAD_CREATE, VISIT_SCHEDULE, LEAD_UPDATE, UNKNOWN) 
    and required entities from this transcript:

    Transcript: "{transcript}"

    Respond in strict JSON with keys: intent, entities.
    Entities keys: [name, phone, city, lead_id, visit_time, status, source, notes].
    If a field is missing, return null for that key.
    """
    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "system", "content": prompt}],
            temperature=0
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        return {"intent": "UNKNOWN", "entities": {}}


# Main NLU Entry Point
def parse_transcript(transcript: str) -> Dict:
    """
    Parse transcript to detect intent, extract entities, and return structured result.
    Args:
        transcript (str): User input text.
    Returns:
        Dict: {
            "intent": str,
            "intent_confidence": float,
            "entities": dict,
            "error": Optional[dict]
        }
    """
    intent, confidence = classify_intent(transcript)
    entities, error = extract_entities(transcript, intent)

    # Fallback to LLM if rules fail completely
    if intent == "UNKNOWN" and all(v is None for v in entities.values()):
        logger.info("Falling back to LLM for NLU...")
        llm_result = extract_with_llm(transcript)
        return {
            "intent": llm_result.get("intent", "UNKNOWN"),
            "intent_confidence": 0.7,
            "entities": llm_result.get("entities", {}),
            "error": None
        }

    return {
        "intent": intent,
        "intent_confidence": confidence,
        "entities": entities,
        "error": error
    }