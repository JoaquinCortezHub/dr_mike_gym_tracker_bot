"""Exercise database loaded from CSV."""
import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.exercise import UserState

from src.models.exercise import Exercise


class ExerciseDatabase:
    """Manages the exercise database loaded from CSV."""

    def __init__(self, csv_path: str = "data/exercises.csv"):
        """Initialize the exercise database from CSV."""
        self.exercises: Dict[str, Exercise] = {}
        self.exercises_by_day: Dict[int, List[Exercise]] = {1: [], 2: [], 3: [], 4: []}
        self._load_exercises(csv_path)

    def _parse_sets_reps(self, sets_reps: str) -> tuple[int, str]:
        """Parse '3 x 6-10' format into (sets, rep_range)."""
        sets_reps = sets_reps.strip()
        match = re.match(r"(\d+)\s*x\s*([\d\-]+)", sets_reps)
        if match:
            sets = int(match.group(1))
            reps = match.group(2)
            return sets, reps
        return 3, "8-12"  # Default fallback

    def _load_exercises(self, csv_path: str) -> None:
        """Load exercises from the CSV file."""
        current_day = None

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            next(reader)  # Skip week labels

            for row in reader:
                if not row or not row[0]:
                    continue

                # Check if this is a day header (Dia 1, Dia 2, etc.)
                if row[0].startswith("Dia"):
                    day_match = re.search(r"Dia\s*(\d+)", row[0])
                    if day_match:
                        current_day = int(day_match.group(1))
                    continue

                # This is an exercise row
                if current_day is None:
                    continue

                exercise_name = row[0].strip()
                if not exercise_name:
                    continue

                # Parse weight (column 2, WEEK 1 Peso)
                weight = None
                if len(row) > 2 and row[2]:
                    try:
                        weight = float(row[2])
                    except ValueError:
                        pass

                # Parse sets x reps (column 3, WEEK 1 Series)
                sets_reps = row[3] if len(row) > 3 else "3 x 8-12"
                sets, rep_range = self._parse_sets_reps(sets_reps)

                # Determine category based on exercise name
                category = self._categorize_exercise(exercise_name)

                exercise = Exercise(
                    name=exercise_name,
                    day=current_day,
                    default_sets=sets,
                    default_rep_range=rep_range,
                    default_weight=weight,
                    category=category,
                )

                self.exercises[exercise_name.lower()] = exercise
                self.exercises_by_day[current_day].append(exercise)

    def _categorize_exercise(self, name: str) -> str:
        """Categorize exercise by muscle group."""
        name_lower = name.lower()

        if any(
            keyword in name_lower
            for keyword in [
                "vuelos",
                "laterales",
                "hombro",
                "shoulder",
                "deltoides",
                "face pulls",
            ]
        ):
            return "Shoulders"
        elif any(
            keyword in name_lower
            for keyword in [
                "press",
                "banca",
                "bench",
                "pec",
                "mariposa",
                "aperturas",
                "pecho",
                "chest",
            ]
        ):
            return "Chest"
        elif any(
            keyword in name_lower
            for keyword in [
                "dorsal",
                "remo",
                "row",
                "dominadas",
                "pull",
                "espalda",
                "back",
            ]
        ):
            return "Back"
        elif any(
            keyword in name_lower
            for keyword in ["curl", "bíceps", "biceps", "bicep"]
        ):
            return "Biceps"
        elif any(
            keyword in name_lower
            for keyword in ["tríceps", "triceps", "extensión", "extension"]
        ):
            return "Triceps"
        elif any(
            keyword in name_lower
            for keyword in [
                "zancadas",
                "lunge",
                "femoral",
                "cuádriceps",
                "quadriceps",
                "hacka",
                "hack",
                "squat",
                "glúteo",
                "glute",
                "aductores",
                "peso muerto",
                "deadlift",
                "rdl",
                "piernas",
                "legs",
            ]
        ):
            return "Legs"
        else:
            return "Other"

    def find_exercise(self, query: str) -> Optional[Exercise]:
        """Find an exercise by name (fuzzy matching)."""
        query_lower = query.lower()

        # Exact match
        if query_lower in self.exercises:
            return self.exercises[query_lower]

        # Partial match
        for name, exercise in self.exercises.items():
            if query_lower in name or name in query_lower:
                return exercise

        return None

    def get_exercises_for_day(self, day: int) -> List[Exercise]:
        """Get all exercises for a specific day."""
        return self.exercises_by_day.get(day, [])

    def get_all_exercises(self) -> List[Exercise]:
        """Get all exercises."""
        return list(self.exercises.values())

    def get_day_summary(self, day: int) -> str:
        """Get a formatted summary of exercises for a day."""
        exercises = self.get_exercises_for_day(day)
        if not exercises:
            return f"No exercises found for Day {day}"

        summary = f"**Day {day} Exercises:**\n\n"
        for exercise in exercises:
            summary += f"- {exercise}\n"
        return summary

    def _map_category_to_muscle(self, category: str) -> str:
        """
        Map internal category to user-facing muscle name.

        Args:
            category: Internal category name

        Returns:
            User-facing muscle name in Spanish
        """
        # Based on the screenshots, we need to identify muscle groups more precisely
        # For now, we'll use a simplified mapping
        mapping = {
            "Shoulders": "Deltoides",
            "Chest": "Pecho",
            "Back": "Dorsal ancho",
            "Biceps": "Bíceps",
            "Triceps": "Tríceps",
            "Legs": "Piernas",
            "Other": "Otros",
        }
        return mapping.get(category, category)

    def _reverse_muscle_mapping(self, muscle_name: str) -> str:
        """
        Map user-facing muscle name back to internal category.

        Args:
            muscle_name: User-facing muscle name

        Returns:
            Internal category name
        """
        reverse_mapping = {
            "Deltoides": "Shoulders",
            "Pecho": "Chest",
            "Dorsal ancho": "Back",
            "Bíceps": "Biceps",
            "Tríceps": "Triceps",
            "Piernas": "Legs",
            "Otros": "Other",
        }
        return reverse_mapping.get(muscle_name, muscle_name)

    def calculate_muscle_group_volumes(self, user_state: "UserState") -> Dict[str, int]:
        """
        Calculate total weekly sets per muscle group.

        Args:
            user_state: User state with custom exercise sets

        Returns:
            Dictionary mapping muscle names to total weekly sets
        """
        volumes: Dict[str, int] = {}

        for exercise in self.get_all_exercises():
            # Get current sets (custom or default)
            sets = user_state.get_exercise_sets(exercise)

            # Map category to display name
            muscle_name = self._map_category_to_muscle(exercise.category)

            if muscle_name not in volumes:
                volumes[muscle_name] = 0
            volumes[muscle_name] += sets

        # Sort by volume (descending)
        return dict(sorted(volumes.items(), key=lambda x: x[1], reverse=True))

    def get_exercises_by_muscle(
        self, muscle_group: str, user_state: "UserState"
    ) -> List[tuple[Exercise, int, int]]:
        """
        Get exercises for a muscle group with current sets.

        Args:
            muscle_group: User-facing muscle name
            user_state: User state with custom exercise sets

        Returns:
            List of tuples (exercise, current_sets, day)
        """
        category = self._reverse_muscle_mapping(muscle_group)
        exercises = []

        for exercise in self.get_all_exercises():
            if exercise.category == category:
                current_sets = user_state.get_exercise_sets(exercise)
                exercises.append((exercise, current_sets, exercise.day))

        # Sort by day
        return sorted(exercises, key=lambda x: x[2])

    def get_muscle_groups(self, user_state: "UserState") -> List[tuple[str, int]]:
        """
        Get all muscle groups with their total weekly volumes.

        Args:
            user_state: User state with custom exercise sets

        Returns:
            List of tuples (muscle_name, total_sets) sorted by volume descending
        """
        volumes = self.calculate_muscle_group_volumes(user_state)
        return [(muscle, sets) for muscle, sets in volumes.items()]
