from __future__ import annotations

import contextlib
import time
from typing import Optional
import platform
import contextlib as _ctx
import os
import tempfile
import threading
from pathlib import Path
import asyncio

import speech_recognition as sr

# Edge TTS - Modern Neural Voice System (compatible with Python 3.13)
try:
    import edge_tts
    import pygame
    import aiofiles
    EDGE_TTS_AVAILABLE = True
    print("[TTS] Edge TTS successfully imported - High-quality neural voices enabled!")
except ImportError as e:
    EDGE_TTS_AVAILABLE = False
    print(f"[TTS] Edge TTS not available: {e}")
    print("[TTS] Please install: pip install edge-tts pygame aiofiles")
    raise ImportError("Edge TTS is required but not available")


class TTS:
    """Edge TTS - High-Quality Neural Voice Synthesis

    This implementation uses Microsoft Edge's neural TTS for realistic voices.
    Compatible with Python 3.13 and provides excellent voice quality.
    """

    def __init__(self, voice: Optional[str] = None, rate: str = "+0%", volume: float = 0.8):
        if not EDGE_TTS_AVAILABLE:
            raise RuntimeError(
                "Edge TTS is not available. Please install the required packages.")

        # Edge TTS settings
        self._voice_pref = voice or os.getenv("JARVIS_VOICE", "female")
        # Edge TTS uses percentage like "+20%", "-10%"
        self._rate = os.getenv("JARVIS_TTS_SPEED", rate)
        self._volume = float(os.getenv("JARVIS_TTS_VOLUME", str(volume)))

        # Setup
        self.temp_dir = Path(tempfile.gettempdir()) / "jarvis_edge_tts"
        self.temp_dir.mkdir(exist_ok=True)

        # Initialize pygame for audio playback
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        print(f"[TTS] Initializing Edge TTS with neural voices...")
        print(
            f"[TTS] Voice: {self._voice_pref}, Rate: {self._rate}, Volume: {self._volume}")

        # Select voice based on preference
        self._select_voice()

        print(f"[TTS] Edge TTS initialized successfully!")
        print(f"[TTS] Using voice: {self.voice_name}")

    def _select_voice(self) -> None:
        """Select the best Edge TTS voice based on user preference"""
        # High-quality Edge TTS voices
        voices = {
            # Female voices - very natural
            "female": "en-US-AriaNeural",
            "woman": "en-US-AriaNeural",
            "aria": "en-US-AriaNeural",
            "jenny": "en-US-JennyNeural",
            "jane": "en-US-JaneNeural",
            "nancy": "en-US-NancyNeural",
            "sara": "en-US-SaraNeural",

            # Male voices - professional
            "male": "en-US-GuyNeural",
            "man": "en-US-GuyNeural",
            "guy": "en-US-GuyNeural",
            "davis": "en-US-DavisNeural",
            "jason": "en-US-JasonNeural",
            "tony": "en-US-TonyNeural",

            # Special voices
            "zira": "en-US-AriaNeural",  # Map old Zira to Aria
            "david": "en-US-GuyNeural",  # Map old David to Guy
        }

        # Select voice
        pref = self._voice_pref.lower()
        self.voice_name = voices.get(pref, voices["aria"])  # Default to Aria

        # Log selected voice
        voice_type = "Female" if "female" in pref or any(
            name in pref for name in ["aria", "jenny", "jane", "nancy", "sara"]) else "Male"
        print(f"[TTS] Selected {voice_type} voice: {self.voice_name}")

    def say(self, text: str, wait: bool = True) -> None:
        """Generate and play realistic speech using Edge TTS"""
        if not text or not text.strip():
            return

        text = text.strip()
        print(
            f"[TTS] Synthesizing: '{text[:50]}{'...' if len(text) > 50 else ''}'")

        try:
            # Run async TTS synthesis
            asyncio.run(self._async_synthesize_and_play(text))
            print(f"[TTS] Speech synthesis completed")

        except Exception as e:
            print(f"[TTS] Speech synthesis failed: {e}")
            raise

    async def _async_synthesize_and_play(self, text: str) -> None:
        """Async method to synthesize and play speech"""
        # Generate unique filename with timestamp to avoid conflicts
        import time
        text_hash = abs(hash(text)) % 1000000
        timestamp = int(time.time() * 1000) % 1000000
        output_file = self.temp_dir / f"speech_{text_hash}_{timestamp}.mp3"

        try:
            # Create TTS communication
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice_name,
                rate=self._rate
            )

            # Save audio to file
            await communicate.save(str(output_file))

            # Play the generated audio
            self._play_audio(str(output_file))

        except Exception as e:
            print(f"[TTS] Speech synthesis error: {e}")
            raise
        finally:
            # Clean up the temporary file with improved deletion
            self._cleanup_audio_file(output_file)

    def _cleanup_audio_file(self, file_path: Path) -> None:
        """Robustly clean up audio files with retry mechanism"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if file_path.exists():
                    # Ensure pygame has released the file
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()

                    # Wait a moment for file system to release
                    time.sleep(0.1 * (attempt + 1))  # Increasing delay

                    # Attempt to delete
                    file_path.unlink()
                    print(f"[TTS] Cleaned up audio file: {file_path.name}")
                    break
            except (PermissionError, OSError) as e:
                if attempt == max_retries - 1:
                    print(
                        f"[TTS] Warning: Could not delete {file_path.name} after {max_retries} attempts")
                    # Schedule for cleanup later
                    self._schedule_cleanup(file_path)
                else:
                    time.sleep(0.2)  # Wait before retry
            except Exception:
                break  # Don't fail the whole operation

    def _schedule_cleanup(self, file_path: Path) -> None:
        """Schedule file for cleanup later (for files that couldn't be deleted immediately)"""
        try:
            # Add to a cleanup list or use a background thread
            # For now, just try again after a longer delay
            import threading

            def delayed_cleanup():
                time.sleep(5)  # Wait 5 seconds
                try:
                    if file_path.exists():
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload()
                        file_path.unlink()
                        print(
                            f"[TTS] Delayed cleanup successful: {file_path.name}")
                except Exception:
                    pass  # Silent fail for delayed cleanup

            thread = threading.Thread(target=delayed_cleanup, daemon=True)
            thread.start()
        except Exception:
            pass  # Don't fail if threading doesn't work

    def _play_audio(self, file_path: str) -> None:
        """Play audio file using pygame with proper cleanup"""
        try:
            # Stop any current playback
            pygame.mixer.music.stop()

            # Load and play with pygame
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play()

            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)  # Fast polling for responsiveness

            # Ensure pygame releases the file by stopping and unloading
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()  # This releases the file handle

        except Exception as e:
            print(f"[TTS] Audio playback failed: {e}")
            # Fallback: try system audio player
            try:
                if platform.system() == "Windows":
                    os.system(
                        f'powershell -c "(New-Object Media.SoundPlayer \'{file_path}\').PlaySync()"')
                else:
                    os.system(f'aplay "{file_path}"')
            except Exception as e2:
                print(f"[TTS] Fallback audio playback also failed: {e2}")

    def stop(self) -> None:
        """Stop current speech playback"""
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def change_voice(self, new_voice: str) -> bool:
        """Change the voice dynamically"""
        try:
            old_voice = self.voice_name
            self._voice_pref = new_voice
            self._select_voice()

            if self.voice_name != old_voice:
                print(
                    f"[TTS] Voice changed from {old_voice} to {self.voice_name}")
                return True
            else:
                print(f"[TTS] Voice remains: {self.voice_name}")
                return False
        except Exception as e:
            print(f"[TTS] Failed to change voice: {e}")
            return False

    def list_available_voices(self) -> list:
        """List available Edge TTS voices"""
        return [
            "aria - Natural female voice (recommended)",
            "jenny - Friendly female voice",
            "jane - Professional female voice",
            "nancy - Warm female voice",
            "sara - Clear female voice",
            "guy - Natural male voice (recommended)",
            "davis - Professional male voice",
            "jason - Friendly male voice",
            "tony - Clear male voice"
        ]

    def get_status(self) -> str:
        """Get current TTS status"""
        return f"Edge TTS - Voice: {self.voice_name}, Rate: {self._rate}, Volume: {self._volume}"


