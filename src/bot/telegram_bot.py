"""Telegram bot handler for gym tracking."""
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
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
        self.application.add_handler(CommandHandler("overload", self.overload_command))

        # Callback handler for overload interactions
        self.application.add_handler(
            CallbackQueryHandler(self.handle_overload_callback, pattern="^ovl:")
        )

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

I'm your AI-powered workout tracking assistant. I'll help you log your exercises, track progress, and manage your progressive overload.

**Getting Started:**
1. Set your current week: /setweek
2. Set your workout day: /setday
3. Start logging exercises by telling me what you did!

**Available Commands:**
/help - Show all commands
/status - See your current week and day
/overload - Manage progressive overload per exercise
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

🏋️ **Progressive Overload:**
/overload - Manage sets per exercise (customize your progression)

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
- Use /overload to control your progressive overload!
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
                        f"Use /overload to manage your progressive overload per exercise."
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

        # Count customized exercises
        custom_count = len(user_state.custom_exercise_sets)

        status_text = f"""
**Your Current Status:**

📅 Week: {user_state.current_week}/6
🏋️ Day: {user_state.current_day if user_state.current_day else 'Not set'}

💪 Custom sets: {custom_count} exercise(s) customized
Use /overload to manage progressive overload
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
            f"Use /overload to adjust your sets if needed.\n"
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

    async def overload_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /overload command - display progressive overload management interface."""
        user_id = update.effective_user.id
        user_state = self.user_state_manager.get_user_state(user_id)

        # Calculate muscle group volumes
        muscle_groups = self.exercise_db.get_muscle_groups(user_state)

        if not muscle_groups:
            await update.message.reply_text(
                "No muscle groups found. Please contact support."
            )
            return

        # Create inline keyboard with muscle groups
        keyboard = []
        for muscle, sets in muscle_groups:
            keyboard.append([
                InlineKeyboardButton(
                    f"{muscle}: {sets} series",
                    callback_data=f"ovl:m:{muscle}"
                )
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🏋️ *Sobrecarga Progresiva de Series*\n\n"
            "1️⃣ Elige un músculo para progresar:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_overload_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle all overload command callbacks."""
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        user_state = self.user_state_manager.get_user_state(user_id)
        data = query.data

        if data.startswith("ovl:m:"):
            # Muscle group selected - show exercises
            await self._show_exercises_for_muscle(query, user_state, data)

        elif data.startswith("ovl:e:"):
            # Exercise selected - show adjustment controls
            await self._show_exercise_adjustment(query, user_state, data)

        elif data.startswith("ovl:s:"):
            # Sets adjustment (+/-)
            await self._adjust_exercise_sets(query, user_state, data)

        elif data.startswith("ovl:c:"):
            # Confirm changes
            await self._confirm_overload_changes(query, user_state, data)

        elif data == "ovl:back":
            # Go back to muscle selection
            muscle_groups = self.exercise_db.get_muscle_groups(user_state)
            keyboard = []
            for muscle, sets in muscle_groups:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{muscle}: {sets} series",
                        callback_data=f"ovl:m:{muscle}"
                    )
                ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🏋️ *Sobrecarga Progresiva de Series*\n\n"
                "1️⃣ Elige un músculo para progresar:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        elif data == "ovl:cancel":
            await query.edit_message_text("❌ Sobrecarga progresiva cancelada.")

    async def _show_exercises_for_muscle(
        self, query, user_state, data: str
    ) -> None:
        """Show exercises for selected muscle group."""
        # Extract muscle name from callback data
        muscle_name = data.replace("ovl:m:", "")

        # Get exercises for this muscle
        exercises_data = self.exercise_db.get_exercises_by_muscle(muscle_name, user_state)

        if not exercises_data:
            await query.edit_message_text(
                f"No hay ejercicios para {muscle_name}."
            )
            return

        # Calculate current and potential new total
        current_total = sum(sets for _, sets, _ in exercises_data)

        # Group exercises by day
        exercises_by_day = {}
        for exercise, sets, day in exercises_data:
            if day not in exercises_by_day:
                exercises_by_day[day] = []
            exercises_by_day[day].append((exercise, sets))

        # Build message and keyboard
        message = f"2️⃣ *Elige los ejercicios*\n\n📊 Series Semanales: {current_total}\n\n"

        keyboard = []
        for day in sorted(exercises_by_day.keys()):
            message += f"*Día {day}*\n"
            for exercise, sets in exercises_by_day[day]:
                message += f"☐ {exercise.name} ({sets} x {exercise.default_rep_range})\n"
                # Add button for each exercise
                keyboard.append([
                    InlineKeyboardButton(
                        f"{exercise.name} - {sets} series",
                        callback_data=f"ovl:e:{exercise.name[:40]}"  # Limit length for callback data
                    )
                ])
            message += "\n"

        # Add back and cancel buttons
        keyboard.append([
            InlineKeyboardButton("⬅️ Volver", callback_data="ovl:back"),
            InlineKeyboardButton("❌ Cancelar", callback_data="ovl:cancel")
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def _show_exercise_adjustment(
        self, query, user_state, data: str
    ) -> None:
        """Show adjustment controls for selected exercise."""
        # Extract exercise name from callback data
        exercise_name = data.replace("ovl:e:", "")

        # Find the exercise
        exercise = self.exercise_db.find_exercise(exercise_name)
        if not exercise:
            await query.edit_message_text(
                f"No se pudo encontrar el ejercicio: {exercise_name}"
            )
            return

        # Get current sets
        current_sets = user_state.get_exercise_sets(exercise)

        # Build message
        message = (
            f"✏️ *{exercise.name}*\n"
            f"Día {exercise.day}\n\n"
            f"Series actuales: {current_sets}"
        )

        # Build keyboard with +/- buttons
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data=f"ovl:s:{exercise_name[:30]}:-"),
                InlineKeyboardButton(f"{current_sets}", callback_data="ovl:noop"),
                InlineKeyboardButton("➕", callback_data=f"ovl:s:{exercise_name[:30]}:+"),
            ],
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=f"ovl:c:{exercise_name[:40]}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="ovl:cancel")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def _adjust_exercise_sets(
        self, query, user_state, data: str
    ) -> None:
        """Adjust exercise sets up or down."""
        # Parse callback data: ovl:s:<exercise_name>:+/-
        parts = data.split(":")
        if len(parts) < 4:
            await query.answer("Error en los datos")
            return

        exercise_name = parts[2]
        direction = parts[3]

        # Find the exercise
        exercise = self.exercise_db.find_exercise(exercise_name)
        if not exercise:
            await query.answer("Ejercicio no encontrado")
            return

        # Get current sets
        current_sets = user_state.get_exercise_sets(exercise)

        # Adjust sets
        if direction == "+":
            new_sets = current_sets + 1
        elif direction == "-":
            new_sets = max(1, current_sets - 1)  # Minimum 1 set
        else:
            await query.answer("Operación inválida")
            return

        # Update user state
        user_state.set_exercise_sets(exercise.name, new_sets)
        self.user_state_manager.update_user_state(user_state)

        # Update the message
        message = (
            f"✏️ *{exercise.name}*\n"
            f"Día {exercise.day}\n\n"
            f"Series actuales: {new_sets}"
        )

        # Rebuild keyboard
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data=f"ovl:s:{exercise_name}:-"),
                InlineKeyboardButton(f"{new_sets}", callback_data="ovl:noop"),
                InlineKeyboardButton("➕", callback_data=f"ovl:s:{exercise_name}:+"),
            ],
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=f"ovl:c:{exercise_name}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="ovl:cancel")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        await query.answer(f"Series ajustadas a {new_sets}")

    async def _confirm_overload_changes(
        self, query, user_state, data: str
    ) -> None:
        """Confirm changes to exercise sets."""
        # Extract exercise name
        exercise_name = data.replace("ovl:c:", "")

        # Find the exercise
        exercise = self.exercise_db.find_exercise(exercise_name)
        if not exercise:
            await query.edit_message_text(
                f"No se pudo encontrar el ejercicio: {exercise_name}"
            )
            return

        # Get the new sets
        new_sets = user_state.get_exercise_sets(exercise)

        # Get muscle group and recalculate volume
        muscle_name = self.exercise_db._map_category_to_muscle(exercise.category)
        muscle_volume = sum(
            sets for _, sets, _ in self.exercise_db.get_exercises_by_muscle(muscle_name, user_state)
        )

        # Build confirmation message
        message = (
            f"✅ *Sobrecarga actualizada!*\n\n"
            f"{exercise.name}: {new_sets} series\n"
            f"Series semanales {muscle_name}: {muscle_volume}\n\n"
        )

        # Offer to continue or finish
        keyboard = [
            [InlineKeyboardButton("🔄 Continuar ajustando", callback_data="ovl:back")],
            [InlineKeyboardButton("✅ Finalizar", callback_data="ovl:cancel")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    def run(self) -> None:
        """Start the bot."""
        print("🤖 Starting Gym Tracker Bot...")
        self.application.run_polling()
