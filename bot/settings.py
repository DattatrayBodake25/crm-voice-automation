"""
Bot Service Settings and Configuration:
Handles environment variable loading, logging setup, and global constants
for CRM integration and OpenAI LLM usage.
"""

#imports
import os
import logging
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()  # Loads .env file into environment

# CRM & Bot Configuration
CRM_BASE_URL: str = os.getenv("CRM_BASE_URL", "http://localhost:8001")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# OpenAI LLM Configuration
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Logging Setup
def configure_logging(name: str = "bot") -> logging.Logger:
    """
    Configure and return a logger instance with stream output.
    Args:
        name (str): Logger name. Defaults to 'bot'.
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers
    if not logger.handlers:
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)

        # Stream handler
        ch = logging.StreamHandler()
        ch.setLevel(log_level)

        # Formatter for console output
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger

# Default logger for the bot
logger: logging.Logger = configure_logging()