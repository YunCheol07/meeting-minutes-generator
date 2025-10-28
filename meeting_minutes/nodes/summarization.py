"""요약 노드 - 회의 내용 요약"""
from ..core.state_schema import MeetingState
from ..core.llm_config import llm_config
from ..core.prompt_templates import PromptTemplates


def summarize_node(state: MeetingState) -> dict:
    """회의 내용 요약 노드
    
    전처리된 회의 내용을 3-5문장으로 요약합니다.
    
    Args:
        state: 현재 상태 (processed_text 필요)
    
    Returns:
        dict: 업데이트할 상태 (summary, current_step)
    """
    print("\n[Step 2/7] 회의 내용 요약 중...")
    
    try:
        # 프롬프트 생성
        prompt = PromptTemplates.get_summary_prompt().format(
            text=state["processed_text"]
        )
        
        # HuggingFace 모델로 생성
        summary = llm_config.generate(prompt)
        
        print(f"✓ 요약 완료 (요약 길이: {len(summary)} 자)")
        
        return {
            "summary": summary.strip(),
            "current_step": "summarized"
        }
    
    except Exception as e:
        print(f"✗ 요약 오류 발생: {str(e)}")
        return {
            "summary": "요약 생성 실패",
            "errors": [f"요약 오류: {str(e)}"],
            "current_step": "summarized"
        }
