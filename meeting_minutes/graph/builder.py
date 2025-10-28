"""그래프 빌더 - LangGraph 워크플로우 구성"""
from langgraph.graph import StateGraph, END
from ..core.state_schema import MeetingState
from ..nodes.preprocessing import preprocess_node
from ..nodes.summarization import summarize_node
from ..nodes.extraction import (
    extract_participants_node,
    extract_agenda_node,
    extract_discussions_node,
    extract_decisions_node,
    extract_action_items_node
)


def build_meeting_minutes_graph():
    """회의록 생성 그래프 구축
    
    7개의 노드를 순차적으로 연결한 LangGraph 워크플로우를 생성합니다.
    
    워크플로우 순서:
    1. preprocess: 텍스트 전처리
    2. extract_participants: 참석자 추출
    3. summarize: 회의 요약
    4. extract_agenda: 안건 추출
    5. extract_discussions: 논의 내용 추출
    6. extract_decisions: 결정 사항 추출
    7. extract_action_items: 액션 아이템 추출
    
    Returns:
        CompiledGraph: 컴파일된 LangGraph 객체
    """
    # StateGraph 생성
    workflow = StateGraph(MeetingState)
    
    # 노드 추가
    workflow.add_node("preprocess", preprocess_node)
    workflow.add_node("extract_participants", extract_participants_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("extract_agenda", extract_agenda_node)
    workflow.add_node("extract_discussions", extract_discussions_node)
    workflow.add_node("extract_decisions", extract_decisions_node)
    workflow.add_node("extract_action_items", extract_action_items_node)
    
    # 엣지 정의 (순차 실행)
    workflow.set_entry_point("preprocess")
    workflow.add_edge("preprocess", "extract_participants")
    workflow.add_edge("extract_participants", "summarize")
    workflow.add_edge("summarize", "extract_agenda")
    workflow.add_edge("extract_agenda", "extract_discussions")
    workflow.add_edge("extract_discussions", "extract_decisions")
    workflow.add_edge("extract_decisions", "extract_action_items")
    workflow.add_edge("extract_action_items", END)
    
    # 컴파일
    graph = workflow.compile()
    
    return graph


def visualize_graph(graph):
    """그래프 구조 시각화
    
    Jupyter 노트북에서 그래프 구조를 Mermaid 다이어그램으로 표시합니다.
    
    Args:
        graph: 컴파일된 LangGraph 객체
    """
    try:
        from IPython.display import Image, display
        display(Image(graph.get_graph().draw_mermaid_png()))
        print("그래프 구조가 표시되었습니다.")
    except ImportError:
        print("IPython이 설치되지 않아 시각화를 표시할 수 없습니다.")
    except Exception as e:
        print(f"시각화 실패: {e}")
