# Raspberry Pi Deployment Guide

Deploy your Telegram CoC Bot on a Raspberry Pi - perfect for self-hosting!

## Why Raspberry Pi?

- ✅ One-time cost (~$35-75)
- ✅ Very low power consumption (~$5/year electricity)
- ✅ Full control over your data
- ✅ No monthly fees
- ✅ Perfect for a simple bot
- ✅ Runs 24/7 reliably

## Prerequisites

### Hardware
- Raspberry Pi (any model with network)
  - **Pi Zero 2 W** - $15 (sufficient for this bot!)
  - **Pi 3/4/5** - $35-75 (more powerful, recommended)
- MicroSD card (8GB minimum, 16GB+ recommended)
- Power supply
- Internet connection (WiFi or Ethernet)

### Software You'll Need
- Raspberry Pi OS (formerly Raspbian)
- SSH access or keyboard/monitor for setup

## Step-by-Step Setup

### Step 1: Install Raspberry Pi OS

1. **Download Raspberry Pi Imager:**
   - https://www.raspberrypi.com/software/

2. **Flash SD Card:**
   - Insert SD card into your computer
   - Open Raspberry Pi Imager
   - Choose OS: "Raspberry Pi OS Lite (64-bit)" (no desktop needed)
   - Choose Storage: Your SD card
   - Click Settings (⚙️):
     - ✅ Set hostname: `telegram-bot.local`
     - ✅ Enable SSH (use password authentication)
     - ✅ Set username/password: `pi` / your_password
     - ✅ Configure WiFi (if using WiFi)
     - ✅ Set timezone
   - Click "Write"

3. **Boot Raspberry Pi:**
   - Insert SD card into Pi
   - Connect power
   - Wait 2-3 minutes for first boot

### Step 2: Connect to Your Pi

**Option A: SSH (Recommended)**

From your computer:
```bash
# On Windows (use PowerShell or install PuTTY)
ssh pi@telegram-bot.local

# On Mac/Linux
ssh pi@telegram-bot.local

# Enter password when prompted
```

**Option B: Direct Connection**
- Connect keyboard, mouse, and monitor to Pi
- Login with username `pi` and your password

### Step 3: Update System

```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip git
```

### Step 4: Clone Your Repository

**Option A: If code is on GitHub**
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/telegram_coc_bot.git
cd telegram_coc_bot
```

**Option B: Transfer files from your computer**

On your computer:
```bash
# Transfer entire folder to Pi
scp -r "C:\Users\jakob\Documents\Cursor projects\telegram_coc_bot" pi@telegram-bot.local:~/
```

Then SSH into Pi:
```bash
ssh pi@telegram-bot.local
cd telegram_coc_bot
```

### Step 5: Install Python Dependencies

```bash
# Install dependencies
pip3 install -r requirements.txt

# Verify installation
python3 -c "import telegram; print('Success!')"
```

### Step 6: Configure Environment

Create your `.env` file:
```bash
nano .env
```

Add your configuration:
```
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=your_user_id_here
COC_VERSION=1.0
COC_LINK=https://your-coc-link-here
STORAGE_TYPE=sqlite
DRY_RUN=false
```

**To save in nano:**
- Press `Ctrl+O` (WriteOut)
- Press `Enter` (confirm)
- Press `Ctrl+X` (exit)

### Step 7: Test the Bot

```bash
# Run bot manually to test
python3 bot.py
```

You should see:
```
Storage type: sqlite
Using database at: coc_agreements.db
Database initialized successfully
Bot starting...
```

**Test it:**
1. Send `/start` to your bot on Telegram
2. Verify it responds
3. Press `Ctrl+C` to stop

If it works, proceed to make it run automatically!

### Step 8: Create Systemd Service (Auto-start on Boot)

Create a service file:
```bash
sudo nano /etc/systemd/system/telegram-coc-bot.service
```

Paste this configuration:
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

**Save and exit** (`Ctrl+O`, `Enter`, `Ctrl+X`)

### Step 9: Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable telegram-coc-bot

# Start service now
sudo systemctl start telegram-coc-bot

# Check status
sudo systemctl status telegram-coc-bot
```

You should see:
```
● telegram-coc-bot.service - Telegram Code of Conduct Bot
   Active: active (running)
```

### Step 10: View Logs

```bash
# View real-time logs
sudo journalctl -u telegram-coc-bot -f

# View last 50 lines
sudo journalctl -u telegram-coc-bot -n 50

# Press Ctrl+C to exit log view
```

## Managing Your Bot

### Check Status
```bash
sudo systemctl status telegram-coc-bot
```

### Stop Bot
```bash
sudo systemctl stop telegram-coc-bot
```

### Start Bot
```bash
sudo systemctl start telegram-coc-bot
```

### Restart Bot
```bash
sudo systemctl restart telegram-coc-bot
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u telegram-coc-bot -f

# Last 100 lines
sudo journalctl -u telegram-coc-bot -n 100
```

### Update Bot Code

```bash
# Stop bot
sudo systemctl stop telegram-coc-bot

# Navigate to bot directory
cd ~/telegram_coc_bot

# Pull latest changes (if using git)
git pull

# Or edit files directly
nano bot.py

# Restart bot
sudo systemctl start telegram-coc-bot
```

## Database Backup

### Manual Backup

```bash
# Create backup directory
mkdir -p ~/backups

# Copy database with timestamp
cp ~/telegram_coc_bot/coc_agreements.db ~/backups/coc_agreements_$(date +%Y%m%d_%H%M%S).db

# List backups
ls -lh ~/backups/
```

### Automatic Daily Backup

Create a backup script:
```bash
nano ~/backup-bot-db.sh
```

