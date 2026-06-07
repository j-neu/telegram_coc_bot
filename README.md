# Telegram Code of Conduct Agreement Bot

<<<<<<< HEAD
A self-hosted Telegram bot (designed for Raspberry Pi) that ensures every group member explicitly agrees to the group's Code of Conduct before being allowed to post messages.

## Features

- **New Member Onboarding**: Automatically restricts new members until they agree to the CoC
- **Power Recovery**: Checks for unagreed members on startup (handles power outages/restarts)
- **Existing Member Prompts**: Allows admins to send CoC agreement requests to all members
- **SQLite Database**: Lightweight local storage, perfect for Raspberry Pi
- **Admin Commands**: Comprehensive admin tools for monitoring and managing agreements
- **Fallback Mechanisms**: DM with group message fallback for user notifications
- **Version Control**: Track different CoC versions and require re-agreement when updated
- **Dry-Run Mode**: Test without restricting users

## Why Raspberry Pi?

- ✅ One-time cost (~$45 for Pi 4)
- ✅ Very low power consumption (~$5/year electricity)
- ✅ Full control over your data
- ✅ No monthly fees
- ✅ Runs 24/7 reliably
- ✅ Handles power outages gracefully

**Cost comparison:** Cloud hosting costs $60-84/year. A Raspberry Pi pays for itself in ~8 months!

## Prerequisites

### Hardware (Recommended)
- **Raspberry Pi 4 (2GB)** - $45 (or Pi 3, Pi Zero 2 W)
- MicroSD card (16GB+)
- Power supply
- Internet connection (WiFi or Ethernet)

