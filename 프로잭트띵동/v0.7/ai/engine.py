import json
import os

import requests

from config import API_KEY_PATH, GROQ_URL, MAX_HISTORY_LEN, MODEL_NAME
from memory.manager import save_user_info


SAVE_USER_INFO_TOOL = {
    "type": "function",
    "function": {
        "name": "save_user_info",
        "description": "유저의 중요한 개인 정보, 고민, 목표, 상태 등을 기억장치에 저장합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "정보 카테고리 (예: '현재 고민', '신체 목표')",
                },
                "value": {
                    "type": "string",
                    "description": "기억해야 할 구체적인 내용",
                },
            },
            "required": ["key", "value"],
        },
    },
}


class GroqEngine:
    """v0.5 groktest Groq 호출 + tool call 루프."""

    def __init__(self):
        self.api_key = self._load_api_key()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _load_api_key(self) -> str:
        if os.path.exists(API_KEY_PATH):
            with open(API_KEY_PATH, "r", encoding="utf-8") as f:
                key = f.read().strip()
                if key:
                    return key

        env_key = os.getenv("GROQ_API_KEY", "").strip()
        if env_key:
            return env_key

        raise ValueError(
            f"Groq API 키가 없습니다. '{API_KEY_PATH}' 파일에 키를 넣거나 "
            "환경 변수 GROQ_API_KEY를 설정하세요."
        )

    def chat(self, messages: list) -> str:
        while True:
            payload = {
                "model": MODEL_NAME,
                "messages": self._trim_messages(messages),
                "tools": [SAVE_USER_INFO_TOOL],
            }

            response = requests.post(
                GROQ_URL,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            res_json = response.json()

            try:
                message = res_json["choices"][0]["message"]
                tool_calls = message.get("tool_calls")
            except (KeyError, IndexError, TypeError):
                return f"서버 에러: {res_json}"

            if tool_calls:
                tool_call = tool_calls[0]
                func_name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])

                if func_name == "save_user_info":
                    print(
                        f"(기억 저장) -> 키: {args['key']}, 값: {args['value']}"
                    )
                    result_msg = save_user_info(args["key"], args["value"])

                    messages.append(message)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": func_name,
                            "content": result_msg,
                        }
                    )
                    continue

            return message.get("content", "잠시 후 다시 말해줄래요?")

    def _trim_messages(self, messages: list) -> list:
        if len(messages) <= MAX_HISTORY_LEN + 1:
            return messages

        system_msg = messages[0]
        recent = messages[-(MAX_HISTORY_LEN):]
        return [system_msg, *recent]
