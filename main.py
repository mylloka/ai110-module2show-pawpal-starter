from datetime import datetime, time, timedelta
from pawpal_system import Owner, Pet, Task, Priority

# Create Owner
owner = Owner(name="Alex", email="alex@email.com", phone="555-1234")

# Create Pets
pet1 = Pet(name="Buddy", age=3, species="Dog", breed="Labrador")
pet2 = Pet(name="Mittens", age=2, species="Cat", breed="Siamese")

# Add Pets to Owner
owner.add_pet(pet1)
owner.add_pet(pet2)

walk_task = Task(
    task_name="Morning Walk",
    description=f"Walk {pet1.name} in the park",
    duration=timedelta(minutes=30),
    priority=Priority.HIGH,
    time_slot=time(hour=8, minute=0)
)

feed_task = Task(
    task_name="Feed Mittens",
    description=f"Feed {pet2.name} her breakfast",
    duration=timedelta(minutes=10),
    priority=Priority.MEDIUM,
    time_slot=time(hour=8, minute=30)
)

play_task = Task(
    task_name="Playtime",
    description=f"Play with {pet1.name} and {pet2.name}",
    duration=timedelta(minutes=20),
    priority=Priority.LOW,
    time_slot=time(hour=9, minute=0)
)

# Intentionally overlapping task to demonstrate conflict detection (8:10 AM overlaps walk 8:00–8:30)
groom_task = Task(
    task_name="Grooming",
    description=f"Groom {pet1.name}",
    duration=timedelta(minutes=30),
    priority=Priority.MEDIUM,
    time_slot=time(hour=8, minute=10)
)

# Add Tasks to Pets out of order to demonstrate sorting
pet1.add_task(play_task)
pet2.add_task(feed_task)
pet1.add_task(walk_task)
pet1.add_task(groom_task)

# Mark one task complete so filtering behavior can be shown
feed_task.mark_done()

# Build today's schedule
scheduler = owner.get_schedule()
scheduler.build_schedule()

# Check for scheduling conflicts and print warnings
print("=== Conflict Check ===")
conflicts = scheduler.get_conflicts()
if conflicts:
    for task_a, task_b in conflicts:
        pet_a = task_a.pet.name if task_a.pet else "Unknown"
        pet_b = task_b.pet.name if task_b.pet else "Unknown"
        print(
            f"WARNING: '{task_a.task_name}' ({pet_a}, {task_a.time_slot.strftime('%I:%M %p')}, "
            f"{task_a.duration_minutes()} min) overlaps with "
            f"'{task_b.task_name}' ({pet_b}, {task_b.time_slot.strftime('%I:%M %p')}, "
            f"{task_b.duration_minutes()} min)"
        )
else:
    print("No conflicts detected.")

# Print Owner and Pets info
print("=== Owner Info ===")
print(f"Name: {owner.name}")
print(f"Email: {owner.email}")
print(f"Phone: {owner.phone}")
print("\nPets:")
for pet in owner.get_pets():
    print(f"- {pet.name} ({pet.species}, {pet.breed}, Age: {pet.age})")

# Print Today's Schedule
print("\n=== Today's Schedule ===")
today_str = datetime.now().strftime('%A, %B %d, %Y')
print(f"Date: {today_str}\n")
for task in scheduler.get_daily_plan():
    time_str = task.time_slot.strftime('%I:%M %p')
    priority_str = f"{task.priority.value} priority"
    duration_text = f"{task.duration_minutes()} min"
    print(f"{time_str} | {task.task_name} ({priority_str}) for {task.pet.name}")
    print(f"    Description: {task.description}")
    print(f"    Duration: {duration_text}")

print("\n=== Filtered Task Views ===")
print(f"-- Pending tasks for {pet1.name} --")
for task in scheduler.filter_tasks(completed=False, pet_name=pet1.name):
    print(f"{task.time_slot.strftime('%I:%M %p')} | {task.task_name} ({task.duration_minutes()} min)")

print("\n-- Completed tasks --")
for task in scheduler.filter_tasks(completed=True):
    pet_name = task.pet.name if task.pet else "Unknown"
    print(f"{task.time_slot.strftime('%I:%M %p')} | {task.task_name} for {pet_name}")

print(f"\n-- All {pet2.name} tasks --")
for task in scheduler.filter_tasks(pet_name=pet2.name):
    status = "Done" if task.is_complete() else "Pending"
    print(f"{task.time_slot.strftime('%I:%M %p')} | {task.task_name} ({status})")
