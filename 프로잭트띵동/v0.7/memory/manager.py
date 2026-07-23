import json
import os

from config import MEMORY_PATH


def load_memory() -> dict:
    if not os.path.exists(MEMORY_PATH) or os.path.getsize(MEMORY_PATH) == 0:
        return {}

    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def load_memory_text() -> str:
    memory = load_memory()
    if not memory:
        return "{}"

    return json.dumps(memory, ensure_ascii=False, indent=2)


def save_user_info(key: str, value: str) -> str:
    memory = load_memory()
    
    # 키가 이미 존재하면 (문자열이든 리스트든) 리스트 형태로 유지하며 새 값을 추가
    if key in memory:
        if isinstance(memory[key], list):
            if value not in memory[key]:
                memory[key].append(value)
        else:
            if memory[key] != value:
                memory[key] = [memory[key], value]
    else:
        # 새로운 키라면 리스트 형태로 시작
        memory[key] = [value]

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)

    return f"성공적으로 로컬 기억장치에 저장됨: [{key}] -> {value}"
