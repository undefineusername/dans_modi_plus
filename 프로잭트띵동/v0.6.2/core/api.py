# core/api.py
import os
import httpx
from config import MODEL_NAME, API_KEY_PATH

class GroqAPIClient:
    def __init__(self):
        self.api_key = self._load_api_key()
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _load_api_key(self) -> str:
        """apikey 파일 또는 환경 변수에서 키를 가져옴"""
        if os.path.exists(API_KEY_PATH):
            with open(API_KEY_PATH, "r", encoding="utf-8") as f:
                key = f.read().strip()
                if key:
                    return key
        
        # 환경 변수 fallback
        env_key = os.getenv("GROQ_API_KEY")
        if env_key:
            return env_key
            
        raise ValueError(
            f"❌ 에러: Groq API 키를 찾을 수 없습니다.\n"
            f"'{API_KEY_PATH}' 파일에 키를 입력하거나, 환경 변수 'GROQ_API_KEY'를 설정해 주세요."
        )

    async def request_completion(self, system_prompt: str, user_text: str) -> str:
        """Groq LLM에 비동기로 응답을 요청하는 핵심 메소드"""
        payload = {
            "model": MODEL_NAME,
            "response_format": {"type": "json_object"},  # JSON 모드 강제 적용
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.5  # 일관된 JSON 스키마를 위해 약간 낮춤
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(self.url, headers=self.headers, json=payload)
                response.raise_for_status()
                res_json = response.json()
                
                # API가 반환한 Raw 텍스트 추출
                return res_json['choices'][0]['message']['content']
                
            except httpx.HTTPStatusError as e:
                print(f"❌ [Groq API HTTP Error] 상태 코드: {e.response.status_code} | 내용: {e.response.text}")
                return "{}"
            except httpx.RequestError as e:
                print(f"❌ [Groq API Connection Error] 네트워크 연결 실패: {e}")
                return "{}"
            except Exception as e:
                print(f"❌ [Groq API Unexpected Error] 알 수 없는 오류: {e}")
                return "{}"