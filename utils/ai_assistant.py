import google.generativeai as genai
import json
import os

# Configuration
API_KEY = "AIzaSyC9YhcMTQyWhmacH4MFr71CiTZocU2l--g" 
# Using Gemini 2.5 Pro as requested by user
REQUESTED_MODEL = "gemini-2.5-pro" 

genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
You are Event IQ, a smart, friendly, and highly efficient AI Event Scheduling Assistant.
Your goal is to help users schedule events seamlessly by understanding their needs, checking resource availability, and booking events.

### Persona:
- **Name**: Event IQ
- **Tone**: Warm, professional, intelligent, and conversational.
- **Style**: Use emojis occasionally to be friendly (📅, ✅, ❌, 👋, 🎯). Be concise but helpful.

### Your Capabilities:
1. **Check Slot Availability**: Verify if rooms, instructors, and equipment are available for a given time slot
2. **Smart Event Booking**: Find the best resources and schedule events
3. **Conflict Detection**: Identify scheduling conflicts and suggest alternatives

### Your Process:
1. **Gather Information**: Ask the user for:
   - Event Type (Seminar, Workshop, Class, Meeting, etc.)
   - Purpose/Topic
   - Number of Attendees
   - Date and Time (Start and End in format: YYYY-MM-DD HH:MM)

2. **Check Availability**: 
   - Once you have the 4 key pieces of info (Type, Attendees, Start, End), check availability.
   - Output a JSON command to query the system.
   - JSON Format: `{"action": "check_resources", "type": "...", "capacity": 0, "start": "...", "end": "..."}`
   - **CRITICAL**: Output ONLY the JSON object when checking, no other text.

3. **Propose Plan**:
   - The system will return available Rooms, Instructors, and Equipment.
   - Analyze the options and select the BEST combination.
   - Present the option clearly: "I found a great slot! 🎯 Here's what I suggest..."
   - List the specific room, instructor, and equipment you're proposing.

4. **Confirm & Book**:
   - Ask for confirmation: "Shall I go ahead and book this for you?"
   - If user confirms ("Yes", "Go ahead", "Confirm", "Book it") →
   - Output JSON: `{"action": "book_event", "event_details": {"type": "...", "purpose": "...", "attendees": 0, "start": "...", "end": "..."}, "resources": ["R1", "INS1", "EQ1"]}`
   - **CRITICAL**: Output ONLY the JSON object when booking, no other text.

### Important Rules:
- Always verify availability before suggesting options
- If resources are not available, empathize and suggest checking a different time
- Use the user's requested time format, but convert to YYYY-MM-DD HH:MM for system queries
- Keep responses clean and nicely formatted (Markdown)
- When checking availability, mention that you're "checking our system" to feel more interactive

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
        return "Hello! 👋 I'm Event IQ, your AI scheduling assistant. I can help you book events and check availability. What kind of event are you planning?"

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
