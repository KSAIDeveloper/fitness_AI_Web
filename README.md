# Food Image Classification & Fitness Vite App

모노레포 형태로 음식 이미지 분류 백엔드(FastAPI)와 프론트엔드(Vite + React) 피트니스 앱이 함께 있습니다.

## 폴더 구조

```
FoodImageChatAPI/        # FastAPI 백엔드 (음식 이미지 분석 API)
fitness-vite-app/        # Vite + React 프론트엔드 (칼로리 계산기 + 이미지 분석 페이지)
README.md                # 이 파일
```

## 주요 기능

- 업로드된 음식 이미지 → Chat 기반 Vision 모델 호출 → JSON (라벨, 칼로리, 신뢰도, 한글 설명) 반환
- 라벨 교정(fuzzy), 2단계 reasoning (경량 → 고성능 모델)
- 프론트엔드에서 칼로리 계산기 / 운동 / 식단 / FAQ / 음식 이미지 분석 페이지 제공

## 요구 사항

- Python 3.10+ (백엔드)
- Node.js 18+ (프론트엔드)
- OpenAI API Key (환경 변수 `.env`)

## 환경 변수 (.env 예시: `FoodImageChatAPI/.env`)

```
OPENAI_API_KEY=sk-...         # 실제 키
CHAT_MODEL=gpt-4.1             # 1차 모델
CHAT_MODEL_FALLBACK=gpt-4.1-mini
USE_REASONING=1                # 2단계 reasoning 사용(옵션)
OUTPUT_LANG=ko                 # 한국어 필드(label_ko 등) 요청
```

> 절대 실제 키를 버전관리(Git)에 올리지 마세요.

## 여기서부터 실행방법 꼭 백엔드 프론트엔드 둘 다 다른 터미널에서 실행하세요!!

## 백엔드 실행 (FastAPI)

PowerShell 기준:

```powershell
cd "c:\Food image classification\FoodImageChatAPI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# .env 파일(위 내용) 작성 후
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

헬스 체크:

```powershell
curl http://localhost:8000/health
```

정상일 경우: `{"status":"ok"}`

## 프론트엔드 실행 (Vite + React)

실행 정책 오류(PowerShell 실행 제한) 발생 시 세션 단위 해제 후 진행:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
cd "c:\Food image classification\fitness-vite-app"
npm install
npm run dev
```

기본 접속: `http://localhost:5173` → 헤더 "음식 이미지 분석" 클릭 → `/food-analyzer` 페이지에서 이미지 업로드

### 프록시 설정

`vite.config.js`에 `/api` 프록시가 구성되어 있으므로 프론트는 기본적으로 `fetch('/api/classify')` 형태로 백엔드 호출.
포트를 변경하려면:

1. 백엔드 포트 변경 (예: 9000)
2. `vite.config.js`의 proxy target을 동일 포트로 수정

환경변수로 직접 URL을 쓰고 싶다면 프론트 루트에 `.env` 생성:

```
VITE_API_BASE=http://localhost:8000
```

그리고 앱 재시작.

## 음식 이미지 분석 요청 예시 (직접 테스트)

```powershell
# 단일 파일 테스트 (폼 전송)
Invoke-WebRequest -Uri http://localhost:8000/classify -Method POST -InFile .\sample.jpg -ContentType multipart/form-data
```

(또는 Postman / 브라우저 업로드 이용)

## 실패(에러) 해결 가이드

| 증상                      | 원인                             | 해결                                                                 |
| ------------------------- | -------------------------------- | -------------------------------------------------------------------- |
| Failed to fetch           | CORS / 포트 불일치 / 서버 미기동 | 백엔드 기동, 프록시 `/api` 확인, 포트 동기화                         |
| 400 model_not_found       | 모델명 오타 / SDK 구버전         | `CHAT_MODEL` 점검, `pip install --upgrade openai`                    |
| Unicode/encoding 에러     | 비 ASCII 프롬프트/키             | `OUTPUT_LANG=ko` 사용하되 핵심 프롬프트는 ASCII 유지, 키 복사 재확인 |
| response_format 인자 오류 | 구버전 SDK                       | 자동 폴백 동작, SDK 업그레이드 권장                                  |

## 로컬 개발 흐름 요약

1. 백엔드 가동 → 헬스 체크 OK
2. 프론트 가동 → `/food-analyzer` 이동
3. 이미지 업로드 → 분석 결과 라벨, 칼로리, 신뢰도 표시
4. 필요 시 모델/프롬프트 튜닝 → `.env` 수정 후 백엔드 재시작

## 배포 간단 전략 (개요)

- 단일 도메인: Nginx 리버스 프록시 `/api` → FastAPI, 정적 파일 → Vite 빌드 결과
- 백엔드: `uvicorn` 또는 `gunicorn + uvicorn workers`
- 프론트: `npm run build` → `dist/` 서빙
- 환경변수: 프로덕션 서버에 `.env` 주입 (키는 CI/CD 시크릿으로 관리)

## 추후 개선 아이디어

- Dockerfile 두 개(백엔드/프론트) 또는 멀티 스테이지 통합
- 더 풍부한 영양 정보(탄수/단백질/지방) 필드 추가
- 이미지 다중 업로드 & 배치 처리
- 에러/성능 로깅 (Prometheus, Sentry 등)

문의나 추가 변경 요청이 있다면 언제든 말씀 주세요.
