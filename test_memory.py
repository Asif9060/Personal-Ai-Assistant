#!/usr/bin/env python3
"""
Test the JARVIS Memory System
"""

from jarvis.memory import JarvisMemory
import sys
from pathlib import Path

# Add jarvis module to path
sys.path.append(str(Path(__file__).parent))


def test_memory_system():
    """Test the memory system functionality"""
    print("🧠 Testing JARVIS Memory System...")

    # Initialize memory
    memory = JarvisMemory("test_memory.db")

    print("✅ Memory system initialized")

    # Test conversation saving
    test_conversations = [
        ("Hello JARVIS", "Hello! How can I help you today?"),
        ("What's the weather like?",
         "I don't have access to weather data, but I can help with other questions."),
        ("Remember that I love Python programming",
         "I've noted that down: you love Python programming"),
    ]

    session_id = "test_session_001"
    memory.start_session(session_id)

    print("\n📝 Saving test conversations...")
    for user_msg, ai_msg in test_conversations:
        success = memory.save_conversation(user_msg, ai_msg, session_id)
        print(f"   {'✅' if success else '❌'} {user_msg[:30]}...")

    # Test task creation
    print("\n📋 Testing task management...")
    tasks = [
        ("Call mom tomorrow", "Call mom", "2024-12-16", "high"),
        ("Buy groceries", "Buy groceries for the week", None, "medium"),
        ("Finish project report", "Complete the quarterly report", "2024-12-20", "high"),
    ]

    for title, desc, due, priority in tasks:
        success = memory.add_task(title, desc, due, priority)
        print(f"   {'✅' if success else '❌'} {title}")

    # Test memory retrieval
    print("\n🔍 Testing memory retrieval...")

    # Get recent conversations
    recent = memory.get_recent_conversations(limit=3)
    print(f"   Recent conversations: {len(recent)} found")

    # Get pending tasks
    pending = memory.get_pending_tasks()
    print(f"   Pending tasks: {len(pending)} found")

    # Search conversations
    search_results = memory.search_conversations("Python")
    print(f"   Search results for 'Python': {len(search_results)} found")

    # Get stats
    stats = memory.get_memory_stats()
    print(f"   Memory stats: {stats}")

    # Test context storage
    print("\n🧠 Testing context storage...")
    memory.store_context("user_language_preference", "Python", "preferences")
    memory.store_context("user_name", "User", "personal")

    # Retrieve context
    lang_pref = memory.get_context("user_language_preference")
    print(f"   Language preference: {lang_pref}")

    # Get all context
    all_context = memory.get_all_context()
    print(f"   All context items: {len(all_context)}")

    print("\n🎉 Memory system test completed successfully!")
    print("\nYou can now run JARVIS with full memory capabilities!")

    # Clean up test database
    import os
    os.remove("test_memory.db")
    print("   Test database cleaned up")


if __name__ == "__main__":
    test_memory_system()
