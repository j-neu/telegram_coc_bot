# Railway Deployment Guide

Complete guide to deploy your Telegram CoC Bot to Railway.app with SQLite database.

## Why Railway?

- Free tier (500 hours/month - plenty for a bot)
- Automatic deployments from GitHub
- Built-in environment variable management
- SQLite database works out of the box (persists with Railway volumes)
- No credit card required for free tier
- Super easy setup

## Prerequisites

1. GitHub account
2. Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
3. Your Telegram User ID (from [@userinfobot](https://t.me/userinfobot))
4. Code of Conduct URL

## Step-by-Step Deployment

### Step 1: Push Code to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit - Telegram CoC Bot"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Step 2: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Login" and sign in with GitHub
3. Authorize Railway to access your GitHub account

### Step 3: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository from the list
4. Railway will detect it's a Python project automatically

### Step 4: Configure Environment Variables

In the Railway dashboard:

1. Click on your deployed service
2. Go to the "Variables" tab
3. Click "+ New Variable"
4. Add these variables one by one:

| Variable | Value | Example |
|----------|-------|---------|
| `BOT_TOKEN` | Your bot token from BotFather | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `ADMIN_IDS` | Your Telegram user ID(s) | `123456789` or `123456789,987654321` |
| `COC_VERSION` | Version number | `1.0` |
| `COC_LINK` | URL to your Code of Conduct | `https://docs.google.com/document/d/YOUR_DOC_ID` |
| `STORAGE_TYPE` | Database type | `sqlite` |
| `DRY_RUN` | Testing mode (optional) | `false` |

**Important Notes:**
- No spaces in `ADMIN_IDS` (use commas only: `123,456,789`)
- Use `DRY_RUN=true` for testing without restricting users
- `STORAGE_TYPE=sqlite` is recommended (no Google Sheets needed!)

### Step 5: Enable Persistent Storage (CRITICAL!)

SQLite database needs persistent storage or it will reset on each deploy.

1. In Railway dashboard, click your service
2. Go to "Settings" tab
3. Scroll to "Volumes"
4. Click "Add Volume"
5. Configure:
   - **Mount Path:** `/app/data`
   - Click "Add"

6. Update one environment variable:
   - Add `DATABASE_PATH` = `/app/data/coc_agreements.db`

### Step 6: Deploy!

Railway automatically deploys when you push to GitHub. To deploy now:

1. Click "Deploy" in the Railway dashboard
2. Or push any commit to your GitHub repository

### Step 7: Monitor Deployment

1. Go to "Deployments" tab
2. Click on the latest deployment
3. View logs to ensure bot started successfully
4. Look for: `Bot starting...` and `Storage type: sqlite`

### Step 8: Test Your Bot

1. Add the bot to a test Telegram group
2. Make the bot an admin with these permissions:
   - ✅ Delete messages
   - ✅ Ban users
   - ✅ **Restrict members (REQUIRED)**
3. Invite a test user to the group
4. Verify they get restricted and receive the CoC message
5. Click "Agree" and verify they can now post

## Managing Your Deployment

### View Logs

```
Railway Dashboard → Your Service → Deployments → Click latest → View Logs
```

Look for:
- `Storage type: sqlite` - Confirms using SQLite
- `Database initialized successfully` - Database is ready
- `Bot starting...` - Bot is running
- `[DRY RUN]` messages if testing with DRY_RUN=true

### Update Environment Variables

1. Go to Variables tab
2. Click variable to edit
3. Save - Railway will automatically redeploy

### Redeploy After Code Changes

```bash
git add .
git commit -m "Update bot features"
git push
```

Railway automatically detects the push and redeploys.

### Manual Redeploy

Railway Dashboard → Settings → Click "Redeploy"

## Testing Workflow

### Phase 1: Dry-Run Testing

1. Set `DRY_RUN=true` in Railway variables
2. Add bot to your production group
3. Monitor logs - see what would happen without restrictions
4. Test admin commands
5. Let volunteers click "Agree" to test the flow

### Phase 2: Live Testing (New Members Only)

1. Set `DRY_RUN=false`
2. Only NEW members will be restricted
3. Existing members unaffected
4. Monitor a few new joins to ensure it works

### Phase 3: Full Rollout

1. Use `/sendcode` in the group to prompt existing members
2. They'll see the CoC message but won't be restricted
3. They can agree at their convenience

## Viewing Agreement Data

Use these admin commands in your Telegram group:

- `/whoagreed` - List all users who agreed.
- `/scan` - Learn how to onboard existing members.
- `/restrict_existing` - Restrict all unagreed members.
- `/sendcode_group` - Send a public CoC prompt to the group.
- `/sendcode_dm` - Privately message all unagreed members.
- `/export` - View recent agreements and statistics.

## Database Backup

Railway doesn't automatically backup SQLite databases. To backup:

### Option 1: Export via Bot

Use `/export` command - shows recent data in Telegram

### Option 2: Manual Backup (Advanced)

Use Railway CLI to download database:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Download database file
railway run cat /app/data/coc_agreements.db > backup.db
```

## Troubleshooting

### Bot not starting

**Check logs for errors:**
- Missing `BOT_TOKEN`? Add it to Variables
- `Storage type: sheets` but want sqlite? Set `STORAGE_TYPE=sqlite`

### Database resets on deploy

**Persistent storage not configured:**
- Add Volume at `/app/data` (see Step 5)
- Set `DATABASE_PATH=/app/data/coc_agreements.db`

### Bot can't restrict users

**Permission issues:**
- Make bot admin in Telegram group
- Enable "Restrict members" permission
- Check logs for `Failed to restrict user` errors

### "This message is no longer available" error

**Bot doesn't have delete permission:**
- Give bot "Delete messages" permission in group settings

## Cost & Limits

**Railway Free Tier:**
- 500 execution hours/month
- $5 free credit/month
- More than enough for a single bot

**Usage:**
- Your bot runs 24/7 = ~720 hours/month
- With free tier, you get ~500 hours
- **Solution:** Railway gives $5 credit = covers the extra ~220 hours

**Bottom line:** Effectively free for a single bot!

## Advanced: Multiple Bots

If you run multiple bots and exceed free tier:

**Option 1:** Upgrade Railway
- $5/month for additional usage

**Option 2:** Split across services
- Deploy different bots to different platforms

## Need Google Sheets Instead?

If you prefer Google Sheets over SQLite:

1. Set `STORAGE_TYPE=sheets`
2. Set `SHEET_ID=your_sheet_id`
3. Set `GOOGLE_CREDENTIALS=<paste entire credentials.json content>`
4. See main README for Google Sheets setup

## Security Notes

- Never commit `.env` to git (already in `.gitignore`)
- Environment variables in Railway are encrypted
- Rotate your `BOT_TOKEN` periodically via BotFather
- Keep `ADMIN_IDS` updated

## Support

**Railway Issues:**
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

**Bot Issues:**
- Check logs in Railway dashboard
- Test with `DRY_RUN=true` first
- Verify bot permissions in Telegram group

## Quick Reference

**Essential URLs:**
- Railway Dashboard: https://railway.app/dashboard
- Get Bot Token: [@BotFather](https://t.me/BotFather)
- Get User ID: [@userinfobot](https://t.me/userinfobot)

**Key Commands:**
- `/whoagreed` - View who agreed.
- `/scan` - Get instructions for onboarding existing members.
- `/restrict_existing` - Restrict all unagreed members.
- `/sendcode_dm` - Privately prompt all unagreed members.
- `/export` - Export data.

**Key Variables:**
- `BOT_TOKEN` - From BotFather
- `ADMIN_IDS` - Your user ID
- `STORAGE_TYPE=sqlite` - Use database
- `DRY_RUN=true` - Test mode
