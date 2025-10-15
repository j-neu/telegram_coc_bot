# Telegram Code of Conduct Agreement Bot

A self-hosted Telegram bot (designed for Raspberry Pi) that ensures every group member explicitly agrees to the group's Code of Conduct before being allowed to post messages.

## Features

- **New Member Onboarding**: Automatically restricts new members until they agree to the CoC.
- **Power Recovery**: Checks for unagreed members on startup (handles power outages/restarts).
- **Existing Member Onboarding**: A suite of admin commands to manage agreement for existing members.
- **SQLite Database**: Lightweight and local storage.
- **Admin Commands**: Comprehensive tools for monitoring and managing agreements.
- **Version Control**: Track different CoC versions and require re-agreement when updated.
- **Dry-Run Mode**: Test commands without actually restricting users.

## Prerequisites

### Hardware
- Raspberry Pi (any model with network access)
- MicroSD card (16GB+)
- Power supply

### Software
- Raspberry Pi OS Lite (installed on SD card)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Your Telegram User ID (from [@userinfobot](https://t.me/userinfobot))

## Quick Start (Raspberry Pi)

### 1. Setup Pi & Connect
- Flash "Raspberry Pi OS Lite" to your SD card using the Raspberry Pi Imager.
- In the imager settings, enable SSH, set a username/password, and configure WiFi.
- Boot the Pi and SSH into it: `ssh YOUR_USERNAME@YOUR_PI_HOSTNAME.local`

### 2. Install Bot
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip git python3-venv

# Clone repository
git clone https://github.com/YOUR_USERNAME/telegram_coc_bot.git
cd telegram_coc_bot

# Create virtual environment and install packages
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Bot
Create a `.env` file (`nano .env`) and add your configuration:
```
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_IDS=your_telegram_user_id
COC_VERSION=1.0
COC_LINK=https://your-code-of-conduct-url
STORAGE_TYPE=sqlite
DRY_RUN=false
```

### 4. Run Manually for Testing
```bash
# Make sure you are in the virtual environment
source venv/bin/activate 
# Run the bot
python3 bot.py
```
Press `Ctrl+C` to stop.

### 5. Auto-Start on Boot (Systemd)
Create a service file: `sudo nano /etc/systemd/system/telegram-coc-bot.service`
```ini
[Unit]
Description=Telegram Code of Conduct Bot
After=network.target

[Service]
Type=simple
User=YOUR_PI_USERNAME
WorkingDirectory=/home/YOUR_PI_USERNAME/telegram_coc_bot
ExecStart=/home/YOUR_PI_USERNAME/telegram_coc_bot/venv/bin/python3 /home/YOUR_PI_USERNAME/telegram_coc_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-coc-bot
sudo systemctl start telegram-coc-bot
sudo systemctl status telegram-coc-bot
```

### 6. Add Bot to Telegram Group
1. Add your bot to the Telegram group.
2. Make it an admin with the **"Restrict Members"** permission.

## Usage

### New Members
New members are automatically restricted and prompted to agree to the CoC.

### Onboarding Existing Members
The bot features a "gatekeeper" function that automatically enforces the CoC on all active members.

**Automatic Enforcement (Gatekeeper):**
The moment an existing member who has not agreed to the CoC sends a message, the bot will:
1.  Delete their message.
2.  Restrict their ability to send more messages.
3.  Send them a private message explaining why and providing the CoC agreement prompt.

This ensures all members must agree before they can participate.

**Manual Admin Tools:**
While the gatekeeper is automatic, admins have manual tools for proactive management:
-   Use `/sendcode_group` to post a public CoC prompt, making everyone aware of the rules.
-   Use `/restrict_existing` to proactively restrict all members who have not yet agreed, without waiting for them to send a message.
-   Use `/sendcode_dm` to send a direct reminder to all known, unagreed members.

### Admin Commands
| Command | Description |
|---|---|
| `/start` | Send CoC agreement prompt (anyone can use). |
| `/whoagreed` | List all users who have agreed to the current CoC version. |
| `/restrict_existing` | Proactively restricts all known, unagreed members. |
| `/sendcode_group` | Sends a public CoC agreement message to the group. |
| `/sendcode_dm` | Sends a private DM to all known, unagreed members. |
| `/setversion <version>`| Displays instructions for updating the CoC version. |
| `/export` | Views agreement statistics and recent agreements. |

## Managing Your Bot

- **View Logs**: `sudo journalctl -u telegram-coc-bot -f`
- **Restart Bot**: `sudo systemctl restart telegram-coc-bot`
- **Stop Bot**: `sudo systemctl stop telegram-coc-bot`
