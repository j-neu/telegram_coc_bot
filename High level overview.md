# High-Level Project Overview

## Goal

Ensure every member of a Telegram group — existing and new — explicitly agrees to the group's Code of Conduct before being allowed to post messages. All user-facing messages are bilingual (English and German). The bot is deployed on Railway for a reliable, always-on setup.

## Core Logic

1. **Gatekeeper on all messages**: Every message is checked. If the sender has not agreed to the current CoC, their message is deleted, they are restricted, and the bot contacts them.
2. **New member join**: Any user who joins a managed group is immediately restricted until they agree.
3. **Agreement flow**: Users receive a bilingual DM with links to the CoC in both languages and an Agree button. If their privacy settings block DMs, the bot posts an inline message in the group tagging them. One tap records their agreement and restores their posting permissions.
4. **Cross-group identity**: If a user has already agreed to the current CoC version in another group, they see a lightweight "confirm for this group" flow rather than the full CoC again.

## Tech Stack

- **Language**: Python 3.11
- **Libraries**: `python-telegram-bot`, `psycopg2`, `python-dotenv`
- **Database**: PostgreSQL (Railway managed plugin — persistent across deploys)
- **Hosting**: Railway (always-on, polling-based, auto-restart on crash)

## Bot Permissions Required (per group)

The bot must be a group admin with:
- **Delete messages** — to remove messages from non-agreed users
- **Restrict members** — to block and unblock posting permissions

---

## Functional Requirements

### 1. Gatekeeper (Existing + New Members)

- On every message: check if sender has agreed to the current CoC version for this group
- If not agreed: delete message, restrict user, send DM (or inline group message as fallback)
- Known limitation: Telegram delivers messages to all clients before the bot can delete (~0.5–2s). Push notifications fire before delete. This is a hard Telegram API constraint, not a solvable bug.

### 2. New Member Join

- Detect join via `ChatMemberHandler`
- Immediately restrict the new member
- DM them with the CoC and Agree button (fallback to inline group message if DMs blocked)

### 3. Cross-Group Identity

- Single agreement database keyed by `(user_id, group_id, coc_version)`
- If a user has agreed in any group under the current version: fast-path confirm ("you've agreed before, confirm for this group") rather than full CoC flow
- Full CoC flow only for users who have never agreed anywhere

### 4. Agreement Flow

- User taps Agree (or Confirm for fast-path)
- Agreement recorded to PostgreSQL
- User unrestricted in the relevant group
- Bot confirms: "You're all set, you can now post in [group name]" (bilingual)

### 5. Admin Commands

| Command | Description |
|---|---|
| `/whoagreed` | List users who have agreed to the current CoC version in this group |
| `/setversion <v>` | Bump CoC version — stored in PostgreSQL, takes effect immediately without restart |
| `/post_onboarding` | Post a pinnable message with a permanent Agree button |

### 6. Configuration

```
BOT_TOKEN        Telegram bot token
ADMIN_IDS        Comma-separated Telegram user IDs with admin access
COC_VERSION      Initial CoC version string (e.g. "1.0") — overridden by DB value after first /setversion
COC_LINK         URL to the English Code of Conduct document
COC_LINK_DE      URL to the German Code of Conduct document
DATABASE_URL     PostgreSQL connection string (from Railway)
DRY_RUN          true/false — log actions without enforcing (for testing)
```

---

## Database Schema

### `agreements` table

Stores one row per user per group per CoC version agreed to.

```
user_id      BIGINT
username     TEXT
full_name    TEXT
group_id     BIGINT
group_name   TEXT
agreed_at    TIMESTAMPTZ
coc_version  TEXT
PRIMARY KEY (user_id, group_id, coc_version)
```

Helper functions: `record_agreement`, `has_agreed`, `has_agreed_anywhere`, `get_all_agreed`

### `settings` table

Stores bot-wide persistent configuration (currently: active CoC version).

```
key    TEXT PRIMARY KEY
value  TEXT
```

Helper functions: `get_setting`, `set_setting`

---

## Deployment (Railway)

- Polling-based (not webhooks) — Railway provides always-on uptime
- PostgreSQL plugin provides managed, persistent database — no ephemeral filesystem risk
- Always-on service with automatic restart on crash
- Environment variables set in Railway dashboard

---

## Documentation Structure

- **`README.md`** — Setup and deployment guide
- **`High level overview.md`** — This file: architecture and requirements
- **`tasks.md`** — Developer task breakdown
- **`TESTING.md`** — Testing strategies and checklist
