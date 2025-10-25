"""Telegram bot handler for gym tracking."""
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from src.agents.gym_agent import GymAgent
from src.database.user_state_manager import UserStateManager
from src.database.exercise_db import ExerciseDatabase
from src.sheets.sheets_manager import SheetsManager

# Conversation states
SETTING_DAY, SETTING_WEEK = range(2)


class GymTelegramBot:
    """Telegram bot for gym workout tracking."""

    def __init__(
        self,
        token: str,
        gym_agent: GymAgent,
        user_state_manager: UserStateManager,
        exercise_db: ExerciseDatabase,
    ):
        """
        Initialize the Telegram bot.

        Args:
            token: Telegram bot token
            gym_agent: GymAgent instance
            user_state_manager: UserStateManager instance
            exercise_db: ExerciseDatabase instance
        """
        self.token = token
        self.gym_agent = gym_agent
        self.user_state_manager = user_state_manager
        self.exercise_db = exercise_db
        self.application = Application.builder().token(token).build()

        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up all command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("setday", self.setday_command))
        self.application.add_handler(CommandHandler("setweek", self.setweek_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("today", self.today_command))
        self.application.add_handler(CommandHandler("week", self.week_command))
        self.application.add_handler(
            CommandHandler("schedule", self.schedule_command)
        )
        self.application.add_handler(CommandHandler("nextweek", self.nextweek_command))

        # Message handler for workout logging
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start command."""
        user_id = update.effective_user.id
        user_state = self.user_state_manager.get_user_state(user_id)

        welcome_message = """
🏋️ Welcome to Dr. Mike's Gym Tracker! 💪

I'm your AI-powered workout tracking assistant. I'll help you log your exercises, track progress, and follow your progressive overload plan.

**Getting Started:**
1. Set your current week: /setweek
2. Set your workout day: /setday
3. Start logging exercises by telling me what you did!

**Available Commands:**
/help - Show all commands
/status - See your current week and day
/today - Today's workout schedule
/week - This week's progress
/schedule - View workout schedule for any day
/nextweek - Move to next week

Ready to crush some sets? Let's go! 🔥
"""
        await update.message.reply_text(welcome_message)

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        help_text = """
**Gym Tracker Commands:**

📅 **Setup:**
/setweek - Set your current week (1-6)
/setday - Set your workout day (1-4)
/status - View your current week and day

📝 **Logging:**
Just message me what you did! Examples:
- "3 sets of 10 reps bench press at 60kg"
- "BP 3x10 @ 60kg"
- "Just finished 3 sets of pull-ups"

📊 **Progress:**
/today - See today's workout schedule
/week - View this week's progress
/schedule - View schedule for any day
/nextweek - Move to the next week

💡 **Tips:**
- I understand natural language!
- I know Spanish and English exercise names
- Tell me sets, reps, and weight, and I'll log it
- Progressive overload is built in - sets increase each week!
"""
        await update.message.reply_text(help_text)

    async def setday_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /setday command."""
        # Check if day is provided as argument
        if context.args and len(context.args) > 0:
            try:
                day = int(context.args[0])
                if 1 <= day <= 4:
                    user_id = update.effective_user.id
                    self.user_state_manager.set_current_day(user_id, day)

                    schedule = self.exercise_db.get_day_summary(day)
                    await update.message.reply_text(
                        f"✅ Set to Day {day}\n\n{schedule}"
                    )
                else:
                    await update.message.reply_text(
                        "Please choose a day between 1 and 4."
                    )
            except ValueError:
                await update.message.reply_text("Please provide a valid day number (1-4).")
        else:
            # Show day selection keyboard
            keyboard = [["1", "2", "3", "4"]]
            reply_markup = ReplyKeyboardMarkup(
                keyboard, one_time_keyboard=True, resize_keyboard=True
            )
            await update.message.reply_text(
                "Which day are you training? (1-4)", reply_markup=reply_markup
            )

    async def setweek_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /setweek command."""
        # Check if week is provided as argument
        if context.args and len(context.args) > 0:
            try:
                week = int(context.args[0])
                if 1 <= week <= 6:
                    user_id = update.effective_user.id
                    self.user_state_manager.set_current_week(user_id, week)
                    await update.message.reply_text(
                        f"✅ Set to Week {week}\n\n"
                        f"Progressive overload will add {week - 1} extra sets to your base routine."
                    )
                else:
                    await update.message.reply_text(
                        "Please choose a week between 1 and 6."
                    )
            except ValueError:
                await update.message.reply_text("Please provide a valid week number (1-6).")
        else:
            # Show week selection keyboard
            keyboard = [["1", "2", "3"], ["4", "5", "6"]]
            reply_markup = ReplyKeyboardMarkup(
                keyboard, one_time_keyboard=True, resize_keyboard=True
            )
            await update.message.reply_text(
                "Which week are you in? (1-6)", reply_markup=reply_markup
            )

    async def status_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /status command."""
        user_id = update.effective_user.id
        user_state = self.user_state_manager.get_user_state(user_id)

        status_text = f"""
**Your Current Status:**

📅 Week: {user_state.current_week}/6
🏋️ Day: {user_state.current_day if user_state.current_day else 'Not set'}

Progressive overload: +{user_state.current_week - 1} sets from base routine
"""
        await update.message.reply_text(status_text)

    async def today_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /today command."""
        user_id = update.effective_user.id
        user_state = self.user_state_manager.get_user_state(user_id)

        if user_state.current_day is None:
            await update.message.reply_text(
                "Please set your workout day first with /setday"
            )
            return

        schedule = self.gym_agent.get_day_summary(user_state)
        await update.message.reply_text(schedule)

    async def week_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /week command."""
        user_id = update.effective_user.id
        user_state = self.user_state_manager.get_user_state(user_id)

        summary = self.gym_agent.get_week_summary(user_state)
        await update.message.reply_text(summary)

    async def schedule_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /schedule command."""
        if context.args and len(context.args) > 0:
            try:
                day = int(context.args[0])
                if 1 <= day <= 4:
                    schedule = self.gym_agent.get_schedule_for_day(day)
                    await update.message.reply_text(schedule)
                else:
                    await update.message.reply_text("Please choose a day between 1 and 4.")
            except ValueError:
                await update.message.reply_text("Usage: /schedule <day_number>")
        else:
            await update.message.reply_text(
                "Usage: /schedule <day_number>\nExample: /schedule 1"
            )

    async def nextweek_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /nextweek command."""
        user_id = update.effective_user.id
        new_week = self.user_state_manager.increment_week(user_id)

        await update.message.reply_text(
            f"🎉 Moved to Week {new_week}!\n\n"
            f"Progressive overload: +{new_week - 1} sets from base routine.\n"
            f"Keep crushing it! 💪"
        )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle regular text messages (workout logging)."""
        user_id = update.effective_user.id
        user_state = self.user_state_manager.get_user_state(user_id)
        message_text = update.message.text

        # Check if user is setting day/week via keyboard
        if message_text in ["1", "2", "3", "4", "5", "6"]:
            # Could be day or week - need better state management
            # For now, treat single digits as day selection
            day = int(message_text)
            if 1 <= day <= 4:
                self.user_state_manager.set_current_day(user_id, day)
                schedule = self.exercise_db.get_day_summary(day)
                await update.message.reply_text(f"✅ Set to Day {day}\n\n{schedule}")
                return

        # Check if day is set
        if user_state.current_day is None:
            await update.message.reply_text(
                "⚠️ Please set your workout day first with /setday"
            )
            return

        # Parse the workout message
        await update.message.reply_text("🤔 Processing your workout...")

        workout_log = self.gym_agent.parse_workout_message(message_text, user_state)

        if workout_log is None:
            await update.message.reply_text(
                "❌ I couldn't understand that exercise. Try being more specific!\n\n"
                "Examples:\n"
                "- '3 sets of 10 reps bench press'\n"
                "- 'Bench press 3x10 @ 60kg'"
            )
            return

        # Log the workout
        success, message = self.gym_agent.log_workout(workout_log)

        if success:
            # Generate encouraging message
            encouragement = self.gym_agent.generate_encouraging_message(workout_log)
            await update.message.reply_text(f"{message}\n\n{encouragement}")
        else:
            await update.message.reply_text(message)

    def run(self) -> None:
        """Start the bot."""
        print("🤖 Starting Gym Tracker Bot...")
        self.application.run_polling()
