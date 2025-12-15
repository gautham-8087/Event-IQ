# EventHub AI 🎯

A smart event scheduling and resource allocation system powered by Event IQ AI and Supabase.

## Features

- 🤖 **AI-Powered Scheduling**: Event IQ AI assistant for intelligent event booking and availability checking
- 📅 **Manual Booking**: Direct event creation with availability checking
- 🔐 **Authentication**: Secure login/signup with Supabase Auth
- 🗄️ **Cloud Database**: Real-time data sync with Supabase
- ✨ **Modern UI**: Glassmorphism design with smooth animations
- 🔍 **Conflict Detection**: Automatic resource availability checking

## Tech Stack

- **Backend**: Python Flask
- **Database**: Supabase (PostgreSQL)
- **AI**: Google Gemini 2.0 Flash (Event IQ powered)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Authentication**: Supabase Auth

## Setup

### Prerequisites

- Python 3.8+
- Supabase Account
- Google AI Studio API Key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gautham-8087/Event-IQ.git
cd Event-IQ
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
USE_SUPABASE=True
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

4. Set up database tables by running the SQL in `supabase_schema.sql` in your Supabase SQL Editor.

5. Run the application:
```bash
python app.py
```

6. Open `http://127.0.0.1:5000` in your browser.

## Project Structure

```
Event-IQ/
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── login.html
├── utils/
│   ├── ai_assistant.py
│   ├── data_manager.py
│   ├── scheduler.py
│   └── supabase_client.py
├── data/
│   ├── events.json
│   ├── resources.json
│   └── allocations.json
├── app.py
├── supabase_schema.sql
└── requirements.txt
```

## Usage

1. **Login**: Use the default credentials or create a new account
2. **View Dashboard**: See upcoming events and available resources
3. **Manual Booking**: Click the green "+" button to create events manually
4. **AI Assistant**: Click the blue chat button to interact with Event IQ AI for intelligent scheduling and availability checking

## License

MIT License
