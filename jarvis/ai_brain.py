"""
JARVIS AI Brain - Intelligent Response Generation
Uses free AI APIs to generate contextual responses to user input.
"""

from __future__ import annotations

import os
import json
import time
import uuid
from typing import Optional, Dict, List
from datetime import datetime

# AI API clients
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Memory system import
try:
    from .memory import JarvisMemory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False


class AIBrain:
    """AI Brain for JARVIS - Generates intelligent responses using free AI APIs"""

    def __init__(self, audio_io=None):
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        # AI configuration
        self.ai_provider = os.getenv("JARVIS_AI_PROVIDER", "groq")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.ai_model = os.getenv("JARVIS_AI_MODEL", "llama-3.1-8b-instant")
        self.personality = os.getenv("JARVIS_PERSONALITY", "helpful_assistant")

        # Audio reference for voice commands
        self.audio_io = audio_io

        # Session management
        self.session_id = str(uuid.uuid4())

        # Memory system
        if MEMORY_AVAILABLE:
            self.memory = JarvisMemory()
            print("[AI] Memory system initialized")
        else:
            self.memory = None
            print("[AI] Memory system not available")

        # Conversation history (in-memory backup)
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = int(os.getenv("JARVIS_MAX_HISTORY", "10"))

        # Initialize AI client
        self.client = None
        self._init_ai_client()

        # JARVIS personality prompts
        self.personalities = {
            "helpful_assistant": "You are JARVIS, a helpful AI assistant. Be concise, friendly, and informative. Keep responses under 2 sentences unless asked for details.",
            "tony_stark_jarvis": "You are JARVIS, Tony Stark's AI assistant. Be sophisticated, slightly witty, and efficient. Address the user as 'Sir' or 'Ma'am' occasionally. Keep responses brief but elegant.",
            "professional": "You are JARVIS, a professional AI assistant. Be formal, precise, and business-like. Provide clear, actionable responses.",
            "casual_friend": "You are JARVIS, a casual and friendly AI companion. Be conversational, warm, and approachable. Use natural language and be helpful.",
            "technical_expert": "You are JARVIS, a technical AI assistant specializing in programming and technology. Be precise, use technical language when appropriate, and provide detailed technical explanations."
        }

        print(
            f"[AI] AI Brain initialized - Provider: {self.ai_provider}, Model: {self.ai_model}")

    def _init_ai_client(self) -> None:
        """Initialize the AI client based on provider"""
        if self.ai_provider == "groq" and GROQ_AVAILABLE:
            if not self.groq_api_key:
                print(
                    "[AI] Warning: GROQ_API_KEY not set. Please get a free API key from https://console.groq.com/")
                print("[AI] Falling back to offline responses")
                return

            try:
                self.client = Groq(api_key=self.groq_api_key)
                print("[AI] Groq AI client initialized successfully")
            except Exception as e:
                print(f"[AI] Groq initialization failed: {e}")

        elif self.ai_provider == "local":
            print("[AI] Using local/offline AI responses")

        else:
            print(f"[AI] Unknown AI provider: {self.ai_provider}")

    def get_system_prompt(self) -> str:
        """Get the system prompt based on current personality"""
        base_prompt = self.personalities.get(
            self.personality, self.personalities["helpful_assistant"])

        # Add current context
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%B %d, %Y")

        context_prompt = f"""
{base_prompt}

Current context:
- Time: {current_time}
- Date: {current_date}
- You are running on a Windows system
- You have voice synthesis capabilities
- Keep responses conversational and concise (1-2 sentences typically)
- If asked about your capabilities, mention you can help with questions, provide information, and assist with various tasks
"""
        return context_prompt.strip()

    def generate_response(self, user_input: str) -> str:
        """Generate an AI response to user input"""
        if not user_input or not user_input.strip():
            return "I didn't catch that. Could you please repeat?"

        user_input = user_input.strip()
        print(f"[AI] Processing: '{user_input}'")

        try:
            # Check for task-related commands first
            task_response = self._handle_task_commands(user_input)
            if task_response:
                return task_response

            # Check for memory/reminder commands
            memory_response = self._handle_memory_commands(user_input)
            if memory_response:
                return memory_response

            # Try Groq API for general conversation
            if self.client and self.ai_provider == "groq":
                response = self._groq_response(user_input)
                if response:
                    # Save conversation to memory
                    if self.memory:
                        self.memory.save_conversation(
                            user_input, response, self.session_id)
                    self._add_to_history(user_input, response)
                    return response

            # Fallback to pattern-based responses
            response = self._fallback_response(user_input)
            self._add_to_history(user_input, response)
            return response

        except Exception as e:
            print(f"[AI] Error generating response: {e}")
            return self._fallback_response(user_input)

    def _groq_response(self, user_input: str) -> Optional[str]:
        """Generate response using Groq API"""
        try:
            # Prepare conversation messages
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]

            # Add conversation history
            for entry in self.conversation_history[-5:]:  # Last 5 exchanges
                messages.append({"role": "user", "content": entry["user"]})
                messages.append(
                    {"role": "assistant", "content": entry["assistant"]})

            # Add current user input
            messages.append({"role": "user", "content": user_input})

            # Make API call
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.ai_model,
                max_tokens=150,  # Keep responses concise
                temperature=0.7,
                top_p=1,
                stop=None,
            )

            response = chat_completion.choices[0].message.content.strip()
            print(f"[AI] Groq response generated: '{response[:50]}...'")
            return response

        except Exception as e:
            print(f"[AI] Groq API error: {e}")
            return None

    def _fallback_response(self, user_input: str) -> str:
        """Generate fallback response when AI API is unavailable"""
        user_lower = user_input.lower()

        # Greeting responses
        if any(word in user_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return "Hello! How can I assist you today?"

        # Time/date queries
        if "time" in user_lower:
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}."

        if "date" in user_lower or "today" in user_lower:
            current_date = datetime.now().strftime("%B %d, %Y")
            return f"Today is {current_date}."

        # Identity questions
        if any(phrase in user_lower for phrase in ["who are you", "what are you", "your name"]):
            return "I'm JARVIS, your AI assistant. I'm here to help you with questions and tasks."

        # Capability questions
        if any(phrase in user_lower for phrase in ["what can you do", "help me", "capabilities"]):
            return "I can answer questions, provide information, help with tasks, and have conversations with you. What would you like to know?"

        # Weather (placeholder)
        if "weather" in user_lower:
            return "I don't have access to current weather data, but I can help you with other questions."

        # Thank you responses
        if any(word in user_lower for word in ["thank you", "thanks", "thank"]):
            return "You're welcome! Is there anything else I can help you with?"

        # Goodbye responses
        if any(word in user_lower for word in ["goodbye", "bye", "see you", "exit", "quit"]):
            return "Goodbye! Have a great day!"

        # Default intelligent response
        responses = [
            "That's interesting. Could you tell me more about what you'd like to know?",
            "I understand. How can I help you with that?",
            "I see. What specific information are you looking for?",
            "Let me help you with that. Could you provide more details?",
            "That's a good question. What would you like to know specifically?",
        ]

        # Simple hash-based selection for consistency
        response_index = hash(user_input) % len(responses)
        return responses[response_index]

    def _add_to_history(self, user_input: str, response: str) -> None:
        """Add conversation to history"""
        self.conversation_history.append({
            "user": user_input,
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })

        # Trim history if too long
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history.clear()
        print("[AI] Conversation history cleared")

    def get_status(self) -> str:
        """Get AI brain status"""
        status = f"AI Provider: {self.ai_provider}"
        if self.client:
            status += f", Model: {self.ai_model}, Connected: Yes"
        else:
            status += ", Connected: No (Using fallbacks)"
        status += f", Personality: {self.personality}"
        return status

    def set_personality(self, personality: str) -> bool:
        """Change JARVIS personality"""
        if personality in self.personalities:
            self.personality = personality
            print(f"[AI] Personality changed to: {personality}")
            return True
        else:
            print(f"[AI] Unknown personality: {personality}")
            print(
                f"[AI] Available personalities: {list(self.personalities.keys())}")
            return False

    def _clean_task_text(self, user_input: str, remove_time_words: bool = True) -> str:
        """Clean up task text by removing command phrases and time words"""
        task_text = user_input.lower()

        # Remove command phrases
        phrases_to_remove = [
            "remind me to", "remind me", "add task", "task for",
            "remember to", "i need to", "don't forget to", "don't forget",
            "make a note to", "make a note", "add reminder", "create task"
        ]

        for phrase in phrases_to_remove:
            task_text = task_text.replace(phrase, "")

        # Remove time words if requested
        if remove_time_words:
            time_words = ["tomorrow", "next week", "today", "later"]
            for word in time_words:
                task_text = task_text.replace(word, "")

        # Clean up and capitalize
        task_text = task_text.strip()
        if task_text.startswith("that "):
            task_text = task_text[5:]  # Remove "that " prefix

        return task_text.capitalize() if task_text else "Reminder"

    def _handle_task_commands(self, user_input: str) -> Optional[str]:
        """Handle task-related commands"""
        if not self.memory:
            return None

        user_lower = user_input.lower()

        # Add task/reminder - enhanced with more natural phrases
        if any(phrase in user_lower for phrase in [
            "remind me", "add task", "task for", "remember to", "i need to",
            "don't forget", "make a note", "add reminder", "create task"
        ]):
            # Extract task details
            task_text = user_input

            # Check for time-based reminders
            if "tomorrow" in user_lower:
                from datetime import datetime, timedelta
                due_date = (datetime.now() + timedelta(days=1)
                            ).strftime('%Y-%m-%d')

                # Clean up the task text
                task_text = self._clean_task_text(
                    user_input, remove_time_words=True)

                if self.memory.add_task(task_text, due_date=due_date, priority="medium"):
                    return f"I'll remind you tomorrow: {task_text}"
                else:
                    return "I had trouble saving that reminder. Please try again."

            elif "next week" in user_lower:
                from datetime import datetime, timedelta
                due_date = (datetime.now() + timedelta(days=7)
                            ).strftime('%Y-%m-%d')

                # Clean up the task text
                task_text = self._clean_task_text(
                    user_input, remove_time_words=True)

                if self.memory.add_task(task_text, due_date=due_date, priority="medium"):
                    return f"I'll remind you next week: {task_text}"
                else:
                    return "I had trouble saving that reminder. Please try again."

            else:
                # General task without specific date
                if any(phrase in user_lower for phrase in ["remind me", "add task", "remember to", "i need to", "don't forget", "make a note", "add reminder", "create task"]):
                    # Clean up the task text
                    task_text = self._clean_task_text(
                        user_input, remove_time_words=False)

                    if self.memory.add_task(task_text, priority="medium"):
                        return f"I've noted that down: {task_text}"
                    else:
                        return "I had trouble saving that task. Please try again."

        # Handle "remember" differently - for preferences, not tasks
        if "remember that" in user_lower or "remember this" in user_lower:
            # This is for storing preferences/context, not tasks
            return None  # Let it be handled by regular AI response

        # Show tasks/reminders
        if any(phrase in user_lower for phrase in ["my tasks", "my reminders", "what do i need to do", "show tasks", "current tasks"]):
            tasks = self.memory.get_pending_tasks()
            if not tasks:
                return "You don't have any pending tasks at the moment."

            task_list = []
            for i, task in enumerate(tasks[:5], 1):  # Show up to 5 tasks
                due_info = f" (due {task['due_date']})" if task['due_date'] else ""
                priority_info = f" [{task['priority']}]" if task['priority'] != 'medium' else ""
                task_list.append(
                    f"{i}. {task['title']}{due_info}{priority_info}")

            tasks_text = "\n".join(task_list)
            return f"Here are your pending tasks:\n{tasks_text}"

        # Complete task
        if any(phrase in user_lower for phrase in ["done with", "completed", "finished", "mark complete"]):
            # For now, just acknowledge - could be enhanced to identify specific tasks
            return "Great! If you tell me which specific task number, I can mark it as completed."

        return None

    def _handle_memory_commands(self, user_input: str) -> Optional[str]:
        """Handle memory-related commands"""
        if not self.memory:
            return None

        user_lower = user_input.lower()

        # Store preferences/context
        if "remember that" in user_lower or "remember this" in user_lower:
            # Extract the preference
            preference = user_input.lower()
            preference = preference.replace(
                "remember that", "").replace("remember this", "").strip()

            # Store as context
            if preference:
                # Create a key from the preference
                key = f"preference_{len(preference.split())}"
                self.memory.store_context(key, preference, "preferences")
                return f"I'll remember that: {preference}"
            else:
                return "What would you like me to remember?"

        # Memory statistics
        if any(phrase in user_lower for phrase in ["memory stats", "what do you remember", "memory status"]):
            stats = self.memory.get_memory_stats()
            return f"Memory Status:\n- Conversations: {stats.get('conversations', 0)}\n- Tasks: {stats.get('pending_tasks', 0)}\n- Context entries: {stats.get('context_entries', 0)}"

        return None

    def get_startup_reminders(self) -> List[str]:
        """Get reminders to show when JARVIS starts up"""
        if not self.memory:
            return []

        reminders = []

        # Get due tasks/reminders
        due_tasks = self.memory.get_due_reminders()
        if due_tasks:
            reminders.append(
                f"You have {len(due_tasks)} tasks that need attention:")
            for task in due_tasks[:3]:  # Show up to 3 most important
                due_info = f" (due {task['due_date']})" if task['due_date'] else ""
                reminders.append(f"• {task['title']}{due_info}")

        # Get memory stats
        stats = self.memory.get_memory_stats()
        if stats.get('pending_tasks', 0) > 0:
            reminders.append(
                f"📝 You have {stats['pending_tasks']} pending tasks")

        return reminders


# Convenience function for easy import
def create_ai_brain() -> AIBrain:
    """Create and return an AIBrain instance"""
    return AIBrain()


if __name__ == "__main__":
    # Test the AI brain
    print("Testing JARVIS AI Brain...")
    brain = AIBrain()

    test_inputs = [
        "Hello JARVIS",
        "What's the time?",
        "Who are you?",
        "What can you do?",
        "Tell me about artificial intelligence",
        "Thank you"
    ]

    for test_input in test_inputs:
        print(f"\nUser: {test_input}")
        response = brain.generate_response(test_input)
        print(f"JARVIS: {response}")
