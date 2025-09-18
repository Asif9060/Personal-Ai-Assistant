# JARVIS Memory System - Installation & Usage Guide

## 🧠 Memory System Overview

JARVIS now has a persistent memory system using SQLite that remembers:

-  **All conversations** across sessions
-  **Tasks and reminders** with due dates
-  **Important context** and facts
-  **Session history** for continuity

## 🚀 Installation Process

### 1. Dependencies Already Installed

The memory system uses SQLite3 which is built into Python, so no additional packages are needed beyond what you already have.

### 2. Database Auto-Creation

The SQLite database (`jarvis_memory.db`) will be automatically created in your project directory when you first run JARVIS.

### 3. Files Added/Modified

-  **`jarvis/memory.py`** - Core memory management system
-  **`jarvis/ai_brain.py`** - Updated with memory integration
-  **`jarvis/assistant.py`** - Shows startup reminders
-  **`manage_memory.py`** - Command-line memory management tool

## 💬 Using the Memory System

### Conversation Memory

JARVIS automatically remembers all your conversations:

```
You: "Remember that I prefer Python over JavaScript"
JARVIS: "I've noted that down: you prefer Python over JavaScript"

[Later session]
You: "What programming language should I use?"
JARVIS: "Based on our previous conversation, you prefer Python..."
```

### Task Management

Add tasks and reminders with natural language:

```
You: "Remind me to call mom tomorrow"
JARVIS: "I'll remind you tomorrow: call mom"

You: "Add task: finish the project report"
JARVIS: "I've noted that down: finish the project report"

You: "Remember to buy groceries next week"
JARVIS: "I'll remind you next week: buy groceries"
```

### View Your Tasks

```
You: "What are my tasks?"
You: "Show my reminders"
You: "What do I need to do?"
```

### Search Previous Conversations

```
You: "What did we talk about yesterday?"
You: "Did I ask about Python?"
You: "Remember when we discussed the project?"
```

### Memory Status

```
You: "What do you remember?"
You: "Memory stats"
```

## 🛠️ Command-Line Memory Management

Use the `manage_memory.py` script for advanced memory management:

### View Recent Conversations

```powershell
python manage_memory.py conversations --limit 5
```

### List All Tasks

```powershell
python manage_memory.py tasks
```

### Add Task from Command Line

```powershell
python manage_memory.py add-task "Buy birthday gift" --due 2024-12-25 --priority high
```

### Complete a Task

```powershell
python manage_memory.py complete 1
```

### Search Conversations

```powershell
python manage_memory.py search "Python programming"
```

### View Memory Statistics

```powershell
python manage_memory.py stats
```

### Show Due Reminders

```powershell
python manage_memory.py reminders
```

### Clean Up Old Data

```powershell
python manage_memory.py cleanup --days 30
```

## 🌟 Key Features

### 1. Persistent Memory

-  All conversations saved automatically
-  Memory persists between JARVIS sessions
-  Context-aware responses based on history

### 2. Smart Task Management

-  Natural language task creation
-  Due date recognition ("tomorrow", "next week")
-  Priority levels (low, medium, high)
-  Automatic startup reminders

### 3. Conversation Context

-  JARVIS remembers previous discussions
-  Can reference past conversations
-  Builds on previous knowledge

### 4. Startup Reminders

When you start JARVIS, it will automatically tell you about:

-  Tasks due today
-  Overdue reminders
-  Important pending items

## 📊 Database Structure

The SQLite database contains these tables:

-  **conversations** - All chat history
-  **tasks** - Tasks and reminders with due dates
-  **context** - Important facts and preferences
-  **sessions** - Conversation session tracking

## 🔧 Advanced Usage

### Custom Database Location

```python
from jarvis.memory import JarvisMemory
memory = JarvisMemory("custom_path/my_jarvis.db")
```

### Backup Your Memory

Simply copy the `jarvis_memory.db` file to backup all your conversations and tasks.

### Memory Cleanup

Old conversations are automatically managed, but tasks and important context are kept indefinitely.

## 🚨 Troubleshooting

### If Memory Features Don't Work

1. Check that `jarvis_memory.db` was created in your project directory
2. Ensure you have write permissions in the project folder
3. Run `python manage_memory.py stats` to verify the database

### Database Corruption

If the database gets corrupted:

1. Delete `jarvis_memory.db`
2. Restart JARVIS (it will create a new database)
3. Your memory will be reset, but the system will work again

## 🎯 Example Usage Session

```
🎤 JARVIS AI assistant online. How can I help you?
🔔 You have 2 tasks that need attention:
   • Call mom (due 2024-12-15)
   • Buy birthday gift (due 2024-12-25)

You: "Remind me to review the code tomorrow"
JARVIS: "I'll remind you tomorrow: review the code"

You: "What are my current tasks?"
JARVIS: "Here are your pending tasks:
1. Call mom (due 2024-12-15)
2. Buy birthday gift (due 2024-12-25) [high]
3. Review the code (due 2024-12-16)"

You: "What did we talk about last time?"
JARVIS: "We've been chatting about various topics. Is there something specific you'd like me to recall?"
```

## 📈 Benefits

✅ **Never forget conversations** - Full chat history preserved
✅ **Smart reminders** - Automatic task notifications  
✅ **Context awareness** - Responses based on past discussions
✅ **Easy management** - Simple voice commands and CLI tools
✅ **Reliable storage** - SQLite database for data integrity
✅ **Privacy focused** - All data stored locally on your machine

The memory system makes JARVIS truly intelligent and personal, learning from your interactions and helping you stay organized! 🎉
