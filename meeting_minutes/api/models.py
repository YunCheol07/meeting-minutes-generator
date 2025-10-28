"""API 요청/응답 모델"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class MeetingStateInput(BaseModel):
    """회의록 생성 요청 모델"""
    raw_transcript: str = Field(
        ...,
        description="원본 회의 대화 내용",
        min_length=10
    )
    meeting_title: str = Field(
        default="회의록",
        description="회의 제목"
    )
    meeting_date: Optional[str] = Field(
        default=None,
        description="회의 날짜 (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    
    # 선택적 필드 (보통 비어있음)
    processed_text: str = ""
    summary: str = ""
    participants: List[str] = []
    agenda_items: List[str] = []
    discussions: List[Dict[str, str]] = []
    decisions: List[str] = []
    action_items: List[Dict[str, str]] = []
    current_step: str = "initialized"
    errors: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "raw_transcript": "김대리: 안녕하세요, 오늘 프로젝트 회의를 시작하겠습니다.\n이과장: 네, 진행 상황을 보고드리겠습니다.",
                "meeting_title": "프로젝트 진행 회의",
                "meeting_date": "2025-10-28"
            }
        }


class SimpleMeetingInput(BaseModel):
    """간단한 회의록 생성 요청"""
    transcript: str = Field(
        ...,
        description="회의 대화 내용",
        min_length=10
    )
    title: str = Field(
        default="회의록",
        description="회의 제목"
    )
    date: Optional[str] = Field(
        default=None,
        description="회의 날짜"
    )


class MeetingMinutesResponse(BaseModel):
    """회의록 생성 응답"""
    success: bool
    message: str
    output_file: Optional[str] = None
    meeting_info: Optional[Dict] = None
    errors: List[str] = []


class HealthResponse(BaseModel):
    """헬스 체크 응답"""
    status: str
    app_name: str
    version: str
    model_loaded: bool
    timestamp: str
