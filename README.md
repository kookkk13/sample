# VCF Backend (FastAPI) + React Frontend

## 1) 프로젝트 초기화

### Backend

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Frontend

```bash
cd frontend
npm install
```

## 2) 실행

### Backend

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
```

## 3) API

- `POST /api/login`
  - body: `{ "baseUrl"?: "https://...", "username": "...", "password": "..." }`
  - return: `{ "success": true }`
  - side effect: HttpOnly `session_token` 쿠키 발급
- `GET /api/virtualcenters`
  - auth: 세션 쿠키(`session_token`) 기반 인증 (Bearer 헤더도 호환)
  - return: `{ "items": [{ id, name, status, version, fqdn, raw }] }`

## 4) 프런트엔드 화면

- `/` (Login): URL, username, password 입력 후 로그인 성공 시 `/virtualcenters` 이동
- `/virtualcenters`: 로딩/실패/빈 데이터 상태 처리 + 목록 테이블 + 새로고침 버튼
- 세션 만료(401) 시 자동으로 로그인 화면으로 이동

## 5) 보안/운영 정책

- 패스워드는 서버 메모리/디스크에 저장하지 않고, 로그인 요청시에만 VCF API로 전달합니다.
- 세션 토큰은 초기 단계로 서버 메모리 저장소를 사용합니다.
- CORS는 `CORS_ALLOW_ORIGINS` 환경변수로 허용 도메인을 제한합니다.
- 에러 포맷은 `{code, message, details}`로 통일됩니다.
