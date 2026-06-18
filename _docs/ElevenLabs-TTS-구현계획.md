# ElevenLabs TTS API 구현 계획서

- **작성일**: 2026-06-18
- **대상**: AIMBP 보컬 기능 (현재 Mock → ElevenLabs 실제 TTS)
- **API**: https://elevenlabs.io/app/developers/api-keys

---

## 현재 상태 (As-Is)

| 항목 | 현황 |
|---|---|
| 보컬 라이브러리 | 하드코딩 Mock 4개 (Aria, Noah, Luna, Jay) |
| TTS 처리 | 4초 대기 후 soundhelix.com 고정 MP3 반환 |
| 음성 ID | 없음 (ElevenLabs voice_id 미연동) |
| 파일 저장 | 없음 |

## 목표 (To-Be)

| 항목 | 목표 |
|---|---|
| 보컬 라이브러리 | ElevenLabs 실제 보이스 DB 시딩 |
| TTS 처리 | ElevenLabs API 호출 → 실제 MP3 생성 |
| 음성 ID | VocalLibrary.elevenlabs_voice_id 필드 추가 |
| 파일 저장 | Docker 볼륨 (/app/uploads/vocals/) 저장 |

---

## 1. ElevenLabs API 스펙

### TTS 엔드포인트
```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
Header: xi-api-key: {ELEVENLABS_API_KEY}
Header: Content-Type: application/json
```

### 요청 본문
```json
{
  "text": "가사 텍스트",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": true
  }
}
```

### 응답
- Content-Type: `audio/mpeg`
- Body: MP3 바이너리

### 사용할 모델
| 모델 ID | 용도 |
|---|---|
| `eleven_multilingual_v2` | 한국어 포함 다국어 지원 (권장) |
| `eleven_monolingual_v1` | 영어 전용, 빠름 |
| `eleven_turbo_v2_5` | 빠른 응답 (저지연) |

---

## 2. ElevenLabs 기본 제공 보이스

```python
ELEVENLABS_VOICES = [
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000001"),
        "name": "Rachel",
        "gender": "female",
        "genre": "pop",
        "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
        "description": "차분하고 부드러운 여성 보컬",
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000002"),
        "name": "Bella",
        "gender": "female",
        "genre": "ballad",
        "elevenlabs_voice_id": "EXAVITQu4vr4xnSDxMaL",
        "description": "따뜻하고 감성적인 여성 보컬",
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000003"),
        "name": "Adam",
        "gender": "male",
        "genre": "rnb",
        "elevenlabs_voice_id": "pNInz6obpgDQGcFmaJgB",
        "description": "깊고 강렬한 남성 보컬",
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000004"),
        "name": "Josh",
        "gender": "male",
        "genre": "rock",
        "elevenlabs_voice_id": "TxGEqnHWrfWFTfGW9XjX",
        "description": "힘있고 카리스마 있는 남성 보컬",
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000005"),
        "name": "Elli",
        "gender": "female",
        "genre": "kpop",
        "elevenlabs_voice_id": "MF3mGyEYCl7XYWbV9V6O",
        "description": "밝고 경쾌한 여성 보컬",
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000006"),
        "name": "Sam",
        "gender": "male",
        "genre": "hiphop",
        "elevenlabs_voice_id": "yoZ06aMxZJJ28mfd3POQ",
        "description": "허스키하고 개성있는 남성 보컬",
    },
]
```

---

## 3. 변경할 파일 목록

### 3-1. `.env`
```env
# ElevenLabs
ELEVENLABS_API_KEY=your-elevenlabs-api-key
ELEVENLABS_API_BASE=https://api.elevenlabs.io
```

### 3-2. `backend/app/core/config.py`
```python
ELEVENLABS_API_KEY: str = ""
ELEVENLABS_API_BASE: str = "https://api.elevenlabs.io"

@property
def has_elevenlabs(self) -> bool:
    return bool(self.ELEVENLABS_API_KEY and self.ELEVENLABS_API_KEY != "your-elevenlabs-api-key")
```

### 3-3. `backend/app/models/vocal.py`
`VocalLibrary` 테이블에 컬럼 추가:
```python
elevenlabs_voice_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
description: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

### 3-4. `backend/app/schemas/vocal.py`
`VocalLibraryResponse`에 필드 추가:
```python
class VocalLibraryResponse(BaseModel):
    id: UUID
    name: str
    gender: str
    genre: str
    sample_url: str
    is_active: bool
    description: Optional[str] = None
    elevenlabs_voice_id: Optional[str] = None
```

### 3-5. `backend/app/services/vocal.py` (핵심 변경)

```python
async def _call_elevenlabs_tts(voice_id: str, text: str) -> bytes:
    """ElevenLabs TTS API 호출 → MP3 바이너리 반환"""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.ELEVENLABS_API_BASE}/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": settings.ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True,
                },
            },
        )
        resp.raise_for_status()
        return resp.content  # MP3 바이너리


