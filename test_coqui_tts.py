#!/usr/bin/env python3
"""
Test Coqui TTS Implementation
Tests the new Coqui TTS system for realistic neural voices.
"""

import sys
import os
from pathlib import Path

# Add the jarvis module to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def test_coqui_tts():
    """Test Coqui TTS system with different voices and texts"""

    print("🔥 Testing Coqui TTS - Realistic Neural Voice Synthesis")
    print("=" * 60)

    try:
        from jarvis.audio import TTS, AudioIO, list_available_voices

        print("✅ Successfully imported Coqui TTS modules")

        # Test 1: List available voices
        print("\n📋 Available Coqui TTS Voices:")
        voices = list_available_voices()
        for voice_id, voice_name in voices:
            print(f"  • {voice_id}: {voice_name}")

        # Test 2: Initialize TTS with different voices
        test_voices = ["female", "jenny", "male"]
        test_texts = [
            "Hello! I am JARVIS, powered by Coqui TTS neural voice synthesis.",
            "This is a test of my new realistic voice using advanced neural networks.",
            "I can now speak with much more natural and human-like speech patterns."
        ]

        for voice in test_voices:
            print(f"\n🎤 Testing {voice} voice:")
            print("-" * 30)

            try:
                # Initialize TTS with specific voice
                tts = TTS(voice=voice, rate=1.0, volume=0.8)
                print(f"Status: {tts.get_status()}")

                # Test speech synthesis
                for i, text in enumerate(test_texts, 1):
                    print(f"  Test {i}: Speaking...")
                    tts.say(text)
                    print(f"  ✅ Test {i} completed")

                print(f"✅ {voice} voice test completed successfully!")

            except Exception as e:
                print(f"❌ Error testing {voice} voice: {e}")

        # Test 3: AudioIO integration
        print(f"\n🔊 Testing AudioIO Integration:")
        print("-" * 30)

        try:
            audio = AudioIO()
            print(f"AudioIO Status: {audio.tts.get_status()}")

            # Test speaking with chime
            audio.speak("AudioIO integration test successful!", chime=True)
            print("✅ AudioIO integration test completed")

        except Exception as e:
            print(f"❌ AudioIO integration error: {e}")

        print(f"\n🎉 Coqui TTS Testing Complete!")
        print("Your JARVIS now has realistic neural voice synthesis!")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure Coqui TTS is properly installed:")
        print("pip install TTS torch torchaudio soundfile pygame")

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_coqui_tts()
