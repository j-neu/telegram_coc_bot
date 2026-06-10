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
COC_LINK = os.getenv('COC_LINK', 'https://icedippers.com/code-of-conduct')
COC_LINK_DE = os.getenv('COC_LINK_DE', 'https://icedippers.com/de/verhaltenskodex')

DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'

WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # if set, bot uses webhooks; otherwise falls back to polling
PORT = int(os.getenv('PORT', '8443'))
