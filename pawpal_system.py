from dataclasses import dataclass, field
from datetime import date, time
from typing import List, Optional


@dataclass
class Task:
    task_name: str
    description: str
    duration: time
    priority: str
    time_slot: time
    _complete: bool = field(default=False, repr=False)

    def is_complete(self) -> bool:
        pass

    def mark_done(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    age: int
    species: str
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> bool:
        pass

    def get_tasks(self) -> List[Task]:
        pass


class Scheduler:
    def __init__(self, owner: "Owner", schedule_date: date):
        self.owner = owner
        self.daily_tasks: List[Task] = []
        self.date = schedule_date

    def build_schedule(self) -> None:
        pass

    def add_task(self, task: Task) -> bool:
        pass

    def remove_task(self, task: Task) -> bool:
        pass

    def get_daily_plan(self) -> List[Task]:
        pass


class Owner:
    def __init__(self, name: str, email: str, phone: str, available_times: Optional[List[time]] = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.available_times: List[time] = available_times or []
        self.pets: List[Pet] = []
        self._scheduler: Optional[Scheduler] = None

    def add_pet(self, pet: Pet) -> bool:
        pass

    def get_pets(self) -> List[Pet]:
        pass

    def get_schedule(self) -> Scheduler:
        pass