### Software
- Raspberry Pi OS Lite (installed on SD card)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Your Telegram User ID (from [@userinfobot](https://t.me/userinfobot))

## Quick Start (Raspberry Pi)

### 1. Flash Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash "Raspberry Pi OS Lite (64-bit)" to SD card
3. In settings (⚙️):
   - Enable SSH
   - Set username/password
   - Configure WiFi
   - Set timezone
4. Insert SD card and boot Pi

### 2. Connect and Setup
=======
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
>>>>>>> d4c25183d4ea93600488801ec62cccb59f8f62c4

### 1. Install
```bash
<<<<<<< HEAD
# SSH into your Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip git

# Clone repository
git clone https://github.com/YOUR_USERNAME/telegram_coc_bot.git
cd telegram_coc_bot

# Install Python dependencies
pip3 install -r requirements.txt
```

### 3. Configure Bot

Create `.env` file:
```bash
nano .env
```

Add your configuration:
```
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_IDS=your_telegram_user_id
COC_VERSION=1.0
COC_LINK=https://your-code-of-conduct-url
STORAGE_TYPE=sqlite
DRY_RUN=false
```

Save with `Ctrl+O`, `Enter`, `Ctrl+X`

### 4. Test the Bot

```bash
# Test run
python3 bot.py

# You should see:
# Storage type: sqlite
# Database initialized successfully
# Bot starting...
# Running startup check for unagreed members...

# Press Ctrl+C to stop
```

### 5. Auto-Start on Boot

Create systemd service:
```bash
sudo nano /etc/systemd/system/telegram-coc-bot.service
```

Paste this:
```ini
[Unit]
Description=Telegram Code of Conduct Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/telegram_coc_bot
ExecStart=/usr/bin/python3 /home/pi/telegram_coc_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable telegram-coc-bot
sudo systemctl start telegram-coc-bot
sudo systemctl status telegram-coc-bot
```

### 6. Add Bot to Telegram Group

1. Add bot to your Telegram group
2. Make it admin with these permissions:
   - ✅ Delete messages
   - ✅ Ban users
   - ✅ **Restrict members (REQUIRED)**

Done! Your bot is now running 24/7.

## Power Recovery Feature

**What happens during power outage:**

1. Pi loses power, bot goes offline
2. Members join the group while bot is offline
3. Pi power returns, bot restarts automatically (systemd)
4. Bot runs startup check:
   - Scans all groups it's in
   - Finds members who haven't agreed
   - Restricts them and sends CoC message
   - Includes "Recovery Notice" in message

**Example recovery message:**
```
⚠️ Recovery Notice: The bot was offline when you joined.

Welcome! 👋

Before you can participate in this group, please review and agree to our Code of Conduct.
```

This ensures **no one slips through** even during downtime!

## Usage

### For New Members

1. New member joins the group
2. Bot automatically restricts them
3. They receive CoC message (DM or in-group)
4. After clicking "Agree", they can post messages

### Admin Commands

All admin commands work in the group:
=======
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
>>>>>>> d4c25183d4ea93600488801ec62cccb59f8f62c4

## Admin Commands
| Command | Description |
<<<<<<< HEAD
|---------|-------------|
| `/start` | Send CoC agreement prompt (anyone can use) |
| `/whoagreed` | List all users who have agreed to current CoC version |
| `/whohasnotagreed` | Check which members haven't agreed yet |
| `/sendcode` | Send CoC agreement request to all group members |
| `/setversion <version>` | Display instructions for updating CoC version |
| `/export` | View agreement statistics and recent agreements |

### Agreement Data

The bot stores in SQLite database (`coc_agreements.db`):
- User ID (Telegram)
- Username
- Full Name
- Group ID
- Group Name
- Agreement Timestamp (UTC)
- CoC Version

## Managing Your Bot

### View Logs
```bash
# Real-time logs
sudo journalctl -u telegram-coc-bot -f

# Last 50 lines
sudo journalctl -u telegram-coc-bot -n 50
```

### Restart Bot
```bash
sudo systemctl restart telegram-coc-bot
```

### Stop Bot
```bash
sudo systemctl stop telegram-coc-bot
```

### Update Bot Code
```bash
cd ~/telegram_coc_bot
sudo systemctl stop telegram-coc-bot
git pull
sudo systemctl start telegram-coc-bot
```

### Backup Database
```bash
# Manual backup
cp ~/telegram_coc_bot/coc_agreements.db ~/coc_backup_$(date +%Y%m%d).db

# Download to your computer
scp pi@raspberrypi.local:~/telegram_coc_bot/coc_agreements.db ./backup.db
```

## Testing Mode

To test without restricting users, set `DRY_RUN=true` in `.env`:

```bash
nano .env
# Change: DRY_RUN=true

sudo systemctl restart telegram-coc-bot
```

In dry-run mode:
- Bot logs what it would do
- No users are actually restricted
- Agreements are still recorded
- Perfect for testing in production groups

View logs to see `[DRY RUN]` messages.

## Troubleshooting

### Bot not starting
```bash
# Check logs
sudo journalctl -u telegram-coc-bot -n 50

# Common issues:
# - Wrong BOT_TOKEN in .env
# - Missing dependencies
# - Database permission issues
```

### Can't restrict users
- Make sure bot is admin in Telegram group
- Verify "Restrict members" permission is enabled
- Check logs for permission errors

### Power recovery not working
- Check systemd service is enabled: `systemctl is-enabled telegram-coc-bot`
- Verify auto-start: `sudo systemctl enable telegram-coc-bot`
- Check logs after reboot: `sudo journalctl -u telegram-coc-bot -n 100`

### Database errors
```bash
# Check database exists
ls -l ~/telegram_coc_bot/coc_agreements.db

# Fix permissions if needed
chmod 644 ~/telegram_coc_bot/coc_agreements.db
```

## Performance

This bot is very lightweight:
- **RAM:** ~50-100 MB
- **CPU:** <1% most of the time
- **Storage:** ~1KB per user agreement
- **Network:** Minimal bandwidth

Even a **Raspberry Pi Zero 2 W ($15)** can handle this!

## Security Notes

- Database stored locally on your Pi
- Never commit `.env` to version control (already in `.gitignore`)
- Change default Pi password: `passwd`
- Keep system updated: `sudo apt update && sudo apt upgrade`
- Consider installing `fail2ban` for SSH protection
- Rotate bot token periodically via [@BotFather](https://t.me/BotFather)

## Alternative Deployment Options

While this bot is optimized for Raspberry Pi, it also works on:

- **Other cloud platforms:** See `RAILWAY_DEPLOY.md` and `RENDER_DEPLOY.md`
- **Any Linux server:** Follow Raspberry Pi guide, adjust paths
- **VPS:** DigitalOcean, Linode, etc. (See `DEPLOYMENT.md`)
- **Windows/Mac:** Run `python bot.py` directly (not recommended for production)

## Full Documentation

- **`RASPBERRY_PI_DEPLOY.md`** - Complete Pi setup guide (recommended)
- **`DEPLOYMENT.md`** - Cloud hosting options (Railway, Render, VPS)
- **`TESTING.md`** - Safe testing strategies
- **`tasks.md`** - Original project task breakdown

## Cost Breakdown

### One-Time Costs
- Raspberry Pi 4 (2GB): $45
- MicroSD card (32GB): $8
- Power supply: Included or $8
- **Total: ~$53-61**

### Ongoing Costs
- Electricity (24/7): ~$0.50/month = **$6/year**

### Cloud Hosting Comparison
- Railway: ~$5-7/month = $60-84/year (recurring)
- Render: $7/month = $84/year (recurring)
- VPS: $5-6/month = $60-72/year (recurring)

**Raspberry Pi pays for itself in 8-12 months!**

## Support

For issues:
1. Check logs: `sudo journalctl -u telegram-coc-bot -n 50`
2. Test with `DRY_RUN=true`
3. Verify bot permissions in Telegram
4. Review documentation in this repository

## License

This project is provided as-is for community use.

---

**Ready to deploy?** Follow `RASPBERRY_PI_DEPLOY.md` for detailed step-by-step instructions!
=======
|---|---|
| `/post_onboarding` | Posts the pinnable message for users to agree. |
| `/whoagreed` | Lists users who have agreed to the current CoC. |
| `/setversion <v>` | Sets a new CoC version, requiring all users to re-agree. |
>>>>>>> d4c25183d4ea93600488801ec62cccb59f8f62c4
