from __future__ import annotations

from datetime import datetime
from typing import Optional

from .audio import AudioIO, list_available_voices
from .nlu import NLU, Intent
from .ai_brain import AIBrain


class Assistant:
    """AI-powered JARVIS assistant with intelligent conversation capabilities."""

    def __init__(self):
        self.audio = AudioIO()
        self.nlu = NLU()
        # Pass audio reference for voice switching
        self.ai_brain = AIBrain(audio_io=self.audio)

        print(f"[JARVIS] {self.ai_brain.get_status()}")

    def handle_intent(self, intent: Intent) -> Optional[str]:
        """Handle user intents - now with AI-powered responses for most cases"""
        name = intent.name

        # Handle specific system commands
        if name == "exit":
            return "Goodbye!"

        if name == "time":
            now = datetime.now().strftime("%I:%M %p").lstrip("0")
            return f"It's {now}."

        if name == "date":
            today = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today}."

        if name == "list_voices":
            voices = list_available_voices()
            if not voices:
                print("(No voices found)")
                return "I couldn't find any installed voices."
            # Print detailed list to terminal
            print("Available voices:")
            for i, (vid, vname) in enumerate(voices):
                print(f"  {i}. {vname} => {vid}")
            # Speak a short summary
            top = ", ".join(vname for _, vname in voices[:3] if vname)
            if top:
                return f"I found {len(voices)} voices, like {top}."
            return f"I found {len(voices)} voices."

        # For echo and general conversation, use AI brain
        if name == "echo" or name == "general":
            return self.ai_brain.generate_response(intent.text)

        # Default: Use AI brain for intelligent responses
        return self.ai_brain.generate_response(intent.text)

    def run(self) -> None:
        """Main conversation loop with AI-powered responses and memory integration"""
        startup_message = "JARVIS AI assistant online. How can I help you?"
        print(f"Jarvis: {startup_message}")
        self.audio.speak(startup_message)

        # Show startup reminders
        reminders = self.ai_brain.get_startup_reminders()
        if reminders:
            print("\n[Startup Reminders]")
            for reminder in reminders:
                print(f"  {reminder}")

            # Speak the most important reminder
            if len(reminders) > 0:
                reminder_message = reminders[0]
                if len(reminders) > 1:
                    reminder_message += f" Plus {len(reminders) - 1} other items."
                print(f"Jarvis: {reminder_message}")
                self.audio.speak(reminder_message)

        while True:
            print("[Listening...]")
            text = self.audio.stt.listen_once()
            if not text:
                continue

            print(f"You: {text}")

            # Check for exit commands first
            if any(exit_word in text.lower() for exit_word in ["goodbye", "exit", "quit", "bye"]):
                reply = "Goodbye! Have a great day!"
                print(f"Jarvis: {reply}")
                self.audio.speak(reply, chime=True)

                # Cleanup session
                self.ai_brain.cleanup_session()
                break

            # Parse intent and generate AI response
            intent = self.nlu.parse(text)
            if not intent:
                # If NLU fails, still use AI for response
                reply = self.ai_brain.generate_response(text)
            else:
                reply = self.handle_intent(
                    intent) or "I'm not sure how to respond to that."

            print(f"Jarvis: {reply}")
            if reply:
                self.audio.speak(reply, chime=True)

        self.audio.close()
