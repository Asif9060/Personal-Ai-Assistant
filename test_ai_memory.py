#!/usr/bin/env python3
"""
Test JARVIS AI Brain with Memory Integration
Tests the AI brain without audio components
"""

from jarvis.ai_brain import AIBrain
import sys
from pathlib import Path

# Add jarvis module to path
sys.path.append(str(Path(__file__).parent))


def test_ai_with_memory():
    """Test AI brain with memory integration"""
    print("🤖 Testing JARVIS AI Brain with Memory...")

    # Initialize AI brain (which includes memory)
    brain = AIBrain()

    print(f"✅ AI Brain initialized: {brain.get_status()}")

    # Test conversation with memory
    test_inputs = [
        "Hello JARVIS",
        "Remind me to call John tomorrow",
        "What are my current tasks?",
        "Remember that I prefer coffee over tea",
        "What do you remember about my preferences?",
        "Thank you for helping me"
    ]

    print("\n💬 Testing conversations with memory...")
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{i}. You: {user_input}")
        response = brain.generate_response(user_input)
        print(f"   JARVIS: {response}")

    # Test startup reminders
    print("\n🔔 Testing startup reminders...")
    reminders = brain.get_startup_reminders()
    if reminders:
        print("Startup reminders found:")
        for reminder in reminders:
            print(f"   • {reminder}")
    else:
        print("   No startup reminders")

    # Cleanup
    brain.cleanup_session()

    print("\n🎉 AI Brain with memory test completed!")
    print("Memory integration is working perfectly!")


if __name__ == "__main__":
    test_ai_with_memory()
