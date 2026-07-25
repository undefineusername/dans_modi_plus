# llm.py
import json
import os
import sys
import time
import traceback
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# 파이참 및 콘솔 터미널 버퍼링 방지 및 한글 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

# =========================================================================
# Gemini API 설정 및 Client 로드
# =========================================================================
API_KEY_FILE = 'API.txt'
MODEL_NAME = 'gemini-3.5-flash-lite'  # 최신 Flash Lite 모델 적용
LOG_FILE = 'consultation_log.json'


def get_client():
    """API.txt 또는 환경변수에서 API 키를 읽어 안전하게 genai Client를 생성합니다."""
    key = None
    if os.path.exists(API_KEY_FILE):
        try:
            with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
                key = f.read().strip()
        except Exception as e:
            print(f"⚠️ {API_KEY_FILE} 읽기 실패: {e}", flush=True)

    if not key:
        key = os.environ.get('GEMINI_API_KEY')

    if not key:
        print("⚠️ 경고: API.txt 파일이나 환경 변수에서 Gemini API 키를 찾을 수 없습니다.", flush=True)
        return None

    return genai.Client(api_key=key)


# 글로벌 Gemini Client 초기화
client = get_client()


# 429 제한 완화를 위해 wait 시간을 최소 5초, 최대 20초로 대폭 늘렸습니다.

def get_empathetic_response_and_clarification(user_input, language):
    """사용자의 첫 답변에 공감하고 구체적 상황을 확인하는 질문 생성"""
    prompt = f"""
    당신은 사용자 심리 상담 AI입니다. 사용자가 말한 내용에 공감하고 구체적인 상황을 확인하세요.
    1. 사용자 입력 언어를 감지하세요.
    2. 사용자 입력에 깊이 공감하며, 다정한 메시지를 {language}로 1~2문장으로 생성하세요.
    3. 신체적 위급 상황이 언급되었다면 상황을 확인하는 질문을, 그렇지 않다면 상황을 조금 더 자세히 들려줄 수 있는지 묻는 질문을 1문장 작성하세요.
    4. 반드시 질문으로 끝나야 합니다.

    사용자 입력: "{user_input}"

    [출력 형식] JSON:
    {{
        "language": "ko" 또는 "en",
        "empathetic_message": "공감 메시지",
        "clarification_question": "질문 문장"
    }}
    """
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)



def generate_next_ai_response_with_analysis(conversation_history_str, language, is_initial_mode_message=False, environmental_data=None):
    """
    고민 분석 및 상담 모드 결정.
    * Mode B(라이프스타일/생활 상담)로 확정된 경우에만 environmental_data를 프롬프트에 제공합니다.
    """
    if is_initial_mode_message:
        mode_prompts = {
            "Mode A": f"당신은 심화 상담 전문가입니다. 깊은 심리적 문제를 분석하고 공감하며, 감정을 탐색하도록 유도하는 질문을 {language}로 작성해주세요.",
            "Mode B": f"당신은 라이프스타일 코치입니다. 대화 및 전달받은 주변 환경 데이터를 바탕으로 일상 습관, 루틴 탐색을 격려하는 질문을 {language}로 작성해주세요.",
            "Mode C": f"당신은 문제 해결 전문가입니다. 문제의 핵심을 요약한 뒤, 사용자에게 동의하는지 묻는 질문을 {language}로 작성해주세요."
        }

        analysis_only_prompt = f"""
        사용자의 고민을 듣고 최적의 상담 모드를 결정해주세요. 언어: {language}
        대화 내용: {conversation_history_str}

        [출력 형식] JSON:
        {{
            "primary_emotion": "주요 감정",
            "main_concern": "주요 고민",
            "counseling_need": "상담 니즈",
            "desired_outcome": "원하는 결과",
            "recommended_mode": "Mode A" 또는 "Mode B" 또는 "Mode C",
            "mode_name": "심화 상담" 또는 "라이프스타일 상담" 또는 "문제 해결",
            "confidence_level": "high"
        }}
        """
        analysis_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=analysis_only_prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        temp_analysis_result = json.loads(analysis_response.text)
        selected_mode = temp_analysis_result.get('recommended_mode', 'Mode A')
        mode_specific_instruction = mode_prompts.get(selected_mode, "")

        # API 연속 요청 시 429 방지를 위해 1.5초 대기
        time.sleep(1.5)

        # Mode B(생활 상담)일 때만 환경 데이터 활용
        env_info_str = ""
        if selected_mode == 'Mode B' and environmental_data:
            env_info_str = f"\n[참고 - 현재 수신된 주변 환경 데이터]: 온도 {environmental_data.get('temperature')}°C, 습도 {environmental_data.get('humidity')}%, 조도 {environmental_data.get('illuminance')}%, 음량 {environmental_data.get('volume')}%\n이 환경 요소를 자연스럽게 언급하며 첫 질문을 구성해주세요."

        full_prompt = f"""
        {mode_specific_instruction}
        [대화 내용]
        {conversation_history_str}
        {env_info_str}

        [출력 형식] JSON:
        {{
            "primary_emotion": "{temp_analysis_result.get('primary_emotion', '')}",
            "main_concern": "{temp_analysis_result.get('main_concern', '')}",
            "counseling_need": "{temp_analysis_result.get('counseling_need', '')}",
            "desired_outcome": "{temp_analysis_result.get('desired_outcome', '')}",
            "recommended_mode": "{selected_mode}",
            "mode_name": "{temp_analysis_result.get('mode_name', '심화 상담')}",
            "confidence_level": "high",
            "ai_message": "상담 진입 메시지 (하나의 질문으로 끝남)"
        }}
        """
    else:
        full_prompt = f"""
        사용자의 문제를 분석하고 공감한 후 하나의 질문을 {language}로 생성하세요.
        [현재까지 대화]
        {conversation_history_str}

        [출력 형식] JSON:
        {{
            "primary_emotion": "주요 감정",
            "main_concern": "주요 고민",
            "counseling_need": "상담 니즈",
            "desired_outcome": "원하는 결과",
            "recommended_mode": "Mode A" 또는 "Mode B" 또는 "Mode C",
            "mode_name": "심화 상담" 또는 "라이프스타일 상담" 또는 "문제 해결",
            "confidence_level": "low" 또는 "medium" 또는 "high",
            "ai_message": "다음 질문 (하나의 질문으로 끝남)"
        }}
        """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)


