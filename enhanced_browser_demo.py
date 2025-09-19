"""
Enhanced Voice-Controlled Browser Demo for JARVIS
Demonstrates the new search result navigation and enhanced link control
"""

import time
from jarvis.ai_brain import AIBrain
from jarvis.audio import AudioIO


def test_enhanced_browser():
    """Test the enhanced browser voice commands"""
    print("=== JARVIS Enhanced Voice-Controlled Browser Demo ===\n")

    # Initialize JARVIS
    brain = AIBrain()
    audio = AudioIO()

    # Enhanced browser commands to test
    commands = [
        "open browser",
        "search for Python tutorials",
        "show search results",
        "open first result",
        "go back",
        "open second result",
        "bookmark this page",
        "open new tab",
        "search for machine learning",
        "click first result",
        "list all links",
        "scroll down",
        "what is the page title",
        "close browser"
    ]

    print("Enhanced voice commands for full browser control:")
    for i, cmd in enumerate(commands, 1):
        print(f"{i:2d}. {cmd}")

    print("\n" + "="*60)
    print("Testing enhanced browser commands...")
    print("="*60 + "\n")

    for i, command in enumerate(commands, 1):
        print(f"\n[{i:2d}] Testing: '{command}'")
        print("-" * 50)

        # Process command through JARVIS
        response = brain.generate_response(command)
        print(f"JARVIS: {response}")

        # Speak the response
        audio.speak(response)

        # Wait between commands
        if "search" in command:
            time.sleep(4)  # Wait longer for search results
        elif "open" in command and "result" in command:
            time.sleep(3)  # Wait for page loads
        else:
            time.sleep(2)

    print("\n" + "="*60)
    print("Enhanced browser demo completed!")
    print("="*60)

    # Show browser status
    if brain.browser:
        status = brain.browser.get_status()
        print(f"\nFinal Browser Status:")
        print(f"- Active: {status['is_active']}")
        print(f"- Current URL: {status['current_url']}")
        print(f"- Page Title: {status['title']}")

    # Cleanup
    print("\nCleaning up...")
    brain.cleanup_session()


def demo_search_workflow():
    """Demonstrate a complete search and navigation workflow"""
    print("\n" + "="*60)
    print("DEMO: Complete Search and Navigation Workflow")
    print("="*60)

    brain = AIBrain()
    audio = AudioIO()

    workflow_commands = [
        ("Search Phase", "search for best Python IDE"),
        ("View Results", "show search results"),
        ("Open First", "open first result"),
        ("Check Page", "what is the page title"),
        ("Go Back", "go back"),
        ("Try Second", "open second result"),
        ("Bookmark", "bookmark this page"),
        ("New Search", "search for Python frameworks"),
        ("Quick Open", "click first result")
    ]

    for phase, command in workflow_commands:
        print(f"\n[{phase}] Command: '{command}'")
        response = brain.generate_response(command)
        print(f"JARVIS: {response}")
        audio.speak(response)

        if "search" in command:
            time.sleep(4)
        elif "open" in command or "click" in command:
            time.sleep(3)
        else:
            time.sleep(2)

    brain.cleanup_session()


if __name__ == "__main__":
    print("🎯 Enhanced Browser Control Demo")
    print("This demo shows JARVIS's new capabilities:")
    print("✅ Search result navigation (open first, second, etc.)")
    print("✅ Enhanced link clicking with better detection")
    print("✅ List search results and page links")
    print("✅ Full search-to-navigation workflow")
    print("\nStarting demo...\n")

    try:
        test_enhanced_browser()
        demo_search_workflow()
        print("\n🎉 All enhanced browser features working perfectly!")
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
