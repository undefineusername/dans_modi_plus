import os
import requests

API_KEY = os.environ.get("GROQ_API_KEY", "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")

def ask_groq(system_prompt: str, history: list, user_message: str) -> str:
    """Groq API 호출 (requests 버전)"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # 이전 대화 추가
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("parts", "")

        if isinstance(content, list):
            content = content[0]

        messages.append({
            "role": role,
            "content": content
        })

    # 현재 사용자 입력
    messages.append({
        "role": "user",
        "content": user_message
    })

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"[LLM Error] Groq 호출 실패: {e}")
        return "미안해, 지금은 생각이 잘 정리되지 않네. 무슨 일 있었는지 다시 말해줄래?"