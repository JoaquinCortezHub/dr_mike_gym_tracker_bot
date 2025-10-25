# Telegram Bot Setup Guide

This guide will walk you through creating a Telegram bot and obtaining your bot token.

## Step 1: Open BotFather

1. Open Telegram on your phone or desktop
2. Search for **@BotFather** (it's an official Telegram bot with a blue checkmark)
3. Start a chat with BotFather

## Step 2: Create Your Bot

1. Send the command: `/newbot`
2. BotFather will ask you to choose a name for your bot
   - Example: `Dr Mike Gym Tracker`
3. Then choose a username for your bot (must end in 'bot')
   - Example: `DrMikeGymTrackerBot` or `my_gym_tracker_bot`

## Step 3: Get Your Token

1. After successful creation, BotFather will send you a message containing your **HTTP API token**
2. It looks like this: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
3. **IMPORTANT:** Keep this token secret! Anyone with this token can control your bot

## Step 4: Configure Your Bot (Optional but Recommended)

You can customize your bot with these BotFather commands:

### Set Bot Description

```
/setdescription
```
Choose your bot, then send:
```
AI-powered gym workout tracker with progressive overload. Log exercises with natural language and track your progress!
```

### Set Bot About Text
```
/setabouttext
```
Choose your bot, then send:
```
Track your gym workouts with AI. I help you log exercises and follow progressive overload principles.
```

### Set Bot Commands
```
/setcommands
```
Choose your bot, then paste this list:
```
start - Start the bot and get welcome message
help - Show all available commands
setday - Set your current workout day (1-4)
setweek - Set your current week (1-6)
status - View your current week and day
today - See today's workout schedule
week - View this week's progress
schedule - View workout schedule for any day
nextweek - Move to the next week
```

## Step 5: Add Token to Your Project

1. Copy your bot token from BotFather
2. Open the `.env` file in your project (create it from `.env.example` if needed)
3. Add your token:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

## Step 6: Test Your Bot

1. Search for your bot in Telegram using the username you created
2. Start a chat with your bot
3. It won't respond yet until you run the application!

## Troubleshooting

### "Username is already taken"
- Try a different username
- Add numbers or underscores to make it unique

### "Can't find my bot in Telegram"
- Make sure you're searching for the exact username
- The username should start with @
- Example: @DrMikeGymTrackerBot

### "Bot token invalid"
- Double-check you copied the entire token
- Make sure there are no extra spaces
- The token should have a colon (:) in the middle

## Security Tips

- Never share your bot token publicly
- Don't commit the `.env` file to git
- If your token is exposed, revoke it with `/revoke` in BotFather and create a new one
- Keep the `.env.example` file without actual values for reference

## Next Steps

Once your bot token is configured, proceed to:
- [Google Sheets Setup Guide](GOOGLE_SHEETS_SETUP.md)
- [AI API Setup Guide](AI_API_SETUP.md)
