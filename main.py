
from datetime import time, date, datetime
from pawpal_system import Owner, Pet, Task, Priority

# Create Owner
owner = Owner(name="Alex", email="alex@email.com", phone="555-1234")

# Create Pets
pet1 = Pet(name="Buddy", age=3, species="Dog", breed="Labrador")
pet2 = Pet(name="Mittens", age=2, species="Cat", breed="Siamese")

# Add Pets to Owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create Tasks (using datetime for demonstration, but only time is stored in Task)
walk_task = Task(
    task_name="Morning Walk",
    description="Walk Buddy in the park",
    duration=time(hour=0, minute=30),
    priority=Priority.HIGH,
    time_slot=time(hour=8, minute=0)
)

feed_task = Task(
    task_name="Feed Mittens",
    description="Feed Mittens her breakfast",
    duration=time(hour=0, minute=10),
    priority=Priority.MEDIUM,
    time_slot=time(hour=8, minute=30)
)

play_task = Task(
    task_name="Playtime",
    description="Play with Buddy and Mittens",
    duration=time(hour=0, minute=20),
    priority=Priority.LOW,
    time_slot=time(hour=9, minute=0)
)

# Add Tasks to Pets
pet1.add_task(walk_task)
pet2.add_task(feed_task)
pet1.add_task(play_task)

# Build today's schedule
scheduler = owner.get_schedule()
scheduler.build_schedule()

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
    print(f"{time_str} | {task.task_name} ({priority_str}) for {task.pet.name}")
    print(f"    Description: {task.description}")
    print(f"    Duration: {task.duration.strftime('%M min')}")
    print()
