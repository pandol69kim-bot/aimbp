# 작업내역: access_token undefined 오류 수정

**날짜:** 2026-06-17 15:20  
**작업자:** Claude Code

## 문제

로그인 시 "Cannot read properties of undefined (reading 'access_token')" 에러

## 원인

API 응답 인터셉터 추가 후 데이터 구조 변경:

```
인터셉터 추가 전:
response.data = { success, data: { access_token, ... }, error }

인터셉터 추가 후:
response.data = { access_token, ... }  // 인터셉터가 이미 data 필드 추출
```

하지만 auth.ts에서 여전히 이중 접근:
```typescript
const response = await api.post('/auth/login', data)
return response.data.data!  // ❌ response.data는 이미 추출됨
```

## 해결 방법

### auth.ts 수정

```typescript
// 변경 전
export async function loginUser(data: LoginRequest): Promise<TokenData> {
  const response = await api.post<ApiResponse<TokenData>>('/auth/login', data)
  return response.data.data!  // ❌ 이중 접근
}

// 변경 후
export async function loginUser(data: LoginRequest): Promise<TokenData> {
  const response = await api.post<TokenData>('/auth/login', data)
  return response.data as TokenData  // ✅ 인터셉터가 이미 처리함
}
```

### 적용된 모든 함수

1. **loginUser()**
   - 변경: `response.data.data!` → `response.data as TokenData`

2. **registerUser()**
   - 변경: `response.data.data!` → `response.data as User`

3. **fetchCurrentUser()**
   - 변경: `response.data.data!` → `response.data as User`

## 데이터 흐름

```
Backend API 응답
├─ { success: true, data: { access_token, ... }, error: null }
│
↓ (Axios 응답 인터셉터)
│
api.post() 반환
├─ response.data = { access_token, ... }  ← 인터셉터가 이미 추출
│
↓ (auth.ts)
│
loginUser() 반환
├─ { access_token, refresh_token }  ✅
```

## 테스트 결과

### Backend API (직접 호출)
```
POST /auth/login
응답: { success, data: { access_token, ... }, error }
✅ 정상
```

### Frontend (인터셉터 적용)
```
const response = await api.post('/auth/login', data)
response.data = { access_token, ... }  ✅ 올바른 구조
```

### 사용자 정보 조회
```
GET /auth/me
응답: { email: "test@aimbp.com", nickname: "tester", plan: "free" }
✅ 정상
```

## 수정된 파일

- `frontend/src/lib/auth.ts`: 3개 함수 모두 수정

## 다음 단계

- ✅ Backend API 정상 작동
- ✅ Frontend auth.ts 수정
- 🔄 로그인 재테스트 필요 (브라우저)

## 주의사항

- 인터셉터는 Frontend (Axios)에서만 작동
- Backend API 직접 호출은 원본 형식 유지
- 다른 페이지의 useQuery도 인터셉터 적용됨
