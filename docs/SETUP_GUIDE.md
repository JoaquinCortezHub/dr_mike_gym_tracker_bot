# Complete Setup Guide

This is your step-by-step guide to get the Dr. Mike Gym Tracker Bot up and running.

## Overview

You need to set up **three** external services:

1. Telegram Bot (for the chat interface)
2. Google Sheets API (for data storage)
3. AI API - OpenAI or Anthropic (for natural language processing)

**Estimated setup time:** 30-45 minutes

---

## Part 1: Project Setup (5 minutes)

### 1.1 Verify Installation

Make sure you have everything installed:

```bash
# Check Python version (should be 3.13+)
python --version

# Check UV is installed
uv --version
```

### 1.2 Install Dependencies

```bash
cd dr-mike-gym-tracker
uv sync
```

You should see all packages installing successfully.

### 1.3 Create Environment File

```bash
# Copy the example file
cp .env.example .env
```

Now you have an `.env` file that you'll fill in during the next steps.

---

## Part 2: Telegram Bot Setup (10 minutes)

### What you'll get

- A Telegram bot token (looks like `1234567890:ABCdef...`)

### Steps

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` to create a new bot
3. Choose a name and username for your bot
4. Copy the token BotFather gives you
5. Open your `.env` file and add:

   ```env
   TELEGRAM_BOT_TOKEN=paste_your_token_here
   ```

**Detailed instructions:** [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)

---

## Part 3: Google Sheets Setup (15-20 minutes)

### What you'll get
- Google Sheets API credentials file
- Your spreadsheet URL

### Steps Overview

1. Create a Google Cloud project
2. Enable Google Sheets API and Google Drive API
3. Create a service account
4. Download credentials JSON file
5. Share your Google Sheet with the service account

### Steps in Detail

1. **Create Google Cloud Project:**
   - Go to [console.cloud.google.com](https://console.cloud.google.com/)
   - Click "New Project"
   - Name it "Gym Tracker Bot"

2. **Enable APIs:**
   - Navigate to "APIs & Services" > "Library"
   - Search and enable "Google Sheets API"
   - Search and enable "Google Drive API"

3. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Name: `gym-tracker-bot`
   - Role: Editor
   - Create and download JSON key

4. **Save Credentials:**
   - Rename the file to `google_credentials.json`
   - Move it to `data/google_credentials.json`

5. **Share Your Sheet:**
   - Open your Google Sheet
   - Click "Share"
   - Paste the service account email from the JSON file
   - Give it "Editor" permission

6. **Update .env:**

   ```env
   GOOGLE_CREDENTIALS_PATH=data/google_credentials.json
   GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/your_sheet_id/edit
   ```

**Detailed instructions:** [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)

---

## Part 4: AI API Setup (10 minutes)

### Choose Your Provider

You need **either** OpenAI **or** Anthropic (not both).

**Recommendation:**
- **OpenAI** - Cheaper (~$0.50/month), faster setup
- **Anthropic** - Better quality, slightly more expensive (~$2/month)

### Option A: OpenAI Setup

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Create account and add payment method
3. Create API key
4. Update `.env`:
   ```env
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-your-key-here
   OPENAI_MODEL=gpt-4o-mini
   ```

### Option B: Anthropic Setup

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Create account and add credits ($5 minimum)
3. Create API key
4. Update `.env`:
   ```env
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ANTHROPIC_MODEL=claude-3-5-sonnet-latest
   ```

**Detailed instructions:** [AI_API_SETUP.md](AI_API_SETUP.md)

---

## Part 5: Final Configuration Check

### Verify Your .env File

Your `.env` file should look like this:

```env
# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdef...

# Google Sheets
GOOGLE_CREDENTIALS_PATH=data/google_credentials.json
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/...

# AI Provider (choose one)
AI_PROVIDER=openai

# OpenAI (if using)
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# OR Anthropic (if using)
# ANTHROPIC_API_KEY=sk-ant-...
# ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

### Verify File Structure

```
data/
  ├── exercises.csv              ✅ (should exist)
  └── google_credentials.json    ✅ (you created this)

.env                             ✅ (you created this)
```

---

## Part 6: Run the Bot!

### Start the Bot

```bash
uv run python main.py
```

### Expected Output