class STT:
    def __init__(self, energy_threshold: int = 300, pause_threshold: float = 0.8):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold

    def listen_once(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = 8) -> Optional[str]:
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                return None
        try:
            # Try offline first if available
            try:
                import pocketsphinx  # type: ignore
                text = self.recognizer.recognize_sphinx(audio)
            except Exception:
                text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None


class AudioIO:
    def __init__(self):
        # Load .env if available for configuration
        try:
            from dotenv import load_dotenv  # type: ignore
            load_dotenv()
        except Exception:
            pass

        voice = os.getenv("JARVIS_VOICE") or "female"
        rate = os.getenv("JARVIS_TTS_SPEED") or "+0%"
        try:
            volume = float(os.getenv("JARVIS_TTS_VOLUME", "0.8"))
        except ValueError:
            volume = 0.8

        self.tts = TTS(voice=voice, rate=rate, volume=volume)
        self.stt = STT()

    def ask_and_listen(self, prompt: Optional[str] = None) -> Optional[str]:
        if prompt:
            self.tts.say(prompt)
            time.sleep(0.2)
        return self.stt.listen_once()

    def _chime(self) -> None:
        """Play a short chime/beep before speaking (Windows-friendly)."""
        # Allow disabling via env
        if os.getenv("JARVIS_CHIME", "1").strip() in {"0", "false", "False"}:
            return
        try:
            if platform.system() == "Windows":
                import winsound  # type: ignore
                # MessageBeep is lightweight and doesn't tie up the device for long
                if not winsound.MessageBeep(getattr(winsound, "MB_ICONASTERISK", 0x00000040)):
                    winsound.Beep(1000, 80)
            else:
                # Cross-platform basic bell; may not always be audible
                print("\a", end="")
        except Exception:
            pass

    def speak(self, text: str, chime: bool = False) -> None:
        if chime:
            self._chime()
            # tiny pause so chime doesn't overlap with TTS
            time.sleep(0.15)
        self.tts.say(text)

    def close(self) -> None:
        self.tts.stop()


def list_available_voices() -> list[tuple[str, str]]:
    """Return a list of Edge TTS voices available."""
    voices = [
        ("aria", "aria - Natural female voice (recommended)"),
        ("jenny", "jenny - Friendly female voice"),
        ("jane", "jane - Professional female voice"),
        ("nancy", "nancy - Warm female voice"),
        ("sara", "sara - Clear female voice"),
        ("guy", "guy - Natural male voice (recommended)"),
        ("davis", "davis - Professional male voice"),
        ("jason", "jason - Friendly male voice"),
        ("tony", "tony - Clear male voice")
    ]
    return voices
