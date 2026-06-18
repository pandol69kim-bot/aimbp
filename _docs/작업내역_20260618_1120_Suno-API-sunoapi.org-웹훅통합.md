# 작업 내역

- **날짜**: 2026-06-18 11:20
- **작업자**: Claude

## 작업 내용

Suno API를 `api.suno.ai` (전면 503) 에서 `sunoapi.org` 로 전환하고, 웹훅 기반 통합을 구현했습니다.

## 문제 분석

| 항목 | 내용 |
|---|---|
| 기존 엔드포인트 | `https://api.suno.ai` — 전면 503 (서버 다운) |
| 올바른 엔드포인트 | `https://api.sunoapi.org/api/v1/generate` |
| API 방식 | 폴링(X) → **웹훅 전용** |
| 필수 파라미터 | `model`, `customMode`, `instrumental`, `callBackUrl` |
| 유효 모델명 | `V3_5`, `V4`, `V4_5`, `V4_5ALL`, `V4_5PLUS`, `V5`, `V5_5` |

## sunoapi.org API 형식

### customMode: false (설명 모드)
```json
{
  "prompt": "happy pop song, upbeat",
  "model": "V4",
  "customMode": false,
  "instrumental": false,
  "callBackUrl": "https://your-backend.com/api/v1/music/webhook/suno"
}
```

### customMode: true (가사 직접 입력)
```json
{
  "prompt": "[Verse]\n가사 내용\n[Chorus]\n후렴구",
  "model": "V4",
  "customMode": true,
  "title": "곡 제목",
  "tags": "pop, happy",
  "instrumental": false,
  "callBackUrl": "https://your-backend.com/api/v1/music/webhook/suno"
}
```

### 응답
```json
{"code": 200, "msg": "success", "data": {"taskId": "9811a69adcebe97259fb7fb7ab2d9dc1"}}
```

### 웹훅 콜백 (sunoapi.org → 백엔드)
```json
{
  "taskId": "9811a69adcebe97259fb7fb7ab2d9dc1",
  "status": "completed",
  "data": [{"audio_url": "https://cdn.sunoapi.org/...mp3"}]
}
```

## 변경된 파일

- `.env`:
  - `SUNO_API_BASE=https://api.sunoapi.org` 추가/수정
  - `BACKEND_CALLBACK_URL=http://localhost:8001` 추가

- `backend/app/core/config.py`:
  - `SUNO_API_BASE` 기본값 변경
  - `BACKEND_CALLBACK_URL` 필드 추가

- `backend/app/services/ai_music.py`:
  - `_call_suno_generate()`: sunoapi.org 형식으로 완전 재작성
  - `_run_suno_generation()`: 폴링 루프 제거, taskId 저장 후 종료
  - `_poll_suno_task()`: 제거 (sunoapi.org는 폴링 엔드포인트 없음)

- `backend/app/api/music.py`:
  - `POST /api/v1/music/webhook/suno` 웹훅 수신 엔드포인트 추가

## 웹훅 수신 흐름

```
프론트엔드 → 백엔드 /generate → sunoapi.org 요청 → taskId DB 저장
                                        ↓ (생성 완료)
백엔드 /webhook/suno ← sunoapi.org 콜백 → Track 상태 업데이트
```

## 로컬 개발 주의사항

`callBackUrl`이 `http://localhost:8001`이면 sunoapi.org가 도달할 수 없어 웹훅이 도착하지 않습니다.

**로컬에서 실제 테스트하려면:**
```bash
# ngrok 설치 후
ngrok http 8001
# 발급된 URL을 .env에 설정
BACKEND_CALLBACK_URL=https://xxxx.ngrok-free.app
```

**프로덕션 배포 시:**
```
BACKEND_CALLBACK_URL=https://api.yourdomain.com
```

## 테스트 결과

```
✅ sunoapi.org API 호출 성공
   taskId=9811a69adcebe97259fb7fb7ab2d9dc1 반환

✅ 웹훅 엔드포인트 정상 응답
   POST /api/v1/music/webhook/suno → {"success": false, "error": "Track not found"}
   (존재하지 않는 taskId이므로 정상 동작)

✅ 백엔드 정상 재기동
```
