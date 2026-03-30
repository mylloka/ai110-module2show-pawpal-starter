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