def chat_with_gemini(mode_name, chat_history, saved_problem_data_ref):
    """본 상담 세션 진행"""
    chat = client.chats.create(model=MODEL_NAME)

    print("\n--- AI 심리 상담 진행 중 (종료하려면 '종료' 또는 'exit' 입력) ---", flush=True)

    while True:
        user_turn = input("\n👤 사용자: ").strip()

        if not user_turn:
            continue

        if user_turn.lower() in ['종료', 'exit']:
            print("\n🤖 AI: 오늘 대화 나누어주셔서 감사해요. 언제든 마음이 힘들 때 다시 찾아주세요!", flush=True)
            break

        chat_history.append({"role": "user", "parts": [user_turn]})
        saved_problem_data_ref['consultation_dialogue'].append({"speaker": "User", "mode": mode_name, "message": user_turn})

        try:
            # 대화 주고받을 때도 약 1초 간격을 줘서 속도 제한 방지
            time.sleep(1.0)
            ai_response_obj = chat.send_message(user_turn)
            ai_message = ai_response_obj.text
            print(f"\n🤖 AI: {ai_message}", flush=True)

            chat_history.append({"role": "model", "parts": [ai_message]})
            saved_problem_data_ref['consultation_dialogue'].append({"speaker": "AI", "mode": mode_name, "message": ai_message})
        except Exception as e:
            print(f"❌ AI 응답 생성 중 오류 발생: {e}", flush=True)
            print("💡 API 호출 할당량이 잠시 초과되었습니다. 잠시 후 다시 입력해 보세요.", flush=True)


