#!/usr/bin/env python3
"""
JARVIS Memory Management Utility
Provides command-line tools for managing JARVIS memory, tasks, and conversations.
"""

from jarvis.memory import JarvisMemory
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add jarvis module to path
sys.path.append(str(Path(__file__).parent))


def list_conversations(memory: JarvisMemory, limit: int = 10):
    """List recent conversations"""
    conversations = memory.get_recent_conversations(limit=limit)

    if not conversations:
        print("No conversations found.")
        return

    print(f"\n=== Recent {len(conversations)} Conversations ===")
    for i, conv in enumerate(conversations, 1):
        timestamp = datetime.fromisoformat(
            conv['timestamp']).strftime("%Y-%m-%d %H:%M")
        print(f"\n{i}. [{timestamp}]")
        print(
            f"   You: {conv['user_message'][:100]}{'...' if len(conv['user_message']) > 100 else ''}")
        print(
            f"   JARVIS: {conv['ai_response'][:100]}{'...' if len(conv['ai_response']) > 100 else ''}")


def list_tasks(memory: JarvisMemory):
    """List all pending tasks"""
    tasks = memory.get_pending_tasks()

    if not tasks:
        print("No pending tasks.")
        return

    print(f"\n=== {len(tasks)} Pending Tasks ===")
    for i, task in enumerate(tasks, 1):
        due_info = f" (due {task['due_date']})" if task['due_date'] else ""
        priority_info = f" [{task['priority'].upper()}]" if task['priority'] != 'medium' else ""
        print(f"{i}. {task['title']}{due_info}{priority_info}")
        if task['description']:
            print(f"   Description: {task['description']}")


def add_task(memory: JarvisMemory, title: str, description: str = "", due_date: str = "", priority: str = "medium"):
    """Add a new task"""
    success = memory.add_task(
        title, description, due_date if due_date else None, priority)
    if success:
        print(f"✅ Added task: {title}")
    else:
        print(f"❌ Failed to add task: {title}")


def complete_task(memory: JarvisMemory, task_id: int):
    """Mark a task as completed"""
    success = memory.complete_task(task_id)
    if success:
        print(f"✅ Completed task ID {task_id}")
    else:
        print(f"❌ Failed to complete task ID {task_id} (task not found?)")


def search_conversations(memory: JarvisMemory, query: str, limit: int = 5):
    """Search conversations"""
    conversations = memory.search_conversations(query, limit=limit)

    if not conversations:
        print(f"No conversations found matching '{query}'.")
        return

    print(f"\n=== {len(conversations)} Conversations matching '{query}' ===")
    for i, conv in enumerate(conversations, 1):
        timestamp = datetime.fromisoformat(
            conv['timestamp']).strftime("%Y-%m-%d %H:%M")
        print(f"\n{i}. [{timestamp}]")
        print(f"   You: {conv['user_message']}")
        print(f"   JARVIS: {conv['ai_response']}")


def show_stats(memory: JarvisMemory):
    """Show memory statistics"""
    stats = memory.get_memory_stats()

    print("\n=== JARVIS Memory Statistics ===")
    print(f"📝 Conversations: {stats.get('conversations', 0)}")
    print(f"⏳ Pending Tasks: {stats.get('pending_tasks', 0)}")
    print(f"✅ Completed Tasks: {stats.get('completed_tasks', 0)}")
    print(f"🧠 Context Items: {stats.get('context_items', 0)}")


def show_reminders(memory: JarvisMemory):
    """Show due reminders"""
    reminders = memory.get_due_reminders()

    if not reminders:
        print("No reminders due today.")
        return

    print(f"\n=== {len(reminders)} Due Reminders ===")
    for i, reminder in enumerate(reminders, 1):
        due_info = f" (due {reminder['due_date']})" if reminder['due_date'] else ""
        priority_info = f" [{reminder['priority'].upper()}]" if reminder['priority'] != 'medium' else ""
        print(f"{i}. {reminder['title']}{due_info}{priority_info}")
        if reminder['description']:
            print(f"   Description: {reminder['description']}")


def cleanup_old_data(memory: JarvisMemory, days: int = 30):
    """Clean up old conversation data"""
    success = memory.cleanup_old_data(days)
    if success:
        print(f"✅ Cleaned up conversations older than {days} days")
    else:
        print(f"❌ Failed to clean up old data")


def main():
    parser = argparse.ArgumentParser(
        description="JARVIS Memory Management Utility")
    parser.add_argument("--db", default="jarvis_memory.db",
                        help="Database file path")

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    # List conversations
    conv_parser = subparsers.add_parser(
        "conversations", help="List recent conversations")
    conv_parser.add_argument(
        "--limit", type=int, default=10, help="Number of conversations to show")

    # List tasks
    tasks_parser = subparsers.add_parser("tasks", help="List pending tasks")

    # Add task
    add_parser = subparsers.add_parser("add-task", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("--description", default="",
                            help="Task description")
    add_parser.add_argument("--due", default="", help="Due date (YYYY-MM-DD)")
    add_parser.add_argument(
        "--priority", choices=["low", "medium", "high"], default="medium", help="Task priority")

    # Complete task
    complete_parser = subparsers.add_parser(
        "complete", help="Mark task as completed")
    complete_parser.add_argument(
        "task_id", type=int, help="Task ID to complete")

    # Search conversations
    search_parser = subparsers.add_parser(
        "search", help="Search conversations")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--limit", type=int, default=5, help="Number of results to show")

    # Show statistics
    stats_parser = subparsers.add_parser(
        "stats", help="Show memory statistics")

    # Show reminders
    reminders_parser = subparsers.add_parser(
        "reminders", help="Show due reminders")

    # Cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old data")
    cleanup_parser.add_argument(
        "--days", type=int, default=30, help="Keep data newer than this many days")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize memory
    memory = JarvisMemory(args.db)

    # Execute command
    if args.command == "conversations":
        list_conversations(memory, args.limit)
    elif args.command == "tasks":
        list_tasks(memory)
    elif args.command == "add-task":
        add_task(memory, args.title, args.description, args.due, args.priority)
    elif args.command == "complete":
        complete_task(memory, args.task_id)
    elif args.command == "search":
        search_conversations(memory, args.query, args.limit)
    elif args.command == "stats":
        show_stats(memory)
    elif args.command == "reminders":
        show_reminders(memory)
    elif args.command == "cleanup":
        cleanup_old_data(memory, args.days)


if __name__ == "__main__":
    main()
