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
        # Get startup reminders first to customize greeting
        reminders = self.ai_brain.get_startup_reminders()

        # Customize startup message based on tasks
        if reminders and not any("no pending tasks" in reminder.lower() for reminder in reminders):
            startup_message = "JARVIS AI assistant online. Let me update you on your tasks."
        else:
            startup_message = "JARVIS AI assistant online. How can I help you?"

        print(f"Jarvis: {startup_message}")
        self.audio.speak(startup_message)

        # Announce specific tasks
        if reminders:
            print("\n[Startup Reminders]")
            for reminder in reminders:
                print(f"  {reminder}")

            # Create a comprehensive spoken announcement
            if len(reminders) > 0:
                # Build a natural spoken message
                spoken_message = ""
                task_lines = [r for r in reminders if r.startswith("•")]

                if task_lines:
                    # Extract the main announcement
                    main_announcement = next(
                        (r for r in reminders if not r.startswith("•") and not r.startswith("...")), "")
                    if main_announcement:
                        spoken_message = main_announcement + " "

                    # Add the specific tasks in a natural way
                    # Limit to 3 tasks to avoid long speech
                    for i, task_line in enumerate(task_lines[:3]):
                        task_text = task_line.replace("• ", "").replace(
                            "(high priority)", "which is high priority")
                        if i == 0:
                            spoken_message += task_text
                        elif i == len(task_lines) - 1 and len(task_lines) > 1:
                            spoken_message += f", and {task_text}"
                        else:
                            spoken_message += f", {task_text}"

                    # Add count info if more tasks exist
                    if len(task_lines) > 3:
                        spoken_message += f", plus {len(task_lines) - 3} more tasks"
                else:
                    # No specific tasks, just use the first reminder
                    spoken_message = reminders[0]

                print(f"Jarvis: {spoken_message}")
                self.audio.speak(spoken_message)

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

            # Use AI for response directly (skip NLU parsing for speed)
            # Only handle critical intents for performance
            text_lower = text.lower()
            if "what time" in text_lower or "current time" in text_lower:
                now = datetime.now().strftime("%I:%M %p").lstrip("0")
                reply = f"It's {now}."
            elif "what date" in text_lower or "today's date" in text_lower:
                today = datetime.now().strftime("%A, %B %d, %Y")
                reply = f"Today is {today}."
            else:
                # Use AI brain for all other responses (faster than NLU parsing)
                reply = self.ai_brain.generate_response(text)

            print(f"Jarvis: {reply}")
            if reply:
                self.audio.speak(reply, chime=True)

        self.audio.close()
