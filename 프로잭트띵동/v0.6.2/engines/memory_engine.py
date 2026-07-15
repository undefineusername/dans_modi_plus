# engines/memory_engine.py
import json
import os
import time
from typing import Dict, Any, List
from config import MEMORY_ACTIVE_PATH, MEMORY_ARCHIVE_PATH

class MemoryEngine:
    def __init__(self):
        self.active_memories = self._load_json(MEMORY_ACTIVE_PATH, [])
        self.archive_memories = self._load_json(MEMORY_ARCHIVE_PATH, [])

    def _load_json(self, path: str, default: Any) -> Any:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return default
        return default

    def _save_json(self, path: str, data: Any):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _generate_id(self, category: str, entity_name: str) -> str:
        """카테고리와 엔티티 명을 활용해 고유 ID 포맷 반환"""
        clean_entity = entity_name.strip().lower().replace(" ", "_")
        clean_category = category.strip().lower()
        return f"{clean_category}_{clean_entity}"

    def search_memories(self, user_text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """간단한 키워드 매칭 기반 기억 소환 (RAG 대체용 v1.0)"""
        if not self.active_memories:
            return []
            
        matched = []
        user_words = [w.strip() for w in user_text.split() if len(w) > 1]
        
        for mem in self.active_memories:
            entity = mem.get("entity_name", "").lower()
            summary = mem.get("summary", "").lower()
            
            # 엔티티명이 유저 입력에 직접 들어가 있거나 단어가 겹치는지 체크
            if entity in user_text.lower() or any(word.lower() in summary for word in user_words):
                matched.append(mem)
                
        # 중요도 순 정렬 후 상위 limit 개만 반환
        matched.sort(key=lambda x: x.get("importance", 50), reverse=True)
        return matched[:limit]

    def update_memory_state(self, memory_delta: Dict[str, Any]):
        """LLM 분석 결과를 받아서 기억을 분기 처리 (CREATE/UPDATE/DELETE/IGNORE)"""
        action = memory_delta.get("action", "IGNORE").upper()
        if action == "IGNORE":
            return

        category = memory_delta.get("category", "etc")
        entity_name = memory_delta.get("entity_name", "").strip()
        if not entity_name:
            return

        mem_id = self._generate_id(category, entity_name)
        summary = memory_delta.get("summary", "")
        importance = memory_delta.get("importance", 50)

        # 기존 기억 탐색
        existing_idx = next((i for i, m in enumerate(self.active_memories) if m.get("id") == mem_id), None)

        if action == "DELETE":
            if existing_idx is not None:
                del self.active_memories[existing_idx]
                print(f"💾 🗑️ [기억 삭제 완료] {mem_id}")
                self._save_json(MEMORY_ACTIVE_PATH, self.active_memories)
            return

        # CREATE / UPDATE 통합 처리
        new_memory = {
            "id": mem_id,
            "category": category,
            "entity_name": entity_name,
            "summary": summary,
            "importance": importance,
            "updated_at": int(time.time())  # TTL 관리를 위한 타임스탬프
        }

        if existing_idx is not None:
            self.active_memories[existing_idx] = new_memory
            print(f"💾 🔄 [기억 업데이트] {mem_id}")
        else:
            self.active_memories.append(new_memory)
            print(f"💾 ✨ [새로운 기억 생성] {mem_id}")

        self._save_json(MEMORY_ACTIVE_PATH, self.active_memories)

    def cleanup_memory(self, days_threshold: int = 30, min_importance: int = 40):
        """
        TTL 정화 엔진:
        오래되었거나(예: 30일 경과) 중요도가 min_importance 미만인 기억을
        Active에서 빼서 Archive(보관소)로 영구히 이동시킴.
        """
        now = int(time.time())
        threshold_seconds = days_threshold * 24 * 60 * 60
        
        new_active = []
        archived_count = 0

        for mem in self.active_memories:
            updated_at = mem.get("updated_at", now)
            importance = mem.get("importance", 50)
            
            is_old = (now - updated_at) > threshold_seconds
            is_unimportant = importance < min_importance

            if is_old or is_unimportant:
                # 아카이브로 이동
                self.archive_memories.append(mem)
                archived_count += 1
            else:
                new_active.append(mem)

        if archived_count > 0:
            self.active_memories = new_active
            self._save_json(MEMORY_ACTIVE_PATH, self.active_memories)
            self._save_json(MEMORY_ARCHIVE_PATH, self.archive_memories)
            print(f"🧹 [기억 클린업 완료] {archived_count}개의 유휴 기억을 Archive로 안전하게 격리했습니다.")