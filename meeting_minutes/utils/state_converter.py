"""State 변환 유틸리티"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
from ..core.state_schema import MeetingState


def dict_to_meeting_state(data: Dict[str, Any]) -> MeetingState:
    """딕셔너리를 MeetingState로 변환
    
    Args:
        data: 입력 딕셔너리
    
    Returns:
        MeetingState: 변환된 상태 객체
    """
    return {
        "raw_transcript": data.get("raw_transcript", ""),
        "meeting_title": data.get("meeting_title", data.get("title", "회의록")),
        "meeting_date": data.get("meeting_date", data.get("date", datetime.now().strftime("%Y-%m-%d"))),
        "processed_text": data.get("processed_text", ""),
        "summary": data.get("summary", ""),
        "participants": data.get("participants", []),
        "agenda_items": data.get("agenda_items", []),
        "discussions": data.get("discussions", []),
        "decisions": data.get("decisions", []),
        "action_items": data.get("action_items", []),
        "current_step": data.get("current_step", "initialized"),
        "errors": data.get("errors", [])
    }


def json_to_meeting_state(json_str: str) -> MeetingState:
    """JSON 문자열을 MeetingState로 변환
    
    Args:
        json_str: JSON 문자열
    
    Returns:
        MeetingState: 변환된 상태 객체
    """
    data = json.loads(json_str)
    return dict_to_meeting_state(data)


def validate_state_dict(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """State 딕셔너리 유효성 검증
    
    Args:
        data: 검증할 딕셔너리
    
    Returns:
        tuple: (유효성, 에러 메시지)
    """
    if not data.get("raw_transcript"):
        return False, "raw_transcript 필드가 비어있거나 없습니다"
    
    if len(data.get("raw_transcript", "").strip()) < 10:
        return False, "raw_transcript가 너무 짧습니다 (최소 10자)"
    
    return True, None
