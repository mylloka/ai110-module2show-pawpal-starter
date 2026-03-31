# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My initial UML design consists of the classes: Owner, Pet, task and scheduler. 
The owner class will store the pet owners information and his available time. 
The Pet class will store the pets information, that includes name, age and species.
The Task class consists of each task activity that the owner would like to implement in daily plan, such as walks, taking to the vet, etc.
Scheduler Class combines the owners schedula and what tasks needs to be done for a daile schedule. 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- The original code manually found the next recurrence day using multiple steps, while the new version simplifies it by using min() and % 7 or 7 to handle everything more cleanly. When a user adds a pet, the UI calls a class method like add_pet() to create and store the object, and Streamlit reruns the app to automatically display the updated list. I changed the net_occurence at paypal_system


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I was able to use AI to help me implement functions and debug and brainstorm.
- What kinds of prompts or questions were most helpful?
Prompts that were specific and not vague ex: when I asked the ai "How could this algorithm be simplified for better readability or performance?"

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
I did not accept an Ai suggestion when it decided to delete everything, without replacing or implementing any codes. When it was asked to connect the UI to backend. 

- How did you evaluate or verify what the AI suggested?
I checked and evaluated the diff. Although the AI suggestion worked it was lacking simplicity and it was repeating if statements. 


---

## 4. Testing and Verification

**a. What you tested**

The test suite covers 13 behaviors across five areas: basic task completion and pet task addition, priority-based conflict resolution (high-priority task wins when two overlap), chronological sorting (tasks added out of order return sorted by time), recurrence logic (daily task spawns tomorrow's copy, weekly task wraps to next week, one-off returns None), conflict detection (both partial overlaps and exact same-time slots), and edge cases (pet with no tasks, owner with no pets, weekly task with no days configured). These tests matter because they verify the core scheduling guarantee — that the plan produced is always conflict-free, correctly ordered, and handles recurring tasks automatically without crashing on bad input.


**b. Confidence**

All 13 tests pass, covering the main happy paths and the most likely failure points, so confidence in the core scheduling logic is high — roughly 4 out of 5. The remaining uncertainty comes from behaviors that were not formally tested: the available_times filter uses an exact time_slot match which could silently exclude valid tasks, tasks that span midnight are not handled since _task_minutes assumes all times fall within a single day, and the Streamlit UI layer has no automated tests at all. Given more time, the next edge cases to test would be an owner with available_times set to confirm tasks are not incorrectly blocked, build_schedule() called on a day where no weekly tasks are scheduled to confirm an empty plan is returned cleanly, and mark_task_complete() called twice on the same task to confirm it does not spawn duplicate next occurrences.


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The scheduling backend in pawpal_system.py is the part most worth being satisfied with — specifically how build_schedule(), get_conflicts(), and next_occurrence() work as a connected system. Each method has a single clear job, the priority bug was caught and fixed with a real solution (_PRIORITY_ORDER dict), and the weekly recurrence logic was refactored from 7 lines down to 2 using modular arithmetic. The result is a backend that runs independently of the UI, passes all 13 tests, and handles recurring tasks automatically without the user having to re-enter them.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
The available_times feature would be redesigned — it currently checks if a task's exact time_slot is in the owner's list, which means a task at 8:05 AM would be blocked even if the owner is free from 8:00–10:00. It should use a time range instead of an exact match. The UI would also be improved by adding a "Mark Complete" button per task in the schedule view so the owner can trigger mark_task_complete() directly from the browser, rather than only being able to do it through code.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The most important thing learned is that AI is most useful when you already understand what you want — it can implement, refactor, and explain, but it cannot decide what the right behavior is. The moments where the output had to be rejected (rewriting the whole file instead of editing it, using the wrong type for duration) were moments where the prompt lacked a constraint the AI had no way to infer. Being specific — "don't delete comments," "only add what is necessary" — produced better results than open-ended requests. The human judgment is in knowing what to ask for and whether the result is actually correct.
