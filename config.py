"""Configuration module for the Telegram CoC Bot."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

# Google Sheets Configuration (only needed if using sheets storage)
SHEET_ID = os.getenv('SHEET_ID', '')

# Admin Configuration
ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip()]

# Code of Conduct Configuration
COC_VERSION = os.getenv('COC_VERSION', '1.0')
COC_LINK = os.getenv('COC_LINK', 'https://example.com/code-of-conduct')

# Testing Configuration
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'

# Storage Configuration
# Options: 'sqlite' or 'sheets'
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'sqlite').lower()

# Messages
WELCOME_MESSAGE = f"""
Welcome! 👋

Before you can participate in this group, please review and agree to our Code of Conduct.

📜 Read the Code of Conduct: {COC_LINK}

By clicking "Agree ✅" below, you confirm that you have read and agree to follow the Code of Conduct.
"""

AGREEMENT_SUCCESS_MESSAGE = "Thank you for agreeing to the Code of Conduct! You can now participate in the group. 🎉"

ADMIN_ONLY_MESSAGE = "This command is only available to administrators."
