# ngrok 설치 및 실행 가이드

## 목적

sunoapi.org 웹훅 콜백을 로컬 백엔드(localhost:8001)에서 수신하기 위해
ngrok으로 외부 접근 가능한 터널 URL을 생성합니다.

---

## 1단계: 설치

PowerShell (관리자 권한)에서 실행:

```powershell
winget install ngrok.ngrok
```

또는 공식 사이트에서 직접 다운로드:
- https://ngrok.com/download
- Windows용 ZIP 다운로드 → 압축 해제 → 경로에 추가

---

## 2단계: 계정 및 인증 토큰 등록

1. https://dashboard.ngrok.com 에서 무료 회원가입
2. 로그인 후 좌측 메뉴 **Your Authtoken** 클릭
3. 토큰 복사 후 아래 명령 실행:

```powershell
ngrok config add-authtoken 여기에_토큰_붙여넣기
```

---

## 3단계: 터널 실행

```powershell
ngrok http 8001
```

실행 후 출력 예시:
```
Forwarding  https://abcd-1234.ngrok-free.app -> http://localhost:8001
```

`https://abcd-1234.ngrok-free.app` 이 외부에서 접근 가능한 URL입니다.

---

## 4단계: .env 업데이트

`.env` 파일에서 `BACKEND_CALLBACK_URL`을 ngrok URL로 변경:

```env
BACKEND_CALLBACK_URL=https://abcd-1234.ngrok-free.app
```

---

## 5단계: 백엔드 재빌드

```powershell
cd "F:\USB Drive\_웹어플\AIMBP"
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

## 6단계: 동작 확인

음악 생성 요청 후 백엔드 로그에서 웹훅 수신 확인:

```powershell
docker logs aimbp-backend -f
# 로그에 아래와 같이 출력되면 성공
# Suno webhook received: {...}
# Track xxxx completed via webhook. audio_url=https://...
```

---

## 주의사항

| 항목 | 내용 |
|---|---|
| URL 변경 | 무료 플랜은 ngrok 재실행 시마다 URL이 바뀜 |
| 재실행 시 | .env 수정 → docker 재빌드 필요 |
| 고정 URL | ngrok 유료 플랜 또는 서버 배포 시 불필요 |
| ngrok 종료 시 | 웹훅 수신 불가 → 터널 항상 켜두기 |
