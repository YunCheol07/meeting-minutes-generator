"""상태 정의 모듈 - 회의록 생성을 위한 상태 스키마"""
from typing import TypedDict, List, Annotated
from typing_extensions import TypedDict as TypedDictExtension
import operator
from datetime import datetime


class MeetingState(TypedDict):
    """회의록 생성을 위한 상태 스키마
    
    LangGraph에서 사용되는 TypedDict 기반 상태 정의.
    각 노드가 이 상태를 읽고 업데이트합니다.
    """
    # 입력 데이터
    raw_transcript: str  # 원본 회의 대화 내용
    meeting_title: str  # 회의 제목
    meeting_date: str  # 회의 날짜 (YYYY-MM-DD)
    
    # 중간 처리 데이터
    processed_text: str  # 전처리된 텍스트
    summary: str  # 회의 요약
    
    # 추출된 정보 (Annotated로 리스트 누적 지원)
    participants: List[str]  # 참석자 목록
    agenda_items: Annotated[List[str], operator.add]  # 안건 항목들
    discussions: Annotated[List[dict], operator.add]  # 논의 내용 (topic, content)
    decisions: Annotated[List[str], operator.add]  # 결정 사항
    action_items: Annotated[List[dict], operator.add]  # 액션 아이템 (task, assignee, deadline)
    
    # 메타데이터
    current_step: str  # 현재 처리 단계
    errors: Annotated[List[str], operator.add]  # 에러 로그


def create_initial_state(
    transcript: str,
    title: str = "회의록",
    date: str = None
) -> MeetingState:
    """초기 상태 객체 생성
    
    Args:
        transcript: 원본 회의 대화 내용
        title: 회의 제목 (기본값: "회의록")
        date: 회의 날짜 (기본값: 오늘 날짜)
    
    Returns:
        MeetingState: 초기화된 상태 객체
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        # 입력 데이터
        "raw_transcript": transcript,
        "meeting_title": title,
        "meeting_date": date,
        
        # 중간 처리 데이터
        "processed_text": "",
        "summary": "",
        
        # 추출된 정보 (빈 리스트로 초기화)
        "participants": [],
        "agenda_items": [],
        "discussions": [],
        "decisions": [],
        "action_items": [],
        
        # 메타데이터
        "current_step": "initialized",
        "errors": []
    }


def validate_state(state: MeetingState) -> bool:
    """상태 유효성 검증
    
    Args:
        state: 검증할 상태 객체
    
    Returns:
        bool: 유효성 검증 결과
    """
    required_fields = ["raw_transcript", "meeting_title", "meeting_date"]
    
    for field in required_fields:
        if not state.get(field):
            print(f"경고: 필수 필드 '{field}'가 비어있습니다.")
            return False
    
    return True
