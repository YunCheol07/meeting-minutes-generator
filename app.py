"""FastAPI 애플리케이션 - 메인 서버"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from meeting_minutes.api.routes import router
from meeting_minutes.core.llm_config import llm_config
from config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행"""
    # 시작 시
    logger.info("=" * 70)
    logger.info(f"  {settings.APP_NAME} v{settings.APP_VERSION} 시작")
    logger.info("=" * 70)
    
    # LLM 모델 사전 로드 (선택사항)
    try:
        logger.info("LLM 모델 로드 중...")
        llm_config.load_model()
        logger.info("✓ LLM 모델 로드 완료")
    except Exception as e:
        logger.warning(f"⚠ LLM 사전 로드 실패 (첫 요청 시 로드됨): {e}")
    
    yield
    
    # 종료 시
    logger.info("서버 종료 중...")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    description="한국어 회의록 자동 생성 API (EXAONE 2.4B 기반)",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router, prefix=settings.API_PREFIX, tags=["회의록 생성"])


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

# uvicorn app:app --reload --host 127.0.0.1 --port 8000