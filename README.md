# VCF Backend (FastAPI)

## 1) 프로젝트 초기화

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 2) 실행

```bash
uvicorn app.main:app --reload --port 8000
```

## 3) API

- `POST /api/login`
  - body: `{ "username": "...", "password": "..." }`
  - return: `{ "token": "server-session-token", "expires_in": 3600 }`
- `GET /api/virtualcenters`
  - header: `Authorization: Bearer <server-session-token>`

## 4) 보안/운영 정책

- 패스워드는 서버 메모리/디스크에 저장하지 않고, 로그인 요청시에만 VCF API로 전달합니다.
- 세션 토큰은 초기 단계로 서버 메모리 저장소를 사용합니다.
- CORS는 `CORS_ALLOW_ORIGINS` 환경변수로 허용 도메인을 제한합니다.
- 에러 포맷은 `{code, message, details}`로 통일됩니다.
