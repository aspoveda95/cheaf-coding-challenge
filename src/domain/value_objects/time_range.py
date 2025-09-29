"""TimeRange value object."""
# Standard Python Libraries
from datetime import datetime, time
from typing import Optional


class TimeRange:
    """TimeRange value object representing a time window."""

    def __init__(self, start_time: time, end_time: time):
        """Initialize TimeRange value object.

        Args:
            start_time: Start time of the range
            end_time: End time of the range
        """
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")

        self._start_time = start_time
        self._end_time = end_time

    @property
    def start_time(self) -> time:
        """Get the start time."""
        return self._start_time

    @property
    def end_time(self) -> time:
        """Get the end time."""
        return self._end_time

    def is_active_now(self, current_time: Optional[datetime] = None) -> bool:
        """Check if the time range is currently active."""
        if current_time is None:
            current_time = datetime.now()

        current_time_only = current_time.time()
        return self._start_time <= current_time_only <= self._end_time

    def is_active_at(self, check_time) -> bool:
        """Check if the time range is active at a specific time."""
        if hasattr(check_time, "time"):
            # If it's a datetime object, extract the time part
            check_time_only = check_time.time()
        else:
            # If it's already a time object, use it directly
            check_time_only = check_time
        return self._start_time <= check_time_only <= self._end_time

    def duration_minutes(self) -> int:
        """Get duration in minutes."""
        start_minutes = self._start_time.hour * 60 + self._start_time.minute
        end_minutes = self._end_time.hour * 60 + self._end_time.minute
        return end_minutes - start_minutes

    def __str__(self) -> str:
        """Return string representation of TimeRange."""
        return f"{self._start_time} - {self._end_time}"

    def __repr__(self) -> str:
        """Return detailed string representation of TimeRange."""
        return f"TimeRange({self._start_time}, {self._end_time})"

    def __eq__(self, other) -> bool:
        """Check equality based on start and end times."""
        if not isinstance(other, TimeRange):
            return False
        return (
            self._start_time == other._start_time and self._end_time == other._end_time
        )

    def __hash__(self) -> int:
        """Return hash based on start and end times."""
        return hash((self._start_time, self._end_time))
