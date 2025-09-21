#!/usr/bin/env python3
"""Test JARVIS application launching via text input simulation"""

from jarvis.ai_brain import AIBrain
from jarvis.audio import AudioIO


def test_jarvis_app_commands():
    """Test JARVIS application launching commands"""
    print("Testing JARVIS Application Commands")
    print("=" * 40)

    # Initialize JARVIS AI Brain
    audio = AudioIO()
    jarvis = AIBrain(audio_io=audio)

    # Test commands
    test_commands = [
        "open calculator",
        "launch notepad",
        "start chrome",
        "run valorant",
        "open val",
        "launch 3ds max",
        "start autodesk",
        "open everything",
        "run docker",
        "launch chrome"
    ]

    print(f"\nTesting {len(test_commands)} application commands:\n")

    for i, command in enumerate(test_commands, 1):
        print(f"{i:2d}. Command: '{command}'")
        try:
            response = jarvis.generate_response(command)
            print(f"    Response: {response}")
        except Exception as e:
            print(f"    Error: {e}")
        print()


if __name__ == "__main__":
    test_jarvis_app_commands()
