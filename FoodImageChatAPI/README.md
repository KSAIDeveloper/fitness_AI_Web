# Food Image Classification (Chat + Local)

FastAPI 기반 음식 이미지 분류 데모. Chat 비전 모델(통합 `gpt-4o-mini` 등) 또는 로컬 MobileNetV2(일반 ImageNet) 추론 후 한국어 JSON 결과와 칼로리 추정치를 제공합니다.

## Features

- 이미지 업로드 후 두 모드 제공: `chat` / `local`
- Chat 모드: OpenAI Responses API 사용, JSON 스키마 `{label, confidence, calories_kcal, serving, notes}`
- 로컬 모드: Torch MobileNetV2 top-3 (음식 특화 아님, 데모 용)
- 한국어 후처리 문구 생성 (`app.py`)
- .env 파일 로드 및 API 키 형식 검증 (placeholder 차단)

## Requirements

Python 3.10+ 권장

## 설치

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 환경변수 설정 (.env 권장)

`.env.example` 복사하여 `.env` 생성:

```
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CHAT_MODEL=gpt-4o-mini
```

임시 세션 설정:

```powershell
$env:OPENAI_API_KEY="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
$env:CHAT_MODEL="gpt-4o-mini"
```

주의: `YOUR_KEY` 같은 placeholder 사용 금지. 형식 검사로 차단됩니다.

## 실행

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8000
```

브라우저에서: http://localhost:8000

## 문제 해결

1. 에러: "유효하지 않은 API 키" → 실제 OpenAI 대시보드에서 키 재발급 후 설정.
2. 에러: deprecated vision preview → `CHAT_MODEL`을 `gpt-4o-mini` 와 같이 `-vision` 없는 이름으로 변경.
3. SDK 경로 오류 → `pip install --upgrade openai` (>=1.0.0) 확인:

```powershell
.\.venv\Scripts\python.exe -c "import openai; print(openai.__version__)"
```

4. 로컬 모드 결과 품질 낮음 → Food-101 파인튜닝 모델 교체 고려.

## 향후 개선

- 실제 Food-101 / Recipe1M 사전학습 모델 연결
- 영양소 DB 매핑 (칼로리 범위 정확도 향상)
- 복수 음식 감지 및 분리
- Dockerfile / CI 테스트

## 보안

`.env` 파일은 커밋 금지. 운영 환경에서는 Secret Manager 또는 Key Vault 사용.

## 라이선스

프로토타입: 내부 학습 용도. 필요 시 추후 라이선스 명시.
