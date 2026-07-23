from datetime import datetime

def get_current_time_str() -> str:
    return datetime.now().isoformat()

def clean_text(text: str) -> str:
    return text.strip()
