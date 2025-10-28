"""JSON 파일 처리 통합 테스트"""
import sys
from pathlib import Path
import time
import requests

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.process_json import process_json_file


def check_api_server(api_url: str = "http://127.0.0.1:8000") -> bool:
    """API 서버 상태 확인"""
    try:
        response = requests.get(f"{api_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✓ API 서버 실행 중")
            return True
        return False
    except:
        print("✗ API 서버가 실행되지 않았습니다")
        print("다음 명령으로 서버를 시작하세요: python app.py")
        return False


def test_single_file():
    """단일 JSON 파일 테스트"""
    print("\n" + "="*70)
    print("  테스트 1: 단일 JSON 파일 처리")
    print("="*70)
    
    json_file = "data/input/sample_meeting_1.json"
    
    if not Path(json_file).exists():
        print(f"✗ 파일 없음: {json_file}")
        return False
    
    result = process_json_file(
        json_file=json_file,
        download=True,
        output_dir="./test_output"
    )
    
    return result is not None


def test_multiple_files():
    """여러 JSON 파일 일괄 처리"""
    print("\n" + "="*70)
    print("  테스트 2: 여러 JSON 파일 일괄 처리")
    print("="*70)
    
    input_dir = Path("data/input")
    json_files = list(input_dir.glob("*.json"))
    
    if not json_files:
        print(f"✗ JSON 파일 없음: {input_dir}")
        return False
    
    print(f"\n발견된 파일: {len(json_files)}개")
    
    results = []
    for idx, json_file in enumerate(json_files, 1):
        print(f"\n[{idx}/{len(json_files)}] 처리 중: {json_file.name}")
        print("-" * 70)
        
        result = process_json_file(
            json_file=str(json_file),
            download=True,
            output_dir="./test_output"
        )
        
        results.append({
            "file": json_file.name,
            "success": result is not None
        })
        
        # 과부하 방지
        if idx < len(json_files):
            print("\n대기 중 (3초)...")
            time.sleep(3)
    
    # 결과 요약
    print("\n" + "="*70)
    print("  처리 결과 요약")
    print("="*70)
    
    for result in results:
        status = "✓ 성공" if result['success'] else "✗ 실패"
        print(f"{status}: {result['file']}")
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\n총 {len(results)}개 파일 중 {success_count}개 성공")
    
    return success_count > 0


def test_direct_api_call():
    """API 직접 호출 테스트"""
    print("\n" + "="*70)
    print("  테스트 3: API 직접 호출")
    print("="*70)
    
    test_data = {
        "raw_transcript": "김대리: 테스트 회의입니다.\n이과장: 네, 확인했습니다.",
        "meeting_title": "API 테스트 회의",
        "meeting_date": "2025-10-28"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/generate-minutes",
            json=test_data,
            timeout=300
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✓ API 호출 성공")
        print(f"출력 파일: {result.get('output_file')}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ API 호출 실패: {e}")
        return False


def main():
    """전체 테스트 실행"""
    print("="*70)
    print("  JSON 파일 처리 통합 테스트")
    print("="*70)
    
    # API 서버 확인
    if not check_api_server():
        return
    
    # 테스트 실행
    tests = [
        ("단일 파일 처리", test_single_file),
        ("여러 파일 일괄 처리", test_multiple_files),
        ("API 직접 호출", test_direct_api_call)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ 테스트 오류: {e}")
            results.append((test_name, False))
    
    # 최종 결과
    print("\n" + "="*70)
    print("  최종 테스트 결과")
    print("="*70)
    
    for test_name, success in results:
        status = "✓ 성공" if success else "✗ 실패"
        print(f"{status}: {test_name}")
    
    success_count = sum(1 for _, s in results if s)
    print(f"\n총 {len(results)}개 테스트 중 {success_count}개 성공")


if __name__ == "__main__":
    main()
