"""
CRM Client module:
Provides functions to interact with the CRM system, including creating leads,
scheduling visits, and updating lead status. Includes retry and timeout
mechanisms for robust HTTP requests.
"""

#imports
import requests
from typing import Optional, Dict
from requests.adapters import HTTPAdapter, Retry
from bot.settings import CRM_BASE_URL, logger

# Configuration
TIMEOUT = 5                 # seconds for HTTP requests
RETRIES = 2                 # number of retries for failed requests
BACKOFF_FACTOR = 1          # backoff factor for retry delays

# HTTP session with retries
session = requests.Session()
retries = Retry(
    total=RETRIES,
    backoff_factor=BACKOFF_FACTOR,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["POST"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)


# CRM Operations
def create_lead(name: str, phone: str, city: str, source: Optional[str] = None) -> Dict:
    """
    Create a new lead in the CRM.
    Args:
        name (str): Lead's full name
        phone (str): Lead's phone number
        city (str): Lead's city
        source (Optional[str]): Optional lead source
    Returns:
        dict: CRM API response or error dictionary
    """
    url = f"{CRM_BASE_URL}/crm/leads"
    payload = {"name": name, "phone": phone, "city": city}
    if source:
        payload["source"] = source

    try:
        resp = session.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return {
            "endpoint": "/crm/leads",
            "method": "POST",
            "status_code": resp.status_code,
            "result": resp.json()
        }
    except requests.RequestException as e:
        logger.error(f"CRM create_lead failed: {e}")
        return {"error": {"type": "CRM_ERROR", "details": str(e)}}


def schedule_visit(lead_id: str, visit_time: str, notes: Optional[str] = None) -> Dict:
    """
    Schedule a visit for a lead.
    Args:
        lead_id (str): Unique lead identifier
        visit_time (str): ISO-formatted visit time
        notes (Optional[str]): Optional visit notes
    Returns:
        dict: CRM API response or error dictionary
    """
    url = f"{CRM_BASE_URL}/crm/visits"
    payload = {"lead_id": lead_id, "visit_time": visit_time}
    if notes:
        payload["notes"] = notes

    try:
        resp = session.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return {
            "endpoint": "/crm/visits",
            "method": "POST",
            "status_code": resp.status_code,
            "result": resp.json()
        }
    except requests.RequestException as e:
        logger.error(f"CRM schedule_visit failed: {e}")
        return {"error": {"type": "CRM_ERROR", "details": str(e)}}


def update_lead_status(lead_id: str, status: str, notes: Optional[str] = None) -> Dict:
    """
    Update the status of an existing lead.
    Args:
        lead_id (str): Unique lead identifier
        status (str): New status (NEW, IN_PROGRESS, FOLLOW_UP, WON, LOST)
        notes (Optional[str]): Optional notes about the update
    Returns:
        dict: CRM API response or error dictionary
    """
    url = f"{CRM_BASE_URL}/crm/leads/{lead_id}/status"
    payload = {"status": status}
    if notes:
        payload["notes"] = notes

    try:
        resp = session.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return {
            "endpoint": f"/crm/leads/{lead_id}/status",
            "method": "POST",
            "status_code": resp.status_code,
            "result": resp.json()
        }
    except requests.RequestException as e:
        logger.error(f"CRM update_lead_status failed: {e}")
        return {"error": {"type": "CRM_ERROR", "details": str(e)}}


# Debug / Utility Helpers
def list_leads() -> Dict:
    """
    Fetch all leads from the CRM.
    Returns:
        dict: CRM API response or empty dict if failed
    """
    try:
        resp = session.get(f"{CRM_BASE_URL}/crm/leads", timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.warning(f"list_leads failed: {e}")
        return {}


def list_visits() -> Dict:
    """
    Fetch all scheduled visits from the CRM.
    Returns:
        dict: CRM API response or empty dict if failed
    """
    try:
        resp = session.get(f"{CRM_BASE_URL}/crm/visits", timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.warning(f"list_visits failed: {e}")
        return {}