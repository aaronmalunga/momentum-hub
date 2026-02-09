import datetime
from typing import Any, Dict, List, Optional

from .habit import Habit


class Category:
    """
    Represents a category for grouping habits.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        is_active: bool = True,
        id: Optional[int] = None,
        created_at: Optional[datetime.datetime] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.color = color  # e.g., hex color code
        self.is_active = is_active
        self.created_at = created_at or datetime.datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        """Create a Category instance from a dictionary."""
        return cls(
            id=data.get("id"),
            name=data["name"],
            description=data.get("description"),
            color=data.get("color"),
            is_active=data.get("is_active", True),
            created_at=(
                datetime.datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Category instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "is_active": self.is_active,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
        }

    def get_habits(self, db_name: str) -> List[Habit]:
        """Get all habits in this category."""
        from . import momentum_db as db

        if self.id is None:
            return []
        return db.get_habits_by_category(self.id, db_name=db_name)

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name='{self.name}')"
