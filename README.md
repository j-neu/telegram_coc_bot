# Telegram Code of Conduct Agreement Bot

A Telegram bot that ensures every group member explicitly agrees to the group's Code of Conduct before being allowed to post. Deployed on Railway for an always-on setup.

## How It Works

1. **Gatekeeper**: Every message is checked. If the sender hasn't agreed to the current CoC, their message is deleted, they're restricted, and the bot contacts them.
2. **New members**: Anyone who joins a managed group is immediately restricted until they agree.
3. **Agreement**: Users receive a DM with an Agree button. If their DMs are blocked, the bot posts inline in the group instead. One tap records their agreement and restores posting permissions.
4. **Cross-group**: Users who've already agreed in another group see a one-tap confirm instead of the full CoC flow.

## Prerequisites

- Telegram bot token (from [@BotFather](https://t.me/BotFather))
- Your Telegram user ID (from [@userinfobot](https://t.me/userinfobot))
- Railway account

## Deployment (Railway)

### 1. Create Railway Project

1. Go to [railway.app](https://railway.app) and create a new project
2. Add a **PostgreSQL** plugin to the project
3. Connect your GitHub repository (or deploy from CLI)

### 2. Set Environment Variables

In the Railway dashboard under Variables:

```
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_IDS=your_telegram_user_id
COC_VERSION=1.0
COC_LINK=https://your-code-of-conduct-url
DATABASE_URL=${{Postgres.DATABASE_URL}}  # auto-filled by Railway plugin
WEBHOOK_URL=https://your-app.railway.app
DRY_RUN=false
```

### 3. Deploy

Railway auto-deploys on push to your connected branch. The bot starts, connects to PostgreSQL, registers the webhook, and is live.

### 4. Add Bot to Your Groups

In each Telegram group:
1. Add the bot as a member
2. Promote it to **admin**
3. Enable these admin permissions:
   - ✅ Delete messages
   - ✅ Restrict members

### 5. Post Onboarding Message (Optional but Recommended)

In each group, type `/post_onboarding` as an admin. Pin the message the bot creates — this gives users a permanent, visible way to agree at any time.

## Admin Commands

| Command | Description |
|---|---|
| `/whoagreed` | List users who have agreed to the current CoC version in this group |
| `/setversion <v>` | Bump CoC version — all users must re-agree |
| `/post_onboarding` | Post a pinnable message with a permanent Agree button |

## Local Development

```bash
git clone https://github.com/YOUR_USERNAME/telegram_coc_bot.git
cd telegram_coc_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```
BOT_TOKEN=your_bot_token
ADMIN_IDS=your_user_id
COC_VERSION=1.0
COC_LINK=https://your-coc-url
DATABASE_URL=postgresql://localhost/coc_bot
DRY_RUN=true
```

Run:
```bash
python3 bot.py
```

For local development, the bot falls back to polling when no `WEBHOOK_URL` is set.

## Known Limitations

- **Message visibility**: Telegram delivers messages to all clients before the bot can delete them (~0.5–2s). Mobile push notifications fire with the message content before the delete. This is a hard Telegram API constraint.
- **DMs blocked**: Some users have privacy settings that prevent unknown bots from DMing them. The bot falls back to an inline group message tagging the user.

## Dry-Run Mode

Set `DRY_RUN=true` to log all enforcement actions without actually restricting users or deleting messages. Agreements are still recorded. Use this when first adding the bot to a production group.

## Documentation

- **`High level overview.md`** — Architecture and requirements
- **`tasks.md`** — Developer task breakdown
- **`TESTING.md`** — Testing strategies and checklist
