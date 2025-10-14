## 🧭 **High-Level Project Overview**

### 🧑‍💼 Project Name

**Telegram Code of Conduct Agreement Bot**

### 🎯 Goal

Ensure every group member — existing and new — explicitly agrees to the group's Code of Conduct (CoC) before being allowed to post messages in Telegram groups you administer. The bot is designed for self-hosting on a Raspberry Pi with power-outage resilience.

### 🧩 Summary

A custom Telegram bot will:

1. **Onboard new members** by requiring them to agree to the CoC before they can post.
2. **Recover from power outages** by checking for unagreed members on startup.
3. **Prompt existing members** to review and agree to the CoC.
4. **Record and track agreement data** (user ID, username, timestamp, CoC version) in a local **SQLite database**.
5. **Allow admins** to view reports and resend agreement prompts.

### 🏗️ Tech Stack

* **Language:** Python 3.10+
* **Libraries:**
  * `python-telegram-bot` (Telegram bot framework)
  * `sqlite3` (built-in database, no external dependencies)
  * `python-dotenv` (environment variable management)
* **Database:** SQLite (local file-based database)
* **Hosting:** Raspberry Pi 4 (or Pi 3, Pi Zero 2 W)
  * Alternative options: Any Linux server, VPS, or cloud platform
* **Bot Permissions:** Must be an admin in all target groups, with "restrict members" permission enabled.

### 🔐 Security

* SQLite database stored locally on Raspberry Pi (full data control)
* Admin-only bot commands protected by Telegram user IDs
* No external API dependencies or cloud services required
* Environment variables stored in `.env` file (git-ignored)

### 💪 Power Recovery Feature

**Key Feature:** The bot handles power outages gracefully:

1. When Pi loses power, systemd service auto-restarts on boot
2. On startup, bot scans all groups for members who haven't agreed
3. Restricts and messages anyone who joined during downtime
4. Includes "Recovery Notice" in messages to affected users

This ensures **zero missed members** even during extended outages.

---

## 📋 **Functional Requirements**

### 1. Onboarding Flow for New Members

* Detects when a new user joins the group.
* Immediately restricts the user (no messaging permissions).
* Sends them a private message (or inline group message) asking to review and agree to the CoC.
* When user clicks **"Agree ✅"**, the bot:
  * Logs agreement details to SQLite database.
  * Unrestricts the user.

### 2. Power Recovery & Missed Members

* On bot startup (after power outage or restart):
  * Scans all managed groups
  * Identifies members who haven't agreed to current CoC version
  * Restricts them and sends CoC agreement message
  * Includes "Recovery Notice" to explain bot was offline

### 3. Existing Members Onboarding

* Admin can trigger `/sendcode` to message all current members asking for agreement.
* Bot checks database to skip users who already agreed.

### 4. Data Storage in SQLite

Each record in the database contains:
| Field | Type | Description |
|-------|------|-------------|
| user_id | INTEGER | Telegram user ID |
| username | TEXT | Telegram username |
| full_name | TEXT | User's display name |
| group_id | INTEGER | Telegram group ID |
| group_name | TEXT | Group title |
| agreed_at | TEXT | ISO timestamp (UTC) |
| coc_version | TEXT | CoC version agreed to |

**Benefits of SQLite:**
- No external dependencies
- Fast and lightweight
- Perfect for Raspberry Pi
- Automatic backups via file copy
- No internet required for database operations

### 5. Admin Commands

| Command            | Description                                       |
| ------------------ | ------------------------------------------------- |
| `/whoagreed`       | List users who have agreed to current version     |
| `/whohasnotagreed` | List users who haven't agreed yet                 |
| `/sendcode`        | Send CoC prompt to all members                    |
| `/export`          | View agreement statistics and recent agreements   |
| `/setversion`      | Display instructions for updating CoC version     |

### 6. Configuration

