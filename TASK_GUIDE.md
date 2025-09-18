# JARVIS Task & Memory System Guide 📝

## How to Tell JARVIS to Remember Tasks

JARVIS now has a sophisticated task memory system that stores everything in a SQLite database. Here's exactly how to use it:

### ✅ **Task Commands That Work:**

#### **Basic Task Addition:**

-  `"Remind me to [task]"`
-  `"Add task [description]"`
-  `"I need to [task]"`
-  `"Make a note [task]"`
-  `"Add reminder [task]"`
-  `"Create task [description]"`

#### **Tasks with Due Dates:**

-  `"Remind me to [task] tomorrow"`
-  `"I need to [task] next week"`
-  `"Add task [description] tomorrow"`

#### **View Your Tasks:**

-  `"My tasks"`
-  `"My reminders"`
-  `"What do I need to do"`
-  `"Show tasks"`
-  `"Current tasks"`

#### **Store General Information:**

-  `"Remember that [information]"`
-  `"Remember this [information]"`

### 📋 **Examples You Can Try:**

```
✅ "Remind me to buy groceries"
✅ "Add task finish the report"
✅ "I need to call mom tomorrow"
✅ "Make a note that I have a meeting at 3 PM"
✅ "Add reminder submit assignment next week"
✅ "Remember that I prefer tea over coffee"
✅ "My tasks"
```

### 🗄️ **Database Storage:**

All tasks are automatically stored in `jarvis_memory.db` with:

-  ✅ Task title and description
-  ✅ Due dates (if specified)
-  ✅ Priority levels
-  ✅ Creation timestamps
-  ✅ Completion status

### 🔍 **Viewing Tasks:**

When you ask "my tasks", JARVIS will show:

```
Here are your pending tasks:
1. Buy groceries
2. Call mom (due 2025-09-20)
3. Meeting at 3 PM [medium]
```

### 💾 **Memory vs Tasks:**

-  **Tasks:** Use "remind me", "add task", "I need to"
-  **Preferences:** Use "remember that", "remember this"
-  **Tasks** go to the tasks table for scheduling
-  **Preferences** go to the context table for personality

### 🚀 **What's New:**

The system now recognizes natural language patterns like:

-  "I need to..." → Creates task
-  "Don't forget..." → May create task or use AI response
-  "Make a note..." → Creates task
-  "Remember that..." → Stores as preference

### 🛠️ **Technical Details:**

-  **Database:** SQLite (`jarvis_memory.db`)
-  **Tables:** `tasks`, `conversations`, `context`
-  **Session:** Each conversation session has unique ID
-  **Persistence:** All data survives JARVIS restarts

Your JARVIS will now properly remember only the tasks you explicitly tell it to remember!
