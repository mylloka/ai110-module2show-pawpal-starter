from datetime import date, time, timedelta

import pytest
from pawpal_system import Owner, Pet, Priority, Recurrence, Scheduler, Task


def test_task_completion():
    task = Task(
        task_name="Test Task",
        description="A test task",
        duration=timedelta(minutes=10),
        priority=Priority.LOW,
        time_slot=time(hour=10, minute=0)
    )
    assert not task.is_complete()
    task.mark_done()
    assert task.is_complete()


def test_task_addition_to_pet():
    pet = Pet(name="TestPet", age=1, species="Dog", breed="TestBreed")
    initial_count = len(pet.get_tasks())
    task = Task(
        task_name="Feed",
        description="Feed the pet",
        duration=timedelta(minutes=5),
        priority=Priority.MEDIUM,
        time_slot=time(hour=8, minute=0)
    )
    pet.add_task(task)
    assert len(pet.get_tasks()) == initial_count + 1


def test_scheduler_resolves_conflict_by_priority():
    owner = Owner(name="Sam", email="sam@example.com", phone="555-0000")
    pet = Pet(name="Buddy", age=4, species="Dog", breed="Beagle")
    owner.add_pet(pet)

    low_task = Task(
        task_name="Slow Walk",
        description="Lower priority overlapping task",
        duration=timedelta(minutes=60),
        priority=Priority.LOW,
        time_slot=time(hour=8, minute=0)
    )
    high_task = Task(
        task_name="Vet Call",
        description="Higher priority same window",
        duration=timedelta(minutes=30),
        priority=Priority.HIGH,
        time_slot=time(hour=8, minute=15)
    )
    pet.add_task(low_task)
    pet.add_task(high_task)

    scheduler = owner.get_schedule()
    scheduler.build_schedule()
    plan = scheduler.get_daily_plan()

    assert len(plan) == 1
    assert plan[0].task_name == "Vet Call"


def test_get_conflicts_detects_overlapping_tasks():
    owner = Owner(name="Lee", email="lee@example.com", phone="555-1111")
    pet = Pet(name="Mittens", age=3, species="Cat", breed="Siamese")
    owner.add_pet(pet)

    task_a = Task(
        task_name="Breakfast",
        description="Feed the cat",
        duration=timedelta(minutes=20),
        priority=Priority.MEDIUM,
        time_slot=time(hour=7, minute=30)
    )
    task_b = Task(
        task_name="Brush",
        description="Brush the cat",
        duration=timedelta(minutes=30),
        priority=Priority.LOW,
        time_slot=time(hour=7, minute=40)
    )
    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler(owner, date.today())
    conflicts = scheduler.get_conflicts()

    assert len(conflicts) == 1
    assert conflicts[0] == (task_a, task_b)


# ── Sorting correctness ───────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """Tasks added in reverse order must come back sorted earliest-first."""
    owner = Owner(name="A", email="a@a.com", phone="0")
    pet = Pet(name="Rex", age=2, species="Dog", breed="Lab")
    owner.add_pet(pet)

    late_task = Task(
        task_name="Evening Walk",
        description="",
        duration=timedelta(minutes=20),
        priority=Priority.LOW,
        time_slot=time(hour=18, minute=0),
    )
    early_task = Task(
        task_name="Morning Feed",
        description="",
        duration=timedelta(minutes=10),
        priority=Priority.HIGH,
        time_slot=time(hour=7, minute=0),
    )
    mid_task = Task(
        task_name="Afternoon Play",
        description="",
        duration=timedelta(minutes=15),
        priority=Priority.MEDIUM,
        time_slot=time(hour=13, minute=0),
    )
    # Add out of order on purpose
    pet.add_task(late_task)
    pet.add_task(early_task)
    pet.add_task(mid_task)

    scheduler = Scheduler(owner, date.today())
    scheduler.build_schedule()
    plan = scheduler.get_daily_plan()

    assert [t.task_name for t in plan] == ["Morning Feed", "Afternoon Play", "Evening Walk"]


# ── Recurrence logic ──────────────────────────────────────────────────────────

def test_mark_complete_daily_task_spawns_next_day():
    """Completing a DAILY task must add a new task scheduled for tomorrow."""
    owner = Owner(name="B", email="b@b.com", phone="0")
    pet = Pet(name="Luna", age=1, species="Cat", breed="Tabby")
    owner.add_pet(pet)
    today = date.today()

    daily_task = Task(
        task_name="Feed Luna",
        description="",
        duration=timedelta(minutes=5),
        priority=Priority.HIGH,
        time_slot=time(hour=8, minute=0),
        recurrence=Recurrence.DAILY,
        scheduled_date=today,
    )
    pet.add_task(daily_task)

    scheduler = Scheduler(owner, today)
    next_task = scheduler.mark_task_complete(daily_task)

    assert daily_task.is_complete()
    assert next_task is not None
    assert next_task.scheduled_date == today + timedelta(days=1)
    assert next_task.is_complete() is False
    assert next_task in pet.get_tasks()


