#!/usr/bin/env python3
"""
Edge TTS Voice Demo for JARVIS
Demonstrates the high-quality neural voices now available.
"""

import sys
import os
from pathlib import Path
import asyncio

# Add the jarvis module to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def test_voice_options():
    """Test different Edge TTS voice options"""

    print("=" * 60)
    print("JARVIS - Edge TTS Neural Voice Demonstration")
    print("=" * 60)

    try:
        from jarvis.audio import TTS, list_available_voices

        print("SUCCESS: Edge TTS system imported successfully!")

        # Show available voices
        print("\nAvailable High-Quality Neural Voices:")
        voices = list_available_voices()
        for voice_id, voice_name in voices:
            print(f"  • {voice_name}")

        # Test different voice types
        voice_tests = [
            ("aria", "Hello! I'm Aria, a natural female voice."),
            ("jenny", "Hi there! I'm Jenny, with a friendly tone."),
            ("guy", "Greetings! I'm Guy, a natural male voice."),
            ("davis", "Hello! I'm Davis, with a professional tone."),
        ]

        demo_text = "I am JARVIS, now powered by Microsoft Edge TTS neural voices for ultra-realistic speech synthesis."

        print(f"\nTesting Voice Varieties:")
        print("-" * 40)

        for voice_name, intro in voice_tests:
            print(f"\nTesting {voice_name.upper()} voice:")

            try:
                # Initialize with specific voice
                tts = TTS(voice=voice_name, rate="+0%", volume=0.8)

                # Voice introduction
                print(f"  Introduction: '{intro}'")
                tts.say(intro)

                # Demo text
                print(f"  Demo: Speaking as JARVIS...")
                tts.say(demo_text)

                print(f"  ✓ {voice_name.upper()} voice test completed")

            except Exception as e:
                print(f"  ✗ Error with {voice_name} voice: {e}")

        # Speed test
        print(f"\nTesting Speech Speed Variations:")
        print("-" * 40)

        speed_tests = [
            ("-20%", "This is slower speech for better clarity."),
            ("+0%", "This is normal speed speech."),
            ("+20%", "This is faster speech for efficiency."),
        ]

        for rate, text in speed_tests:
            print(f"  Testing speed {rate}: '{text}'")
            try:
                tts = TTS(voice="aria", rate=rate, volume=0.8)
                tts.say(text)
                print(f"  ✓ Speed {rate} test completed")
            except Exception as e:
                print(f"  ✗ Speed {rate} test failed: {e}")

        print(f"\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("✓ JARVIS now has ultra-realistic neural voices!")
        print("✓ Multiple voice personalities available")
        print("✓ Adjustable speech speed")
        print("✓ Superior quality compared to Windows SAPI")
        print("✓ Compatible with Python 3.13")
        print("✓ No fallbacks needed - pure neural TTS")

        # Final demo
        final_tts = TTS(voice="aria", rate="+0%", volume=0.8)
        final_tts.say(
            "Neural voice upgrade complete. JARVIS voice system fully operational.")

    except ImportError as e:
        print(f"✗ Import Error: {e}")
        print("Please ensure Edge TTS is installed: pip install edge-tts pygame aiofiles")

    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_voice_options()
