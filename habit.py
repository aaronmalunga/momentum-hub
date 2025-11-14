import datetime
from typing import Optional, Dict, Any, List
from error_manager import error_manager

class Habit:
    """
    Class to represent a habit
    Attributes:
        - id: Unique identifier for the habit
        - name: The name of the habit
        - frequency: The frequency at which the habit is to be performed (daily, weekly, monthly)
        - notes: Additional notes about the habit
        - reminder_time: Morning reminder time
        - evening_reminder_time: Evening reminder time
        - streak: Current streak count
        - created_at: When the habit was created
        - last_completed: When the habit was last completed
        - is_active: Whether the habit is active
        - reactivated_at: When the habit was last reactivated (optional)
    """

    def __init__(self, id=None, name=None, frequency=None, notes=None,
                 reminder_time=None, evening_reminder_time=None, streak=0,
                 created_at=None, last_completed=None, is_active=True, reactivated_at=None, category_id=None):
        self.id = id
        self.name = name
        self.frequency = frequency
        self.notes = notes
        self.reminder_time = reminder_time
        self.evening_reminder_time = evening_reminder_time
        self.streak = streak
        self.created_at = created_at
        self.last_completed = last_completed
        self.is_active = is_active
        self.reactivated_at = reactivated_at
        self.category_id = category_id

    def edit_habit(self, name: Optional[str] = None, frequency: Optional[str] = None,
                    notes: Optional[str] = None, reminder_time: Optional[str] = None,
                    evening_reminder_time: Optional[str] = None):
        """
        Edit the habit's attributes.
        """
        if name is not None:
            self.name = name
        if frequency is not None:
            self.frequency = frequency
        if notes is not None:
            self.notes = notes
        if reminder_time is not None:
            self.reminder_time = reminder_time
        if evening_reminder_time is not None:
            self.evening_reminder_time = evening_reminder_time
    
    def delete_habit(self):
        """
        Mark the habit as inactive (soft deletion).
        """
        self.is_active = False

    def mark_completed(self, dt: Optional[datetime.datetime] = None):
        """
        Mark the habit as completed for a particular datetime.( default set to now)
        Updates streak and last completed date and time of habit
        """
        now = dt or datetime.datetime.now()
        if self.last_completed is not None:
            delta_days = (now.date() - self.last_completed.date()).days
            if self.frequency == 'daily' and delta_days == 1:
                self.streak += 1
            elif self.frequency == 'weekly' and delta_days > 0:
                self.streak += 1
            else:
                self.streak = 1 # where streak is reset if missed
        else:
            self.streak = 1 # first completion        
        self.last_completed = now

    def calculate_longest_streak(self, completions: List[datetime.datetime]) -> int:
        """
        Calculate the longest streak of habit completions.

        Args:
            completions: List of datetime objects representing habit completions.
        Returns:
            int: The longest streak of consecutive completions.
        """
        if not completions:
            return 0

        if self.frequency == 'daily':
            unique_dates = sorted(list(set(c.date() for c in completions)))
            if not unique_dates:
                return 0

            longest_streak = 1
            current_streak = 1
            last_completed_date = unique_dates[0]

            for current_date in unique_dates[1:]:
                if (current_date - last_completed_date).days == 1:
                    current_streak += 1
                else:
                    current_streak = 1
                longest_streak = max(longest_streak, current_streak)
                last_completed_date = current_date

            return longest_streak
        elif self.frequency == 'weekly':
            unique_weeks = sorted(set(c.date().isocalendar()[:2] for c in completions))
            if not unique_weeks:
                return 0

            longest_streak = 1
            current_streak = 1
            last_week = unique_weeks[0]

            for current_week in unique_weeks[1:]:
                # Check if consecutive weeks
                if (current_week[0] == last_week[0] and current_week[1] == last_week[1] + 1) or \
                   (current_week[0] == last_week[0] + 1 and current_week[1] == 1 and last_week[1] == 52):
                    current_streak += 1
                else:
                    current_streak = 1
                longest_streak = max(longest_streak, current_streak)
                last_week = current_week

            return longest_streak
        else:
            # For other frequencies, treat as daily for now
            return 0

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the habit to a dictionary for database storage (db)
        """
        return {
            'id': self.id,
            'name': self.name,
            'frequency': self.frequency,
            'notes': self.notes,
            'reminder_time': self.reminder_time,
            'evening_reminder_time': self.evening_reminder_time,
            'streak': self.streak,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_completed': self.last_completed.isoformat() if self.last_completed else None,
            'is_active': self.is_active,
            'reactivated_at': self.reactivated_at.isoformat() if self.reactivated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str,Any]) -> 'Habit':
        """
        Create a Habit instance from a dictionary (e.g from db).
        """
        created_at_dt = None
        if data.get('created_at'):
            try:
                created_at_dt = datetime.datetime.fromisoformat(data['created_at'])
            except ValueError:
                try:
                    created_at_dt = datetime.datetime.strptime(data['created_at'], '%Y-%m-%d')
                except ValueError:
                    created_at_dt = None

        last_completed_dt = None
        if data.get('last_completed'):
            try:
                last_completed_dt = datetime.datetime.fromisoformat(data['last_completed'])
            except ValueError:
                try:
                    last_completed_dt = datetime.datetime.strptime(data['last_completed'], '%Y-%m-%d')
                except ValueError:
                    last_completed_dt = None

        reactivated_at_dt = None
        if data.get('reactivated_at'):
            try:
                reactivated_at_dt = datetime.datetime.fromisoformat(data['reactivated_at'])
            except ValueError:
                try:
                    reactivated_at_dt = datetime.datetime.strptime(data['reactivated_at'], '%Y-%m-%d')
                except ValueError:
                    reactivated_at_dt = None

        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            frequency=data.get('frequency', ''),
            notes=data.get('notes'),
            reminder_time=data.get('reminder_time'),
            evening_reminder_time=data.get('evening_reminder_time'),
            streak=data.get('streak', 0),
            created_at=created_at_dt,
            last_completed=last_completed_dt,
            is_active=data.get('is_active', True),
            reactivated_at=reactivated_at_dt,
            category_id=data.get('category_id')
        )

    
        
        


