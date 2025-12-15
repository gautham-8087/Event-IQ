from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from utils.data_manager import DataManager
from utils.scheduler import Scheduler
from utils.ai_assistant import AIAssistant
from utils.supabase_client import supabase
import json
import re
import os
from functools import wraps

app = Flask(__name__)
# Secure secret key for sessions (in production, use random env var)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_super_secret_key_123')

ai_assistant = AIAssistant()

# --- Auth Middleware ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # If API request, return 401
            if request.path.startswith('/api/'):
                 return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/login')
def login_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        if not supabase:
             return jsonify({"error": "Supabase client not initialized"}), 500
             
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            session['user'] = res.user.id
            session['email'] = res.user.email
            return jsonify({"success": True, "user": {"id": res.user.id, "email": res.user.email}})
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        if not supabase:
             return jsonify({"error": "Supabase client not initialized"}), 500
             
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            # Depending on config, might not log in immediately if email confirm needed
             return jsonify({"success": True, "user": {"id": res.user.id, "email": res.user.email}})
        else:
             return jsonify({"error": "Signup failed"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/logout')
def logout():
    session.clear()
    if supabase:
        supabase.auth.sign_out()
    return redirect(url_for('login_page'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user_email=session.get('email'))

@app.route('/api/resources', methods=['GET'])
@login_required
def get_resources():
    return jsonify(DataManager.get_resources())

@app.route('/api/events', methods=['GET'])
@login_required
def get_events():
    return jsonify(DataManager.get_events())

@app.route('/api/events/<event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    DataManager.delete_event(event_id)
    return jsonify({"success": True, "message": "Event deleted successfully"})

def extract_json(text):
    """Extracts JSON object from text (handles markdown code blocks)."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # 1. Send message to AI
    ai_response = ai_assistant.send_message(user_message)
    
    # 2. Check for JSON command
    command = extract_json(ai_response)
    
    if command:
        action = command.get('action')
        
        if action == 'check_resources':
            # Run availability check
            r_type = command.get('type') # 'Seminar', 'Workshop', etc. maps to room/instructor/equip logic
            # Mapping logic:
            # Seminar -> Room (Auditorium/Hall), Proj, Mic
            # Workshop -> Room (Lab/Studio), Computers
            # Class -> Room (Classroom), Whiteboard
            
            # Simplified Logic:
            start = command.get('start')
            end = command.get('end')
            capacity = command.get('capacity', 0)
            
            # Find Room
            rooms = Scheduler.find_suitable_resources('Room', start, end, min_capacity=capacity)
            
            # Find Instructor
            instructors = Scheduler.find_suitable_resources('Instructor', start, end)
            
            # Find Equipment (generic grab for now, or specific based on type)
            equipment = Scheduler.find_suitable_resources('Equipment', start, end)
            
            system_context = {
                "available_rooms": [f"{r['id']} - {r['name']} (Cap: {r['capacity']})" for r in rooms[:5]], # Limit to 5
                "available_instructors": [f"{i['id']} - {i['name']} ({i.get('specialization', '')})" for i in instructors[:5]],
                "available_equipment": [f"{e['id']} - {e['name']}" for e in equipment[:5]]
            }
            
            # Feed back to AI
            final_response = ai_assistant.send_message("Here is the availability data.", system_context=json.dumps(system_context))
            return jsonify({"response": final_response})
            
        elif action == 'book_event':
            # Book the event
            event_details = command.get('event_details')
            resources = command.get('resources') # List of IDs
            
            # Create event object
            new_event = {
                "id": f"EVT-{len(DataManager.get_events()) + 100}",
                "title": f"{event_details.get('type')} - {event_details.get('purpose', 'Event')}",
                "type": event_details.get('type'),
                "start_time": event_details.get('start'),
                "end_time": event_details.get('end'),
                "description": f"Attendees: {event_details.get('attendees')}. Purpose: {event_details.get('purpose')}"
            }
            
            success, msg = Scheduler.schedule_event(new_event, resources)
            
            if success:
                return jsonify({"response": f"✅ Event Confirmed! {msg}\n\n**Details:**\n- {new_event['title']}\n- {new_event['start_time']}"})
            else:
                # Tell AI it failed
                retry_response = ai_assistant.send_message(f"Booking failed: {msg}. Please ask user for alternative.")
                return jsonify({"response": retry_response})
                
    # Normal textual response
    return jsonify({"response": ai_response})

# --- Manual Booking Endpoints ---

@app.route('/api/check-availability', methods=['POST'])
@login_required
def check_availability():
    try:
        data = request.json
        start = data.get('start')
        end = data.get('end')
        
        cap_str = data.get('capacity')
        min_capacity = int(cap_str) if cap_str and cap_str.strip() else 0
        limit = 20 # Show more for manual
        
        rooms = Scheduler.find_suitable_resources('Room', start, end, min_capacity=min_capacity)
        instructors = Scheduler.find_suitable_resources('Instructor', start, end)
        equipment = Scheduler.find_suitable_resources('Equipment', start, end)
        
        return jsonify({
            "rooms": rooms[:limit],
            "instructors": instructors[:limit],
            "equipment": equipment[:limit]
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/book-manual', methods=['POST'])
@login_required
def book_manual():
    try:
        data = request.json
        event_details = data.get('event')
        resource_ids = data.get('resources') # List
        
        # Create Event Object
        new_event = {
            "id": f"EVT-{len(DataManager.get_events()) + 300}", # Different range
            "title": event_details.get('title'),
            "type": event_details.get('type'),
            "start_time": event_details.get('start'),
            "end_time": event_details.get('end'),
            "description": f"Manual Booking. Purpose: {event_details.get('purpose')}. Attendees: {event_details.get('capacity')}"
        }
        
        success, msg = Scheduler.schedule_event(new_event, resource_ids)
        
        if success:
            return jsonify({"success": True, "message": "Event Booked Successfully!"})
        else:
            return jsonify({"success": False, "message": msg}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"System Error: {str(e)}"}), 500

@app.route('/api/event/<event_id>', methods=['GET'])
@login_required
def get_event_details(event_id):
    events = {e['id']: e for e in DataManager.get_events()}
    event = events.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    
    # Get allocations for this event
    allocs = DataManager.get_allocations()
    resources = {r['id']: r for r in DataManager.get_resources()}
    
    allocated_resources = []
    for a in allocs:
        if a['event_id'] == event_id:
            res = resources.get(a['resource_id'])
            if res:
               allocated_resources.append(res)
               
    return jsonify({
        "event": event,
        "resources": allocated_resources
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
