"""Google Sheets manager for logging workouts."""
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional
from src.models.exercise import WorkoutLog


class SheetsManager:
    """Manages Google Sheets integration for workout logging."""

    def __init__(self, credentials_path: str, spreadsheet_url: str):
        """
        Initialize the Google Sheets manager.

        Args:
            credentials_path: Path to the Google service account JSON credentials
            spreadsheet_url: URL of the Google Sheet to use
        """
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.client: Optional[gspread.Client] = None
        self.spreadsheet: Optional[gspread.Spreadsheet] = None
        self.worksheet: Optional[gspread.Worksheet] = None

    def connect(self) -> None:
        """Connect to Google Sheets API."""
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_file(
            self.credentials_path, scopes=scopes
        )
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_url(self.spreadsheet_url)
        self.worksheet = self.spreadsheet.sheet1  # Use first sheet by default

    def _get_column_for_week(self, week: int, column_type: str) -> int:
        """
        Get the column index for a specific week and column type.

        Column structure:
        - WEEK 1: Peso (col 3), Series (col 4), Notas (col 5)
        - WEEK 2: Peso (col 6), Series (col 7), Notas (col 8)
        - etc.

        Args:
            week: Week number (1-6)
            column_type: 'peso', 'series', or 'notas'

        Returns:
            Column index (1-based)
        """
        base_column = 3  # WEEK 1 starts at column 3
        week_offset = (week - 1) * 3  # Each week has 3 columns

        column_map = {"peso": 0, "series": 1, "notas": 2}
        type_offset = column_map.get(column_type.lower(), 0)

        return base_column + week_offset + type_offset

    def _find_exercise_row(self, exercise_name: str, day: int) -> Optional[int]:
        """
        Find the row number for a specific exercise on a specific day.

        Args:
            exercise_name: Name of the exercise to find
            day: Day number (1-4)

        Returns:
            Row number (1-based) or None if not found
        """
        if not self.worksheet:
            return None

        # Get all values from column A (exercise names)
        all_values = self.worksheet.col_values(1)

        # Find the day header first
        day_header = f"Dia {day}"
        day_row = None

        for i, value in enumerate(all_values, start=1):
            if day_header in value:
                day_row = i
                break

        if day_row is None:
            return None

        # Search for the exercise after the day header
        exercise_lower = exercise_name.lower()
        for i in range(day_row + 1, len(all_values) + 1):
            if i >= len(all_values):
                break

            cell_value = all_values[i - 1].lower()

            # Stop if we hit another day header
            if cell_value.startswith("dia"):
                break

            # Check if this is the exercise we're looking for
            if exercise_lower in cell_value or cell_value in exercise_lower:
                return i

        return None

    def log_workout(self, log: WorkoutLog) -> bool:
        """
        Log a workout entry to the Google Sheet.

        Args:
            log: WorkoutLog object with exercise details

        Returns:
            True if successful, False otherwise
        """
        if not self.worksheet:
            return False

        row = self._find_exercise_row(log.exercise_name, log.day)
        if row is None:
            print(f"Exercise '{log.exercise_name}' not found in Day {log.day}")
            return False

        try:
            # Update weight column
            if log.weight is not None:
                peso_col = self._get_column_for_week(log.week, "peso")
                self.worksheet.update_cell(row, peso_col, log.weight)

            # Update sets/reps column
            series_col = self._get_column_for_week(log.week, "series")
            series_value = f"{log.sets} x {log.reps}"
            self.worksheet.update_cell(row, series_col, series_value)

            # Update notes column if provided
            if log.notes:
                notas_col = self._get_column_for_week(log.week, "notas")
                self.worksheet.update_cell(row, notas_col, log.notes)

            return True

        except Exception as e:
            print(f"Error logging workout: {e}")
            return False

    def get_exercise_history(
        self, exercise_name: str, day: int
    ) -> list[tuple[int, Optional[float], str, str]]:
        """
        Get the workout history for an exercise across all weeks.

        Args:
            exercise_name: Name of the exercise
            day: Day number (1-4)

        Returns:
            List of tuples: (week, weight, sets_reps, notes)
        """
        if not self.worksheet:
            return []

        row = self._find_exercise_row(exercise_name, day)
        if row is None:
            return []

        history = []
        for week in range(1, 7):  # Weeks 1-6
            peso_col = self._get_column_for_week(week, "peso")
            series_col = self._get_column_for_week(week, "series")
            notas_col = self._get_column_for_week(week, "notas")

            weight_val = self.worksheet.cell(row, peso_col).value
            series_val = self.worksheet.cell(row, series_col).value or ""
            notes_val = self.worksheet.cell(row, notas_col).value or ""

            weight = float(weight_val) if weight_val else None

            history.append((week, weight, series_val, notes_val))

        return history

    def get_day_progress(self, day: int, week: int) -> str:
        """
        Get a summary of progress for a specific day and week.

        Args:
            day: Day number (1-4)
            week: Week number (1-6)

        Returns:
            Formatted string with workout summary
        """
        if not self.worksheet:
            return "Not connected to Google Sheets"

        summary = f"**Day {day}, Week {week} Progress:**\n\n"

        # Find all exercises for this day
        all_values = self.worksheet.col_values(1)
        day_header = f"Dia {day}"
        day_row = None

        for i, value in enumerate(all_values, start=1):
            if day_header in value:
                day_row = i
                break

        if day_row is None:
            return f"Day {day} not found in sheet"

        # Get exercises for this day
        series_col = self._get_column_for_week(week, "series")
        peso_col = self._get_column_for_week(week, "peso")

        for i in range(day_row + 1, len(all_values) + 1):
            if i >= len(all_values):
                break

            exercise_name = all_values[i - 1]
            if not exercise_name or exercise_name.startswith("Dia"):
                break

            series_val = self.worksheet.cell(i, series_col).value or "Not logged"
            peso_val = self.worksheet.cell(i, peso_col).value or ""

            weight_str = f" @ {peso_val}kg" if peso_val else ""
            summary += f"- {exercise_name}: {series_val}{weight_str}\n"

        return summary
