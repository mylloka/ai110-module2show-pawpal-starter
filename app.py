import streamlit as st
from datetime import time, timedelta
from pawpal_system import Owner, Pet, Task, Priority, Recurrence

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")

# Keep the Owner instance in Streamlit session state so it is not recreated on every rerun.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", email="", phone="")

owner = st.session_state.owner
owner.name = st.text_input("Owner name", value=owner.name)
owner.email = st.text_input("Owner email", value=owner.email)
owner.phone = st.text_input("Owner phone", value=owner.phone)

st.markdown("### Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["Dog", "Cat", "Other"])
    with col2:
        pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
        pet_breed = st.text_input("Breed", value="Mixed")
    if st.form_submit_button("Add Pet"):
        if pet_name.strip():
            new_pet = Pet(name=pet_name.strip(), age=int(pet_age), species=species, breed=pet_breed.strip())
            if owner.add_pet(new_pet):
                st.success(f"Added {new_pet.name} to your pets!")
            else:
                st.warning(f"{new_pet.name} is already in your list.")
        else:
            st.error("Please enter a pet name.")

pets = owner.get_pets()
if pets:
    st.markdown("**Your pets:** " + ", ".join(f"{p.name} ({p.species})" for p in pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Add a Task")
if not pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title")
            selected_pet_name = st.selectbox("Assign to pet", [p.name for p in pets])
            recurrence = st.selectbox("Recurrence", ["None", "Daily", "Weekly"])
            recurrence_days = []
            if recurrence == "Weekly":
                recurrence_days = st.multiselect("Weekly on", DAYS_OF_WEEK, default=["Monday"])
        with col2:
            duration_mins = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            task_time_slot = st.time_input("Time slot", value=time(8, 0))
        with col3:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            task_description = st.text_input("Description", value="")
        if st.form_submit_button("Add task"):
            if task_title.strip():
                recurrence_indices = [DAYS_OF_WEEK.index(day) for day in recurrence_days]
                new_task = Task(
                    task_name=task_title.strip(),
                    description=task_description.strip(),
                    duration=timedelta(minutes=int(duration_mins)),
                    priority=Priority(priority),
                    time_slot=task_time_slot,
                    recurrence=Recurrence(recurrence),
                    recurrence_days=recurrence_indices,
                )
                target_pet = next(p for p in pets if p.name == selected_pet_name)
                if target_pet.add_task(new_task):
                    st.success(f"Added '{new_task.task_name}' to {target_pet.name}.")
                else:
                    st.warning("That task is already assigned to this pet.")
            else:
                st.error("Please enter a task name.")

    # Show tasks per pet, sorted chronologically
    scheduler_preview = owner.get_schedule()
    for pet in pets:
        pet_tasks = scheduler_preview.sort_by_time(pet.get_tasks())
        if pet_tasks:
            st.markdown(f"**{pet.name}'s tasks:**")
            st.table([
                {
                    "Task": t.task_name,
                    "Time": t.time_slot.strftime("%I:%M %p"),
                    "Duration": f"{t.duration_minutes()} min",
                    "Priority": t.priority.value,
                    "Repeats": t.recurrence.value,
                    "Status": "Done" if t.is_complete() else "Pending",
                }
                for t in pet_tasks
            ])

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not pets:
        st.warning("Add a pet and some tasks first.")
    else:
        scheduler = owner.get_schedule()
        scheduler.build_schedule()

        # Warn about any overlapping tasks before showing the plan
        conflicts = scheduler.get_conflicts()
        if conflicts:
            st.error(f"⚠️ {len(conflicts)} scheduling conflict(s) found — only the higher-priority task was kept in the plan.")
            for task_a, task_b in conflicts:
                pet_a = task_a.pet.name if task_a.pet else "Unknown"
                pet_b = task_b.pet.name if task_b.pet else "Unknown"
                st.warning(
                    f"**'{task_a.task_name}'** ({pet_a}) runs {task_a.time_slot.strftime('%I:%M %p')} – "
                    f"{(task_a.time_slot.replace(hour=(task_a.time_slot.hour + task_a.duration_minutes() // 60) % 24, minute=(task_a.time_slot.minute + task_a.duration_minutes()) % 60)).strftime('%I:%M %p')}"
                    f" · overlaps with **'{task_b.task_name}'** ({pet_b}) at {task_b.time_slot.strftime('%I:%M %p')}. "
                    f"Fix: reschedule one of these tasks to a different time."
                )

        plan = scheduler.get_daily_plan()
        if not plan:
            st.info("No tasks to schedule. Make sure your pets have tasks added.")
        else:
            pending = scheduler.get_pending_tasks()
            completed = scheduler.get_completed_tasks()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total scheduled", len(plan))
            col2.metric("Pending", len(pending))
            col3.metric("Completed", len(completed))

            st.markdown("#### Today's Plan")
            st.table([
                {
                    "Time": t.time_slot.strftime("%I:%M %p"),
                    "Task": t.task_name,
                    "Pet": t.pet.name if t.pet else "—",
                    "Priority": t.priority.value,
                    "Duration": f"{t.duration_minutes()} min",
                    "Repeats": t.recurrence.value,
                    "Notes": t.description or "—",
                }
                for t in plan
            ])
