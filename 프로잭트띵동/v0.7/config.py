import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# AI (v1.0)
API_KEY_PATH = os.path.join(BASE_DIR, "api.txt")
MODEL_NAME = "openai/gpt-oss-120b"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MAX_HISTORY_LEN = 8
MEMORY_PATH = os.path.join(DATA_DIR, "memory.json")
MOOD_HISTORY_PATH = os.path.join(DATA_DIR, "mood_history.json")
STORIES_PATH = os.path.join(DATA_DIR, "stories.json")
SESSIONS_PATH = os.path.join(DATA_DIR, "sessions.json")
PROFILE_PATH = os.path.join(DATA_DIR, "profile.json")
