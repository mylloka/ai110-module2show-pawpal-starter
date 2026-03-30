from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from enum import Enum
from typing import List, Optional, Tuple


class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


# Numeric rank so HIGH sorts first
_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}


class Recurrence(str, Enum):
    NONE = "None"
    DAILY = "Daily"
    WEEKLY = "Weekly"


@dataclass
class Task:
    task_name: str
    description: str
    duration: timedelta
    priority: Priority
    time_slot: time
    pet: Optional["Pet"] = field(default=None, repr=False)
    complete: bool = field(default=False, repr=False)
    recurrence: Recurrence = field(default=Recurrence.NONE)
    recurrence_days: List[int] = field(default_factory=list)  # 0=Mon … 6=Sun, used for WEEKLY
    scheduled_date: Optional[date] = field(default=None, repr=False)

    def is_complete(self) -> bool:
        """Return True if the task is complete."""
        return self.complete

    def mark_done(self) -> None:
        """Mark the task as complete."""
        self.complete = True

    def duration_minutes(self) -> int:
        """Return the task duration as whole minutes."""
        return int(self.duration.total_seconds() // 60)

    def next_occurrence(self, from_date: Optional[date] = None) -> Optional["Task"]:
        """Return a new Task for the next occurrence, or None if non-recurring.

        - DAILY:  next date = from_date + timedelta(days=1)
        - WEEKLY: next date = the nearest future weekday listed in recurrence_days
        """
        if self.recurrence == Recurrence.NONE:
            return None

        base = from_date or self.scheduled_date or date.today()

        if self.recurrence == Recurrence.DAILY:
            next_date = base + timedelta(days=1)
        else:  # WEEKLY
            if not self.recurrence_days:
                return None
            # For each recurrence day, compute days until next occurrence (% 7 wraps,
            # "or 7" turns 0 into 7 so same-weekday means next week, not today)
            days_until = min((d - base.weekday()) % 7 or 7 for d in self.recurrence_days)
            next_date = base + timedelta(days=days_until)

        return replace(self, complete=False, scheduled_date=next_date)


@dataclass
class Pet:
    name: str
    age: int
    species: str
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> bool:
        """Add a task to the pet's task list."""
        if task in self.tasks:
            return False
        task.pet = self
        self.tasks.append(task)
        return True

    def get_tasks(self) -> List[Task]:
        """Return the list of tasks for the pet."""
        return self.tasks


class Scheduler:
    def __init__(self, owner: "Owner", schedule_date: date):
        """Initialize the Scheduler with an owner and date."""
        self.owner = owner
        self.daily_tasks: List[Task] = []
        self.date = schedule_date

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _task_minutes(self, t: time, duration: timedelta) -> Tuple[int, int]:
        """Return (start_minutes, end_minutes) for a task."""
        start = t.hour * 60 + t.minute
        end = start + int(duration.total_seconds() // 60)
        return start, end

    def _has_time_conflict(self, task: Task) -> bool:
        """Return True if the given task overlaps in time with any already-scheduled task.

        Uses interval overlap logic: two tasks conflict when one starts before the
        other ends — i.e., new_start < existing_end AND new_end > existing_start.
        This catches partial overlaps, not just exact same-time matches.
        """
        new_start, new_end = self._task_minutes(task.time_slot, task.duration)
        for existing in self.daily_tasks:
            ex_start, ex_end = self._task_minutes(existing.time_slot, existing.duration)
            if new_start < ex_end and new_end > ex_start:
                return True
        return False

    def _is_within_available_times(self, task: Task) -> bool:
        """Check if the task's time slot is within the owner's available times."""
        if not self.owner.available_times:
            return True
        return task.time_slot in self.owner.available_times

    def _is_active_today(self, task: Task) -> bool:
        """Return True if a task should appear on the scheduler's current date.

        Rules by recurrence type:
        - DAILY:  always active.
        - WEEKLY: active only if today's weekday is in recurrence_days (0=Mon, 6=Sun).
        - NONE:   active if scheduled_date matches today, or if no date is set at all.
        """
        if task.recurrence == Recurrence.DAILY:
            return True
        if task.recurrence == Recurrence.WEEKLY:
            return self.date.weekday() in task.recurrence_days
        if task.scheduled_date is None:
            return True
        return task.scheduled_date == self.date

    # ------------------------------------------------------------------
    # Schedule building
    # ------------------------------------------------------------------

    def _collect_tasks(self, pet_filter: Optional["Pet"] = None, include_completed: bool = False) -> List[Task]:
        """Gather all tasks that are active on the scheduler's date, with optional filters.

        Arguments:
            pet_filter: if provided, only tasks belonging to this pet are included.
            include_completed: if False (default), completed tasks are excluded.

        Returns a flat list of Task objects pulled from every qualifying pet.
        """
        return [
            task
            for pet in self.owner.get_pets()
            if pet_filter is None or pet == pet_filter
            for task in pet.get_tasks()
            if (include_completed or not task.is_complete()) and self._is_active_today(task)
        ]

    def build_schedule(self, pet_filter: Optional["Pet"] = None, include_completed: bool = False) -> None:
        """Build the daily schedule from all available tasks.

        Arguments:
            pet_filter: include tasks only for a specific pet.
            include_completed: if True, completed tasks are kept in the plan.
        """
        self.daily_tasks.clear()
        all_tasks = self._collect_tasks(pet_filter, include_completed)
        # Sort by priority rank first, then by scheduled time.
        # The final daily plan is returned chronologically by get_daily_plan().
        all_tasks.sort(key=lambda t: (_PRIORITY_ORDER[t.priority], t.time_slot))
        for task in all_tasks:
            if not self._has_time_conflict(task) and self._is_within_available_times(task):
                self.daily_tasks.append(task)

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and automatically spawn the next occurrence for recurring tasks.

        Returns the newly created Task if one was spawned, otherwise None.
        """
        task.mark_done()
        next_task = task.next_occurrence(from_date=self.date)
        if next_task is not None and task.pet is not None:
            task.pet.add_task(next_task)
        return next_task

    def add_task(self, task: Task) -> bool:
        """Add a task to the daily schedule if possible."""
        if self._has_time_conflict(task) or not self._is_within_available_times(task):
            return False
        self.daily_tasks.append(task)
        return True

    def remove_task(self, task: Task) -> bool:
        """Remove a task from the daily schedule."""
        if task in self.daily_tasks:
            self.daily_tasks.remove(task)
            return True
        return False

    # ------------------------------------------------------------------
    # Querying the schedule
    # ------------------------------------------------------------------

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return a new list of tasks sorted chronologically by time_slot.

        Uses Python's sorted() with a lambda key on time_slot (a datetime.time
        object), which supports direct comparison so no string parsing is needed.
        The original list is not modified.
        """
        return sorted(tasks, key=lambda t: t.time_slot)

    def get_daily_plan(self) -> List[Task]:
        """Return all scheduled tasks sorted chronologically by time slot."""
        return self.sort_by_time(self.daily_tasks)

    def get_tasks_for_pet(self, pet: "Pet") -> List[Task]:
        """Return scheduled tasks assigned to a specific pet."""
        return [t for t in self.daily_tasks if t.pet == pet]

    def get_pending_tasks(self) -> List[Task]:
        """Return scheduled tasks that are not yet complete."""
        return [t for t in self.daily_tasks if not t.is_complete()]

    def get_completed_tasks(self) -> List[Task]:
        """Return scheduled tasks that have been marked complete."""
        return [t for t in self.daily_tasks if t.is_complete()]

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name."""
        tasks = self._collect_tasks(include_completed=True)
        if pet_name is not None:
            tasks = [task for task in tasks if task.pet and task.pet.name == pet_name]
        if completed is not None:
            tasks = [task for task in tasks if task.is_complete() == completed]
        return self.sort_by_time(tasks)

    def get_conflicts(self, pet_filter: Optional["Pet"] = None, include_completed: bool = False) -> List[Tuple[Task, Task]]:
        """Return all pairs of tasks that overlap in time on the current schedule date.

        Uses an O(n²) pairwise comparison across all collected tasks. For each pair,
        interval overlap is checked using: a_start < b_end AND a_end > b_start.
        Returns a list of (Task, Task) tuples — one tuple per conflicting pair.
        An empty list means no conflicts were found.
        """
        conflicts = []
        all_tasks = self._collect_tasks(pet_filter, include_completed)
        for i, a in enumerate(all_tasks):
            for b in all_tasks[i + 1:]:
                a_start, a_end = self._task_minutes(a.time_slot, a.duration)
                b_start, b_end = self._task_minutes(b.time_slot, b.duration)
                if a_start < b_end and a_end > b_start:
                    conflicts.append((a, b))
        return conflicts


class Owner:
    def __init__(self, name: str, email: str, phone: str, available_times: Optional[List[time]] = None):
        """Initialize the Owner with contact info and available times."""
        self.name = name
        self.email = email
        self.phone = phone
        self.available_times: List[time] = available_times or []
        self.pets: List[Pet] = []
        self._scheduler: Optional[Scheduler] = None

    def add_pet(self, pet: Pet) -> bool:
        """Add a pet to the owner's list of pets."""
        if pet in self.pets:
            return False
        self.pets.append(pet)
        return True

    def get_pets(self) -> List[Pet]:
        """Return the list of the owner's pets."""
        return self.pets

    def get_schedule(self) -> Scheduler:
        """Return the owner's Scheduler, creating it if necessary."""
        if self._scheduler is None:
            self._scheduler = Scheduler(self, date.today())
        return self._scheduler
