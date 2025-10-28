"""API 의존성"""
from fastapi import HTTPException
from ..core.llm_config import llm_config


async def verify_llm_loaded():
    """LLM 모델이 로드되었는지 확인"""
    if not llm_config._is_loaded:
        try:
            llm_config.load_model()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"LLM 모델 로드 실패: {str(e)}"
            )
