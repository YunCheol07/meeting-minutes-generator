"""JSON 파일로부터 회의록 생성"""
import json
import sys
from pathlib import Path
import argparse
import requests
from datetime import datetime

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_json_file(file_path: str) -> dict:
    """JSON 파일 로드
    
    Args:
        file_path: JSON 파일 경로
    
    Returns:
        dict: JSON 데이터
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ JSON 파일 로드 성공: {file_path}")
        return data
    except FileNotFoundError:
        print(f"✗ 파일을 찾을 수 없습니다: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ JSON 파싱 오류: {e}")
        return None


def validate_json_data(data: dict) -> bool:
    """JSON 데이터 유효성 검증"""
    required_fields = ["raw_transcript"]
    
    for field in required_fields:
        if field not in data:
            print(f"✗ 필수 필드 누락: {field}")
            return False
    
    if len(data.get("raw_transcript", "").strip()) < 10:
        print("✗ raw_transcript가 너무 짧습니다 (최소 10자)")
        return False
    
    return True


def generate_via_api(json_data: dict, api_url: str = "http://127.0.0.1:8000") -> dict:
    """API를 통해 회의록 생성
    
    Args:
        json_data: 회의 데이터
        api_url: API 서버 URL
    
    Returns:
        dict: API 응답
    """
    endpoint = f"{api_url}/api/v1/generate-minutes"
    
    print(f"\n[API 요청] {endpoint}")
    print(f"회의 제목: {json_data.get('meeting_title', '회의록')}")
    print(f"회의 날짜: {json_data.get('meeting_date', 'N/A')}")
    print(f"대화 길이: {len(json_data.get('raw_transcript', ''))} 자")
    
    try:
        response = requests.post(endpoint, json=json_data, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        print("\n✓ 회의록 생성 성공!")
        return result
        
    except requests.exceptions.ConnectionError:
        print("\n✗ API 서버에 연결할 수 없습니다.")
        print("서버가 실행 중인지 확인하세요: python app.py")
        return None
    except requests.exceptions.Timeout:
        print("\n✗ 요청 시간 초과 (5분)")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP 오류: {e}")
        if response.text:
            print(f"상세: {response.text}")
        return None
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        return None


def download_file(api_url: str, filename: str, output_path: str = None):
    """생성된 파일 다운로드"""
    download_endpoint = f"{api_url}/api/v1/download/{filename}"
    
    try:
        response = requests.get(download_endpoint)
        response.raise_for_status()
        
        if output_path is None:
            output_path = filename
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ 파일 다운로드 완료: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ 파일 다운로드 실패: {e}")
        return False


def process_json_file(
    json_file: str,
    api_url: str = "http://127.0.0.1:8000",
    download: bool = False,
    output_dir: str = None
):
    """JSON 파일을 처리하여 회의록 생성
    
    Args:
        json_file: JSON 파일 경로
        api_url: API 서버 URL
        download: 파일 다운로드 여부
        output_dir: 다운로드 디렉토리
    """
    print("=" * 70)
    print("  JSON 파일 기반 회의록 생성")
    print("=" * 70)
    
    # 1. JSON 로드
    json_data = load_json_file(json_file)
    if json_data is None:
        return None
    
    # 2. 유효성 검증
    if not validate_json_data(json_data):
        return None
    
    # 3. API 호출
    result = generate_via_api(json_data, api_url)
    if result is None:
        return None
    
    # 4. 결과 출력
    print("\n" + "=" * 70)
    print("  생성 결과")
    print("=" * 70)
    print(f"성공: {result.get('success')}")
    print(f"메시지: {result.get('message')}")
    print(f"출력 파일: {result.get('output_file')}")
    
    if result.get('meeting_info'):
        info = result['meeting_info']
        print(f"\n회의 정보:")
        print(f"  - 제목: {info.get('title')}")
        print(f"  - 날짜: {info.get('date')}")
        print(f"  - 참석자: {', '.join(info.get('participants', []))}")
        print(f"  - 안건 수: {info.get('agenda_count')}")
        print(f"  - 액션 아이템 수: {info.get('action_items_count')}")
    
    # 5. 파일 다운로드 (옵션)
    if download and result.get('output_file'):
        filename = Path(result['output_file']).name
        
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            output_path = Path(output_dir) / filename
        else:
            output_path = filename
        
        print(f"\n[파일 다운로드]")
        download_file(api_url, filename, str(output_path))
    
    print("\n" + "=" * 70)
    
    return result


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="JSON 파일로부터 회의록 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 단일 파일 처리
  python scripts/process_json.py data/input/sample_meeting_1.json
  
  # 파일 다운로드 포함
  python scripts/process_json.py data/input/sample_meeting_1.json --download
  
  # 출력 디렉토리 지정
  python scripts/process_json.py data/input/sample_meeting_1.json -d -o ./downloads
  
  # API 서버 URL 지정
  python scripts/process_json.py data/input/sample_meeting_1.json --api http://localhost:8000
        """
    )
    
    parser.add_argument(
        "json_file",
        help="입력 JSON 파일 경로"
    )
    parser.add_argument(
        "--api",
        default="http://127.0.0.1:8000",
        help="API 서버 URL (기본값: http://127.0.0.1:8000)"
    )
    parser.add_argument(
        "-d", "--download",
        action="store_true",
        help="생성된 파일 다운로드"
    )
    parser.add_argument(
        "-o", "--output",
        help="다운로드 디렉토리"
    )
    
    args = parser.parse_args()
    
    # 처리 실행
    process_json_file(
        json_file=args.json_file,
        api_url=args.api,
        download=args.download,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