Add this content:
```bash
#!/bin/bash
BACKUP_DIR="/home/pi/backups"
DB_PATH="/home/pi/telegram_coc_bot/coc_agreements.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_PATH $BACKUP_DIR/coc_agreements_$TIMESTAMP.db

# Keep only last 30 backups
cd $BACKUP_DIR
ls -t coc_agreements_*.db | tail -n +31 | xargs rm -f
```

Make it executable:
```bash
chmod +x ~/backup-bot-db.sh
```

Add to crontab (runs daily at 3 AM):
```bash
crontab -e
```

Add this line:
```
0 3 * * * /home/pi/backup-bot-db.sh
```

## Accessing Database from Your Computer

### Option 1: SCP (Secure Copy)

From your computer:
```bash
# Download database
scp pi@telegram-bot.local:~/telegram_coc_bot/coc_agreements.db ./coc_backup.db

# Open with SQLite browser on your computer
```

### Option 2: Export via Bot

Use the `/export` command in Telegram to view data.

## Network Configuration

### Static IP (Recommended)

Make your Pi always accessible at the same IP:

```bash
sudo nano /etc/dhcpcd.conf
```

Add at the end (adjust for your network):
```
interface wlan0  # Use 'eth0' for ethernet
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Reboot:
```bash
sudo reboot
```

### Access from Outside Home (Advanced)

If you want to SSH from outside your home network:

1. **Set up port forwarding** on your router:
   - Forward port 22 (SSH) to your Pi's IP
   - Or use a different port for security (e.g., 2222)

2. **Use Dynamic DNS** (if you don't have static IP):
   - Services: No-IP, DuckDNS, Dynu
   - Gives you a domain like `mypi.duckdns.org`

3. **Security:**
   - Change default password: `passwd`
   - Use SSH keys instead of password
   - Consider installing `fail2ban`

## Power & Reliability

### Handle Power Outages

The bot auto-starts on boot, so it recovers automatically from power outages!

### UPS (Uninterruptible Power Supply)

For maximum reliability:
- Get a small UPS (~$50)
- Gives 30-60 min runtime during outages
- Prevents SD card corruption

### Monitor Uptime

```bash
# Check how long Pi has been running
uptime

# Check bot uptime
sudo systemctl status telegram-coc-bot
```

## Troubleshooting

### Bot not starting
```bash
# Check logs for errors
sudo journalctl -u telegram-coc-bot -n 50

# Common issues:
# - Wrong BOT_TOKEN in .env
# - Missing dependencies: pip3 install -r requirements.txt
# - Database permission issues: check file permissions
```

### Can't SSH into Pi
```bash
# From another computer, ping the Pi
ping telegram-bot.local

# If doesn't respond:
# - Check Pi is powered on (green LED on)
# - Check network connection
# - Try IP address instead: ping 192.168.1.100
# - Connect monitor/keyboard to Pi
```

### Database errors
```bash
# Check database file exists
ls -l ~/telegram_coc_bot/coc_agreements.db

# Check permissions
chmod 644 ~/telegram_coc_bot/coc_agreements.db
```

### High memory usage
```bash
# Check memory
free -h

# If low, add swap space:
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE to 1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## Performance

This bot is very lightweight:
- **RAM:** ~50-100 MB
- **CPU:** <1% most of the time
- **Storage:** Database grows ~1KB per user agreement
- **Network:** Minimal (only when users interact)

Even a **Raspberry Pi Zero 2 W** can handle this easily!

## Cost Comparison

| Solution | Setup Cost | Monthly Cost | Total Year 1 |
|----------|-----------|--------------|--------------|
| **Raspberry Pi Zero 2 W** | $15 + SD card ($10) | ~$0.42 electricity | ~$30 |
| **Raspberry Pi 4** | $55 + SD card ($10) | ~$0.50 electricity | ~$71 |
| **Railway/Render** | $0 | $5-7 | $60-84 |
| **VPS** | $0 | $5-6 | $60-72 |

**Winner for long-term:** Raspberry Pi (pays for itself in ~6 months!)

## Security Best Practices

```bash
# 1. Change default password
passwd

# 2. Update regularly
sudo apt update && sudo apt upgrade -y

# 3. Install fail2ban (blocks brute force)
sudo apt install fail2ban -y

# 4. Firewall (allow only SSH)
sudo apt install ufw -y
sudo ufw allow 22
sudo ufw enable

# 5. Keep logs clean
sudo journalctl --vacuum-time=7d
```

## Remote Management

### VNC (Desktop Access)

If you want GUI access:
```bash
sudo apt install realvnc-vnc-server -y
sudo raspi-config
# Interface Options -> VNC -> Enable
```

Use VNC Viewer on your computer to connect.

### VS Code Remote SSH

Code directly on Pi from VS Code:
1. Install "Remote - SSH" extension in VS Code
2. Connect to `pi@telegram-bot.local`
3. Edit files directly on Pi!

## Monitoring

### Simple Status Check Script

Create a monitoring script:
```bash
nano ~/check-bot.sh
```

```bash
#!/bin/bash
if ! systemctl is-active --quiet telegram-coc-bot; then
    echo "Bot is down! Restarting..."
    sudo systemctl restart telegram-coc-bot
fi
```

Make executable and add to cron:
```bash
chmod +x ~/check-bot.sh
crontab -e
```

Add (checks every 5 minutes):
```
*/5 * * * * /home/pi/check-bot.sh
```

## Summary

Your Raspberry Pi is now:
- ✅ Running your bot 24/7
- ✅ Auto-starts on boot
- ✅ Auto-restarts if crashed
- ✅ Backing up database daily
- ✅ Accessible via SSH
- ✅ Costing ~$0.50/month in electricity

**Total setup time:** ~30 minutes
**Total cost:** ~$25-65 one-time + $6/year electricity

Enjoy your self-hosted Telegram bot! 🎉
