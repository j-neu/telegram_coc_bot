# Telegram Code of Conduct Agreement Bot

A self-hosted Telegram bot that ensures every group member explicitly agrees to the group's Code of Conduct before being allowed to post messages.

## Features

- **Gatekeeper Enforcement**: Automatically deletes messages from and restricts any user who has not agreed to the current CoC. This applies to both new and existing members.
- **Direct Agreement**: A simple, one-click agreement process that happens directly from a pinned message in your group.
- **SQLite Database**: Lightweight and local storage for agreements.
- **Admin Commands**: Essential tools for monitoring agreements.

## How It Works

1.  **Gatekeeper**: The bot checks every message. If a user has not agreed to the CoC, their message is deleted, they are restricted, and the bot attempts to DM them with instructions.
2.  **Onboarding Message**: An admin uses the `/post_onboarding` command to create a message with an "Agree" button. This message should be pinned.
3.  **Agreement**: Any user (new or existing) clicks the "Agree" button on the pinned message. The bot records their agreement and grants them speaking permissions.

## Prerequisites

- Raspberry Pi (or any Linux server)
- Python 3.10+
- Telegram Bot Token & Your Admin User ID

## Quick Start

### 1. Install
```bash
git clone https://github.com/YOUR_USERNAME/telegram_coc_bot.git
cd telegram_coc_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure
Create a `.env` file (`nano .env`):
```
BOT_TOKEN=your_bot_token
ADMIN_IDS=your_telegram_user_id
COC_VERSION=1.0
COC_LINK=https://your-code-of-conduct-url
```

### 3. Run as a Service
Create a service file: `sudo nano /etc/systemd/system/telegram-coc-bot.service`
(See `RASPBERRY_PI_DEPLOY.md` for the full template)

Then enable and start it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-coc-bot
sudo systemctl start telegram-coc-bot
```

## Usage

1.  **Add Bot to Group**: Make it an admin with **"Restrict Members"** and **"Delete Messages"** permissions.
2.  **Post and Pin**: As an admin, type `/post_onboarding` in the group. Pin the message the bot creates.
3.  **Done**: The bot will now automatically handle all users.

## Admin Commands
| Command | Description |
|---|---|
| `/post_onboarding` | Posts the pinnable message for users to agree. |
| `/whoagreed` | Lists users who have agreed to the current CoC. |
| `/setversion <v>` | Sets a new CoC version, requiring all users to re-agree. |
