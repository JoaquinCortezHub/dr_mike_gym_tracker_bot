# Google Sheets API Setup Guide

This guide will help you set up Google Sheets API access for the gym tracker bot.

## Prerequisites

- A Google account
- Your workout spreadsheet (already created from the CSV)

## Part 1: Create Google Cloud Project

### Step 1: Go to Google Cloud Console

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account

### Step 2: Create a New Project

1. Click the project dropdown at the top of the page
2. Click **"NEW PROJECT"**
3. Enter a project name: `Gym Tracker Bot`
4. Click **"CREATE"**
5. Wait for the project to be created (about 30 seconds)
6. Make sure your new project is selected in the dropdown

## Part 2: Enable Google Sheets API

### Step 1: Enable APIs

1. In the left sidebar, go to **"APIs & Services" > "Library"**
2. Search for **"Google Sheets API"**
3. Click on **"Google Sheets API"**
4. Click **"ENABLE"**
5. Go back to the Library and search for **"Google Drive API"**
6. Click on **"Google Drive API"**
7. Click **"ENABLE"**

## Part 3: Create Service Account

A service account allows your bot to access Google Sheets without manual login.

### Step 1: Create Service Account

1. In the left sidebar, go to **"APIs & Services" > "Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"Service Account"**
4. Fill in the details:
   - **Service account name:** `gym-tracker-bot`
   - **Service account ID:** (auto-filled)
   - **Description:** `Service account for gym tracker bot to access Google Sheets`
5. Click **"CREATE AND CONTINUE"**
6. For "Grant this service account access to project":
   - Select role: **"Editor"**
7. Click **"CONTINUE"**
8. Click **"DONE"** (you can skip the last step)

### Step 2: Create Service Account Key

1. You should now see your service account in the list
2. Click on the service account email (looks like `gym-tracker-bot@project-name.iam.gserviceaccount.com`)
3. Go to the **"KEYS"** tab
4. Click **"ADD KEY" > "Create new key"**
5. Choose **"JSON"** as the key type
6. Click **"CREATE"**
7. A JSON file will download automatically - **save this file securely!**

### Step 3: Save Credentials to Project

1. Rename the downloaded file to `google_credentials.json`
2. Move it to the `data/` folder in your project
3. **IMPORTANT:** Never commit this file to git! It's already in `.gitignore`

## Part 4: Share Google Sheet with Service Account

Your bot needs permission to access your Google Sheet.

### Step 1: Get Service Account Email

1. Open the `google_credentials.json` file
2. Find the `client_email` field
3. Copy the email address (looks like `gym-tracker-bot@project-name.iam.gserviceaccount.com`)

### Step 2: Share Your Google Sheet

1. Open your gym tracking Google Sheet
2. Click the **"Share"** button in the top right
3. Paste the service account email
4. Make sure the permission is set to **"Editor"**
5. **UNCHECK** "Notify people" (no need to send email)
6. Click **"Share"**

## Part 5: Get Your Google Sheet URL

### Step 1: Copy Sheet URL

1. While viewing your Google Sheet, copy the entire URL from the browser
2. It should look like:
   ```
   https://docs.google.com/spreadsheets/d/1abc...xyz/edit#gid=0
   ```
3. Copy this entire URL

### Step 2: Add to Environment Variables

1. Open your `.env` file
2. Add the Google Sheet URL:
   ```
   GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/your_id_here/edit
   ```

## Part 6: Verify Configuration

Your `.env` file should now have:

```env
GOOGLE_CREDENTIALS_PATH=data/google_credentials.json
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/your_id/edit
```

And your project structure should include:

```
data/
  ├── google_credentials.json  (your service account key)
  └── exercises.csv
```

## Troubleshooting

### "Permission denied" error
- Make sure you shared the sheet with the service account email
- Verify the service account has "Editor" permissions
- Wait a few minutes after sharing (sometimes takes time to propagate)

### "File not found" error
- Check that `google_credentials.json` is in the `data/` folder
- Verify the path in `.env` matches the actual file location

### "Invalid credentials" error
- Make sure you downloaded the JSON key file, not another format
- Verify the JSON file is not corrupted (should be valid JSON)
- Try creating a new key if the current one doesn't work

### "Spreadsheet not found" error
- Verify the Google Sheet URL is correct
- Make sure the sheet is shared with the service account
- Check that the sheet hasn't been deleted or moved

## Security Best Practices

1. **Never share** your `google_credentials.json` file
2. **Never commit** it to version control
3. If compromised, delete the service account key in Google Cloud Console and create a new one
4. Only share the Google Sheet with necessary accounts
5. Consider using read-only access if you don't need the bot to write

## Next Steps

Once Google Sheets is configured, proceed to:
- [AI API Setup Guide](AI_API_SETUP.md)
