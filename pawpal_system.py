from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from typing import List, Optional


class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class Task:
    task_name: str
    description: str
    duration: time
    priority: Priority
    time_slot: time
    pet: Optional["Pet"] = field(default=None, repr=False)
    complete: bool = field(default=False, repr=False)

    def is_complete(self) -> bool:
        """Return True if the task is complete."""
        return self.complete

    def mark_done(self) -> None:
        """Mark the task as complete."""
        self.complete = True


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
    def get_all_owner_tasks(self) -> List[Task]:
        """Return all tasks from all pets belonging to the owner."""
        tasks = []
        for pet in self.owner.get_pets():
            tasks.extend(pet.get_tasks())
        return tasks
    def __init__(self, owner: "Owner", schedule_date: date):
        """Initialize the Scheduler with an owner and date."""
        self.owner = owner
        self.daily_tasks: List[Task] = []
        self.date = schedule_date

    def _has_time_conflict(self, task: Task) -> bool:
        """Check if the task's time slot conflicts with existing tasks."""
        return any(existing.time_slot == task.time_slot for existing in self.daily_tasks)

    def _is_within_available_times(self, task: Task) -> bool:
        """Check if the task's time slot is within the owner's available times."""
        if not self.owner.available_times:
            return True
        return task.time_slot in self.owner.available_times

    def build_schedule(self) -> None:
        """Build the daily schedule from all available tasks."""
        self.daily_tasks.clear()
        all_tasks = []
        for pet in self.owner.get_pets():
            all_tasks.extend([task for task in pet.get_tasks() if not task.is_complete()])
        all_tasks.sort(key=lambda t: (t.priority.value, t.time_slot))
        for task in all_tasks:
            if not self._has_time_conflict(task) and self._is_within_available_times(task):
                self.daily_tasks.append(task)

    def add_task(self, task: Task) -> bool:
        """Add a task to the daily schedule if possible."""
        if self._has_time_conflict(task):
            return False
        if not self._is_within_available_times(task):
            return False
        self.daily_tasks.append(task)
        return True

    def remove_task(self, task: Task) -> bool:
        """Remove a task from the daily schedule."""
        if task in self.daily_tasks:
            self.daily_tasks.remove(task)
            return True
        return False

    def get_daily_plan(self) -> List[Task]:
        """Return the list of tasks scheduled for today."""
        return list(self.daily_tasks)


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
