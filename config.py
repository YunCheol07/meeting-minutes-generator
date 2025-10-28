"""설정 파일"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 앱 설정
    APP_NAME: str = "회의록 자동 생성 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API 설정
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # 파일 경로
    OUTPUT_DIR: Path = Path("./output")
    SAMPLE_DATA_DIR: Path = Path("./data/samples")
    
    # LLM 설정
    LLM_MODEL: str = "exaone-2.4b"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_LENGTH: int = 2048
    
    # 기본 회의 정보
    DEFAULT_MEETING_TITLE: str = "회의록"
    USE_SAMPLE_ON_ERROR: bool = True  # 에러 시 샘플 데이터 사용
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()

# 출력 디렉토리 생성
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
