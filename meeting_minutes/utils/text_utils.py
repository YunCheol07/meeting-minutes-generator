"""텍스트 처리 유틸리티 함수"""
import re
from typing import List, Tuple


def clean_text(text: str) -> str:
    """텍스트 정제 - 불필요한 공백, 특수문자 제거
    
    Args:
        text: 정제할 텍스트
    
    Returns:
        str: 정제된 텍스트
    """
    # 연속된 공백을 하나로
    text = re.sub(r'\s+', ' ', text)
    
    # 줄바꿈 정규화
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    return text


def split_by_speaker(text: str) -> List[Tuple[str, str]]:
    """화자별로 발언 분리
    
    Args:
        text: 회의 대화 텍스트
    
    Returns:
        List[Tuple[str, str]]: (화자, 발언) 튜플 리스트
    """
    # 패턴: "이름:" 또는 "이름님:" 형식
    pattern = r'([가-힣a-zA-Z]+(?:님)?)\s*:\s*([^\n]+(?:\n(?![가-힣a-zA-Z]+(?:님)?\s*:)[^\n]+)*)'
    
    matches = re.findall(pattern, text)
    
    result = []
    for speaker, content in matches:
        speaker = speaker.replace('님', '').strip()
        content = clean_text(content)
        result.append((speaker, content))
    
    return result


def extract_names(text: str) -> List[str]:
    """텍스트에서 한글 이름 추출
    
    Args:
        text: 이름을 추출할 텍스트
    
    Returns:
        List[str]: 추출된 이름 리스트
    """
    # 2-4글자 한글 이름 패턴
    pattern = r'([가-힣]{2,4})(?:님|씨|대리|과장|부장|팀장|이사|사장)?'
    
    matches = re.findall(pattern, text)
    
    # 중복 제거 및 필터링
    names = list(set(matches))
    
    # 일반 단어 제외 (간단한 필터)
    excluded = ['회의', '안건', '결정', '논의', '진행', '완료', '시작', '종료']
    names = [name for name in names if name not in excluded]
    
    return names


def truncate_text(text: str, max_length: int = 1000) -> str:
    """텍스트를 지정된 길이로 자르기
    
    Args:
        text: 자를 텍스트
        max_length: 최대 길이
    
    Returns:
        str: 잘린 텍스트
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."


def count_words(text: str) -> dict:
    """텍스트 통계 계산
    
    Args:
        text: 분석할 텍스트
    
    Returns:
        dict: 문자 수, 단어 수, 줄 수 등
    """
    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(text.split('\n')),
        "paragraphs": len([p for p in text.split('\n\n') if p.strip()])
    }
