# 관리자 페이지 — AI Model 키관리 메뉴 개발 계획서

**작성일:** 2026-06-18  
**작성자:** Claude Code  
**상태:** 초안 (Ready for Implementation)  
**예상 기간:** 3주 (Phase 1 내)

---

## 📋 목차

1. [기능 개요](#1-기능-개요)
2. [요구사항 분석](#2-요구사항-분석)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [데이터베이스 설계](#4-데이터베이스-설계)
5. [Backend API 설계](#5-backend-api-설계)
6. [Frontend UI/UX 설계](#6-frontend-uiux-설계)
7. [보안 고려사항](#7-보안-고려사항)
8. [개발 단계 계획](#8-개발-단계-계획)
9. [테스트 전략](#9-테스트-전략)
10. [배포 및 모니터링](#10-배포-및-모니터링)

---

## 1. 기능 개요

### 1.1 목표

AIMBP 플랫폼에서 사용하는 모든 AI/LLM API 키를 중앙에서 안전하게 관리하고, 각 AI 서비스의 사용량, 비용, 상태를 실시간으로 모니터링하는 관리 시스템 구축.

### 1.2 핵심 기능

| # | 기능 | 설명 | 우선순위 |
|---|------|------|---------|
| 1 | 키 등록 | 새로운 AI API 키 추가 | 🔴 필수 |
| 2 | 키 관리 | 기존 키 수정, 삭제, 활성화/비활성화 | 🔴 필수 |
| 3 | 키 검증 | 등록된 키의 유효성 검증 | 🔴 필수 |
| 4 | 사용량 모니터링 | 각 API별 일일/월별 사용량 추적 | 🟠 높음 |
| 5 | 비용 추적 | API 사용료 집계 및 비용 분석 | 🟠 높음 |
| 6 | 상태 대시보드 | 모든 AI 서비스의 실시간 상태 | 🟠 높음 |
| 7 | 에러 로그 | API 에러 및 실패 원인 추적 | 🟡 중간 |
| 8 | 할당량 관리 | 각 AI 서비스별 월간 사용 제한 설정 | 🟡 중간 |
| 9 | 알림 설정 | 할당량 초과 시 알림 | 🟡 중간 |
| 10 | 감사 로그 | 키 관리 작업의 감사 추적 | 🟡 중간 |

### 1.3 지원 AI 서비스

```
Tier 1 (필수)
├── OpenAI (GPT-4, GPT-3.5)
├── Anthropic Claude (Claude 3 Opus/Sonnet/Haiku)
├── Suno (AI 음악 생성)
└── Udio (AI 음악 생성 대안)

Tier 2 (Phase 2)
├── Stable Diffusion (이미지 생성)
├── Flux (이미지 생성)
├── Runway (비디오 생성)
└── Kling (비디오 생성)

Tier 3 (향후)
├── Gemini (Google)
├── Replicate (오픈소스 모델)
└── HuggingFace (모델 허브)
```

---

## 2. 요구사항 분석

### 2.1 기능 요구사항 (FRs)

#### FR1: 키 등록
```gherkin
Scenario: 관리자가 새 AI API 키를 등록
  Given 관리자는 관리자 페이지에 로그인함
  When "AI 키관리" 메뉴를 클릭
  And "새 키 등록" 버튼을 클릭
  And AI 서비스 선택 (OpenAI, Claude, Suno 등)
  And API 키를 입력
  And 선택사항: 기본 키 설정, 월간 할당량 입력
  And "검증 및 저장" 버튼을 클릭
  Then 키 유효성 자동 검증
  And 성공 시 리스트에 추가
  And 실패 시 에러 메시지 표시
```

#### FR2: 키 수정/삭제
```gherkin
Scenario: 관리자가 등록된 키 정보를 수정
  Given 키 리스트 화면
  When 특정 키의 "편집" 버튼을 클릭
  And 월간 할당량, 상태 등을 수정
  And "저장" 버튼을 클릭
  Then 변경사항 저장
  And 감시 로그 기록
  And 사용자에게 알림 (선택적)

Scenario: 관리자가 API 키 삭제
  Given 키 리스트 화면
  When 특정 키의 "삭제" 버튼을 클릭
  And 삭제 확인 다이얼로그 표시
  Then 삭제 전 사용 중인지 확인
  And 사용 중이면 경고 메시지
  And 최종 확인 후 삭제
```

#### FR3: 키 검증
```gherkin
Scenario: 등록 시 자동 검증
  Given 새 키 입력 후 검증 요청
  When API에 테스트 요청 전송
  Then 응답 확인
  And 키 유효성 판단
  And 할당량 정보 자동 조회 (가능한 경우)

Scenario: 정기 검증 (Daily)
  Given 매일 자정
  When 모든 등록된 키에 대해 검증 실행
  Then 각 키의 상태 업데이트
  And 상태 변화 감지 시 알림
```

#### FR4: 사용량 모니터링
```gherkin
Scenario: 사용량 현황 조회
  Given 키관리 대시보드
  When 특정 AI 서비스 선택
  Then 일일 사용량 차트 표시
  And 월간 누적 사용량 표시
  And 할당량 대비 현황 (%) 표시
  And 남은 할당량 표시
```

#### FR5: 비용 추적
```gherkin
Scenario: 월간 비용 조회
  Given 비용 대시보드
  When 월 선택
  Then 각 AI 서비스별 비용 표시
  And 총 비용 합계
  And 비용 추이 그래프
  And 예상 월말 비용
```

### 2.2 비기능 요구사항 (NFRs)

| 요구사항 | 기준 | 설명 |
|---------|------|------|
| 보안 | 🔴 필수 | API 키는 암호화하여 저장 (AES-256) |
| 성능 | 🔴 필수 | 키 검증 응답 시간 < 2초 |
| 가용성 | 🔴 필수 | 키 검증 실패해도 시스템 운영 가능 |
| 확장성 | 🟠 높음 | 새로운 AI 서비스 추가 용이 |
| 감시 | 🟠 높음 | 모든 키 관리 작업 로깅 |
| 성능 | 🟡 중간 | 사용량 데이터 집계 < 1초 |

---

## 3. 시스템 아키텍처

### 3.1 아키텍처 다이어그램

```
┌────────────────────────────────────────────────────────────┐
│                  관리자 대시보드 (Frontend)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ AI 키관리 페이지                                       │  │
│  │ ├─ 키 목록 (테이블)                                   │  │
│  │ ├─ 키 등록/수정 (모달/폼)                            │  │
│  │ ├─ 사용량 대시보드 (차트)                            │  │
│  │ ├─ 비용 분석 (그래프)                                │  │
│  │ └─ 상태 모니터 (실시간)                              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌────────────────────────────────────────────────────────────┐
│            Backend API (FastAPI)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Admin Router (/api/v1/admin/ai-keys)                 │  │
│  │ ├─ POST   /                    (키 등록)             │  │
│  │ ├─ GET    /                    (키 목록)             │  │
│  │ ├─ GET    /{key_id}            (키 상세)             │  │
│  │ ├─ PUT    /{key_id}            (키 수정)             │  │
│  │ ├─ DELETE /{key_id}            (키 삭제)             │  │
│  │ ├─ POST   /{key_id}/validate   (키 검증)             │  │
│  │ ├─ GET    /{key_id}/usage      (사용량)              │  │
│  │ ├─ GET    /dashboard/overview  (대시보드)            │  │
│  │ └─ GET    /logs                (감사 로그)           │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Services                                              │  │
│  │ ├─ AIKeyService (CRUD)                               │  │
│  │ ├─ KeyValidationService (검증)                       │  │
│  │ ├─ UsageTrackingService (사용량)                     │  │
│  │ ├─ CostCalculationService (비용)                     │  │
│  │ └─ AuditLogService (감사)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┬────────────────┐
         │           │           │                │
         ▼           ▼           ▼                ▼
    ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
    │PostgreSQL│ │  Redis   │ │ Vault*   │ │ External APIs│
    │          │ │(Cache)   │ │(Secrets) │ │              │
    │- AI Keys │ │          │ │          │ │- OpenAI      │
    │- Logs    │ │- Sessions│ │- Encrypted   │- Claude      │
    │- Usage   │ │- Metrics │ │  Keys    │ │- Suno        │
    │- Costs   │ │          │ │          │ │- Udio        │
    └─────────┘ └──────────┘ └──────────┘ └──────────────┘
```

### 3.2 데이터 흐름

#### 키 등록 시
```
관리자 입력 
  ↓
Frontend Validation 
  ↓
Backend Pydantic Validation 
  ↓
Key Encryption (AES-256)
  ↓
Database 저장 
  ↓
비동기 검증 (테스트 API 호출)
  ↓
상태 업데이트 (valid/invalid)
  ↓
Frontend 업데이트
```

#### 사용량 추적 시
```
Application 코드 
  ↓
API 호출 발생 
  ↓
Middleware/Hook 에서 감시
  ↓
사용량 데이터 기록 (Redis)
  ↓
정기적으로 DB에 집계
  ↓
Dashboard에 표시
```

---

## 4. 데이터베이스 설계

### 4.1 테이블 스키마

#### 4.1.1 ai_api_keys 테이블
```sql
CREATE TABLE ai_api_keys (
    id VARCHAR(36) PRIMARY KEY,
    
    -- 기본 정보
    service_name VARCHAR(100) NOT NULL,  -- openai, claude, suno, udio
    key_name VARCHAR(200) NOT NULL,      -- "OpenAI GPT-4 Production Key"
    api_key_encrypted VARCHAR(500) NOT NULL,  -- 암호화된 키
    
    -- 상태
    is_active BOOLEAN DEFAULT true,
    is_valid BOOLEAN DEFAULT NULL,       -- 검증 상태
    last_validated_at TIMESTAMP,
    validation_error VARCHAR(500),       -- 검증 실패 원인
    
    -- 할당량 & 비용
    monthly_quota INT DEFAULT NULL,      -- 월간 사용 제한 (NULL = 무제한)
    current_month_usage INT DEFAULT 0,   -- 현재월 사용량
    monthly_budget DECIMAL(10, 2),       -- 월간 예산
    
    -- 메타데이터
    priority INT DEFAULT 0,              -- 우선순위 (높을수록 먼저 사용)
    fallback_key_id VARCHAR(36),         -- 대체 키 (실패시)
    config JSON,                         -- 서비스별 추가 설정
    
    -- 감시
    created_by VARCHAR(36) NOT NULL,     -- 생성자 (admin)
    updated_by VARCHAR(36),              -- 수정자
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (fallback_key_id) REFERENCES ai_api_keys(id),
    
    INDEX idx_service (service_name),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at)
);
```

#### 4.1.2 ai_usage_logs 테이블
```sql
CREATE TABLE ai_usage_logs (
    id VARCHAR(36) PRIMARY KEY,
    
    -- 키 정보
    ai_key_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36),                 -- NULL = 내부 사용
    
    -- 사용 정보
    service_name VARCHAR(100),           -- openai, claude, suno, udio
    model VARCHAR(100),                  -- gpt-4, claude-3-opus, etc
    endpoint VARCHAR(200),               -- /v1/chat/completions, etc
    
    -- 메트릭
    input_tokens INT,                    -- 입력 토큰 수
    output_tokens INT,                   -- 출력 토큰 수
    total_tokens INT,
    
    cost DECIMAL(10, 6),                 -- 사용료
    response_time_ms INT,                -- 응답 시간 (밀리초)
    
    -- 상태
    status VARCHAR(50),                  -- success, failed, rate_limited
    error_message VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ai_key_id) REFERENCES ai_api_keys(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    
    INDEX idx_ai_key_id (ai_key_id),
    INDEX idx_service (service_name),
    INDEX idx_created_at (created_at),
    INDEX idx_user_id (user_id)
);
```

#### 4.1.3 ai_key_audit_logs 테이블
```sql
CREATE TABLE ai_key_audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    
    -- 대상
    ai_key_id VARCHAR(36) NOT NULL,
    
    -- 작업
    action VARCHAR(50) NOT NULL,         -- create, update, delete, validate, enable, disable
    actor_id VARCHAR(36) NOT NULL,       -- 관리자 ID
    
    -- 변경 내용
    changes JSON,                        -- {"key_name": {...}, "monthly_quota": {...}}
    
    -- 상세
    reason VARCHAR(500),                 -- 작업 사유
    ip_address VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ai_key_id) REFERENCES ai_api_keys(id),
    FOREIGN KEY (actor_id) REFERENCES users(id),
    
    INDEX idx_ai_key_id (ai_key_id),
    INDEX idx_actor_id (actor_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);
```

#### 4.1.4 ai_daily_aggregates 테이블 (성능 최적화)
```sql
CREATE TABLE ai_daily_aggregates (
    id VARCHAR(36) PRIMARY KEY,
    
    -- 키 정보
    ai_key_id VARCHAR(36) NOT NULL,
    service_name VARCHAR(100),
    
    -- 날짜
    date DATE NOT NULL,
    
    -- 집계
    total_requests INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    total_cost DECIMAL(10, 6) DEFAULT 0,
    
    success_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ai_key_id) REFERENCES ai_api_keys(id),
    
    UNIQUE KEY unique_date_key (date, ai_key_id),
    INDEX idx_date (date)
);
```

### 4.2 데이터 흐름

```
ai_usage_logs (실시간, 상세)
    ↓
[일일 집계 배치]
    ↓
ai_daily_aggregates (요약)
    ↓
Dashboard 조회
```

---

## 5. Backend API 설계

### 5.1 API 엔드포인트

#### Base URL: `/api/v1/admin/ai-keys`

### 5.2 키 관리 API

#### 5.2.1 키 등록
```http
POST /api/v1/admin/ai-keys

Request Body:
{
  "service_name": "openai",           # openai, claude, suno, udio
  "key_name": "OpenAI GPT-4 Prod",
  "api_key": "sk-...",
  "monthly_quota": 100000,             # NULL = 무제한
  "monthly_budget": 500.00,            # 월간 예산 (USD)
  "priority": 1,                       # 0~10, 높을수록 우선 사용
  "is_active": true,
  "config": {
    "region": "us-east-1",             # 서비스별 옵션
    "custom_field": "value"
  }
}

Response (201):
{
  "success": true,
  "data": {
    "id": "key_123abc",
    "service_name": "openai",
    "key_name": "OpenAI GPT-4 Prod",
    "is_active": true,
    "is_valid": true,
    "last_validated_at": "2026-06-18T11:30:00Z",
    "created_at": "2026-06-18T11:30:00Z"
  }
}
```

#### 5.2.2 키 목록 조회
```http
GET /api/v1/admin/ai-keys?service=openai&is_active=true&page=1&limit=10

Query Parameters:
- service: openai, claude, suno, udio (선택)
- is_active: true/false (선택)
- page: 페이지 번호 (기본값 1)
- limit: 페이지 크기 (기본값 10)

Response (200):
{
  "success": true,
  "data": [
    {
      "id": "key_123",
      "service_name": "openai",
      "key_name": "OpenAI GPT-4 Prod",
      "is_active": true,
      "is_valid": true,
      "last_validated_at": "2026-06-18T11:30:00Z",
      "current_month_usage": 45000,
      "monthly_quota": 100000,
      "monthly_budget": 500.00,
      "priority": 1
    },
    ...
  ],
  "meta": {
    "total": 24,
    "page": 1,
    "limit": 10,
    "total_pages": 3
  }
}
```

#### 5.2.3 키 상세 조회
```http
GET /api/v1/admin/ai-keys/{key_id}

Response (200):
{
  "success": true,
  "data": {
    "id": "key_123",
    "service_name": "openai",
    "key_name": "OpenAI GPT-4 Prod",
    "is_active": true,
    "is_valid": true,
    "is_masked": true,              # 마스킹된 키
    "api_key_preview": "sk-***...abc",
    "last_validated_at": "2026-06-18T11:30:00Z",
    "validation_error": null,
    "current_month_usage": 45000,
    "monthly_quota": 100000,
    "monthly_budget": 500.00,
    "fallback_key_id": "key_456",
    "priority": 1,
    "config": { ... },
    "created_by": "admin_123",
    "created_at": "2026-06-15T10:00:00Z",
    "updated_at": "2026-06-18T11:30:00Z"
  }
}
```

#### 5.2.4 키 수정
```http
PUT /api/v1/admin/ai-keys/{key_id}

Request Body:
{
  "key_name": "OpenAI GPT-4 Prod (Updated)",
  "monthly_quota": 150000,
  "monthly_budget": 700.00,
  "priority": 2,
  "is_active": true,
  "config": { ... }
}

Response (200):
{
  "success": true,
  "data": { ... 수정된 키 정보 ... }
}
```

#### 5.2.5 키 삭제
```http
DELETE /api/v1/admin/ai-keys/{key_id}

Request Body:
{
  "reason": "Expired key"  # (선택) 삭제 사유
}

Response (200):
{
  "success": true,
  "data": {
    "id": "key_123",
    "message": "Key deleted successfully"
  }
}

# 주의: 사용 중인 키 삭제 시
Response (409):
{
  "success": false,
  "error": {
    "code": "KEY_IN_USE",
    "message": "Cannot delete key that is currently in use",
    "details": {
      "usage_count": 45000,
      "last_used": "2026-06-18T10:30:00Z"
    }
  }
}
```

### 5.3 검증 API

#### 5.3.1 키 검증
```http
POST /api/v1/admin/ai-keys/{key_id}/validate

Request Body:
{
  "force": false  # true = 캐시 무시하고 재검증
}

Response (200):
{
  "success": true,
  "data": {
    "key_id": "key_123",
    "is_valid": true,
    "service_name": "openai",
    "model": "gpt-4",
    "remaining_quota": {
      "daily_limit": 10000000,
      "daily_usage": 45000,
      "monthly_limit": 1000000,
      "monthly_usage": 450000
    },
    "organization": "OpenAI Organization ID",
    "validated_at": "2026-06-18T11:35:00Z",
    "next_validation": "2026-06-19T11:35:00Z"
  }
}

# 검증 실패 시
Response (400):
{
  "success": false,
  "error": {
    "code": "INVALID_API_KEY",
    "message": "API key is invalid or expired",
    "details": {
      "api_error_code": 401,
      "api_error_message": "Invalid Authentication"
    }
  }
}
```

### 5.4 사용량 및 비용 API

#### 5.4.1 사용량 조회
```http
GET /api/v1/admin/ai-keys/{key_id}/usage?date_from=2026-06-01&date_to=2026-06-18

Query Parameters:
- date_from: YYYY-MM-DD (기본값: 이번 달 1일)
- date_to: YYYY-MM-DD (기본값: 오늘)
- group_by: daily, hourly (기본값: daily)

Response (200):
{
  "success": true,
  "data": {
    "key_id": "key_123",
    "service_name": "openai",
    "date_range": {
      "from": "2026-06-01",
      "to": "2026-06-18"
    },
    "summary": {
      "total_requests": 450000,
      "total_tokens": 15000000,
      "total_cost": 145.50,
      "average_cost_per_request": 0.000323,
      "success_rate": 99.8
    },
    "daily_usage": [
      {
        "date": "2026-06-18",
        "requests": 25000,
        "tokens": 850000,
        "cost": 8.50,
        "success": 24990,
        "failed": 10
      },
      ...
    ]
  }
}
```

#### 5.4.2 비용 분석
```http
GET /api/v1/admin/ai-keys/dashboard/costs?month=2026-06

Query Parameters:
- month: YYYY-MM (기본값: 현재월)

Response (200):
{
  "success": true,
  "data": {
    "month": "2026-06",
    "total_cost": 2450.75,
    "by_service": [
      {
        "service_name": "openai",
        "cost": 1200.50,
        "percentage": 49,
        "requests": 450000
      },
      {
        "service_name": "claude",
        "cost": 800.25,
        "percentage": 33,
        "requests": 120000
      },
      {
        "service_name": "suno",
        "cost": 350.00,
        "percentage": 14,
        "requests": 1000
      },
      ...
    ],
    "daily_trend": [
      {
        "date": "2026-06-01",
        "cost": 75.50
      },
      ...
    ],
    "projected_month_end": 3500.00
  }
}
```

### 5.5 대시보드 API

#### 5.5.1 개요
```http
GET /api/v1/admin/ai-keys/dashboard/overview

Response (200):
{
  "success": true,
  "data": {
    "summary": {
      "total_keys": 24,
      "active_keys": 22,
      "inactive_keys": 2,
      "invalid_keys": 0
    },
    "status": [
      {
        "service_name": "openai",
        "total_keys": 5,
        "active_keys": 5,
        "valid_keys": 5,
        "current_usage": 45000,
        "monthly_quota": 100000,
        "quota_percentage": 45,
        "status": "healthy"  # healthy, warning, critical
      },
      {
        "service_name": "claude",
        "total_keys": 3,
        "active_keys": 3,
        "valid_keys": 3,
        "current_usage": 85000,
        "monthly_quota": 100000,
        "quota_percentage": 85,
        "status": "warning"  # 85% 이상
      },
      ...
    ],
    "alerts": [
      {
        "level": "warning",
        "message": "Claude API approaching quota limit (85%)",
        "ai_key_id": "key_456",
        "action": "Consider adding new key or increase quota"
      },
      {
        "level": "error",
        "message": "Suno API key validation failed",
        "ai_key_id": "key_789",
        "last_error": "Rate limit exceeded"
      }
    ],
    "this_month_cost": 2450.75,
    "last_month_cost": 2100.50,
    "cost_trend": "up_16"  # 16% 증가
  }
}
```

### 5.6 감시 로그 API

#### 5.6.1 감시 로그 조회
```http
GET /api/v1/admin/ai-keys/logs?ai_key_id=key_123&action=update&page=1

Query Parameters:
- ai_key_id: (선택)
- action: create, update, delete, validate (선택)
- date_from: (선택)
- date_to: (선택)

Response (200):
{
  "success": true,
  "data": [
    {
      "id": "audit_123",
      "ai_key_id": "key_123",
      "action": "update",
      "actor": {
        "id": "admin_456",
        "email": "admin@example.com"
      },
      "changes": {
        "monthly_quota": {
          "before": 100000,
          "after": 150000
        },
        "priority": {
          "before": 1,
          "after": 2
        }
      },
      "reason": "Increased quota for production use",
      "ip_address": "192.168.1.100",
      "created_at": "2026-06-18T11:30:00Z"
    },
    ...
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "limit": 20
  }
}
```

---

## 6. Frontend UI/UX 설계

### 6.1 페이지 구조

```
Admin Dashboard
└── AI 키관리
    ├── 키 목록 (Table View)
    │   ├── 검색 & 필터
    │   ├── 키 항목 (각각)
    │   │   ├─ 키 상태 배지
    │   │   ├─ 사용량 프로그레스 바
    │   │   ├─ 편집 버튼
    │   │   ├─ 삭제 버튼
    │   │   └─ 더보기 메뉴
    │   └── 페이지네이션
    ├── 새 키 등록 (Modal)
    │   ├─ 서비스 선택 (Dropdown)
    │   ├─ 키 이름 (Text Input)
    │   ├─ API 키 (Password Input)
    │   ├─ 월간 할당량 (Number Input)
    │   ├─ 월간 예산 (Currency Input)
    │   ├─ 우선순위 (Slider)
    │   ├─ 활성화 (Toggle)
    │   └─ 검증 & 저장 (Button)
    ├── 대시보드 탭
    │   ├─ 상태 요약 카드
    │   ├─ 서비스별 현황 카드
    │   ├─ 사용량 차트 (Line)
    │   ├─ 비용 차트 (Bar)
    │   └─ 알림 목록
    └── 감시 로그 탭
        ├─ 로그 테이블
        └─ 필터 & 검색
```

### 6.2 주요 컴포넌트

#### 6.2.1 키 목록 테이블
```typescript
interface AIKeyTableRow {
  id: string;
  serviceName: string;
  keyName: string;
  isActive: boolean;
  isValid: boolean;
  lastValidated: Date;
  usagePercentage: number;
  monthlyQuota: number | null;
  currentUsage: number;
  monthlyBudget: number | null;
  priority: number;
}

// 열 정의
columns = [
  { header: 'Service', key: 'serviceName', width: '15%' },
  { header: 'Key Name', key: 'keyName', width: '25%' },
  { header: 'Status', key: 'status', width: '12%', type: 'badge' },
  { header: 'Usage', key: 'usage', width: '20%', type: 'progressBar' },
  { header: 'Budget', key: 'budget', width: '12%' },
  { header: 'Actions', key: 'actions', width: '16%', type: 'actionMenu' }
];
```

#### 6.2.2 상태 배지
```typescript
StatusBadge 컴포넌트
├─ valid (green): "✓ Valid"
├─ invalid (red): "✗ Invalid"
├─ expired (orange): "⚠ Expired"
├─ active (blue): "○ Active"
└─ inactive (gray): "○ Inactive"
```

#### 6.2.3 사용량 프로그레스 바
```typescript
UsageProgressBar 컴포넌트
├─ 배경: 할당량 대비 사용량 %
├─ 안내 텍스트: "45,000 / 100,000 (45%)"
├─ 색상:
│  ├─ green: 0-70%
│  ├─ yellow: 70-90%
│  └─ red: 90-100%
└─ hover: "Click to view detailed usage"
```

#### 6.2.4 키 등록 폼 (Modal)
```typescript
AIKeyRegisterModal 컴포넌트
├─ FormField: Service Select (required)
│  └─ options: OpenAI, Claude, Suno, Udio, Stable Diffusion, Flux
├─ FormField: Key Name (required, max 200)
├─ FormField: API Key (required, password input)
│  └─ hint: "Key will be encrypted and never displayed again"
├─ FormField: Monthly Quota (optional, number)
│  └─ hint: "Leave empty for unlimited"
├─ FormField: Monthly Budget (optional, currency)
│  └─ hint: "USD. Alert when exceeded"
├─ FormField: Priority (1-10, slider)
│  └─ hint: "Higher = used first when multiple keys available"
├─ FormField: Active (toggle)
├─ FormField: Fallback Key (select, optional)
│  └─ hint: "Used if this key fails"
├─ Validate Button
│  └─ shows loading + validation result
└─ Save & Cancel Buttons
```

### 6.3 대시보드 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│              AI 키관리 대시보드                            │
├─────────────────────────────────────────────────────────┤
│ 상태 요약                                                │
│ ┌────────────┬─────────────┬─────────────┬──────────────┐
│ │ 총 키: 24  │ 활성: 22    │ 검증됨: 24  │ 이번 달: $2.4K│
│ └────────────┴─────────────┴─────────────┴──────────────┘
│
│ 서비스별 현황 (카드)
│ ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐
│ │ OpenAI          │ │ Claude          │ │ Suno         │
│ │ ━━━━━━━━━━━━    │ │ ━━━━━━━━━━━━━━━ │ │ ━━━━━━━━━━   │
│ │ 45% (45K/100K)  │ │ 85% (85K/100K)  │ │ 60% (6K/10K) │
│ │ ⚠️ Warning      │ │ 🟢 Healthy       │ │ 🟢 Healthy   │
│ └─────────────────┘ └─────────────────┘ └──────────────┘
│
│ 사용량 추이
│ ┌─────────────────────────────────────────────────────┐
│ │ Line Chart                                          │
│ │ 18  │         ┌─┐                                  │
│ │ 12  │      ┌──┴─┴──┐                               │
│ │  6  │   ┌──┘       └──┐                            │
│ │  0  └───┴──────────────┴─────────────────────────┘│
│ │      6/1  6/5  6/10  6/15  6/18                     │
│ └─────────────────────────────────────────────────────┘
│
│ 비용 분석
│ ┌─────────────────────────────────────────────────────┐
│ │ Bar Chart (Service별)                              │
│ │ $1200.50 (OpenAI)                                  │
│ │ $800.25 (Claude)                                   │
│ │ $350.00 (Suno)                                     │
│ └─────────────────────────────────────────────────────┘
│
│ 알림
│ ┌─────────────────────────────────────────────────────┐
│ │ ⚠️  Claude API approaching quota (85%)              │
│ │ 🔴 Suno API key validation failed                   │
│ │ ℹ️  New Suno key added (2 hours ago)               │
│ └─────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────┘
```

### 6.4 색상 & 상태 정의

```typescript
enum AIKeyStatus {
  VALID = 'valid',       // 🟢 Green
  INVALID = 'invalid',   // 🔴 Red
  EXPIRED = 'expired',   // 🟠 Orange
  PENDING = 'pending',   // 🔵 Blue (검증 중)
}

enum AlertLevel {
  INFO = 'info',         // ℹ️ Blue
  WARNING = 'warning',   // ⚠️ Orange
  ERROR = 'error',       // 🔴 Red
}

enum ServiceColor {
  openai: '#00A67E',
  claude: '#000000',
  suno: '#FF6B6B',
  udio: '#4ECDC4',
}
```

---

## 7. 보안 고려사항

### 7.1 API 키 보안

#### 7.1.1 저장
```python
# ❌ Bad
api_key = request.api_key
db.save(api_key)  # 평문 저장

# ✅ Good
from cryptography.fernet import Fernet

cipher = Fernet(settings.ENCRYPTION_KEY)
encrypted_key = cipher.encrypt(request.api_key.encode())
db.save(encrypted_key)
```

#### 7.1.2 조회
```python
# DB에서 조회할 때 복호화
encrypted_key = db.get_ai_key(key_id).api_key_encrypted
decrypted_key = cipher.decrypt(encrypted_key).decode()
```

#### 7.1.3 표시
```python
# 관리자에게도 전체 키를 표시하지 않음
def mask_api_key(api_key: str) -> str:
    if len(api_key) < 20:
        return "*" * len(api_key)
    return api_key[:3] + "*" * (len(api_key) - 6) + api_key[-3:]

# "sk-... (masked)"를 표시
```

### 7.2 접근 제어

#### 7.2.1 권한 검증
```python
@app.post("/api/v1/admin/ai-keys")
async def create_ai_key(
    request: CreateAIKeyRequest,
    current_user: User = Depends(get_current_user),
):
    # 관리자 권한 확인
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
```

#### 7.2.2 감시 로깅
```python
async def create_ai_key(...):
    # 키 생성
    ai_key = AIKey(...)
    db.add(ai_key)
    
    # 감시 로그
    audit_log = AuditLog(
        ai_key_id=ai_key.id,
        action="create",
        actor_id=current_user.id,
        ip_address=request.client.host,
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
```

### 7.3 검증 & 레이트 제한

#### 7.3.1 입력 검증
```python
class CreateAIKeyRequest(BaseModel):
    service_name: str = Field(..., regex="^(openai|claude|suno|udio)$")
    key_name: str = Field(..., min_length=1, max_length=200)
    api_key: str = Field(..., min_length=20)
    monthly_quota: Optional[int] = Field(None, ge=1)
    monthly_budget: Optional[float] = Field(None, ge=0.01)
    priority: int = Field(default=0, ge=0, le=10)
```

#### 7.3.2 레이트 제한
```python
# API 키 검증 시 (외부 API 호출이므로 제한 필요)
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/admin/ai-keys/{key_id}/validate")
@limiter.limit("5/minute")  # 분당 5회
async def validate_key(key_id: str):
    ...
```

### 7.4 네트워크 보안

#### 7.4.1 HTTPS Only
```python
response.headers["Strict-Transport-Security"] = "max-age=31536000"
```

#### 7.4.2 CORS
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://admin.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)
```

### 7.5 외부 API 호출 보안

#### 7.5.1 Timeout & Retry
```python
async def validate_openai_key(api_key: str) -> bool:
    try:
        # timeout 설정
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
        return response.status_code == 200
    except httpx.TimeoutException:
        # 타임아웃 처리
        return None  # 검증 불가 (유지)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False
```

---

## 8. 개발 단계 계획

### 8.1 Timeline

```
Week 1 (6월 18-22)
├─ Database 설계 완료 ✅
├─ Backend Models 구현
├─ Backend Schemas 작성
└─ 마이그레이션 파일 생성

Week 2 (6월 23-29)
├─ API 엔드포인트 구현 (CRUD)
├─ 검증 로직 구현
├─ 감시 로깅 구현
└─ Backend 단위 테스트

Week 3 (6월 30-7월 6)
├─ Frontend 페이지 구현
├─ UI 컴포넌트 작성
├─ API 통합 (Axios)
├─ Frontend 테스트
└─ E2E 테스트
```

### 8.2 Phase 1: Backend 개발 (Week 1-2)

#### Sprint 1.1: 데이터 모델 (Day 1-2)
```python
# models/ai_api_key.py
class AIAPIKey(Base):
    __tablename__ = "ai_api_keys"
    
    id = Column(String, primary_key=True)
    service_name = Column(String, nullable=False)
    key_name = Column(String, nullable=False)
    api_key_encrypted = Column(String, nullable=False)
    # ... 추가 필드

# models/ai_usage_log.py
class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"
    # ... 필드

# models/ai_key_audit_log.py
class AIKeyAuditLog(Base):
    __tablename__ = "ai_key_audit_logs"
    # ... 필드
```

#### Sprint 1.2: Schemas (Day 2-3)
```python
# schemas/ai_key.py
class CreateAIKeyRequest(BaseModel):
    service_name: str
    key_name: str
    api_key: str
    # ...

class AIKeyResponse(BaseModel):
    id: str
    service_name: str
    key_name: str
    is_valid: bool
    # ... (마스킹된 키)
    
    class Config:
        from_attributes = True
```

#### Sprint 1.3: 서비스 레이어 (Day 3-5)
```python
# services/ai_key_service.py
class AIKeyService:
    async def create_key(self, request: CreateAIKeyRequest) -> AIAPIKey:
        # 암호화
        encrypted = encrypt_api_key(request.api_key)
        # DB 저장
        # 검증 (비동기)
        
    async def validate_key(self, key_id: str) -> bool:
        # 키 가져오기
        # 복호화
        # 외부 API 호출로 검증
        
    async def delete_key(self, key_id: str) -> bool:
        # 사용 중 확인
        # 감시 로그
        # 삭제

# services/ai_usage_service.py
class AIUsageService:
    async def log_usage(self, key_id: str, usage_data: dict):
        # 로그 기록
        # 캐시 업데이트
        
    async def get_usage(self, key_id: str, date_from, date_to):
        # 데이터 집계
        # 비용 계산

# services/ai_cost_service.py
class AICostService:
    async def calculate_cost(self, service: str, tokens: int) -> float:
        # 서비스별 가격 계산
        
    async def get_monthly_cost(self, ai_key_id: str) -> float:
        # 월별 비용 집계
```

#### Sprint 1.4: API 엔드포인트 (Day 5-10)
```python
# api/admin/ai_keys.py
router = APIRouter(prefix="/admin/ai-keys", tags=["admin-ai-keys"])

@router.post("/")
async def create_ai_key(request: CreateAIKeyRequest, ...):
    """새 AI API 키 등록"""
    
@router.get("/")
async def list_ai_keys(...):
    """등록된 키 목록 조회"""
    
@router.get("/{key_id}")
async def get_ai_key(key_id: str, ...):
    """키 상세 조회"""
    
@router.put("/{key_id}")
async def update_ai_key(key_id: str, request: UpdateAIKeyRequest, ...):
    """키 정보 수정"""
    
@router.delete("/{key_id}")
async def delete_ai_key(key_id: str, ...):
    """키 삭제"""
    
@router.post("/{key_id}/validate")
async def validate_ai_key(key_id: str, ...):
    """키 검증"""
    
@router.get("/{key_id}/usage")
async def get_key_usage(key_id: str, ...):
    """사용량 조회"""
    
@router.get("/dashboard/overview")
async def get_dashboard_overview(...):
    """대시보드 개요"""
    
@router.get("/dashboard/costs")
async def get_cost_analysis(...):
    """비용 분석"""
    
@router.get("/logs")
async def get_audit_logs(...):
    """감시 로그"""
```

#### Sprint 1.5: 테스트 (Day 10-12)
```python
# tests/test_ai_key_service.py
@pytest.mark.asyncio
async def test_create_ai_key():
    service = AIKeyService(db)
    result = await service.create_key(test_request)
    assert result.id is not None
    assert result.is_valid is True

@pytest.mark.asyncio
async def test_validate_ai_key():
    # 유효한 키 검증
    # 무효한 키 검증
    # 만료된 키 검증

@pytest.mark.asyncio
async def test_encrypt_decrypt():
    # 암호화/복호화 테스트
```

### 8.3 Phase 2: Frontend 개발 (Week 3)

#### Sprint 2.1: 페이지 레이아웃 (Day 1-2)
```typescript
// app/(admin)/admin/ai-keys/page.tsx
export default function AdminAIKeysPage() {
  return (
    <AdminLayout>
      <div className="space-y-6">
        <Header title="AI Model Key Management" />
        <Tabs defaultValue="keys">
          <TabsList>
            <TabsTrigger value="keys">Keys</TabsTrigger>
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="logs">Audit Logs</TabsTrigger>
          </TabsList>
          <TabsContent value="keys">
            {/* 키 목록 */}
          </TabsContent>
          <TabsContent value="dashboard">
            {/* 대시보드 */}
          </TabsContent>
          <TabsContent value="logs">
            {/* 감시 로그 */}
          </TabsContent>
        </Tabs>
      </div>
    </AdminLayout>
  );
}
```

#### Sprint 2.2: 컴포넌트 구현 (Day 2-4)
```typescript
// components/features/admin/AIKeyTable.tsx
export function AIKeyTable({ keys }: { keys: AIKey[] }) {
  const [selectedKey, setSelectedKey] = useState<AIKey | null>(null);
  
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Service</TableHead>
          <TableHead>Key Name</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Usage</TableHead>
          <TableHead>Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {keys.map((key) => (
          <TableRow key={key.id}>
            <TableCell>{key.serviceName}</TableCell>
            <TableCell>{key.keyName}</TableCell>
            <TableCell>
              <StatusBadge status={key.status} />
            </TableCell>
            <TableCell>
              <UsageProgressBar usage={key.usage} />
            </TableCell>
            <TableCell>
              <ActionMenu
                onEdit={() => setSelectedKey(key)}
                onDelete={() => handleDelete(key.id)}
              />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

// components/features/admin/AIKeyRegisterModal.tsx
export function AIKeyRegisterModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState<CreateAIKeyRequest>({});
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  
  const handleValidate = async () => {
    const result = await api.post(`/admin/ai-keys/validate`, formData);
    setValidation(result);
  };
  
  const handleSubmit = async () => {
    await api.post(`/admin/ai-keys`, formData);
    onSuccess();
    onClose();
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Register New AI API Key</DialogTitle>
        </DialogHeader>
        <Form>
          <FormField label="Service" component={<ServiceSelect />} />
          <FormField label="Key Name" component={<TextInput />} />
          <FormField label="API Key" component={<PasswordInput />} />
          <FormField label="Monthly Quota" component={<NumberInput />} />
          <FormField label="Monthly Budget" component={<CurrencyInput />} />
          <FormField label="Priority" component={<PrioritySlider />} />
          <FormField label="Active" component={<Toggle />} />
          
          <div className="flex gap-2">
            <Button onClick={handleValidate} variant="outline">
              Validate Key
            </Button>
            {validation && (
              <ValidationResult result={validation} />
            )}
          </div>
        </Form>
        <DialogFooter>
          <Button onClick={handleSubmit} disabled={!validation?.isValid}>
            Save Key
          </Button>
          <Button onClick={onClose} variant="outline">
            Cancel
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// components/features/admin/AIKeyDashboard.tsx
export function AIKeyDashboard() {
  const { data: overview } = useQuery(() => api.get('/admin/ai-keys/dashboard/overview'));
  const { data: costs } = useQuery(() => api.get('/admin/ai-keys/dashboard/costs'));
  
  return (
    <div className="space-y-6">
      <SummaryCards data={overview?.summary} />
      <ServiceStatusCards data={overview?.status} />
      <UsageChart data={costs?.daily_trend} />
      <CostChart data={costs?.by_service} />
      <AlertsList alerts={overview?.alerts} />
    </div>
  );
}
```

#### Sprint 2.3: API 통합 (Day 4-5)
```typescript
// lib/api/ai-keys.ts
export const aiKeysApi = {
  // 키 관리
  create: (data: CreateAIKeyRequest) =>
    api.post('/admin/ai-keys', data),
  
  list: (params: ListParams) =>
    api.get('/admin/ai-keys', { params }),
  
  get: (keyId: string) =>
    api.get(`/admin/ai-keys/${keyId}`),
  
  update: (keyId: string, data: UpdateAIKeyRequest) =>
    api.put(`/admin/ai-keys/${keyId}`, data),
  
  delete: (keyId: string, reason?: string) =>
    api.delete(`/admin/ai-keys/${keyId}`, { data: { reason } }),
  
  // 검증
  validate: (keyId: string) =>
    api.post(`/admin/ai-keys/${keyId}/validate`),
  
  // 사용량
  getUsage: (keyId: string, dateFrom: string, dateTo: string) =>
    api.get(`/admin/ai-keys/${keyId}/usage`, {
      params: { date_from: dateFrom, date_to: dateTo }
    }),
  
  // 대시보드
  getDashboardOverview: () =>
    api.get('/admin/ai-keys/dashboard/overview'),
  
  getCosts: (month?: string) =>
    api.get('/admin/ai-keys/dashboard/costs', {
      params: { month }
    }),
  
  // 로그
  getAuditLogs: (params: LogParams) =>
    api.get('/admin/ai-keys/logs', { params }),
};
```

#### Sprint 2.4: 테스트 (Day 5)
```typescript
// components/__tests__/AIKeyTable.test.tsx
describe('AIKeyTable', () => {
  it('renders key list', () => {
    const keys = [
      { id: '1', serviceName: 'openai', keyName: 'GPT-4' },
    ];
    render(<AIKeyTable keys={keys} />);
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });
});

// api/__tests__/ai-keys.test.ts
describe('AI Keys API', () => {
  it('should create new key', async () => {
    const response = await aiKeysApi.create({
      serviceName: 'openai',
      keyName: 'Test Key',
      apiKey: 'sk-test',
    });
    expect(response.data.id).toBeDefined();
  });
});
```

---

## 9. 테스트 전략

### 9.1 단위 테스트 (Unit Tests)

#### Backend Services
```python
# tests/test_ai_key_service.py
class TestAIKeyService:
    @pytest.mark.asyncio
    async def test_create_key_success(self):
        # Given
        service = AIKeyService(db)
        request = CreateAIKeyRequest(
            service_name="openai",
            key_name="Test Key",
            api_key="sk-test123456789012345"
        )
        
        # When
        result = await service.create_key(request)
        
        # Then
        assert result.id is not None
        assert result.is_valid is True
        assert result.service_name == "openai"
    
    @pytest.mark.asyncio
    async def test_encrypt_api_key(self):
        # API 키 암호화 확인
        key = "sk-secret"
        encrypted = encrypt_api_key(key)
        decrypted = decrypt_api_key(encrypted)
        assert decrypted == key
    
    @pytest.mark.asyncio
    async def test_delete_key_in_use(self):
        # 사용 중인 키 삭제 시도
        service = AIKeyService(db)
        key = await create_test_key_with_usage()
        
        with pytest.raises(KeyInUseError):
            await service.delete_key(key.id)
```

### 9.2 통합 테스트 (Integration Tests)

#### API Endpoints
```python
# tests/test_admin_ai_keys_api.py
@pytest.mark.asyncio
class TestAdminAIKeysAPI:
    async def test_create_key_endpoint(self, client: AsyncClient):
        # POST /api/v1/admin/ai-keys
        response = await client.post(
            "/api/v1/admin/ai-keys",
            json={
                "service_name": "openai",
                "key_name": "Test",
                "api_key": "sk-test"
            }
        )
        assert response.status_code == 201
        assert response.json()["data"]["id"]
    
    async def test_list_keys_with_filters(self, client: AsyncClient):
        # GET /api/v1/admin/ai-keys?service=openai&is_active=true
        response = await client.get(
            "/api/v1/admin/ai-keys?service=openai&is_active=true"
        )
        assert response.status_code == 200
        assert len(response.json()["data"]) >= 0
    
    async def test_validate_key_endpoint(self, client: AsyncClient):
        # POST /api/v1/admin/ai-keys/{key_id}/validate
        key = await create_test_key()
        response = await client.post(
            f"/api/v1/admin/ai-keys/{key.id}/validate"
        )
        assert response.status_code == 200
        assert response.json()["data"]["is_valid"] in [True, False]
```

### 9.3 E2E 테스트 (End-to-End Tests)

#### Workflow Tests
```python
# tests/test_ai_key_workflow.py
@pytest.mark.asyncio
async def test_complete_key_lifecycle():
    """키 등록 → 검증 → 사용 → 삭제 전체 워크플로우"""
    client = AsyncClient(app=app)
    
    # 1. 키 등록
    create_resp = await client.post(
        "/api/v1/admin/ai-keys",
        json={"service_name": "openai", "key_name": "Prod", "api_key": "sk-..."}
    )
    key_id = create_resp.json()["data"]["id"]
    
    # 2. 키 검증
    validate_resp = await client.post(
        f"/api/v1/admin/ai-keys/{key_id}/validate"
    )
    assert validate_resp.json()["data"]["is_valid"] is True
    
    # 3. 사용량 조회
    usage_resp = await client.get(
        f"/api/v1/admin/ai-keys/{key_id}/usage"
    )
    assert usage_resp.status_code == 200
    
    # 4. 키 삭제
    delete_resp = await client.delete(
        f"/api/v1/admin/ai-keys/{key_id}"
    )
    assert delete_resp.status_code == 200
```

### 9.4 테스트 커버리지 목표

| 모듈 | 커버리지 |
|------|---------|
| Services | 95% |
| API Routers | 90% |
| Models | 85% |
| Frontend Components | 80% |
| **전체** | **85%** |

---

## 10. 배포 및 모니터링

### 10.1 배포 체크리스트

- [ ] 데이터베이스 마이그레이션 완료
- [ ] Backend 단위/통합 테스트 통과 (커버리지 95%)
- [ ] Frontend 컴포넌트 테스트 통과
- [ ] E2E 테스트 통과
- [ ] 보안 검토 완료
  - [ ] API 키 암호화 확인
  - [ ] 접근 제어 확인
  - [ ] 입력 검증 확인
- [ ] 성능 테스트 통과 (응답시간 < 2초)
- [ ] 환경 변수 설정 완료
- [ ] 모니터링 설정 완료

### 10.2 모니터링

#### 주요 메트릭
- API 응답 시간 (P50, P95, P99)
- 에러율 (API 호출 실패 %)
- 키 검증 성공률
- 사용량 데이터 수집 지연 시간

#### 알림 설정
```python
# API 응답 시간이 2초 이상이면 알림
response_time_alert = "response_time_p99 > 2000"

# 에러율이 5%를 초과하면 알림
error_rate_alert = "error_rate > 5"

# 키 검증 실패율이 증가하면 알림
validation_failure_alert = "validation_failure_rate > 10"
```

### 10.3 로깅

#### 로그 레벨
```python
logger.debug("Encrypting API key...")
logger.info("AI key created: key_123")
logger.warning("API key approaching quota limit: 85%")
logger.error("Failed to validate OpenAI key: Invalid API key")
logger.critical("Database connection lost!")
```

---

## 11. 향후 확장 계획

### Phase 2 (7월-8월)
- [ ] 자동 키 로테이션
- [ ] 다중 데이터센터 지원
- [ ] AI 서비스별 고급 설정
- [ ] Webhook 알림

### Phase 3 (8월-9월)
- [ ] 머신러닝 기반 이상 탐지
- [ ] 비용 최적화 제안
- [ ] 자동 장애 조치 (Failover)

---

## 12. 참고 자료

- FastAPI 공식 문서: https://fastapi.tiangolo.com/
- SQLAlchemy 공식 문서: https://docs.sqlalchemy.org/
- Cryptography 라이브러리: https://cryptography.io/
- OpenAI API: https://platform.openai.com/docs/
- Anthropic Claude API: https://console.anthropic.com/

---

**문서 버전**: 1.0.0  
**예상 기간**: 3주 (Phase 1 내)  
**예상 완료**: 2026-07-09  
**작성자**: Claude Code  
**최종 수정**: 2026-06-18
