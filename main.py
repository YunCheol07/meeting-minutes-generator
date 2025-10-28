"""메인 실행 파일 - CLI 및 샘플 데이터 폴백"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meeting_minutes.core.state_schema import create_initial_state, validate_state, MeetingState
from meeting_minutes.graph.builder import build_meeting_minutes_graph
from meeting_minutes.output.document_generator import MeetingMinutesDocGenerator
from meeting_minutes.core.llm_config import llm_config
from config import settings


# 샘플 회의 데이터
SAMPLE_TRANSCRIPT = """
김대리: 안녕하세요, 오늘 신규 프로젝트 킥오프 미팅을 시작하겠습니다.
참석자는 저와 이과장님, 박부장님이십니다.

이과장: 네, 프로젝트명은 'AI 회의록 자동화 시스템'으로 확정되었습니다.
목표는 회의 내용을 자동으로 정리하고 액션 아이템을 추출하는 것입니다.

박부장: 좋습니다. 개발 일정은 어떻게 되나요?

김대리: 1단계로 11월 30일까지 프로토타입 개발을 완료하고,
12월에 베타 테스트를 진행할 예정입니다.

이과장: 기술 스택은 Python, LangGraph, EXAONE을 사용하기로 했습니다.

박부장: 알겠습니다. 그럼 김대리님은 프로토타입 개발을 담당하고,
이과장님은 테스트 시나리오 작성을 11월 15일까지 완료해주세요.
예산은 500만원으로 승인하겠습니다.

김대리: 네, 알겠습니다. 11월 30일까지 완료하겠습니다.

이과장: 확인했습니다. 11월 15일까지 테스트 시나리오를 제출하겠습니다.

박부장: 좋습니다. 다음 주 화요일 오후 3시에 진행 상황 점검 회의를 하겠습니다.
모두 수고하셨습니다.
"""


def generate_meeting_minutes_from_state(
    state: MeetingState,
    output_path: str = "회의록.docx"
) -> dict:
    """State 객체로 회의록 생성"""
    print("=" * 70)
    print("  회의록 자동 생성 시스템")
    print("=" * 70)
    
    # 상태 검증
    if not validate_state(state):
        print("\n⚠ 경고: State가 유효하지 않습니다")
        if settings.USE_SAMPLE_ON_ERROR:
            print("✓ 샘플 데이터를 사용합니다")
            state = create_initial_state(
                transcript=SAMPLE_TRANSCRIPT,
                title="프로젝트 킥오프 회의 (샘플)",
                date="2025-10-28"
            )
        else:
            return None
    
    print(f"\n✓ 회의 제목: {state['meeting_title']}")
    print(f"✓ 회의 날짜: {state['meeting_date']}")
    print(f"✓ 대화 길이: {len(state['raw_transcript'])} 자")
    
    # LLM 연결
    print("\n[초기화] LLM 모델 연결 중...")
    try:
        if not llm_config.test_connection():
            raise Exception("LLM 연결 실패")
    except Exception as e:
        print(f"✗ LLM 로드 실패: {e}")
        if settings.USE_SAMPLE_ON_ERROR:
            print("⚠ 샘플 모드로 계속 진행합니다 (실제 생성 불가)")
            return None
        raise
    
    # 그래프 실행
    print("\n[처리 시작] 회의록 생성 파이프라인 실행...")
    print("-" * 70)
    
    try:
        graph = build_meeting_minutes_graph()
        final_state = graph.invoke(state)
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    print("-" * 70)
    
    # 문서 생성
    try:
        doc_generator = MeetingMinutesDocGenerator()
        output_file = doc_generator.generate(final_state, output_path)
    except Exception as e:
        print(f"\n오류: 문서 생성 실패: {e}")
        return None
    
    # 결과
    print("\n" + "=" * 70)
    print("  회의록 생성 완료!")
    print("=" * 70)
    print(f"\n📄 출력 파일: {output_file}")
    print(f"\n📊 생성 결과:")
    print(f"  - 참석자: {len(final_state['participants'])}명")
    print(f"  - 안건: {len(final_state['agenda_items'])}개")
    print(f"  - 논의 내용: {len(final_state['discussions'])}개")
    print(f"  - 결정 사항: {len(final_state['decisions'])}개")
    print(f"  - 액션 아이템: {len(final_state['action_items'])}개")
    
    if final_state.get("errors"):
        print(f"\n⚠ 발생한 오류 ({len(final_state['errors'])}개):")
        for error in final_state["errors"]:
            print(f"  - {error}")
    
    print("\n" + "=" * 70)
    
    return final_state


def generate_meeting_minutes(
    transcript: str = None,
    meeting_title: str = "회의록",
    meeting_date: str = None,
    output_path: str = "회의록.docx"
) -> dict:
    """텍스트로 회의록 생성 (샘플 데이터 폴백 포함)"""
    
    # transcript가 없으면 샘플 사용
    if not transcript or len(transcript.strip()) < 10:
        print("\n⚠ 입력 데이터가 없거나 너무 짧습니다")
        if settings.USE_SAMPLE_ON_ERROR:
            print("✓ 샘플 데이터를 사용합니다\n")
            transcript = SAMPLE_TRANSCRIPT
            meeting_title = "프로젝트 킥오프 회의 (샘플)"
        else:
            print("✗ USE_SAMPLE_ON_ERROR가 비활성화되어 있습니다")
            return None
    
    # State 생성
    initial_state = create_initial_state(
        transcript=transcript,
        title=meeting_title,
        date=meeting_date
    )
    
    return generate_meeting_minutes_from_state(initial_state, output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="회의록 자동 생성")
    parser.add_argument("--input", "-i", help="입력 텍스트 파일 경로")
    parser.add_argument("--output", "-o", default="회의록.docx", help="출력 파일 경로")
    parser.add_argument("--title", "-t", default="회의록", help="회의 제목")
    parser.add_argument("--date", "-d", help="회의 날짜 (YYYY-MM-DD)")
    parser.add_argument("--sample", "-s", action="store_true", help="샘플 데이터 사용")
    
    args = parser.parse_args()
    
    # 입력 데이터 결정
    transcript = None
    
    if args.sample:
        # 샘플 데이터 강제 사용
        transcript = SAMPLE_TRANSCRIPT
        args.title = "프로젝트 킥오프 회의 (샘플)"
    elif args.input:
        # 파일에서 읽기
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                transcript = f.read()
        except Exception as e:
            print(f"파일 읽기 실패: {e}")
            transcript = None
    
    # 회의록 생성
    generate_meeting_minutes(
        transcript=transcript,
        meeting_title=args.title,
        meeting_date=args.date,
        output_path=args.output
    )
