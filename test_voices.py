#!/usr/bin/env python3
"""
Voice testing script for J.A.R.V.I.S
Allows you to test different voices and settings before configuring them
"""

import comtypes.client as cc
from jarvis.audio import TTS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def list_available_voices():
    """List all available SAPI voices"""
    print("Available Windows SAPI voices:")
    print("-" * 50)

    try:
        sapi_voice = cc.CreateObject("SAPI.SpVoice")
        voices = sapi_voice.GetVoices()

        for i in range(voices.Count):
            voice_token = voices.Item(i)
            voice_name = voice_token.GetDescription()
            print(f"{i}: {voice_name}")

        return voices
    except Exception as e:
        print(f"Error listing voices: {e}")
        return None


def test_voice(voice_name=None, rate=170, volume=0.85):
    """Test a specific voice with given settings"""
    test_phrases = [
        "Hello, I am J.A.R.V.I.S., your personal assistant.",
        "How can I help you today?",
        "The current time is 3:30 PM.",
        "I'm here to assist you with various tasks."
    ]

    print(f"\nTesting voice: {voice_name or 'Default'}")
    print(f"Rate: {rate}, Volume: {volume}")
    print("-" * 40)

    tts = TTS(voice=voice_name, rate=rate, volume=volume)

    for i, phrase in enumerate(test_phrases, 1):
        print(f"Speaking phrase {i}: {phrase}")
        tts.say(phrase)
        input("Press Enter for next phrase...")


def interactive_voice_selection():
    """Interactive voice selection and testing"""
    voices = list_available_voices()
    if not voices:
        return

    print("\nVoice Recommendations:")
    print("• Microsoft Zira Desktop - Female, generally more natural")
    print("• Microsoft David Desktop - Male, clear but more robotic")

    while True:
        print("\nOptions:")
        print("1. Test Zira (female, recommended)")
        print("2. Test David (male)")
        print("3. Test custom voice name")
        print("4. Adjust speech rate")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            test_voice("Zira", 170, 0.85)
        elif choice == "2":
            test_voice("David", 170, 0.85)
        elif choice == "3":
            voice_name = input("Enter voice name (or part of name): ").strip()
            test_voice(voice_name, 170, 0.85)
        elif choice == "4":
            try:
                rate = int(
                    input("Enter speech rate (150-210, default 170): ").strip())
                voice_name = input(
                    "Voice name (Zira/David or press Enter for Zira): ").strip()
                if not voice_name:
                    voice_name = "Zira"
                test_voice(voice_name, rate, 0.85)
            except ValueError:
                print("Invalid rate entered!")
        elif choice == "5":
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    print("J.A.R.V.I.S Voice Testing Tool")
    print("=" * 40)
    interactive_voice_selection()
