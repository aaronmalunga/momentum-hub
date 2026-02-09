import datetime
from typing import Any, Dict, Optional

from . import momentum_db as db
from .habit import Habit


class Goal:
    """
    Represents a goal for a habit, tracking progress over a defined period.
    """

    def __init__(
        self,
        habit_id: int,
        target_period_days: int = 28,
        target_completions: Optional[int] = None,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        is_active: bool = True,
        id: Optional[int] = None,
        created_at: Optional[datetime.datetime] = None,
    ):
        self.id = id
        self.habit_id = habit_id
        self.target_period_days = (
            target_period_days  # e.g., 28 for daily, 28 for weekly (4 weeks)
        )
        self.target_completions = target_completions  # optional specific target
        self.start_date = (
            start_date  # Allow None for goals that start from habit creation
        )
        self.end_date = end_date
        self.is_active = is_active
        self.created_at = created_at or datetime.datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Goal":
        """Create a Goal instance from a dictionary."""
        return cls(
            id=data.get("id"),
            habit_id=data["habit_id"],
            target_period_days=data.get("target_period_days", 28),
            target_completions=data.get("target_completions"),
            start_date=(
                datetime.datetime.fromisoformat(data["start_date"])
                if data.get("start_date")
                else None
            ),
            end_date=(
                datetime.datetime.fromisoformat(data["end_date"])
                if data.get("end_date")
                else None
            ),
            is_active=data.get("is_active", True),
            created_at=(
                datetime.datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Goal instance to a dictionary."""
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "target_period_days": self.target_period_days,
            "target_completions": self.target_completions,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def calculate_progress(self, db_name: str) -> Dict[str, Any]:
        """
        Calculate progress towards this goal.
        Returns: {'count': int, 'total': int, 'percent': float, 'achieved': bool}
        """
        habit = db.get_habit(self.habit_id, db_name)
        if not habit:
            return {"count": 0, "total": 0, "percent": 0.0, "achieved": False}

        completions = db.get_completions(self.habit_id, db_name)
        # Filter completions within the goal period
        if self.start_date:
            completions = [c for c in completions if c >= self.start_date]
        if self.end_date:
            completions = [c for c in completions if c <= self.end_date]

        total = self.target_completions or self._calculate_expected_completions(habit)
        count = len(completions)
        percent = (count / total * 100) if total > 0 else 0.0
        achieved = count >= total

        return {
            "count": count,
            "total": total,
            "percent": percent,
            "achieved": achieved,
        }

    def _calculate_expected_completions(self, habit: Habit) -> int:
        """Calculate expected completions based on habit frequency and period."""
        if habit.frequency == "weekly":
            # For weekly habits, target is number of weeks in period
            return max(1, self.target_period_days // 7)
        else:  # daily
            return self.target_period_days

    def is_expired(self) -> bool:
        """Check if the goal has expired."""
        if not self.end_date:
            return False
        return datetime.datetime.now() > self.end_date

    def __repr__(self) -> str:
        return f"Goal(id={self.id}, habit_id={self.habit_id}, target_period_days={self.target_period_days})"
