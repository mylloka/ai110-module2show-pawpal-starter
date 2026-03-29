import pytest
from datetime import time
from pawpal_system import Task, Pet, Priority

def test_task_completion():
    task = Task(
        task_name="Test Task",
        description="A test task",
        duration=time(hour=0, minute=10),
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
        duration=time(hour=0, minute=5),
        priority=Priority.MEDIUM,
        time_slot=time(hour=8, minute=0)
    )
    pet.add_task(task)
    assert len(pet.get_tasks()) == initial_count + 1
