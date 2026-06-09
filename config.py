"""Configuration for the Telegram CoC Bot."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip()]

COC_VERSION = os.getenv('COC_VERSION', '1.0')
COC_LINK = os.getenv('COC_LINK', 'https://example.com/code-of-conduct')

DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'

WELCOME_MESSAGE = (
    f"Welcome! 👋\n\n"
    f"Before you can participate in this group, please review and agree to our Code of Conduct.\n\n"
    f"📜 Read the Code of Conduct: {COC_LINK}\n\n"
    f"By clicking \"Agree ✅\" below, you confirm that you have read and agree to follow the Code of Conduct."
)

AGREEMENT_SUCCESS_MESSAGE = "Thank you for agreeing to the Code of Conduct! You can now participate in the group. 🎉"

ADMIN_ONLY_MESSAGE = "This command is only available to administrators."