def test_mark_complete_non_recurring_returns_none():
    """Completing a one-off task must return None — no next occurrence."""
    owner = Owner(name="C", email="c@c.com", phone="0")
    pet = Pet(name="Pip", age=3, species="Dog", breed="Pug")
    owner.add_pet(pet)

    one_off = Task(
        task_name="Vet Visit",
        description="",
        duration=timedelta(minutes=60),
        priority=Priority.HIGH,
        time_slot=time(hour=10, minute=0),
        recurrence=Recurrence.NONE,
    )
    pet.add_task(one_off)
    scheduler = Scheduler(owner, date.today())
    result = scheduler.mark_task_complete(one_off)

    assert one_off.is_complete()
    assert result is None


def test_weekly_next_occurrence_wraps_to_next_week():
    """A weekly task completed on its only recurrence day must land 7 days later."""
    today = date.today()
    task = Task(
        task_name="Weekly Bath",
        description="",
        duration=timedelta(minutes=20),
        priority=Priority.MEDIUM,
        time_slot=time(hour=9, minute=0),
        recurrence=Recurrence.WEEKLY,
        recurrence_days=[today.weekday()],  # only today's weekday
        scheduled_date=today,
    )
    next_task = task.next_occurrence(from_date=today)

    assert next_task is not None
    assert next_task.scheduled_date == today + timedelta(days=7)


# ── Conflict detection ────────────────────────────────────────────────────────

def test_exact_same_time_slot_is_a_conflict():
    """Two tasks starting at the identical time must be flagged as a conflict."""
    owner = Owner(name="D", email="d@d.com", phone="0")
    pet = Pet(name="Max", age=2, species="Dog", breed="Boxer")
    owner.add_pet(pet)

    task_a = Task(
        task_name="Walk",
        description="",
        duration=timedelta(minutes=30),
        priority=Priority.HIGH,
        time_slot=time(hour=8, minute=0),
    )
    task_b = Task(
        task_name="Feed",
        description="",
        duration=timedelta(minutes=10),
        priority=Priority.MEDIUM,
        time_slot=time(hour=8, minute=0),  # exact same time
    )
    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler(owner, date.today())
    conflicts = scheduler.get_conflicts()

    assert len(conflicts) == 1


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_pet_with_no_tasks_produces_empty_schedule():
    """A pet with no tasks should not crash and should return an empty plan."""
    owner = Owner(name="E", email="e@e.com", phone="0")
    pet = Pet(name="Ghost", age=1, species="Cat", breed="Unknown")
    owner.add_pet(pet)

    scheduler = Scheduler(owner, date.today())
    scheduler.build_schedule()

    assert scheduler.get_daily_plan() == []


def test_owner_with_no_pets_produces_empty_schedule():
    """An owner with zero pets should return an empty plan without crashing."""
    owner = Owner(name="F", email="f@f.com", phone="0")
    scheduler = Scheduler(owner, date.today())
    scheduler.build_schedule()

    assert scheduler.get_daily_plan() == []


def test_weekly_task_empty_recurrence_days_returns_none():
    """A WEEKLY task with no days configured must return None from next_occurrence."""
    task = Task(
        task_name="Orphan Task",
        description="",
        duration=timedelta(minutes=10),
        priority=Priority.LOW,
        time_slot=time(hour=9, minute=0),
        recurrence=Recurrence.WEEKLY,
        recurrence_days=[],  # misconfigured — no days set
    )
    assert task.next_occurrence() is None


def test_recurring_task_active_today():
    owner = Owner(name="Jill", email="jill@example.com", phone="555-2222")
    pet = Pet(name="Goldie", age=1, species="Fish", breed="Goldfish")
    owner.add_pet(pet)

    today = date.today()
    daily_task = Task(
        task_name="Water Check",
        description="Check tank water",
        duration=timedelta(minutes=5),
        priority=Priority.HIGH,
        time_slot=time(hour=9, minute=0),
        recurrence=Recurrence.DAILY,
    )
    weekly_task = Task(
        task_name="Filter Clean",
        description="Clean the filter",
        duration=timedelta(minutes=15),
        priority=Priority.MEDIUM,
        time_slot=time(hour=10, minute=0),
        recurrence=Recurrence.WEEKLY,
        recurrence_days=[today.weekday()],
    )
    one_off_task = Task(
        task_name="Vet Reminder",
        description="Reminder for today",
        duration=timedelta(minutes=10),
        priority=Priority.LOW,
        time_slot=time(hour=11, minute=0),
        scheduled_date=today,
    )
    skip_task = Task(
        task_name="Later Task",
        description="Not today",
        duration=timedelta(minutes=10),
        priority=Priority.LOW,
        time_slot=time(hour=12, minute=0),
        scheduled_date=today + timedelta(days=1),
    )

    pet.add_task(daily_task)
    pet.add_task(weekly_task)
    pet.add_task(one_off_task)
    pet.add_task(skip_task)

    scheduler = Scheduler(owner, today)
    scheduler.build_schedule()
    plan_names = [task.task_name for task in scheduler.get_daily_plan()]

    assert "Water Check" in plan_names
    assert "Filter Clean" in plan_names
    assert "Vet Reminder" in plan_names
    assert "Later Task" not in plan_names
