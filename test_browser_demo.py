"""
Voice-Controlled Browser Demo for JARVIS
Demonstrates all browser voice commands available
"""

import time
from jarvis.ai_brain import AIBrain
from jarvis.audio import AudioIO


def test_browser_commands():
    """Test various browser voice commands"""
    print("=== JARVIS Voice-Controlled Browser Demo ===\n")

    # Initialize JARVIS
    brain = AIBrain()
    audio = AudioIO()

    # List of browser commands to test
    commands = [
        "open browser",
        "search for Python programming",
        "go to github.com",
        "bookmark this page",
        "open new tab",
        "search for machine learning",
        "go back",
        "refresh page",
        "scroll down",
        "what is the page title",
        "what is the current url"
    ]

    print("Available voice commands for browser control:")
    for i, cmd in enumerate(commands, 1):
        print(f"{i:2d}. {cmd}")

    print("\n" + "="*50)
    print("Testing browser commands...")
    print("="*50 + "\n")

    for i, command in enumerate(commands, 1):
        print(f"\n[{i:2d}] Testing: '{command}'")
        print("-" * 40)

        # Process command through JARVIS
        response = brain.generate_response(command)
        print(f"JARVIS Response: {response}")

        # Speak the response
        audio.speak(response)

        # Wait a bit between commands
        time.sleep(2)

        if i == 3:  # After visiting github.com
            print("\n[INFO] Browser should now be at GitHub")
            time.sleep(3)

    print("\n" + "="*50)
    print("Browser demo completed!")
    print("="*50)

    # Show browser status
    if brain.browser:
        status = brain.browser.get_status()
        print(f"\nBrowser Status:")
        print(f"- Active: {status['is_active']}")
        print(f"- Current URL: {status['current_url']}")
        print(f"- Page Title: {status['title']}")

    # Cleanup
    print("\nCleaning up...")
    brain.cleanup_session()


if __name__ == "__main__":
    test_browser_commands()
