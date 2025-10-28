"""정보 추출 노드들 - 구조화된 정보 추출"""
from ..core.state_schema import MeetingState
from ..core.llm_config import llm_config
from ..core.prompt_templates import PromptTemplates
import json


def extract_participants_node(state: MeetingState) -> dict:
    """참석자 추출 노드"""
    print("\n[Step 3/7] 참석자 추출 중...")
    
    try:
        prompt = PromptTemplates.get_participant_extraction_prompt().format(
            text=state["processed_text"]
        )
        
        # HuggingFace 모델로 생성
        response = llm_config.generate(prompt)
        
        # 쉼표로 분리하여 리스트로 변환
        participants = [p.strip() for p in response.split(",") if p.strip()]
        
        if not participants:
            participants = ["참석자 미상"]
        
        print(f"✓ 참석자 추출 완료: {', '.join(participants)}")
        
        return {
            "participants": participants,
            "current_step": "participants_extracted"
        }
    
    except Exception as e:
        print(f"✗ 참석자 추출 오류: {str(e)}")
        return {
            "participants": ["참석자 미상"],
            "errors": [f"참석자 추출 오류: {str(e)}"],
            "current_step": "participants_extracted"
        }


def extract_agenda_node(state: MeetingState) -> dict:
    """안건 추출 노드"""
    print("\n[Step 4/7] 안건 추출 중...")
    
    try:
        prompt = PromptTemplates.get_agenda_extraction_prompt().format(
            text=state["processed_text"]
        )
        
        response = llm_config.generate(prompt)
        
        agenda_items = [
            item.strip()
            for item in response.split("\n")
            if item.strip() and not item.strip().startswith(("안건", "형식", "예시"))
        ]
        
        if not agenda_items:
            agenda_items = ["안건 내용 없음"]
        
        print(f"✓ 안건 추출 완료: {len(agenda_items)}개 안건")
        for idx, agenda in enumerate(agenda_items, 1):
            print(f"  {idx}. {agenda}")
        
        return {
            "agenda_items": agenda_items,
            "current_step": "agenda_extracted"
        }
    
    except Exception as e:
        print(f"✗ 안건 추출 오류: {str(e)}")
        return {
            "agenda_items": ["안건 추출 실패"],
            "errors": [f"안건 추출 오류: {str(e)}"],
            "current_step": "agenda_extracted"
        }


def extract_discussions_node(state: MeetingState) -> dict:
    """논의 내용 추출 노드"""
    print("\n[Step 5/7] 논의 내용 추출 중...")
    
    try:
        prompt = PromptTemplates.get_discussion_extraction_prompt().format(
            text=state["processed_text"]
        )
        
        response = llm_config.generate(prompt)
        discussions = []
        
        for line in response.split("\n"):
            line = line.strip()
            if line and line.startswith("{"):
                try:
                    disc = json.loads(line)
                    if "topic" in disc and "content" in disc:
                        discussions.append({
                            "topic": disc["topic"],
                            "content": disc["content"]
                        })
                except json.JSONDecodeError:
                    continue
        
        if not discussions:
            discussions = [{
                "topic": "일반 논의",
                "content": state.get("summary", "논의 내용 추출 실패")
            }]
        
        print(f"✓ 논의 내용 추출 완료: {len(discussions)}개 논의")
        for idx, disc in enumerate(discussions, 1):
            print(f"  {idx}. {disc['topic']}")
        
        return {
            "discussions": discussions,
            "current_step": "discussions_extracted"
        }
    
    except Exception as e:
        print(f"✗ 논의 내용 추출 오류: {str(e)}")
        return {
            "discussions": [{"topic": "논의 내용", "content": "추출 실패"}],
            "errors": [f"논의 내용 추출 오류: {str(e)}"],
            "current_step": "discussions_extracted"
        }


def extract_decisions_node(state: MeetingState) -> dict:
    """결정 사항 추출 노드"""
    print("\n[Step 6/7] 결정 사항 추출 중...")
    
    try:
        prompt = PromptTemplates.get_decision_extraction_prompt().format(
            text=state["processed_text"]
        )
        
        response = llm_config.generate(prompt)
        
        decisions = [
            dec.strip()
            for dec in response.split("\n")
            if dec.strip() and not dec.strip().startswith(("결정", "지침", "예시"))
        ]
        
        if not decisions:
            decisions = ["특별한 결정 사항 없음"]
        
        print(f"✓ 결정 사항 추출 완료: {len(decisions)}개 결정")
        for idx, decision in enumerate(decisions, 1):
            print(f"  {idx}. {decision}")
        
        return {
            "decisions": decisions,
            "current_step": "decisions_extracted"
        }
    
    except Exception as e:
        print(f"✗ 결정 사항 추출 오류: {str(e)}")
        return {
            "decisions": ["결정 사항 추출 실패"],
            "errors": [f"결정 사항 추출 오류: {str(e)}"],
            "current_step": "decisions_extracted"
        }


def extract_action_items_node(state: MeetingState) -> dict:
    """액션 아이템 추출 노드"""
    print("\n[Step 7/7] 액션 아이템 추출 중...")
    
    try:
        prompt = PromptTemplates.get_action_item_extraction_prompt().format(
            text=state["processed_text"]
        )
        
        response = llm_config.generate(prompt)
        action_items = []
        
        for line in response.split("\n"):
            line = line.strip()
            if line and line.startswith("{"):
                try:
                    action = json.loads(line)
                    if "task" in action:
                        action_items.append({
                            "task": action.get("task", ""),
                            "assignee": action.get("assignee", "미지정"),
                            "deadline": action.get("deadline", "미정")
                        })
                except json.JSONDecodeError:
                    continue
        
        if not action_items:
            action_items = [{
                "task": "후속 조치 없음",
                "assignee": "-",
                "deadline": "-"
            }]
        
        print(f"✓ 액션 아이템 추출 완료: {len(action_items)}개 과제")
        for idx, item in enumerate(action_items, 1):
            print(f"  {idx}. {item['task']} (담당: {item['assignee']}, 마감: {item['deadline']})")
        
        return {
            "action_items": action_items,
            "current_step": "action_items_extracted"
        }
    
    except Exception as e:
        print(f"✗ 액션 아이템 추출 오류: {str(e)}")
        return {
            "action_items": [{
                "task": "추출 실패",
                "assignee": "-",
                "deadline": "-"
            }],
            "errors": [f"액션 아이템 추출 오류: {str(e)}"],
            "current_step": "action_items_extracted"
        }
