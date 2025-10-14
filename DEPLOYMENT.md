# Deployment Guide

## Recommended Hosting Options (Ranked)

### 1. Railway.app (BEST - Easiest + Free Tier)

**Pros:**
- Free tier available (500 hours/month)
- Supports long-running processes
- Easy GitHub integration
- Built-in environment variables
- Automatic restarts

**Setup:**

1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables in Railway dashboard:
   - `BOT_TOKEN`
   - `SHEET_ID`
   - `ADMIN_IDS`
   - `COC_VERSION`
   - `COC_LINK`
   - `DRY_RUN` (optional)

5. Upload `credentials.json`:
   - In Railway project settings, go to "Variables"
   - Add a new variable called `GOOGLE_CREDENTIALS`
   - Paste the entire contents of your `credentials.json` file
   - Update `config.py` to read from this variable (see Railway section below)

6. Railway will automatically detect Python and run your bot

**Cost:** Free tier is usually sufficient for small-medium bots

---

### 2. Render.com (Great Alternative)

**Pros:**
- Free tier (with limitations)
- Simple setup
- Automatic deploys from GitHub
- Supports background workers

**Setup:**

1. Create account at [render.com](https://render.com)
2. Click "New +" → "Background Worker"
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Add environment variables in dashboard
6. Upload `credentials.json` as a secret file

**Cost:** Free tier available (may spin down after inactivity)

---

### 3. DigitalOcean App Platform

**Pros:**
- Reliable
- $5/month tier
- Good performance
- Easy scaling

**Setup:**

1. Create account at [digitalocean.com](https://www.digitalocean.com/products/app-platform)
2. Create new app from GitHub
3. Select "Worker" type (not Web Service)
4. Set run command: `python bot.py`
5. Add environment variables
6. Upload credentials.json

**Cost:** Starts at $5/month

---

### 4. PythonAnywhere (Traditional Hosting)

**Pros:**
- Python-specific hosting
- Free tier available
- Easy to use

**Cons:**
- Free tier has limitations (scheduled tasks only run once/day)
- Need paid tier ($5/month) for "always-on" tasks

**Setup:**

1. Create account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your code via Files tab or git clone
3. Upload `credentials.json`
4. Create a new "Always-on task" (requires paid plan)
5. Set it to run `python /path/to/bot.py`

**Cost:** Free tier limited, $5/month for always-on

---

### 5. VPS (Most Control)

**Providers:** DigitalOcean, Linode, Vultr, AWS EC2, Google Cloud

**Pros:**
- Full control
- Best for production
- Can run multiple bots

**Cons:**
- Requires Linux knowledge
- More setup required

**Setup:**

1. Create a VPS (Ubuntu 22.04 recommended)
2. SSH into server
3. Install Python 3.10+:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git -y
   ```

4. Clone your repository:
   ```bash
   git clone <your-repo-url>
   cd telegram_coc_bot
   ```

5. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

6. Create `.env` file:
   ```bash
   nano .env
   # Add your configuration
   ```

7. Upload `credentials.json` (via SCP or nano)

8. Create systemd service for auto-restart:
   ```bash
   sudo nano /etc/systemd/system/coc-bot.service
   ```

   ```ini
   [Unit]
   Description=Telegram CoC Bot
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/home/your_username/telegram_coc_bot
   ExecStart=/usr/bin/python3 /home/your_username/telegram_coc_bot/bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

9. Enable and start service:
   ```bash
   sudo systemctl enable coc-bot
   sudo systemctl start coc-bot
   sudo systemctl status coc-bot
   ```

10. View logs:
    ```bash
    sudo journalctl -u coc-bot -f
    ```

**Cost:** Starts at $4-6/month

---

## What About Vercel?

**Vercel is NOT recommended** for this bot because:

- Designed for serverless functions (short-lived)
- Not suitable for long-running processes
- Would require webhook implementation (more complex)
- Function timeouts would interrupt the bot

**If you really want serverless:**
You'd need to refactor to use webhooks instead of polling. This requires:
- Converting to webhook-based updates
- HTTPS domain
- Handling cold starts
- More complex error handling

---

## Quick Comparison Table

| Platform | Free Tier | Ease of Use | Best For |
|----------|-----------|-------------|----------|
| **Railway** | ✅ 500hrs/mo | ⭐⭐⭐⭐⭐ | Best choice for most users |
| **Render** | ✅ Limited | ⭐⭐⭐⭐ | Great alternative |
| **DigitalOcean** | ❌ $5/mo | ⭐⭐⭐⭐ | Production apps |
| **PythonAnywhere** | ⚠️ Limited | ⭐⭐⭐ | Python-focused devs |
| **VPS** | ❌ $4-6/mo | ⭐⭐ | Advanced users |
| **Vercel** | ❌ Not suitable | ❌ | Don't use |

---

## My Recommendation

**For your use case (large group CoC bot):**

1. **Start with Railway.app** - Free, easy, perfect for this
2. **Upgrade to DigitalOcean App Platform** if you need more reliability
3. **Use a VPS** if you want to run multiple bots or have full control

---

## Railway Setup (Detailed)

Since Railway is the best option, here's a complete setup:

### Step 1: Prepare Your Code

Add `credentials.json` handling for Railway:

Create a new file `get_credentials.py`:

```python
import os
import json

def get_google_credentials():
    """Get Google credentials from environment or file."""
    # Try to get from environment variable (Railway)
    creds_json = os.getenv('GOOGLE_CREDENTIALS')
    if creds_json:
        # Write to temporary file
        with open('credentials.json', 'w') as f:
            f.write(creds_json)
        return 'credentials.json'

    # Otherwise use local file
    return 'credentials.json'
```

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Add bot code"
git push origin main
```

### Step 3: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Python and installs dependencies
6. Add environment variables in the Variables tab
7. Copy entire `credentials.json` content to `GOOGLE_CREDENTIALS` variable
8. Deploy!

### Step 4: Monitor

- View logs in Railway dashboard
- Check for "[DRY RUN]" messages if testing
- Monitor Google Sheets for agreements

---

## Security Notes for All Platforms

- Never commit `.env` or `credentials.json` to git
- Use environment variables for secrets
- Rotate credentials periodically
- Monitor logs for unauthorized access
- Keep dependencies updated: `pip install -U -r requirements.txt`
