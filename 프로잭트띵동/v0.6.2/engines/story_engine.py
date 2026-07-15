# engines/story_engine.py
import json
import os
from typing import Dict, Any, List
from config import STORY_PATH

class StoryEngine:
    def __init__(self):
        self.story_data = self._load_story()

    def _load_story(self) -> Dict[str, Any]:
        default_story = {
            "active_story": {
                "title": "일상",
                "scene": "Intro",               # Scene 단위 관리 (S급 4번)
                "goal": "comfort",              # 대화 목표 (A급 10번)
                "emotion": "neutral",           # 스토리 감정 (A급 12번)
                "priority": 10,                 # 우선순위 (A급 13번)
                "missing": []                   # Scene 한정 미싱 인포 (S급 3번)
            },
            "story_stack": [],                  # 멈춰둔 이전 스토리들 (A급 8번)
            "open_loops": [],                   # 회수해야 할 열린 결말 (A급 9번)
            "completed_stories": []             # Closed 된 스토리 아카이브 (A급 14번)
        }
        if os.path.exists(STORY_PATH):
            try:
                with open(STORY_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return default_story
        return default_story

    def save_story(self):
        with open(STORY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.story_data, f, ensure_ascii=False, indent=4)

    def get_current_context(self) -> Dict[str, Any]:
        return self.story_data

    def switch_story(self, new_story_title: str, priority: int = 50, goal: str = "comfort"):
        """새로운 주제 감지 시 기존 스토리를 Stack에 저장하고 전환 (S급 7번, A급 8번 해결)"""
        current = self.story_data["active_story"]
        
        # 현재 활성화된 스토리가 '일상'이 아니라면 스택에 쌓음
        if current["title"] != "일상":
            self.story_data["story_stack"].append(current)
            print(f"⏸️ [스토리 일시정지] '{current['title']}' 스토리가 스택으로 이동했습니다.")
            
        # 새 스토리 생성
        self.story_data["active_story"] = {
            "title": new_story_title,
            "scene": "Intro",
            "goal": goal,
            "emotion": "neutral",
            "priority": priority,
            "missing": []
        }
        self.save_story()
        print(f"🚀 [새 스토리 활성화] 주제: '{new_story_title}'")

    def resume_story(self) -> bool:
        """가장 우선순위가 높은 멈춘 이야기를 꺼내 대화를 다시 이어감 (Story Stack 복구)"""
        if not self.story_data["story_stack"]:
            return False
            
        # 스택에서 가장 최근 멈춘 이야기 팝(Pop)
        prev_story = self.story_data["story_stack"].pop()
        self.story_data["active_story"] = prev_story
        self.save_story()
        print(f"▶️ [스토리 재개] '{prev_story['title']}' 스토리로 복귀했습니다.")
        return True

    def close_current_story(self):
        """사용자가 '됐어', '그만'이라고 할 때 명시적으로 종료 (A급 14번 해결)"""
        current = self.story_data["active_story"]
        self.story_data["completed_stories"].append(current["title"])
        print(f"✅ [스토리 종료] '{current['title']}' 스토리가 완료 및 잠금 처리되었습니다.")
        
        # 이전 대화가 있다면 복구하고 없으면 일상으로 컴백
        if not self.resume_story():
            self.story_data["active_story"] = {
                "title": "일상",
                "scene": "Intro",
                "goal": "comfort",
                "emotion": "neutral",
                "priority": 10,
                "missing": []
            }
            self.save_story()