"""Agno AI agent for interpreting gym workout messages."""
from typing import Optional
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude

from src.models.exercise import WorkoutLog, UserState
from src.database.exercise_db import ExerciseDatabase
from src.sheets.sheets_manager import SheetsManager


class GymAgent:
    """AI agent for interpreting workout messages and logging to Google Sheets."""

    def __init__(
        self,
        exercise_db: ExerciseDatabase,
        sheets_manager: SheetsManager,
        model_provider: str = "openai",
        model_id: str = "gpt-4o-mini",
    ):
        """
        Initialize the gym agent.

        Args:
            exercise_db: Exercise database instance
            sheets_manager: Google Sheets manager instance
            model_provider: 'openai' or 'anthropic'
            model_id: Model identifier (e.g., 'gpt-4o-mini', 'claude-3-5-sonnet-latest')
        """
        self.exercise_db = exercise_db
        self.sheets_manager = sheets_manager

        # Create the AI agent based on provider
        if model_provider.lower() == "anthropic":
            model = Claude(id=model_id)
        else:
            model = OpenAIChat(id=model_id)

        self.agent = Agent(
            name="Gym Tracker Agent",
            model=model,
            description="You are a helpful gym workout tracking assistant. You help users log their exercises, track progress, and provide workout summaries.",
            instructions=[
                "Parse user messages to extract exercise names, sets, reps, and weights",
                "Be conversational and encouraging",
                "Understand both Spanish and English exercise names",
                "Accept natural language like 'just did 3 sets of 10 reps bench press at 60kg'",
                "Also understand abbreviated formats like 'BP 3x10 @ 60kg'",
            ],
            markdown=True,
        )

    def parse_workout_message(
        self, message: str, user_state: UserState
    ) -> Optional[WorkoutLog]:
        """
        Parse a user's workout message and extract exercise information.

        Args:
            message: User's message describing their workout
            user_state: Current user state (week, day)

        Returns:
            WorkoutLog if successfully parsed, None otherwise
        """
        # Create a prompt for the agent to parse the message
        prompt = f"""
Parse this workout message and extract the following information:
- Exercise name (match it to known exercises)
- Number of sets
- Reps (can be a range like 8-12 or specific like 10)
- Weight (if mentioned, in kg)

Message: "{message}"

Known exercises for today (Day {user_state.current_day or 'unknown'}):
{self._format_exercises_for_day(user_state.current_day)}

Respond in this exact JSON format:
{{
    "exercise_name": "exact exercise name from database",
    "sets": number,
    "reps": "range or number",
    "weight": number or null,
    "found": true/false
}}
"""

        try:
            response = self.agent.run(prompt)
            result = self._parse_agent_response(response.content)

            if result and result.get("found"):
                exercise = self.exercise_db.find_exercise(result["exercise_name"])
                if exercise:
                    return WorkoutLog(
                        exercise_name=exercise.name,
                        week=user_state.current_week,
                        day=exercise.day,
                        sets=result["sets"],
                        reps=str(result["reps"]),
                        weight=result.get("weight"),
                    )

        except Exception as e:
            print(f"Error parsing workout message: {e}")

        return None

    def _format_exercises_for_day(self, day: Optional[int]) -> str:
        """Format exercises for a specific day as a string."""
        if day is None:
            return "No day selected yet"

        exercises = self.exercise_db.get_exercises_for_day(day)
        return "\n".join([f"- {ex.name}" for ex in exercises])

    def _parse_agent_response(self, response: str) -> Optional[dict]:
        """Parse the agent's JSON response."""
        import json
        import re

        # Try to find JSON in the response
        json_match = re.search(r"\{[^}]+\}", response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return None

    def get_day_summary(self, user_state: UserState) -> str:
        """Get a summary of today's workout."""
        if user_state.current_day is None:
            return "No day selected. Please set your current workout day."

        return self.exercise_db.get_day_summary(user_state.current_day)

    def get_week_summary(self, user_state: UserState) -> str:
        """Get a summary of the current week's progress."""
        summary = f"**Week {user_state.current_week} Summary:**\n\n"

        for day in range(1, 5):
            try:
                day_progress = self.sheets_manager.get_day_progress(
                    day, user_state.current_week
                )
                summary += f"\n{day_progress}\n"
            except Exception as e:
                summary += f"\nDay {day}: Error loading progress ({e})\n"

        return summary

    def get_schedule_for_day(self, day: int) -> str:
        """Get the exercise schedule for a specific day."""
        return self.exercise_db.get_day_summary(day)

    def log_workout(self, workout_log: WorkoutLog) -> tuple[bool, str]:
        """
        Log a workout to Google Sheets.

        Args:
            workout_log: WorkoutLog object to log

        Returns:
            Tuple of (success, message)
        """
        try:
            success = self.sheets_manager.log_workout(workout_log)
            if success:
                message = f"✅ Logged: {workout_log}"
                return True, message
            else:
                message = f"❌ Failed to log workout"
                return False, message
        except Exception as e:
            return False, f"❌ Error: {e}"

    def generate_encouraging_message(self, workout_log: WorkoutLog) -> str:
        """Generate an encouraging message after logging a workout."""
        prompt = f"""
The user just completed this exercise:
{workout_log}

Generate a short, encouraging message (1-2 sentences) to congratulate them.
Make it energetic and motivating!
"""

        try:
            response = self.agent.run(prompt)
            return response.content
        except Exception as e:
            return f"Great work on completing {workout_log.exercise_name}! 💪"
