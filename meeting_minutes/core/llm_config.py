"""LLM 설정 모듈 - EXAONE 3.5 2.4B (경량 로컬 모델)"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional
import warnings

warnings.filterwarnings("ignore")


class LightweightLLMConfig:
    """경량 HuggingFace LLM 설정 (노트북 최적화)"""
    
    # 추천 경량 모델 목록
    RECOMMENDED_MODELS = {
        "exaone-2.4b": "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct",  # 가장 추천
        "qwen-1.5b": "Qwen/Qwen2.5-1.5B-Instruct",
        "qwen-3b": "Qwen/Qwen2.5-3B-Instruct",
    }
    
    def __init__(
        self,
        model_name: str = "exaone-2.4b",
        device: str = "auto",
        max_length: int = 2048,
        temperature: float = 0.2,
        load_in_8bit: bool = False
    ):
        """경량 모델 설정 초기화
        
        Args:
            model_name: 모델 이름 (exaone-2.4b 권장)
            device: 디바이스 ("auto", "cpu", "cuda")
            max_length: 최대 생성 길이
            temperature: 생성 온도
            load_in_8bit: 8bit 양자화 사용 (메모리 절약)
        """
        # 모델 ID
        if model_name in self.RECOMMENDED_MODELS:
            self.model_id = self.RECOMMENDED_MODELS[model_name]
            self.model_name = model_name
        else:
            self.model_id = model_name
            self.model_name = model_name.split("/")[-1]
        
        self.device = device
        self.max_length = max_length
        self.temperature = temperature
        self.load_in_8bit = load_in_8bit
        
        self._model = None
        self._tokenizer = None
        self._is_loaded = False
    
    def load_model(self):
        """모델 로드 (자동 최적화)"""
        if self._is_loaded:
            print(f"✓ 모델이 이미 로드되어 있습니다: {self.model_name}")
            return
        
        print(f"\n[모델 로드] {self.model_id}")
        print("노트북 최적화 중... (1-3분 소요)")
        
        try:
            # 디바이스 설정
            if torch.cuda.is_available():
                device_map = "cuda"
                torch_dtype = torch.float16
                print("✓ GPU 사용 가능 - GPU에서 실행")
            else:
                device_map = "cpu"
                torch_dtype = torch.float32
                print("✓ CPU에서 실행 (GPU보다 느림)")
            
            # 토크나이저 로드
            print("  [1/2] 토크나이저 로드 중...")
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                trust_remote_code=True
            )
            
            # 모델 로드 (메모리 최적화)
            print("  [2/2] 모델 로드 중...")
            load_kwargs = {
                "pretrained_model_name_or_path": self.model_id,
                "torch_dtype": torch_dtype,
                "trust_remote_code": True,
                "low_cpu_mem_usage": True
            }
            
            # 8bit 양자화 옵션
            if self.load_in_8bit and torch.cuda.is_available():
                load_kwargs["load_in_8bit"] = True
                load_kwargs["device_map"] = "auto"
                print("  - 8bit 양자화 활성화 (메모리 절약)")
            else:
                load_kwargs["device_map"] = device_map
            
            self._model = AutoModelForCausalLM.from_pretrained(**load_kwargs)
            
            self._is_loaded = True
            print(f"✓ 모델 로드 완료: {self.model_name}")
            print(f"  - 파라미터: 2.4B")
            print(f"  - 디바이스: {device_map}")
            
        except Exception as e:
            print(f"✗ 모델 로드 실패: {e}")
            print("\n해결 방법:")
            print("  1. 인터넷 연결 확인")
            print("  2. 메모리 부족 시: load_in_8bit=True 설정")
            print("  3. 재부팅 후 재시도")
            raise
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """텍스트 생성
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
        
        Returns:
            str: 생성된 텍스트
        """
        if not self._is_loaded:
            self.load_model()
        
        # 메시지 구성
        if system_prompt:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        else:
            messages = [
                {"role": "system", "content": "당신은 한국어 문서 처리 전문 AI입니다."},
                {"role": "user", "content": prompt}
            ]
        
        # 토큰화
        try:
            input_ids = self._tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(self._model.device)
        except:
            # apply_chat_template 미지원 시 대체 방법
            text = f"{system_prompt or ''}\n\n{prompt}"
            input_ids = self._tokenizer(
                text,
                return_tensors="pt"
            ).input_ids.to(self._model.device)
        
        # 생성
        with torch.no_grad():
            output = self._model.generate(
                input_ids,
                max_new_tokens=self.max_length,
                temperature=self.temperature,
                do_sample=True,
                top_p=0.9,
                eos_token_id=self._tokenizer.eos_token_id,
                pad_token_id=self._tokenizer.pad_token_id or self._tokenizer.eos_token_id,
                use_cache=True
            )
        
        # 디코딩
        generated_text = self._tokenizer.decode(
            output[0][input_ids.shape[-1]:],
            skip_special_tokens=True
        )
        
        return generated_text.strip()
    
    def test_connection(self) -> bool:
        """모델 테스트"""
        try:
            if not self._is_loaded:
                self.load_model()
            
            print("\n[테스트] 모델 응답 확인 중...")
            test_result = self.generate("안녕하세요. 간단히 인사해주세요.")
            
            if test_result and len(test_result) > 0:
                print(f"✓ 모델 테스트 성공")
                print(f"  응답 예시: {test_result[:50]}...")
                return True
            else:
                print(f"✗ 모델 응답이 비어있습니다")
                return False
                
        except Exception as e:
            print(f"✗ 모델 테스트 실패: {e}")
            return False
    
    def get_model_info(self) -> dict:
        """모델 정보"""
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "device": "GPU" if torch.cuda.is_available() else "CPU",
            "is_loaded": self._is_loaded,
            "max_length": self.max_length,
            "temperature": self.temperature,
            "cuda_available": torch.cuda.is_available(),
            "parameters": "2.4B"
        }


# 전역 설정 (노트북 최적화)
llm_config = LightweightLLMConfig(
    model_name="exaone-2.4b",  # EXAONE 2.4B 사용
    device="auto",
    max_length=2048,
    temperature=0.2,
    load_in_8bit=False  # 메모리 부족 시 True로 변경
)
