# GeminiCord
GeminiCord: Discord Bot with Gemini 2.0 Flash and Function Calling

## 🚀 Installation

### Prerequisites

```bash
# Requires Python 3.9+
python --version

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Setup

1. Clone the repository
```bash
git clone https://github.com/codejoa/geminicord.git
cd geminicord
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env` file
```env
# Discord Bot Token - https://discord.com/developers/applications
# 1. Go to Discord Developer Portal
# 2. Create New Application
# 3. Go to Bot section
# 4. Create Bot and copy token
DISCORD_TOKEN=your_discord_bot_token

# OpenWeather API Key - https://openweathermap.org/api
# 1. Sign up for free account
# 2. Go to API Keys section
# 3. Generate API Key
OPENWEATHER_API_KEY=your_openweather_api_key

# SerpAPI Key - https://serpapi.com/
# 1. Create free account
# 2. Get API Key from dashboard
SERPAPI_API_KEY=your_serpapi_api_key

# Google AI (Gemini) API Key - https://aistudio.google.com/app/apikey
# 1. Go to Google AI Studio
# 2. Click on "Get API key"
# 3. Create new API key or use existing one
GENAI_API_KEY=your_google_genai_api_key
```



## 🔧 Function Calling Features

The bot implements several function calls that can be triggered through natural conversation:

1. **Weather Information**
   - Triggered by weather-related queries
   - Provides real-time weather data

2. **Google Search**
   - Performs web searches
   - Returns formatted, embedded results

3. **Dice Rolling**
   - Supports various dice types
   - Random number generation

4. **User Settings**
   - Manages user preferences
   - Stores custom prompts
  
## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License
Free to Use!

## ⭐ Star History
[![Star History Chart](https://api.star-history.com/svg?repos=codejoa/geminicord&type=Date)](https://star-history.com/#codejoa/geminicord&Date)
