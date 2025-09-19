#!/usr/bin/env python3
"""
JARVIS AI Setup Guide
How to get your free Groq API key for intelligent responses.
"""

print("🤖 JARVIS AI Brain Setup Guide")
print("=" * 50)
print()

print("✅ CURRENT STATUS:")
print("- ✅ Edge TTS neural voices working")
print("- ✅ AI brain module installed")
print("- ✅ Fallback responses working")
print("- ✅ Tony Stark JARVIS personality ready")
print()

print("🔑 TO GET FREE AI RESPONSES:")
print("1. Go to: https://console.groq.com/")
print("2. Click 'Sign Up' (free account)")
print("3. Verify your email")
print("4. Go to 'API Keys' section")
print("5. Click 'Create API Key'")
print("6. Copy your API key")
print()

print("📝 SETUP YOUR API KEY:")
print("1. Open the .env file in your JARVIS folder")
print("2. Find the line: GROQ_API_KEY=your_groq_api_key_here")
print("3. Replace 'your_groq_api_key_here' with your actual API key")
print("4. Save the file")
print()

print("🎭 PERSONALITY OPTIONS:")
personalities = {
    "tony_stark_jarvis": "Sophisticated, calls you 'Boss', like Tony Stark's JARVIS",
    "helpful_assistant": "Friendly and helpful general assistant",
    "professional": "Formal and business-like responses",
    "casual_friend": "Conversational and warm, like talking to a friend",
    "technical_expert": "Technical focus, great for programming questions"
}

for name, description in personalities.items():
    print(f"  • {name}: {description}")

print()
print("To change personality, edit JARVIS_PERSONALITY in your .env file")
print()

print("🚀 USAGE:")
print("1. Set up your API key (above)")
print("2. Run: python main.py")
print("3. Say anything to JARVIS")
print("4. Get intelligent AI responses!")
print()

print("💡 FREE LIMITS:")
print("- Groq provides generous free tier")
print("- Fast inference (usually under 1 second)")
print("- Multiple AI models available")
print("- No credit card required for signup")
print()

print("🔧 CURRENT SETTINGS:")
try:
    import os
    from dotenv import load_dotenv
    load_dotenv()

    voice = os.getenv("JARVIS_VOICE", "aria")
    personality = os.getenv("JARVIS_PERSONALITY", "tony_stark_jarvis")
    model = os.getenv("JARVIS_AI_MODEL", "llama-3.1-8b-instant")
    api_key = os.getenv("GROQ_API_KEY", "not_set")

    print(f"  Voice: {voice}")
    print(f"  Personality: {personality}")
    print(f"  AI Model: {model}")
    print(
        f"  API Key: {'✅ Set' if api_key != 'your_groq_api_key_here' and api_key != 'not_set' else '❌ Not set'}")

except Exception:
    print("  (Could not load current settings)")

print()
print("🎯 READY TO TEST:")
print("Even without an API key, JARVIS will work with intelligent fallback responses!")
print("With an API key, you get full AI conversational capabilities!")
print()
print("Run: python main.py")
print("Say: 'Hello JARVIS, how are you today?'")
print("Enjoy your AI assistant! 🎉")
