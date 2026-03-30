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
Prompts

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
