# Telegram Code of Conduct Agreement Bot

A Telegram bot that ensures every group member explicitly agrees to the group's Code of Conduct before being allowed to post messages.

## Features

- **New Member Onboarding**: Automatically restricts new members until they agree to the CoC
- **Existing Member Prompts**: Allows admins to send CoC agreement requests to all members
- **Google Sheets Integration**: Tracks all agreements with timestamps and version control
- **Admin Commands**: Comprehensive admin tools for monitoring and managing agreements
- **Fallback Mechanisms**: DM with group message fallback for user notifications
- **Version Control**: Track different CoC versions and require re-agreement when updated

## Prerequisites

- Python 3.10 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A Google Service Account with Sheets API access
- A Google Sheet for storing agreement data

## Setup Instructions

### 1. Create Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Save the bot token you receive
4. Add your bot as an admin to your Telegram group with these permissions:
   - Delete messages
   - Ban users
   - Restrict members (REQUIRED)

### 2. Set Up Google Sheets

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create a Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and click "Create"
   - Grant the service account "Editor" role
   - Click "Done"
5. Create and download the JSON key:
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select "JSON" and click "Create"
   - Save the downloaded file as `credentials.json` in the project directory
6. Create a Google Sheet:
   - Go to [Google Sheets](https://sheets.google.com)
   - Create a new spreadsheet
   - Copy the Sheet ID from the URL (the long string between `/d/` and `/edit`)
   - Share the sheet with the service account email (found in `credentials.json` under `client_email`) with Editor permissions

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   SHEET_ID=your_google_sheet_id_here
   ADMIN_IDS=123456789,987654321  # Your Telegram user ID(s)
   COC_VERSION=1.0
   COC_LINK=https://example.com/code-of-conduct
   ```

   **To find your Telegram user ID:**
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - It will reply with your user ID

### 5. Run the Bot

```bash
python bot.py
```

The bot will start polling for updates and is ready to use!

## Usage

### For New Members

1. When a new member joins the group, they are automatically restricted
2. They receive a message (DM or in-group) with the CoC and an "Agree" button
3. After clicking "Agree", they can post messages in the group

### Admin Commands

All admin commands must be sent in the group where the bot is an admin:

| Command | Description |
|---------|-------------|
| `/start` | Send CoC agreement prompt (can be used by anyone) |
| `/whoagreed` | List all users who have agreed to the current CoC version |
| `/whohasnotagreed` | Check which members haven't agreed yet |
| `/sendcode` | Send CoC agreement request to all group members |
| `/setversion <version>` | Display instructions for updating CoC version |
| `/export` | Get link to the Google Sheet with all agreement data |

### Agreement Data

The bot stores the following information in Google Sheets for each agreement:

- User ID (Telegram)
- Username
- Full Name
- Group ID
- Group Name
- Agreement Timestamp (UTC)
- CoC Version

## Deployment

### Option 1: PythonAnywhere

1. Create a free account at [PythonAnywhere](https://www.pythonanywhere.com)
2. Upload your code and `credentials.json`
3. Set up a virtual environment and install dependencies
4. Create a scheduled task to run `python bot.py`

### Option 2: Render

1. Create a free account at [Render](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set environment variables in Render dashboard
5. Upload `credentials.json` as a secret file

### Option 3: VPS (Recommended for production)

1. Set up a VPS (DigitalOcean, Linode, AWS EC2, etc.)
2. Install Python 3.10+
3. Clone your repository
4. Install dependencies
5. Set up a systemd service to run the bot:

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
WorkingDirectory=/path/to/telegram_coc_bot
ExecStart=/usr/bin/python3 /path/to/telegram_coc_bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable coc-bot
sudo systemctl start coc-bot
```

## Security Notes

- Never commit `.env` or `credentials.json` to version control
- Keep your bot token secret
- Only share the Google Sheet with the service account email
- Regularly review admin user IDs in the configuration

## Troubleshooting

### Bot can't restrict users
- Ensure the bot is an admin in the group
- Verify "Restrict members" permission is enabled for the bot

### Google Sheets connection fails
- Check that `credentials.json` is in the project directory
- Verify the service account has Editor access to the sheet
- Confirm the SHEET_ID in `.env` is correct

### Users can't receive DMs
- This is normal - Telegram requires users to start a conversation with the bot first
- The bot will fallback to sending a message in the group

### Bot doesn't respond to commands
- Verify the bot is running (`python bot.py`)
- Check that you're using commands in a group where the bot is admin
- For admin commands, ensure your user ID is in ADMIN_IDS

## License

This project is provided as-is for community use.

## Support

For issues or questions, please review the configuration and logs first. Common issues are usually related to:
- Bot permissions in the Telegram group
- Google Sheets API access
- Environment variable configuration
