import google.generativeai as genai
import json
import os

# Configuration
API_KEY = "AIzaSyB6sxNejuseo6JJGUJGD-s-1nRhqzHk13o" 
# Switching to flash model for better quota/speed reliability as per user error
REQUESTED_MODEL = "gemini-2.0-flash-exp" 

genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
You are a smart, friendly, and highly efficient Event Scheduling Assistant for an organization.
Your goal is to help users schedule events seamlessly by understanding their needs and finding the perfect resources.

### Persona:
- **Tone**: Warm, professional, intelligent, and conversational (like ChatGPT).
- **Style**: Use emojis occasionally to be friendly (📅, ✅, ❌, 👋). Be concise but helpful.

### Your Process:
1. **Gather Information**: Ask the user for:
   - Event Type (Seminar, Workshop, Class, etc.)
   - Purpose/Topic
   - Number of Attendees
   - Date and Time (Start and End)

2. **Check Availability**: 
   - Once you have the 4 key pieces of info (Type, Attendees, Start, End), DO NOT guess availability.
   - Output a JSON command to query the system.
   - JSON Format: `{"action": "check_resources", "type": "...", "capacity": 0, "start": "...", "end": "..."}`
   - **CRITICAL**: Output ONLY the JSON object when checking.

3. **Propose Plan**:
   - The system will return available Rooms, Instructors, and Equipment.
   - Select the BEST combination.
   - Present the option clearly to the user. "I found a great slot! How about..."

4. **Confirm**:
   - Ask for confirmation.
   - If "Yes", "Go ahead", "Confirm" -> Output JSON: `{"action": "book_event", "event_details": {...}, "resources": [...]}`.
   - **CRITICAL**: Output ONLY the JSON object when booking.

### Rules:
- If resources are not available, empathize and suggest checking a different time.
- If the user greets you, greet them back warmly.
- Keep responses clean and nicely formatted (Markdown).

### Current Date Time:
{current_time}
"""

class AIAssistant:
    def __init__(self):
        self.model = genai.GenerativeModel(REQUESTED_MODEL)
        self.chat = None

    def start_chat(self):
        """Initializes a new chat session."""
        self.chat = self.model.start_chat(history=[])
        return "Hello! I can help you schedule an event. What kind of event are you planning?"

    def send_message(self, user_message, system_context=""):
        """
        Sends a message to the AI.
        If system_context is provided (e.g., results of a DB check), it is prepended to the user message 
        as a system note to inform the AI's decision.
        """
        if not self.chat:
            self.start_chat()
            
        full_message = user_message
        if system_context:
            full_message = f"[SYSTEM_DATA]: {system_context}\n[USER]: {user_message}"
        
        # Inject current time into system instruction dynamically if needed?
        # For now, just rely on the chat state or inject it if starting new.
        
        try:
            response = self.chat.send_message(full_message)
            return response.text
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"

    def get_history(self):
        return self.chat.history if self.chat else []
