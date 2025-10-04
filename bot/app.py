"""
FastAPI application for the Voice-Style Bot Service.
This service receives user transcripts, extracts intent and entities using NLU,
validates inputs, interacts with a CRM system based on detected intent,
logs analytics, and returns structured responses.
"""

#imports
import json
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from bot import nlu, crm_client
from bot.models import BotRequest, BotResponse
from bot.settings import logger

# Initialize FastAPI application
app = FastAPI(title="Voice-Style Bot Service")

# Analytics log file (JSON Lines format)
ANALYTICS_LOG = Path("analytics.jsonl")

# Analytics logging
def log_analytics(intent: str, entities: dict, success: bool):
    """
    Append request/response analytics to a local JSONL file.
    Args:
        intent (str): Detected intent from the transcript
        entities (dict): Extracted entities from the transcript
        success (bool): Whether the CRM action was successful
    """
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "intent": intent,
        "entities": entities,
        "success": success,
    }
    with open(ANALYTICS_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")


# API Endpoint: /bot/handle
@app.post("/bot/handle", response_model=BotResponse)
def handle_bot(request: BotRequest):
    """
    Main bot handler endpoint.
    Workflow:
    1. Validate transcript length
    2. Parse transcript via NLU
    3. Validate extracted entities
    4. Call appropriate CRM operation based on intent
    5. Log analytics
    6. Return structured BotResponse
    """
  
    # Safety check
    if len(request.transcript) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Transcript too long (max 1000 chars)"
        )

    logger.info(f"Received transcript: {request.transcript}")

    # NLU parsing
    nlu_result = nlu.parse_transcript(request.transcript)
    intent = nlu_result["intent"]
    intent_confidence = nlu_result.get("intent_confidence")
    entities = nlu_result.get("entities") or {}
    error = nlu_result.get("error")

    crm_response = {}
    success = False
    result_message = None

    # Handle validation errors
    if error:
        logger.warning(f"Validation error: {error}")
        log_analytics(intent, entities, success=False)

        return BotResponse(
            intent=intent,
            intent_confidence=intent_confidence,
            entities=entities,
            crm_call=None,
            result=None,
            error={
                "type": error.get("type", "VALIDATION_ERROR"),
                "details": error.get("details", "Required entities missing or invalid.")
            }
        )

    # CRM Integration
    try:
        if intent == "LEAD_CREATE":
            crm_response = crm_client.create_lead(
                name=entities.get("name", ""),
                phone=entities.get("phone", ""),
                city=entities.get("city", ""),
                source=entities.get("source")
            )
            if "error" not in crm_response:
                result_message = "Lead created successfully."
                success = True

        elif intent == "VISIT_SCHEDULE":
            crm_response = crm_client.schedule_visit(
                lead_id=entities.get("lead_id", ""),
                visit_time=entities.get("visit_time", ""),
                notes=entities.get("notes")
            )
            if "error" not in crm_response:
                result_message = "Visit scheduled successfully."
                success = True

        elif intent == "LEAD_UPDATE":
            crm_response = crm_client.update_lead_status(
                lead_id=entities.get("lead_id", ""),
                status=entities.get("status", ""),
                notes=entities.get("notes")
            )
            if "error" not in crm_response:
                result_message = "Lead status updated successfully."
                success = True

        else:
            result_message = "Unknown intent. No CRM action performed."

    except Exception as e:
        logger.error(f"CRM call failed: {e}")
        crm_response = {
            "error": {
                "type": "CRM_ERROR",
                "details": str(e)
            }
        }

    # Log analytics
    log_analytics(intent, entities, success)

    # Construct and return response
    return BotResponse(
        intent=intent,
        intent_confidence=intent_confidence,
        entities=entities,
        crm_call=crm_response if crm_response else None,
        result={"message": result_message} if result_message else None,
        error=crm_response.get("error") if "error" in crm_response else None
    )