# Environment Configuration Example
# Copy this file to config/settings.py and fill in your actual values

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "your_elevenlabs_api_key_here")

# Slack Integration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "xoxb-your-slack-bot-token")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "xapp-your-slack-app-token")

# Gmail Integration
GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")

# Notion Integration
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "your_notion_api_key_here")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///context.db")

# Server Configuration
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
