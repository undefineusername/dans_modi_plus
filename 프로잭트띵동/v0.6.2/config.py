# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# os.exist_ok=True -> exist_ok=True 로 수정!
os.makedirs(DATA_DIR, exist_ok=True)

# 파일 경로 정의
PROFILE_PATH = os.path.join(DATA_DIR, "profile.json")
MEMORY_ACTIVE_PATH = os.path.join(DATA_DIR, "active_memory.json")
MEMORY_ARCHIVE_PATH = os.path.join(DATA_DIR, "archive_memory.json")
STORY_PATH = os.path.join(DATA_DIR, "story.json")
EMOTION_PATH = os.path.join(DATA_DIR, "emotion.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")
API_KEY_PATH = os.path.join(BASE_DIR, "apikey")

# LLM 설정
MODEL_NAME = "llama-3.1-8b-instant"
MAX_HISTORY_LEN = 6