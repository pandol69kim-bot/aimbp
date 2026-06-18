# 작업 내역

- **날짜**: 2026-06-18 14:30
- **작업자**: Claude

## 작업 내용

ElevenLabs TTS API 연동 구현 완료. 기존 Mock(soundhelix 고정 URL) 방식에서 실제 ElevenLabs TTS 호출로 전환하는 코드를 작성하고, DB 스키마를 업데이트했습니다.

## 변경된 파일

- `backend/app/models/vocal.py`: `VocalLibrary`에 `elevenlabs_voice_id`, `description` 컬럼 추가; `Vocal`에 `error_message` 컬럼 추가
- `backend/app/schemas/vocal.py`: `VocalLibraryResponse`에 `description`, `elevenlabs_voice_id` 추가; `VocalResponse`에 `error_message` 추가
- `backend/app/services/vocal.py`: 전면 재작성 — ElevenLabs TTS 호출 구현, SAMPLE_VOCAL_LIBRARY ElevenLabs 6개 보이스로 교체
- `backend/app/api/vocal.py`: `/library` 엔드포인트 — 빈 DB시 mock 반환 대신 실제 DB 시딩으로 변경
- `frontend/src/types/index.ts`: `VocalLibrary.elevenlabs_voice_id`, `VocalTrack.error_message` 필드 추가

## 주요 결정 사항

### 폴백 전략
ElevenLabs API 키 미설정 시 mock fallback(soundhelix URL + 2초 대기)으로 동작. `.env`의 `ELEVENLABS_API_KEY`를 실제 키로 교체하면 즉시 실제 TTS 활성화됨.

### DB 시딩 방식
`GET /vocal/library` 호출 시 vocal_library 테이블이 비어있으면 자동으로 6개 ElevenLabs 보이스를 INSERT. 재시작해도 중복 삽입 없음(이미 데이터 존재).

### ElevenLabs 보이스 목록 (DB에 시딩됨)
| 이름 | 성별 | 장르 | ElevenLabs Voice ID |
|------|------|------|---------------------|
| Rachel | female | pop | 21m00Tcm4TlvDq8ikWAM |
| Bella | female | ballad | EXAVITQu4vr4xnSDxMaL |
| Adam | male | rnb | pNInz6obpgDQGcFmaJgB |
| Josh | male | rock | TxGEqnHWrfWFTfGW9XjX |
| Elli | female | kpop | MF3mGyEYCl7XYWbV9V6O |
| Sam | male | hiphop | yoZ06aMxZJJ28mfd3POQ |

### 파일 저장 경로
- Docker 볼륨: `uploads_data → /app/uploads/`
- 보컬 MP3: `/app/uploads/vocals/{vocal_id}.mp3`
- 서빙 URL: `/api/v1/files/vocals/{vocal_id}.mp3`

## 작업 커맨드 로그

- `14:00` : DB 스키마 변경 (models/vocal.py)
- `14:10` : schemas/vocal.py 업데이트
- `14:15` : services/vocal.py 전면 재작성 (ElevenLabs TTS 구현)
- `14:20` : api/vocal.py 시딩 로직 변경
- `14:25` : frontend/types/index.ts 타입 업데이트
- `14:28` : `docker-compose down -v && docker-compose build --no-cache backend && docker-compose up -d`
- `14:30` : API 테스트 — `/api/v1/vocal/library` 정상 반환 (6개 보이스 + elevenlabs_voice_id 포함) ✅

## 다음 단계

1. **ElevenLabs API 키 발급**: https://elevenlabs.io/app/developers/api-keys
2. `.env`의 `ELEVENLABS_API_KEY=your-elevenlabs-api-key`를 실제 키로 교체
3. `docker-compose restart backend`
4. E2E 테스트: 트랙 생성 → 보이스 선택 → 보컬 생성 → MP3 파일 확인
