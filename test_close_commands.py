#!/usr/bin/env python3
"""Test JARVIS close application commands"""

from jarvis.ai_brain import AIBrain
from jarvis.audio import AudioIO


def test_jarvis_close_commands():
    """Test JARVIS application close commands"""
    print("Testing JARVIS Close Application Commands")
    print("=" * 45)

    # Initialize JARVIS AI Brain
    audio = AudioIO()
    jarvis = AIBrain(audio_io=audio)

    # Test commands - First open some apps, then close them
    test_commands = [
        # Open some applications first
        "open notepad",
        "launch calculator",
        "start chrome",

        # Now test closing them
        "close notepad",
        "kill calculator",
        "stop chrome",
        "close chrome",
        "quit notepad",
        "end valorant",
        "close discord",
        "stop steam"
    ]

    print(f"\nTesting {len(test_commands)} commands (open and close):\n")

    for i, command in enumerate(test_commands, 1):
        print(f"{i:2d}. Command: '{command}'")
        try:
            response = jarvis.generate_response(command)
            print(f"    Response: {response}")
        except Exception as e:
            print(f"    Error: {e}")
        print()

        # Add a small delay between commands
        import time
        time.sleep(1)


if __name__ == "__main__":
    test_jarvis_close_commands()
