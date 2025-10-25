"""User state management with persistent storage."""
import json
from pathlib import Path
from typing import Dict, Optional

from src.models.exercise import UserState


class UserStateManager:
    """Manages user states with JSON file persistence."""

    def __init__(self, storage_path: str = "data/user_states.json"):
        """
        Initialize the user state manager.

        Args:
            storage_path: Path to JSON file for storing user states
        """
        self.storage_path = Path(storage_path)
        self.user_states: Dict[int, UserState] = {}
        self._load_states()

    def _load_states(self) -> None:
        """Load user states from JSON file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for telegram_id_str, state_data in data.items():
                        telegram_id = int(telegram_id_str)
                        self.user_states[telegram_id] = UserState(
                            telegram_id=telegram_id,
                            current_week=state_data.get("current_week", 1),
                            current_day=state_data.get("current_day"),
                            split_configured=state_data.get("split_configured", False),
                            custom_exercise_sets=state_data.get("custom_exercise_sets", {}),
                        )
            except Exception as e:
                print(f"Error loading user states: {e}")
                self.user_states = {}

    def _save_states(self) -> None:
        """Save user states to JSON file."""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            data = {}
            for telegram_id, state in self.user_states.items():
                data[str(telegram_id)] = {
                    "current_week": state.current_week,
                    "current_day": state.current_day,
                    "split_configured": state.split_configured,
                    "custom_exercise_sets": state.custom_exercise_sets,
                }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving user states: {e}")

    def get_user_state(self, telegram_id: int) -> UserState:
        """
        Get or create a user state.

        Args:
            telegram_id: Telegram user ID

        Returns:
            UserState for the user
        """
        if telegram_id not in self.user_states:
            self.user_states[telegram_id] = UserState(telegram_id=telegram_id)
            self._save_states()

        return self.user_states[telegram_id]

    def update_user_state(self, state: UserState) -> None:
        """
        Update a user's state and persist to storage.

        Args:
            state: Updated UserState
        """
        self.user_states[state.telegram_id] = state
        self._save_states()

    def set_current_day(self, telegram_id: int, day: int) -> None:
        """
        Set the current workout day for a user.

        Args:
            telegram_id: Telegram user ID
            day: Day number (1-4)
        """
        state = self.get_user_state(telegram_id)
        state.current_day = day
        self.update_user_state(state)

    def set_current_week(self, telegram_id: int, week: int) -> None:
        """
        Set the current week for a user.

        Args:
            telegram_id: Telegram user ID
            week: Week number (1-6)
        """
        state = self.get_user_state(telegram_id)
        state.current_week = week
        self.update_user_state(state)

    def configure_split(self, telegram_id: int) -> None:
        """
        Mark a user's split as configured.

        Args:
            telegram_id: Telegram user ID
        """
        state = self.get_user_state(telegram_id)
        state.split_configured = True
        self.update_user_state(state)

    def increment_week(self, telegram_id: int) -> int:
        """
        Move user to the next week in the cycle.

        Args:
            telegram_id: Telegram user ID

        Returns:
            New week number
        """
        state = self.get_user_state(telegram_id)
        state.increment_week()
        self.update_user_state(state)
        return state.current_week

    def reset_user(self, telegram_id: int) -> None:
        """
        Reset a user's state to default.

        Args:
            telegram_id: Telegram user ID
        """
        self.user_states[telegram_id] = UserState(telegram_id=telegram_id)
        self._save_states()

    def get_all_users(self) -> list[int]:
        """Get list of all user IDs."""
        return list(self.user_states.keys())