```
🏋️ Dr. Mike's Gym Tracker Bot
==================================================
AI Provider: openai
Model: gpt-4o-mini
==================================================
📊 Loading exercise database...
✅ Loaded 30 exercises
👤 Initializing user state manager...
✅ Managing 0 users
📝 Connecting to Google Sheets...
✅ Connected to Google Sheets
🤖 Initializing AI agent...
✅ AI agent ready
📱 Starting Telegram bot...
✅ Bot is running! Press Ctrl+C to stop.
==================================================
```

If you see this, **congratulations!** Your bot is running! 🎉

---

## Part 7: Test the Bot

### 7.1 Find Your Bot

1. Open Telegram
2. Search for your bot username (the one you created with BotFather)
3. Start a chat

### 7.2 Test Basic Commands

```
You: /start
Bot: (Should send welcome message)

You: /setweek 1
Bot: ✅ Set to Week 1

You: /setday 1
Bot: (Shows Day 1 exercises)

You: 3 sets of 10 bench press at 60kg
Bot: (Should process and log to Google Sheets)
```

### 7.3 Verify Google Sheets

1. Open your Google Sheet
2. Navigate to Day 1
3. Check Week 1 columns
4. You should see your workout logged!

---

## Troubleshooting

### Bot doesn't respond

**Check:**
- Is `main.py` still running in your terminal?
- Did you use the correct bot username in Telegram?
- Is the TELEGRAM_BOT_TOKEN correct?

**Fix:** Restart the bot and try again

### "Can't connect to Google Sheets"

**Check:**
- Is `google_credentials.json` in the `data/` folder?
- Did you share the sheet with the service account email?
- Is the GOOGLE_SHEET_URL correct?

**Fix:** See [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) troubleshooting section

### "Invalid API key" for AI

**Check:**
- Did you copy the entire API key?
- Are there extra spaces in the `.env` file?
- Do you have credits/billing set up?

**Fix:** See [AI_API_SETUP.md](AI_API_SETUP.md) troubleshooting section

### "Exercise not found"

**Check:**
- Is the exercise in your CSV file?
- Try being more specific with the exercise name

**Fix:** Use `/today` to see available exercises for the day

---

## Common Issues and Solutions

### Issue: Bot is slow to respond

**Cause:** AI API might be slow
**Solution:** This is normal for the first request. Subsequent requests will be faster.

### Issue: Wrong exercise logged

**Cause:** AI misunderstood the exercise name
**Solution:** Be more specific, or use the exact exercise name from `/today`

### Issue: Can't find service account email

**Cause:** Need to look in the credentials file
**Solution:**
```bash
# On Windows PowerShell:
Select-String -Path data/google_credentials.json -Pattern "client_email"

# On Mac/Linux:
grep "client_email" data/google_credentials.json
```

---

## Next Steps

Once everything is working:

1. **Set your current week:** `/setweek 1`
2. **Set your training day:** `/setday 1`
3. **Start logging workouts!**
4. **Use `/help`** to see all commands
5. **Check Google Sheets** after each workout to verify logging

---

## Security Reminders

- ✅ `.env` is in `.gitignore` - never commit it!
- ✅ `google_credentials.json` is in `.gitignore` - never share it!
- ✅ Keep your API keys private
- ✅ Set spending limits on AI APIs
- ✅ Rotate keys periodically

---

## Getting Help

If you encounter issues not covered here:

1. Check the detailed setup guides in the `docs/` folder
2. Verify all environment variables are set correctly
3. Check that all services (Telegram, Google, AI) are working independently
4. Look for error messages in the terminal where the bot is running

---

## Summary Checklist

Before running the bot, verify:

- [ ] Python 3.13+ installed
- [ ] UV package manager installed
- [ ] Dependencies installed (`uv sync`)
- [ ] `.env` file created and filled out
- [ ] Telegram bot created and token added to `.env`
- [ ] Google Cloud project created
- [ ] Google Sheets API & Drive API enabled
- [ ] Service account created and JSON downloaded to `data/`
- [ ] Google Sheet shared with service account
- [ ] AI API key created and added to `.env`
- [ ] Bot runs without errors (`uv run python main.py`)
- [ ] Bot responds in Telegram
- [ ] Workouts log to Google Sheets

If all checkboxes are checked, you're ready to track your gains! 💪

---

**Need more help?** Check the individual setup guides:
- [Telegram Setup](TELEGRAM_SETUP.md)
- [Google Sheets Setup](GOOGLE_SHEETS_SETUP.md)
- [AI API Setup](AI_API_SETUP.md)