* CoC link (Google Doc, website, or any URL)
* Admin Telegram IDs (comma-separated)
* CoC version number
* Storage type (SQLite or Google Sheets)
* Dry-run mode for safe testing

---

## 🍓 **Raspberry Pi Deployment**

### Why Raspberry Pi?

* **One-time cost:** ~$45-60 (Pi 4 + SD card)
* **Ongoing cost:** ~$6/year electricity
* **Cloud hosting cost:** $60-84/year recurring
* **ROI:** Pays for itself in 8-12 months

### Hardware Requirements

**Recommended:**
- Raspberry Pi 4 (2GB RAM) - $45
- MicroSD card (32GB) - $8
- Power supply - Usually included

**Minimum:**
- Raspberry Pi Zero 2 W - $15 (sufficient for this bot!)

### Setup Time

- **Flash SD card:** 5 minutes
- **SSH setup & dependencies:** 10 minutes
- **Bot configuration:** 5 minutes
- **Systemd service setup:** 5 minutes
- **Total:** ~25-30 minutes

### Key Features for Pi

1. **Auto-start on boot:** systemd service
2. **Auto-restart on crash:** systemd watchdog
3. **Power outage recovery:** Startup member check
4. **Low resource usage:** ~50MB RAM, <1% CPU
5. **Database persistence:** SQLite file survives reboots

---

## 🧪 **Testing & Safety**

### Dry-Run Mode

Set `DRY_RUN=true` in `.env`:
- Bot logs all actions without restricting users
- Perfect for testing in production groups
- Agreements are still recorded
- See exactly what would happen

### Testing Workflow

1. **Phase 1:** Test in private group with friends
2. **Phase 2:** Enable dry-run in production group
3. **Phase 3:** Monitor logs, let volunteers agree
4. **Phase 4:** Disable dry-run for new members only
5. **Phase 5:** Use `/sendcode` for existing members

---

## 📊 **Cost Comparison**

| Solution | Setup Cost | Year 1 Total | Year 2+ |
|----------|-----------|--------------|---------|
| **Raspberry Pi 4** | $53 | $59 | $6/year |
| Railway | $0 | $60-84 | $60-84/year |
| Render | $0 | $84 | $84/year |
| VPS | $0 | $60-72 | $60-72/year |

**Winner:** Raspberry Pi (pays for itself in ~9 months)

---

## 📚 **Documentation Structure**

- **`README.md`** - Quick start guide (Raspberry Pi focused)
- **`RASPBERRY_PI_DEPLOY.md`** - Detailed Pi setup instructions
- **`DEPLOYMENT.md`** - Cloud hosting alternatives
- **`TESTING.md`** - Safe testing strategies
- **`tasks.md`** - Original development task breakdown

---

## 🚀 **Quick Start Summary**

```bash
# 1. Flash Raspberry Pi OS to SD card
# 2. SSH into Pi
ssh pi@raspberrypi.local

# 3. Clone and setup
git clone https://github.com/YOUR_USERNAME/telegram_coc_bot.git
cd telegram_coc_bot
pip3 install -r requirements.txt

# 4. Configure
nano .env
# Add BOT_TOKEN, ADMIN_IDS, etc.

# 5. Setup auto-start
sudo nano /etc/systemd/system/telegram-coc-bot.service
# (paste service configuration)
sudo systemctl enable telegram-coc-bot
sudo systemctl start telegram-coc-bot

# Done! Bot runs 24/7 with auto-restart and power recovery
```

---

## ✨ **Key Differentiators**

What makes this bot special:

1. **Power-outage resilient** - Catches missed members on restart
2. **Self-hosted** - Your data stays on your hardware
3. **Cost-effective** - One-time ~$50, then ~$6/year
4. **Zero cloud dependencies** - Works offline (except Telegram API)
5. **Lightweight** - Runs on a $15 Pi Zero 2 W
6. **Production-ready** - Dry-run mode, logging, error handling
7. **Admin-friendly** - Simple commands, clear reports
