# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler goes beyond a simple task list — it applies real logic to build a conflict-free, priority-ordered daily plan.

**Priority-based selection**
Tasks are ranked High → Medium → Low using a numeric lookup (`_PRIORITY_ORDER`) before being added to the schedule. Higher-priority tasks always get their time slot first; lower-priority tasks are only added if no conflict exists.

**Interval conflict detection**
Two tasks conflict when their time windows overlap — not just when they share an exact start time. The check uses: `a_start < b_end AND a_end > b_start`. `build_schedule()` silently blocks conflicting tasks; `get_conflicts()` returns warning pairs so the UI can alert the user without crashing.

**Recurring tasks**
Tasks can repeat `Daily` or `Weekly`. When `mark_task_complete()` is called on a recurring task, it automatically calculates the next occurrence using `timedelta` arithmetic and registers it on the pet — no manual re-entry needed. Weekly recurrence supports multiple days and uses modular weekday math to always find the nearest future occurrence.

**Chronological output**
`sort_by_time()` uses Python's `sorted()` with a `lambda` key on `time_slot` to return the final plan in clock order, regardless of the priority order used internally during scheduling.

## Testing PawPal+

### Run the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Area | Tests |
|---|---|
| **Sorting** | Tasks added out of order are returned chronologically by `get_daily_plan()` |
| **Recurrence — Daily** | Completing a daily task spawns a new task scheduled for the next day |
| **Recurrence — Weekly** | Completing a weekly task on its only day schedules it exactly 7 days later |
| **Recurrence — None** | Completing a one-off task returns `None` and spawns nothing |
| **Conflict detection** | Overlapping tasks and exact same-time tasks are both flagged by `get_conflicts()` |
| **Priority resolution** | When two tasks conflict, the higher-priority task wins the slot |
| **Edge cases** | Pet with no tasks, owner with no pets, and weekly task with no days configured all return safely without crashing |
| **Recurrence gate** | Daily, weekly, and date-specific tasks are correctly included or excluded based on the schedule date |

### Confidence level

⭐⭐⭐⭐ 4/5

All 13 tests pass. Core behaviors — scheduling, conflict detection, sorting, and recurrence — are verified. One star held back because `available_times` filtering and midnight-spanning tasks have not been tested yet, and the test suite does not cover the Streamlit UI layer directly.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
