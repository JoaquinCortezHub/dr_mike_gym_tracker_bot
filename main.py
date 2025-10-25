"""Main entry point for Dr. Mike's Gym Tracker Bot."""
import os
from pathlib import Path
from dotenv import load_dotenv

from src.database.exercise_db import ExerciseDatabase
from src.database.user_state_manager import UserStateManager
from src.sheets.sheets_manager import SheetsManager
from src.agents.gym_agent import GymAgent
from src.bot.telegram_bot import GymTelegramBot


def main():
    """Initialize and run the gym tracker bot."""
    # Load environment variables
    load_dotenv()

    # Validate required environment variables
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

    google_creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "data/google_credentials.json")
    google_sheet_url = os.getenv("GOOGLE_SHEET_URL")
    if not google_sheet_url:
        raise ValueError("GOOGLE_SHEET_URL not found in environment variables")

    # AI provider configuration
    ai_provider = os.getenv("AI_PROVIDER", "openai").lower()

    if ai_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        os.environ["OPENAI_API_KEY"] = api_key
        model_id = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    elif ai_provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        os.environ["ANTHROPIC_API_KEY"] = api_key
        model_id = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
    else:
        raise ValueError(f"Invalid AI_PROVIDER: {ai_provider}. Choose 'openai' or 'anthropic'")

    print("🏋️ Dr. Mike's Gym Tracker Bot")
    print("=" * 50)
    print(f"AI Provider: {ai_provider}")
    print(f"Model: {model_id}")
    print("=" * 50)

    # Initialize components
    print("📊 Loading exercise database...")
    exercise_db = ExerciseDatabase("data/exercises.csv")
    print(f"✅ Loaded {len(exercise_db.get_all_exercises())} exercises")

    print("👤 Initializing user state manager...")
    user_state_path = os.getenv("USER_STATE_PATH", "data/user_states.json")
    user_state_manager = UserStateManager(user_state_path)
    print(f"✅ Managing {len(user_state_manager.get_all_users())} users")

    print("📝 Connecting to Google Sheets...")
    sheets_manager = SheetsManager(google_creds_path, google_sheet_url)
    try:
        sheets_manager.connect()
        print("✅ Connected to Google Sheets")
    except Exception as e:
        print(f"⚠️ Warning: Could not connect to Google Sheets: {e}")
        print("The bot will still run, but logging won't work until this is fixed.")

    print("🤖 Initializing AI agent...")
    gym_agent = GymAgent(
        exercise_db=exercise_db,
        sheets_manager=sheets_manager,
        model_provider=ai_provider,
        model_id=model_id,
    )
    print("✅ AI agent ready")

    print("📱 Starting Telegram bot...")
    bot = GymTelegramBot(
        token=telegram_token,
        gym_agent=gym_agent,
        user_state_manager=user_state_manager,
        exercise_db=exercise_db,
    )

    print("✅ Bot is running! Press Ctrl+C to stop.")
    print("=" * 50)
    bot.run()


if __name__ == "__main__":
    main()
