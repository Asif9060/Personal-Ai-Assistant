"""
JARVIS AI Brain - Intelligent Response Generation
Uses free AI APIs to generate contextual responses to user input.
"""

from __future__ import annotations

import os
import json
import time
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


class AIBrain:
    """AI Brain for JARVIS - Generates intelligent responses using free AI APIs"""

    def __init__(self):
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

        # Conversation history
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
            # Try Groq API first
            if self.client and self.ai_provider == "groq":
                response = self._groq_response(user_input)
                if response:
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
