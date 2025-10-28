"""데이터 검증 유틸리티"""
import re
from datetime import datetime
from typing import Optional


def validate_transcript(transcript: str) -> tuple[bool, Optional[str]]:
    """회의 대화 내용 검증
    
    Args:
        transcript: 검증할 대화 내용
    
    Returns:
        tuple[bool, Optional[str]]: (유효성, 에러 메시지)
    """
    if not transcript:
        return False, "대화 내용이 비어있습니다."
    
    if len(transcript.strip()) < 10:
        return False, "대화 내용이 너무 짧습니다 (최소 10자 이상)."
    
    if len(transcript) > 100000:
        return False, "대화 내용이 너무 깁니다 (최대 100,000자)."
    
    return True, None


def validate_date_format(date_string: str) -> tuple[bool, Optional[str]]:
    """날짜 형식 검증 (YYYY-MM-DD)
    
    Args:
        date_string: 검증할 날짜 문자열
    
    Returns:
        tuple[bool, Optional[str]]: (유효성, 에러 메시지)
    """
    if not date_string:
        return False, "날짜가 비어있습니다."
    
    # YYYY-MM-DD 형식 검증
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_string):
        return False, "날짜 형식이 올바르지 않습니다 (YYYY-MM-DD 형식 필요)."
    
    # 실제 날짜 유효성 검증
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True, None
    except ValueError:
        return False, "유효하지 않은 날짜입니다."


def validate_title(title: str) -> tuple[bool, Optional[str]]:
    """회의 제목 검증
    
    Args:
        title: 검증할 제목
    
    Returns:
        tuple[bool, Optional[str]]: (유효성, 에러 메시지)
    """
    if not title:
        return False, "제목이 비어있습니다."
    
    if len(title.strip()) < 2:
        return False, "제목이 너무 짧습니다 (최소 2자 이상)."
    
    if len(title) > 200:
        return False, "제목이 너무 깁니다 (최대 200자)."
    
    return True, None


def validate_output_path(path: str) -> tuple[bool, Optional[str]]:
    """출력 파일 경로 검증
    
    Args:
        path: 검증할 파일 경로
    
    Returns:
        tuple[bool, Optional[str]]: (유효성, 에러 메시지)
    """
    if not path:
        return False, "출력 경로가 비어있습니다."
    
    if not path.endswith('.docx'):
        return False, "출력 파일은 .docx 확장자여야 합니다."
    
    # 파일명에 사용할 수 없는 문자 검증
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in invalid_chars:
        if char in path:
            return False, f"파일명에 사용할 수 없는 문자가 포함되어 있습니다: {char}"
    
    return True, None
