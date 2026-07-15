# app.py
import asyncio
import sys
from engines.dialogue_manager import DialogueManager

async def get_user_input(prompt: str) -> str:
    """하위 버전 파이썬에서도 안전하게 작동하는 비동기 입력 함수"""
    loop = asyncio.get_event_loop()
    # run_in_executor를 사용해 동기 input()을 별도 스레드에서 실행
    return await loop.run_in_executor(None, input, prompt)

async def main():
    print("🤖 [Dialogue OS v1.0] 시스템 초기화 중...")
    
    try:
        manager = DialogueManager()
    except ValueError as e:
        print(e)
        sys.exit(1)
        
    print("✨ [Dialogue OS v1.0] 준비 완료! 친구 대화 상담 엔진 작동 중...")
    print("👉 종료하려면 'q', 'quit', '종료'를 입력하세요.\n")
    print("-" * 60)
    
    while True:
        try:
            # 안전하게 비동기 입력 받기
            user_input = await get_user_input("\n유저: ")
            user_input = user_input.strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["q", "quit", "exit", "종료"]:
                print("\nAI: 오늘 얘기 들어줘서 정말 고마웠어. 다음에 또 심심하면 찾아와! 👋")
                break
                
            # 대화 파이프라인 구동 (답변 대기 표시)
            print("AI가 생각 중...", end="\r", flush=True)
            reply = await manager.handle_message(user_input)
            
            # 이전 대기 문구 지우기
            print(" " * 25, end="\r") 
            print(f"AI: {reply}")
            
        except KeyboardInterrupt:
            print("\nAI: 다음에 또 봐! 기다릴게 👋")
            break
        except Exception as e:
            print(f"\n❌ [Runtime Error] 치명적인 오류 발생: {e}")
            break

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())