async def _process_vocal(vocal_id: str, db_session_factory) -> None:
    """백그라운드 태스크: ElevenLabs TTS 호출 → 파일 저장 → DB 업데이트"""
    async with db_session_factory() as session:
        vocal = await session.get(Vocal, uuid.UUID(vocal_id))
        if not vocal:
            return

        # 가사 가져오기 (트랙 → 가사)
        track = await session.get(Track, vocal.track_id)
        lyrics_text = await _get_lyrics_text(session, track)

        # ElevenLabs voice_id 조회
        library = await session.get(VocalLibrary, vocal.library_id)
        elevenlabs_voice_id = library.elevenlabs_voice_id if library else None

        if not settings.has_elevenlabs or not elevenlabs_voice_id:
            # Mock fallback
            await _mock_vocal(vocal, session)
            return

        try:
            mp3_bytes = await _call_elevenlabs_tts(elevenlabs_voice_id, lyrics_text)

            # 파일 저장 (/app/uploads/vocals/{vocal_id}.mp3)
            file_path = f"/app/uploads/vocals/{vocal_id}.mp3"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(mp3_bytes)

            vocal.status = "completed"
            vocal.file_url = f"/api/v1/files/vocals/{vocal_id}.mp3"
            vocal.file_key = f"vocals/{vocal_id}.mp3"
            await session.commit()

        except Exception as e:
            vocal.status = "failed"
            vocal.error_message = str(e)
            await session.commit()
```

### 3-6. `backend/app/api/vocal.py`
- `GET /vocal/library`: DB에 ElevenLabs 보이스 시딩 로직 추가
- `Vocal` 모델에 `error_message` 필드 추가 필요

### 3-7. `backend/app/models/vocal.py`
`Vocal` 테이블에 컬럼 추가:
```python
error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
```

### 3-8. `frontend/src/types/index.ts`
```typescript
export interface VocalLibrary {
  id: string
  name: string
  gender: 'male' | 'female' | 'neutral'
  genre: string
  sample_url?: string
  description?: string
  elevenlabs_voice_id?: string  // 추가
}

export interface VocalTrack {
  id: string
  track_id: string
  library_id: string
  language: string
  file_url?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string  // 추가
  created_at: string
}
```

---

## 4. 가사 텍스트 추출 로직

```python
async def _get_lyrics_text(session, track) -> str:
    """트랙에 연결된 가사를 가져옴. 없으면 트랙 제목 사용."""
    if track and track.lyrics_id:
        from app.models.lyrics import Lyrics
        lyrics = await session.get(Lyrics, track.lyrics_id)
        if lyrics:
            parts = [lyrics.verse, lyrics.chorus, lyrics.bridge]
            return "\n\n".join(p for p in parts if p)

    # 가사 없으면 기본 텍스트
    title = track.title if track else "song"
    return f"This is {title}. A beautiful melody fills the air."
```

---

## 5. 파일 서빙 방식

현재 `/api/v1/files/` 라우터를 통해 업로드 파일 서빙 중.
새로 생성된 보컬 MP3는 `/app/uploads/vocals/` 에 저장하고 동일 방식으로 서빙.

```
Docker Volume: uploads_data → /app/uploads/
파일 경로: /app/uploads/vocals/{vocal_id}.mp3
접근 URL: http://localhost:8001/api/v1/files/vocals/{vocal_id}.mp3
```

---

## 6. 구현 순서

```
Step 1: .env + config.py — API 키 설정
Step 2: models/vocal.py — elevenlabs_voice_id, description, error_message 컬럼 추가
Step 3: schemas/vocal.py — VocalLibraryResponse 업데이트
Step 4: services/vocal.py — ElevenLabs TTS 함수 구현
Step 5: api/vocal.py — 라이브러리 시딩 로직 구현
Step 6: 백엔드 재빌드 & DB 마이그레이션 (alembic 또는 recreate)
Step 7: frontend/types/index.ts — 타입 업데이트
Step 8: 프론트엔드 재빌드
Step 9: E2E 테스트
```

---

## 7. ElevenLabs 요금 참고

| 플랜 | 크레딧/월 | 가격 |
|---|---|---|
| Free | 10,000자 | 무료 |
| Starter | 30,000자 | $5/월 |
| Creator | 100,000자 | $22/월 |

- 1크레딧 = 1문자
- `eleven_multilingual_v2` 모델 사용 시 동일 크레딧 소비

---

## 8. 주의사항

- ElevenLabs API 키는 `.env`에만 보관, 코드에 하드코딩 금지
- `/app/uploads/vocals/` 디렉토리가 Docker 볼륨에 포함되어야 파일이 유지됨
- `docker-compose.yml`의 `uploads_data` 볼륨이 이미 설정되어 있으므로 별도 작업 불필요
- DB 스키마 변경 후 `docker-compose down -v` 없이 컬럼만 추가하려면 Alembic 마이그레이션 필요
  - 또는 `docker-compose down -v && docker-compose up -d` (데이터 초기화 방식)
