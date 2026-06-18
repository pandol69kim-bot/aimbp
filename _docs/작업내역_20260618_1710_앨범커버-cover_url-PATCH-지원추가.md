# 작업 내역

- **날짜**: 2026-06-18 17:10
- **작업자**: Claude

## 작업 내용

"생성된 커버 가져오기" → "앨범에 적용" 클릭 시 헤더 커버가 반영되지 않는 버그 수정.
`cover_url` 필드가 백엔드 AlbumUpdate 스키마와 프론트 훅 타입 양쪽에서 누락되어 있어,
PATCH 요청이 무시되고 있었습니다.

## 변경된 파일

### `backend/app/schemas/album.py`
- `AlbumUpdate`에 `cover_url: Optional[str] = None` 추가

### `backend/app/api/albums.py`
- `update_album` 핸들러에 `cover_url` 처리 로직 추가:
  ```python
  if payload.cover_url is not None:
      album.cover_url = payload.cover_url
  ```

### `frontend/src/hooks/useAlbums.ts`
- `useUpdateAlbum` mutationFn 타입에 `cover_url: string` 추가:
  ```typescript
  data: Partial<CreateAlbumRequest & { status: string; cover_url: string }>
  ```

## 동작 흐름 (수정 후)

1. 다이얼로그에서 커버 이미지 클릭 → `selectedCoverUrl` 로컬 상태 업데이트 (링 표시)
2. "앨범에 적용" 클릭 → `PATCH /albums/{id}` with `{ cover_url: "..." }`
3. 백엔드 `album.cover_url` 업데이트 → DB 저장
4. `onSuccess`: `['albums', id]` & `['albums']` 쿼리 무효화 → 자동 리페치
5. 헤더의 `album.cover_url` 값이 새 이미지 URL로 갱신 → 즉시 반영

## 배포

```bash
docker-compose build --no-cache backend
docker-compose up -d backend
# 프론트엔드 page.tsx는 이전 세션에서 이미 수정 완료
```
