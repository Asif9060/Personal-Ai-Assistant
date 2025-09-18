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

import pyttsx3
import speech_recognition as sr

# Coqui TTS imports
try:
    from TTS.api import TTS as CoquiTTS
    import torch
    import soundfile as sf
    import simpleaudio as sa
    COQUI_AVAILABLE = True
except ImportError as e:
    print(f"[TTS] Coqui TTS not available: {e}")
    COQUI_AVAILABLE = False


class TTS:
    def __init__(self, voice: Optional[str] = None, rate: int = 190, volume: float = 1.0):
        self._voice_pref = voice
        self._rate = rate
        self._volume = volume
        self.engine = None
        self.coqui_tts = None
        self.temp_dir = Path(tempfile.gettempdir()) / "jarvis_tts"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Try Coqui TTS first for best quality
        if COQUI_AVAILABLE:
            self._init_coqui_tts()
        
        # Fallback to Windows SAPI if Coqui fails
        if not hasattr(self, 'coqui_tts') or self.coqui_tts is None:
            if platform.system() == "Windows":
                self._init_sapi()
            if not hasattr(self, '_sapi_voice'):
                self._init_pyttsx3()

    def _init_coqui_tts(self) -> None:
        """Initialize Coqui TTS with high-quality neural voices."""
        try:
            # Use a high-quality multilingual model
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            
            print("[TTS] Initializing Coqui TTS (this may take a moment for first run)...")
            
            # Check if CUDA is available for faster inference
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Initialize Coqui TTS
            self.coqui_tts = CoquiTTS(
                model_name=model_name,
                gpu=torch.cuda.is_available()
            )
            
            # Set default speaker (can be customized)
            self.speaker = self._voice_pref or "Claribel Dervla"  # Default to a natural female voice
            
            print(f"[TTS] Coqui TTS initialized successfully on {device}")
            print(f"[TTS] Using speaker: {self.speaker}")
            
        except Exception as e:
            print(f"[TTS] Coqui TTS init failed: {e}")
            self.coqui_tts = None
    
    def _init_sapi(self) -> None:
        """Initialize Windows SAPI directly for better reliability."""
        try:
            import comtypes.client as cc  # type: ignore
            self._sapi_voice = cc.CreateObject("SAPI.SpVoice")

            # Configure voice
            if self._voice_pref:
                try:
                    voices = self._sapi_voice.GetVoices()
                    for i in range(voices.Count):
                        voice_token = voices.Item(i)
                        voice_name = voice_token.GetDescription()
                        if self._voice_pref.lower() in voice_name.lower():
                            self._sapi_voice.Voice = voice_token
                            break
                except Exception:
                    pass

            # Configure rate (-10 to 10)
            sapi_rate = max(-10, min(10, int((self._rate - 200) / 20)))
            self._sapi_voice.Rate = sapi_rate

            # Configure volume (0 to 100)
            sapi_volume = max(0, min(100, int(self._volume * 100)))
            self._sapi_voice.Volume = sapi_volume

            print("[TTS] Windows SAPI initialized successfully")

        except Exception as e:
            print(f"[TTS] SAPI init failed: {e}")
            if hasattr(self, '_sapi_voice'):
                delattr(self, '_sapi_voice')

    def _init_pyttsx3(self) -> None:
        """Initialize pyttsx3 as fallback."""
        try:
            if platform.system() == "Windows":
                self.engine = pyttsx3.init("sapi5")
            else:
                self.engine = pyttsx3.init()

            if self.engine:
                # Configure voice
                voices = self.engine.getProperty("voices")
                if voices:
                    if self._voice_pref:
                        for v in voices:
                            if self._voice_pref.lower() in (v.name or "").lower():
                                self.engine.setProperty("voice", v.id)
                                break
                    else:
                        # Use first available voice
                        self.engine.setProperty("voice", voices[0].id)

                # Configure rate and volume
                self.engine.setProperty("rate", self._rate)
                self.engine.setProperty("volume", self._volume)

                print("[TTS] pyttsx3 initialized successfully")

        except Exception as e:
            print(f"[TTS] pyttsx3 init failed: {e}")
            self.engine = None

    def say(self, text: str, wait: bool = True) -> None:
        if not text:
            return

        print(f"[TTS] Attempting to speak: {text[:50]}...")

        # Try Coqui TTS first (highest quality)
        if self.coqui_tts is not None:
            try:
                self._speak_coqui(text)
                print("[TTS] Spoke via Coqui TTS")
                return
            except Exception as e:
                print(f"[TTS] Coqui TTS speak failed: {e}")

        # Fallback to Windows SAPI
        if hasattr(self, '_sapi_voice'):
            try:
                self._sapi_voice.Speak(text, 0)  # 0 = synchronous
                print("[TTS] Spoke via Windows SAPI")
                return
            except Exception as e:
                print(f"[TTS] SAPI speak failed: {e}")

        # Final fallback to pyttsx3
        if self.engine:
            try:
                # Clear any queued speech
                self.engine.stop()

                # Re-apply settings to ensure they're current
                self.engine.setProperty("rate", self._rate)
                self.engine.setProperty("volume", self._volume)

                self.engine.say(text)
                if wait:
                    self.engine.runAndWait()
                print("[TTS] Spoke via pyttsx3")
                return
            except Exception as e:
                print(f"[TTS] pyttsx3 speak failed: {e}")

        print("[TTS] All speech methods failed!")
    
    def _speak_coqui(self, text: str) -> None:
        """Generate and play speech using Coqui TTS."""
        # Generate audio file
        output_path = self.temp_dir / f"speech_{hash(text) % 1000000}.wav"
        
        # Use clone voice or default speaker
        if hasattr(self.coqui_tts, 'tts_to_file'):
            self.coqui_tts.tts_to_file(
                text=text,
                speaker=self.speaker,
                file_path=str(output_path)
            )
        else:
            # For models that don't support speaker selection
            self.coqui_tts.tts_to_file(
                text=text,
                file_path=str(output_path)
            )
        
        # Play the generated audio
        self._play_audio_file(str(output_path))
        
        # Clean up temporary file
        try:
            output_path.unlink()
        except Exception:
            pass
    
    def _play_audio_file(self, file_path: str) -> None:
        """Play an audio file using simpleaudio."""
        try:
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Wait until playback is finished
        except Exception as e:
            print(f"[TTS] Audio playback failed: {e}")
            # Fallback to system audio player
            try:
                import subprocess
                if platform.system() == "Windows":
                    subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()"], 
                                 check=True, capture_output=True)
                else:
                    subprocess.run(["aplay", file_path], check=True, capture_output=True)
            except Exception as e2:
                print(f"[TTS] System audio fallback also failed: {e2}")

    def stop(self) -> None:
        with contextlib.suppress(Exception):
            self.engine.stop()


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

        voice = os.getenv("JARVIS_VOICE") or None
        try:
            rate = int(os.getenv("JARVIS_TTS_RATE", "190"))
        except ValueError:
            rate = 190
        try:
            volume = float(os.getenv("JARVIS_TTS_VOLUME", "1.0"))
        except ValueError:
            volume = 1.0

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
    """Return a list of (id, name) for installed TTS voices."""
    voices: list[tuple[str, str]] = []
    try:
        eng = pyttsx3.init("sapi5" if platform.system() == "Windows" else None)
        for v in eng.getProperty("voices"):
            voices.append((getattr(v, "id", ""), getattr(v, "name", "")))
    except Exception:
        pass
    return voices
