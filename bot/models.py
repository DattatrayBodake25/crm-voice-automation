"""
Pydantic models for the Voice-Style Bot Service.
Defines structured request and response schemas, as well as error handling models.
These models are used for data validation and serialization/deserialization
between the API, NLU, and CRM client layers.
"""

#imports
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, List


# Bot Request Model
class BotRequest(BaseModel):
    """
    Request model for the bot API.
    """
    transcript: str = Field(..., description="User input text for the bot")
    metadata: Optional[Dict[str, str]] = Field(
        None, description="Optional dictionary containing additional metadata"
    )

    def __init__(self, **data):
        """
        Initialize BotRequest and catch validation errors to raise as ValueError.
        """
        try:
            super().__init__(**data)
        except ValidationError as e:
            raise ValueError(f"Invalid BotRequest data: {e}")


# Structured Error Model
class ErrorModel(BaseModel):
    """
    Structured error model for bot responses.
    """
    type: str = Field(..., description="Type of the error, e.g., VALIDATION_ERROR")
    missing_fields: Optional[List[str]] = Field(
        None, description="List of missing required fields, if any"
    )
    details: Optional[str] = Field(
        None, description="Optional error details or message"
    )


# Bot Response Model
class BotResponse(BaseModel):
    """
    Response model returned by the bot API.
    """
    intent: str = Field(..., description="Detected intent from transcript")
    intent_confidence: Optional[float] = Field(
        None, description="Confidence score of detected intent"
    )
    entities: Optional[Dict[str, Optional[str]]] = Field(
        None, description="Extracted entities from the transcript"
    )
    crm_call: Optional[Dict] = Field(
        None, description="Information about the CRM call made by bot"
    )
    result: Optional[Dict[str, str]] = Field(
        None, description="Optional result message from bot operation"
    )
    error: Optional[ErrorModel] = Field(
        None, description="Structured error details if something failed"
    )

    def __init__(self, **data):
        """
        Initialize BotResponse and catch validation errors to raise as ValueError.
        """
        try:
            super().__init__(**data)
        except ValidationError as e:
            raise ValueError(f"Invalid BotResponse data: {e}")