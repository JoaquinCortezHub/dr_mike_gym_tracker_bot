"""Exercise data models."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Exercise:
    """Represents a gym exercise."""

    name: str
    day: int  # 1-4 for the 4-day split
    default_sets: int
    default_rep_range: str  # e.g., "6-10" or "10-15"
    default_weight: Optional[float] = None
    category: str = ""  # e.g., "Shoulders", "Chest", "Legs"

    def __str__(self) -> str:
        weight_str = f" @ {self.default_weight}kg" if self.default_weight else ""
        return f"{self.name}: {self.default_sets} x {self.default_rep_range}{weight_str}"


@dataclass
class WorkoutLog:
    """Represents a logged workout entry."""

    exercise_name: str
    week: int  # 1-6
    day: int  # 1-4
    sets: int
    reps: str  # Could be a range like "8-12" or actual reps per set
    weight: Optional[float] = None
    notes: str = ""

    def __str__(self) -> str:
        weight_str = f" @ {self.weight}kg" if self.weight else ""
        return f"{self.exercise_name}: {self.sets} x {self.reps}{weight_str}"


@dataclass
class UserState:
    """Represents user's current workout state."""

    telegram_id: int
    current_week: int = 1  # 1-6
    current_day: Optional[int] = None  # 1-4
    split_configured: bool = False

    def increment_week(self) -> None:
        """Move to next week in the 6-week cycle."""
        self.current_week = (self.current_week % 6) + 1

    def get_progressive_sets(self, base_sets: int) -> int:
        """Calculate sets with progressive overload."""
        return base_sets + (self.current_week - 1)