def run_consultation_system(user_mood=None, env_data=None):
    """메인 시스템에서 전달받은 user_mood, env_data를 활용해 상담을 실행합니다."""
    global client
    if not client:
        client = get_client()
        if not client:
            print("❌ API 키가 설정되지 않아 시스템을 시작할 수 없습니다. API.txt 파일 상태를 확인하세요.", flush=True)
            return

    full_user_problem_description = []
    chat_history_for_analysis = []
    current_language = 'ko'

    # 기본 환경 데이터 보장
    environmental_data = env_data if env_data else {
        'temperature': 24.0,
        'humidity': 50.0,
        'illuminance': 30.0,
        'volume': 10.0
    }

    print("\n==========================================", flush=True)
    print("        [MindMODI] AI 심리 상담 모드        ", flush=True)
    print("==========================================", flush=True)

    # 기본 첫 인사
    first_greeting = "안녕하세요! 오늘 어떤 일이나 고민이 있으셨나요? 편하게 이야기해 주세요."
    print(f"\n🤖 AI: {first_greeting}\n", flush=True)

    # 1. 사용자 첫 답변
    user_input = input("👤 사용자: ").strip()
    full_user_problem_description.append(user_input)
    chat_history_for_analysis.append(f"AI: {first_greeting}")
    chat_history_for_analysis.append(f"사용자: {user_input}")

    # 2. 공감 및 정황 질문 (에러 발생 시 Fallback 처리)
    try:
        empathy_and_question = get_empathetic_response_and_clarification(user_input, current_language)
        current_language = empathy_and_question.get('language', 'ko')
        print(f"\n🤖 AI: {empathy_and_question['empathetic_message']} {empathy_and_question['clarification_question']}\n", flush=True)
    except Exception as e:
        print(f"\n⚠️ API 요청량이 많아 기본 응답으로 전환합니다.", flush=True)
        print(f"\n🤖 AI: 마음이 많이 복잡하시겠어요. 당시 상황이나 느끼신 점을 조금 더 말씀해 주실 수 있나요?\n", flush=True)

    user_clarification_input = input("👤 사용자: ").strip()
    full_user_problem_description.append(user_clarification_input)
    chat_history_for_analysis.append(f"사용자: {user_clarification_input}")

    # 3. 고민 분류 루프
    analysis_result = {'confidence_level': 'low'}
    clarification_count = 0

    while analysis_result.get('confidence_level') != 'high' and clarification_count < 2:
        print("\n⏳ AI가 고민 내용을 분석 중입니다...", flush=True)
        time.sleep(1.5)  # 429 에러 방지용 대기시간
        current_conversation_str = "\n".join(chat_history_for_analysis)
        try:
            combined_output = generate_next_ai_response_with_analysis(
                current_conversation_str,
                current_language,
                is_initial_mode_message=False
            )
            analysis_result = {k: combined_output[k] for k in combined_output if k != 'ai_message'}
            next_question = combined_output.get('ai_message', '조금 더 설명해 주실 수 있나요?')

            if analysis_result.get('confidence_level') == 'high':
                break

            print(f"\n🤖 AI: {next_question}\n", flush=True)
            user_additional_input = input("👤 사용자: ").strip()
            full_user_problem_description.append(user_additional_input)
            chat_history_for_analysis.append(f"사용자: {user_additional_input}")
            clarification_count += 1
        except Exception as e:
            print(f"⚠️ 분석 중 일시적 지연이 발생했습니다. 바로 다음 단계로 진행합니다.", flush=True)
            break

    # 4. 데이터 세팅 및 저장용 구조체 준비
    final_user_problem = " ".join(full_user_problem_description)
    mode_name = analysis_result.get('mode_name', '심화 상담')

    saved_problem_data = {
        "original_text": final_user_problem,
        "recorded_mood": user_mood,
        "environmental_data": environmental_data,
        "primary_emotion": analysis_result.get("primary_emotion", ""),
        "main_concern": analysis_result.get("main_concern", ""),
        "counseling_need": analysis_result.get("counseling_need", ""),
        "desired_outcome": analysis_result.get("desired_outcome", ""),
        "recommended_mode": analysis_result.get("recommended_mode", "Mode A"),
        "mode_name": mode_name,
        "consultation_dialogue": []
    }

    # 5. 본 상담 모드 진입 (Mode B일 때만 환경 데이터 전달)
    try:
        time.sleep(1.5)
        initial_mode_output = generate_next_ai_response_with_analysis(
            "\n".join(chat_history_for_analysis),
            current_language,
            is_initial_mode_message=True,
            environmental_data=environmental_data if analysis_result.get('recommended_mode') == 'Mode B' else None
        )
        initial_mode_message = initial_mode_output.get('ai_message', "이야기해 주셔서 감사해요. 이제 차근차근 나누어 볼까요?")
    except Exception:
        initial_mode_message = "이야기해 주셔서 감사해요. 이제 차근차근 나누어 볼까요?"

    chat_history = [{"role": "model", "parts": [initial_mode_message]}]
    saved_problem_data['consultation_dialogue'].append({"speaker": "AI", "mode": mode_name, "message": initial_mode_message})

    print(f"\n🤖 AI: {initial_mode_message}\n", flush=True)

    # 6. 채팅 대화 진행
    chat_with_gemini(mode_name, chat_history, saved_problem_data)

    # 7. 로그 저장
    try:
        log_data = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                log_data = json.load(f)

        log_data.append(saved_problem_data)

        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ 상담 로그가 '{LOG_FILE}'에 저장되었습니다.", flush=True)
    except Exception as e:
        print(f"❌ 로그 저장 실패: {e}", flush=True)


if __name__ == "__main__":
    sample_user_mood = 3
    sample_env_data = {'temperature': 22.5, 'humidity': 45.0, 'illuminance': 15.0, 'volume': 5.0}

    run_consultation_system(user_mood=sample_user_mood, env_data=sample_env_data)
