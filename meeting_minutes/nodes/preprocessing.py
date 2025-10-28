"""전처리 노드 - 원본 텍스트 정제 및 구조화"""
from ..core.state_schema import MeetingState
from ..core.llm_config import llm_config
from ..core.prompt_templates import PromptTemplates


def preprocess_node(state: MeetingState) -> dict:
    """텍스트 전처리 노드
    
    원본 회의 대화 내용을 정제하고 구조화합니다.
    
    Args:
        state: 현재 상태 (raw_transcript 필요)
    
    Returns:
        dict: 업데이트할 상태 (processed_text, current_step)
    """
    print("\n[Step 1/7] 텍스트 전처리 중...")
    
    try:
        # 프롬프트 생성
        prompt = PromptTemplates.get_preprocessing_prompt().format(
            transcript=state["raw_transcript"]
        )
        
        # HuggingFace 모델로 생성
        processed_text = llm_config.generate(prompt)
        
        print(f"✓ 전처리 완료 (처리된 텍스트 길이: {len(processed_text)} 자)")
        
        return {
            "processed_text": processed_text.strip(),
            "current_step": "preprocessed"
        }
    
    except Exception as e:
        print(f"✗ 전처리 오류 발생: {str(e)}")
        # 오류 시 원본 텍스트 사용
        return {
            "processed_text": state["raw_transcript"],
            "errors": [f"전처리 오류: {str(e)}"],
            "current_step": "preprocessed"
        }
