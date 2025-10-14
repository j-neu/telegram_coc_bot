## 🧭 **High-Level Project Overview**

### 🧑‍💼 Project Name

**Telegram Code of Conduct Agreement Bot**

### 🎯 Goal

Ensure every group member — existing and new — explicitly agrees to the group’s Code of Conduct (CoC) before being allowed to post messages in Telegram groups you administer.

### 🧩 Summary

A custom Telegram bot will:

1. **Onboard new members** by requiring them to agree to the CoC before they can post.
2. **Prompt existing members** to review and agree to the CoC.
3. **Record and track agreement data** (user ID, username, timestamp, CoC version) in a **Google Sheet**.
4. **Allow admins** to view reports and resend agreement prompts.

### 🏗️ Tech Stack

* **Language:** Python 3.10+
* **Libraries:**

  * `python-telegram-bot` (Telegram bot framework)
  * `gspread` (Google Sheets API client)
  * `oauth2client` (for Google API auth)
* **Database:** Google Sheets
* **Hosting:** PythonAnywhere, Render, or a simple VPS
* **Bot Permissions:** Must be an admin in all target groups, with “restrict members” permission enabled.

### 🔐 Security

* Google Service Account credentials (JSON file) stored securely on the server.
* Admin-only bot commands protected by Telegram user IDs.

---

## 📋 **Functional Requirements**

### 1. Onboarding Flow for New Members

* Detects when a new user joins the group.
* Immediately restricts the user (no messaging permissions).
* Sends them a private message (or inline group message) asking to review and agree to the CoC.
* When user clicks **“Agree ✅”**, the bot:

  * Logs agreement details to Google Sheets.
  * Unrestricts the user.

### 2. Existing Members Onboarding

* Admin can trigger `/sendcode` to tag or message all current members asking for agreement.
* Bot checks Google Sheet to skip users who already agreed.

### 3. Data Storage in Google Sheets

Each row represents one agreement record:
| user_id | username | full_name | group_id | group_name | agreed_at | coc_version |

### 4. Admin Commands

| Command            | Description                                       |
| ------------------ | ------------------------------------------------- |
| `/whoagreed`       | List (or count) of users who have agreed.         |
| `/whohasnotagreed` | List of users who haven’t agreed yet.             |
| `/sendcode`        | Re-send CoC prompt to all or specific users.      |
| `/export`          | Export Google Sheet data as CSV.                  |
| `/setversion`      | Update current CoC version (forces re-agreement). |

### 5. Configuration

* CoC link (Google Doc or website)
* Admin Telegram IDs
* Google Sheet ID
* CoC version number