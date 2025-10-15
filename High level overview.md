## 🧭 High-Level Project Overview

### 🧑‍💼 Project Name
**Telegram Code of Conduct Agreement Bot**

### 🎯 Goal
Ensure every group member — existing and new — explicitly agrees to the group's Code of Conduct (CoC) before being allowed to post messages in Telegram groups you administer. The bot is designed for self-hosting on a Raspberry Pi with power-outage resilience.

### 🧩 Summary
A custom Telegram bot will:
1. **Onboard new members** by requiring them to agree to the CoC before they can post.
2. **Recover from power outages** by checking for unagreed members on startup.
3. **Provide tools for onboarding existing members** through a series of admin commands.
4. **Record and track agreement data** in a local SQLite database.
5. **Allow admins** to view reports and manage the agreement process.

### 🏗️ Tech Stack
* **Language:** Python 3.10+
* **Libraries:** `python-telegram-bot`, `sqlite3`, `python-dotenv`
* **Database:** SQLite
* **Hosting:** Raspberry Pi (or any Linux server)

---

## 📋 Functional Requirements

### 1. Onboarding Flow for New Members
* Detects when a new user joins the group.
* Immediately restricts the user from sending messages.
* Sends them a private message (or inline group message) with a link to the CoC and an "Agree" button.
* When the user clicks "Agree", the bot records their agreement and lifts the restrictions.

### 2. Onboarding Flow for Existing Members
*   **Automatic Gatekeeper**: The bot checks every message sent in the group. If a user who has not agreed to the CoC attempts to chat, their message is deleted, they are restricted, and they are sent a DM with instructions. This ensures all active members are onboarded.
*   **Manual Admin Commands**: For proactive management, admins can use `/restrict_existing` to restrict all known unagreed members at once, and `/sendcode_dm` or `/sendcode_group` to notify them.

### 3. Power Recovery & Missed Members
* On bot startup, it scans its database for all known users in all known groups.
* It identifies any member who has not agreed to the *current* CoC version (this handles users who joined during downtime or users who need to agree to a new version).
* It restricts them and sends a "Recovery Notice" with the agreement prompt.

### 4. Data Storage in SQLite
The database stores user agreements, including:
* User ID, username, and full name
* Group ID and name
* Timestamp of agreement
* CoC version agreed to

### 5. Admin Commands
| Command | Description |
|---|---|
| `/whoagreed` | List users who have agreed to the current version. |
| `/restrict_existing` | Proactively restricts all known, unagreed members. |
| `/sendcode_group` | Sends a public CoC agreement message to the group. |
| `/sendcode_dm` | Sends a private DM to all known, unagreed members. |
| `/export` | View agreement statistics and recent agreements. |
| `/setversion` | Display instructions for updating the CoC version. |

### 6. Configuration
All configuration is handled via an `.env` file, including the bot token, admin user IDs, CoC link, and CoC version.
