import json
import os
from datetime import datetime

from config import MOOD_HISTORY_PATH


def save_mood_score(score: int):
    history = []
    if os.path.exists(MOOD_HISTORY_PATH) and os.path.getsize(MOOD_HISTORY_PATH) > 0:
        try:
            with open(MOOD_HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []

    history.append(
        {
            "score": score,
            "at": datetime.now().isoformat(timespec="seconds"),
        }
    )

    with open(MOOD_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
