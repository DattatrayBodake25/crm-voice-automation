""" 
End-to-end tests for the Bot Service.

"""

#imports
import os
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from bot.app import app

# FastAPI test client
client = TestClient(app)

# Shared state for carrying lead_id between tests
lead_data = {}

# Analytics file path (same as used in app.py)
ANALYTICS_FILE = "analytics.jsonl"

def read_last_analytics_entry():
    """
    Utility function to read the last JSON line entry
    from the analytics log file.
    """
    if not os.path.exists(ANALYTICS_FILE):
        return None
    with open(ANALYTICS_FILE, "r") as f:
        lines = f.read().strip().split("\n")
        if lines:
            return json.loads(lines[-1])
    return None

# Mock CRM responses

def mock_create_lead(*args, **kwargs):
    """Simulates successful lead creation in CRM."""
    return {
        "endpoint": "/crm/leads",
        "method": "POST",
        "status_code": 200,
        "result": {
            "lead_id": "mock-lead-id-1234",
            "status": "NEW",
        },
    }

def mock_schedule_visit(*args, **kwargs):
    """Simulates successful visit scheduling in CRM."""
    return {
        "endpoint": "/crm/visits",
        "method": "POST",
        "status_code": 200,
        "result": {
            "visit_id": "mock-visit-id-5678",
            "status": "SCHEDULED",
        },
    }

def mock_update_lead_status(*args, **kwargs):
    """Simulates successful lead status update in CRM."""
    return {
        "endpoint": f"/crm/leads/{kwargs.get('lead_id')}/status",
        "method": "POST",
        "status_code": 200,
        "result": {
            "lead_id": kwargs.get("lead_id"),
            "status": kwargs.get("status"),
        },
    }

# Mock NLU parser

def mock_parse_transcript(transcript):
    """
    Mock parser to simulate NLU outputs for testing,
    based on the transcript content.
    """
    if "Add a new lead" in transcript:
        return {
            "intent": "LEAD_CREATE",
            "intent_confidence": 0.9,
            "entities": {
                "name": "Rohan Sharma",
                "phone": "9876543210",
                "city": "Gurgaon",
                "source": "Instagram",
                "lead_id": "mock-lead-id-1234",
            },
            "error": None,
        }
    elif "Schedule a visit" in transcript:
        return {
            "intent": "VISIT_SCHEDULE",
            "intent_confidence": 0.9,
            "entities": {
                "lead_id": "mock-lead-id-1234",
                "visit_time": "2025-10-02T17:00:00+05:30",
                "notes": "Discuss project details.",
            },
            "error": None,
        }
    elif "Update lead" in transcript:
        return {
            "intent": "LEAD_UPDATE",
            "intent_confidence": 0.9,
            "entities": {
                "lead_id": "mock-lead-id-1234",
                "status": "WON",
                "notes": "Booked unit A2.",
            },
            "error": None,
        }
    return {
        "intent": "UNKNOWN",
        "intent_confidence": 0.0,
        "entities": {},
        "error": None,
    }


# Tests

@pytest.mark.order(1)
@patch("bot.nlu.parse_transcript", side_effect=mock_parse_transcript)
@patch("bot.crm_client.create_lead", side_effect=mock_create_lead)
def test_lead_create(mock_crm, mock_nlu):
    """
    Test happy path for LEAD_CREATE intent.
    """
    transcript = (
        "Add a new lead: Rohan Sharma from Gurgaon, "
        "phone 9876543210, source Instagram."
    )
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert data["intent"] == "LEAD_CREATE"
    assert data["entities"]["lead_id"] == "mock-lead-id-1234"

    # Save lead_id for use in subsequent tests
    lead_data["lead_id"] = data["crm_call"]["result"]["lead_id"]

    # Verify analytics log
    last_entry = read_last_analytics_entry()
    assert last_entry["intent"] == "LEAD_CREATE"
    assert last_entry["success"] is True

@pytest.mark.order(2)
@patch("bot.nlu.parse_transcript", side_effect=mock_parse_transcript)
@patch("bot.crm_client.schedule_visit", side_effect=mock_schedule_visit)
def test_visit_schedule(mock_crm, mock_nlu):
    """
    Test happy path for VISIT_SCHEDULE intent.
    """
    lead_id = lead_data.get("lead_id")
    assert lead_id is not None

    transcript = (
        f"Schedule a visit for lead {lead_id} at 2025-10-02T17:00:00+05:30. "
        "Notes: Discuss project details."
    )
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert data["intent"] == "VISIT_SCHEDULE"
    assert data["entities"]["lead_id"] == lead_id
    assert data["entities"]["visit_time"] == "2025-10-02T17:00:00+05:30"
    assert data["entities"]["notes"].rstrip(".") == "Discuss project details"

@pytest.mark.order(3)
@patch("bot.nlu.parse_transcript", side_effect=mock_parse_transcript)
@patch("bot.crm_client.update_lead_status", side_effect=mock_update_lead_status)
def test_lead_update(mock_crm, mock_nlu):
    """
    Test happy path for LEAD_UPDATE intent.
    """
    lead_id = lead_data.get("lead_id")
    assert lead_id is not None

    transcript = f"Update lead {lead_id} to WON. Notes: Booked unit A2."
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert data["intent"] == "LEAD_UPDATE"
    assert data["entities"]["lead_id"] == lead_id
    assert data["entities"]["status"] == "WON"
    assert data["entities"]["notes"].rstrip(".") == "Booked unit A2"

def test_missing_required_entity():
    """
    Test validation error when required entities are missing.
    """
    transcript = "Add a new lead with no phone number"
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    assert response.status_code == 200
    assert data["intent"] == "LEAD_CREATE"
    assert data["error"]["type"] == "VALIDATION_ERROR"

@patch("bot.nlu.parse_transcript", side_effect=mock_parse_transcript)
@patch("bot.crm_client.update_lead_status")
def test_crm_error(mock_crm, mock_nlu):
    """
    Test CRM_ERROR handling when CRM client raises an exception.
    """
    mock_crm.side_effect = Exception("CRM server error")
    lead_id = lead_data.get("lead_id")

    transcript = f"Update lead {lead_id} to WON."
    response = client.post("/bot/handle", json={"transcript": transcript})
    data = response.json()

    assert response.status_code == 200
    assert data["intent"] == "LEAD_UPDATE"
    assert data["error"]["type"] == "CRM_ERROR"