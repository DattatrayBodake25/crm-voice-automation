"""
Mock CRM Service
Provides in-memory endpoints for testing CRM operations:
- Lead creation
- Visit scheduling
- Lead status update
"""

#imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Optional
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(title="Mock CRM Service")

# Pydantic Models
class LeadCreate(BaseModel):
    """Payload for creating a new lead."""
    name: str
    phone: str
    city: str
    source: Optional[str] = None

class VisitCreate(BaseModel):
    """Payload for scheduling a visit for an existing lead."""
    lead_id: str
    visit_time: datetime
    notes: Optional[str] = None

class LeadStatusUpdate(BaseModel):
    """Payload for updating the status of an existing lead."""
    status: str = Field(
        pattern="^(NEW|IN_PROGRESS|FOLLOW_UP|WON|LOST)$",
        description="Lead status must be one of: NEW, IN_PROGRESS, FOLLOW_UP, WON, LOST"
    )
    notes: Optional[str] = None

# In-memory data stores
LEADS = {}
VISITS = {}

# API Endpoints
@app.post("/crm/leads")
def create_lead(payload: LeadCreate):
    """
    Create a new lead with a unique ID.
    """
    lead_id = str(uuid4())
    LEADS[lead_id] = {**payload.dict(), "lead_id": lead_id, "status": "NEW"}
    return {"lead_id": lead_id, "status": "NEW"}

@app.post("/crm/visits")
def create_visit(payload: VisitCreate):
    """
    Schedule a visit for an existing lead.
    """
    if payload.lead_id not in LEADS:
        raise HTTPException(status_code=404, detail="Lead not found")

    visit_id = str(uuid4())
    VISITS[visit_id] = {**payload.dict(), "visit_id": visit_id, "status": "SCHEDULED"}
    return {"visit_id": visit_id, "status": "SCHEDULED"}

@app.post("/crm/leads/{lead_id}/status")
def update_lead_status(lead_id: str, payload: LeadStatusUpdate):
    """
    Update the status of a lead.
    """
    if lead_id not in LEADS:
        raise HTTPException(status_code=404, detail="Lead not found")

    LEADS[lead_id]["status"] = payload.status
    if payload.notes:
        LEADS[lead_id]["notes"] = payload.notes

    return {"lead_id": lead_id, "status": payload.status}