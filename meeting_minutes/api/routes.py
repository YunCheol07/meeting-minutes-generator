"""API 라우트"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from datetime import datetime
from pathlib import Path
import logging

from .models import (
    MeetingStateInput,
    SimpleMeetingInput,
    MeetingMinutesResponse,
    HealthResponse
)
from ..utils.state_converter import dict_to_meeting_state, validate_state_dict
from ..core.state_schema import MeetingState
from ..graph.builder import build_meeting_minutes_graph
from ..output.document_generator import MeetingMinutesDocGenerator
from ..core.llm_config import llm_config
from config import settings

# 로거 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()


def generate_from_state(state: MeetingState) -> tuple[dict, str]:
    """State로부터 회의록 생성
    
    Returns:
        tuple: (최종 상태, 출력 파일 경로)
    """
    # 그래프 실행
    graph = build_meeting_minutes_graph()
    final_state = graph.invoke(state)
    
    # 문서 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"회의록_{timestamp}.docx"
    output_path = settings.OUTPUT_DIR / output_filename
    
    doc_generator = MeetingMinutesDocGenerator()
    doc_generator.generate(final_state, str(output_path))
    
    return final_state, str(output_path)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스 체크"""
    try:
        model_loaded = llm_config._is_loaded
        return HealthResponse(
            status="healthy",
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            model_loaded=model_loaded,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-minutes", response_model=MeetingMinutesResponse)
async def generate_minutes_full(state_input: MeetingStateInput):
    """완전한 State 객체로 회의록 생성
    
    Request Body:
    {
        "raw_transcript": "회의 내용...",
        "meeting_title": "프로젝트 회의",
        "meeting_date": "2025-10-28"
    }
    """
    try:
        logger.info(f"회의록 생성 요청: {state_input.meeting_title}")
        
        # State로 변환
        state_dict = state_input.model_dump()
        
        # 유효성 검증
        is_valid, error_msg = validate_state_dict(state_dict)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 날짜 기본값 설정
        if not state_dict.get("meeting_date"):
            state_dict["meeting_date"] = datetime.now().strftime("%Y-%m-%d")
        
        meeting_state = dict_to_meeting_state(state_dict)
        
        # 회의록 생성
        final_state, output_path = generate_from_state(meeting_state)
        
        logger.info(f"회의록 생성 완료: {output_path}")
        
        return MeetingMinutesResponse(
            success=True,
            message="회의록이 성공적으로 생성되었습니다",
            output_file=output_path,
            meeting_info={
                "title": final_state["meeting_title"],
                "date": final_state["meeting_date"],
                "participants": final_state["participants"],
                "agenda_count": len(final_state["agenda_items"]),
                "action_items_count": len(final_state["action_items"])
            },
            errors=final_state.get("errors", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회의록 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"회의록 생성 실패: {str(e)}")


@router.post("/generate-minutes/simple", response_model=MeetingMinutesResponse)
async def generate_minutes_simple(input_data: SimpleMeetingInput):
    """간단한 텍스트 입력으로 회의록 생성
    
    Request Body:
    {
        "transcript": "회의 내용...",
        "title": "프로젝트 회의",
        "date": "2025-10-28"
    }
    """
    # SimpleMeetingInput을 MeetingStateInput으로 변환
    state_input = MeetingStateInput(
        raw_transcript=input_data.transcript,
        meeting_title=input_data.title,
        meeting_date=input_data.date
    )
    
    return await generate_minutes_full(state_input)


@router.get("/download/{filename}")
async def download_file(filename: str):
    """생성된 회의록 다운로드"""
    file_path = settings.OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.post("/generate-minutes/with-file")
async def generate_minutes_with_download(state_input: MeetingStateInput):
    """회의록 생성 후 파일 직접 반환"""
    try:
        # State로 변환
        state_dict = state_input.model_dump()
        if not state_dict.get("meeting_date"):
            state_dict["meeting_date"] = datetime.now().strftime("%Y-%m-%d")
        
        meeting_state = dict_to_meeting_state(state_dict)
        
        # 회의록 생성
        final_state, output_path = generate_from_state(meeting_state)
        
        # 파일 직접 반환
        return FileResponse(
            path=output_path,
            filename=Path(output_path).name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
