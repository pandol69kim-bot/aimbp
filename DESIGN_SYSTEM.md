# AIMBP UI/UX 디자인 시스템 가이드라인

> 프로젝트의 모든 UI/UX 개발이 따라야 할 표준 가이드라인입니다. 이 문서는 표준 작업을 정의하며 새로운 기능 개발 시 이를 참고하여 일관된 사용자 경험을 제공합니다.

---

## 1. 디자인 철학

### 1.1 핵심 원칙

- **다크 럭셔리 (Dark Luxury)**: 고급스럽고 세련된 다크 테마
- **미니멀리즘**: 불필요한 요소를 제거하고 핵심만 강조
- **글래스모픽**: 반투명한 글래스 효과로 깊이감 표현
- **목적성**: 모든 디자인 결정은 사용자 경험을 개선해야 함

### 1.2 시각적 계층

1. **배경 (Background)**: 가장 어두운 레이어, 컨텐츠의 기반
2. **컨테이너 (Container)**: 배경보다 밝은 섹션, 글래스 효과 적용
3. **컴포넌트 (Component)**: 상호작용 가능한 UI 요소
4. **텍스트 (Text)**: 최상단 레이어, 명확한 가독성

---

## 2. 색상 시스템

### 2.1 팔레트

#### 기본 색상

| 색상 | Hex | RGB | 사용처 |
|------|------|------|--------|
| **Primary** (보라색) | `#7c3aed` | `124 58 237` | 주요 버튼, 강조, 링크 |
| **Secondary** (파란색) | `#3b82f6` | `59 130 246` | 보조 버튼, 정보성 요소 |
| **Accent** (시안) | `#06b6d4` | `6 182 212` | 강조 포인트, 상태 표시 |
| **Destructive** (빨강) | `#ef4444` | `239 68 68` | 위험, 삭제, 오류 |

#### 배경 색상

| 레벨 | Hex | 사용처 |
|------|------|--------|
| **Background** | `#0f0f0f` | 페이지 배경 |
| **Card Dark** | `#1a1a2e` | 카드, 섹션 배경 |
| **Overlay** | `#1a1a2e` (80% opacity) | 모달, 드롭다운 |

#### 텍스트 색상

| 레벨 | Hex | 사용처 |
|------|------|--------|
| **Primary Text** | `#ffffff` | 주요 텍스트 |
| **Secondary Text** | `#9ca3af` | 보조 텍스트, 라벨 |
| **Muted Text** | `#6b7280` | 비활성화, 힌트 |

#### 테두리 색상

| 스타일 | RGBA | 사용처 |
|-------|------|--------|
| **Base** | `rgba(255, 255, 255, 0.1)` | 기본 보더 |
| **Hover** | `rgba(255, 255, 255, 0.2)` | 호버 상태 |
| **Focus** | Primary Color | 포커스 상태 |

### 2.2 색상 활용 규칙

```typescript
// ✅ GOOD: 의미 있는 색상 사용
<Button variant="destructive">삭제</Button>  // 빨강: 위험 행동
<Button variant="primary">저장</Button>      // 보라: 주요 행동

// ❌ BAD: 무의미한 색상 사용
<Button style={{ color: '#random-color' }}>  // 일관성 없음
```

---

## 3. 타이포그래피

### 3.1 타입 스케일

기본 폰트: **시스템 폰트 스택**

| 레벨 | 크기 | 두께 | 사용처 |
|------|------|------|--------|
| **Hero** | 2.25rem (36px) | 700 | 페이지 제목 |
| **Title** | 1.875rem (30px) | 600 | 섹션 제목 |
| **Large** | 1.5rem (24px) | 600 | 서브 제목 |
| **Body** | 1rem (16px) | 400 | 본문 텍스트 |
| **Small** | 0.875rem (14px) | 400 | 보조 텍스트 |
| **Tiny** | 0.75rem (12px) | 500 | 라벨, 뱃지 |

### 3.2 라인 높이

- **Title**: 1.2 (타이트한 레이아웃)
- **Body**: 1.5 (가독성)
- **Small**: 1.4 (밀집도)

### 3.3 사용 예시

```html
<!-- Page Title -->
<h1 class="text-3xl font-bold text-white">대시보드</h1>

<!-- Section Title -->
<h2 class="section-title">최근 앨범</h2>

<!-- Body Text -->
<p class="text-base text-white">설명 텍스트</p>

<!-- Secondary Text -->
<span class="text-sm text-gray-400">보조 정보</span>
```

---

## 4. 간격 (Spacing)

### 4.1 스페이싱 스케일

기본 단위: **4px**

| 레벨 | Rem | Px | 사용처 |
|------|-----|-----|--------|
| **xs** | 0.25rem | 4px | 아이콘 간격 |
| **sm** | 0.5rem | 8px | 좁은 간격 |
| **md** | 1rem | 16px | 기본 간격 |
| **lg** | 1.5rem | 24px | 섹션 간격 |
| **xl** | 2rem | 32px | 큰 섹션 간격 |
| **2xl** | 3rem | 48px | 매우 큰 간격 |

### 4.2 일반적인 패턴

```tsx
// 컨테이너
<div class="p-6">            {/* 수평: 24px */}
  {/* 섹션 제목 + 설명 */}
  <h2 class="text-xl font-semibold mb-1">제목</h2>
  <p class="text-sm text-gray-400 mb-6">설명</p>

  {/* 컨텐츠 */}
  <div class="space-y-4">   {/* 아이템 간 16px */}
    {/* 아이템들 */}
  </div>
</div>
```

---

## 5. 컴포넌트 디자인

### 5.1 버튼 (Button)

#### 스타일 시스템

```typescript
// CVA 패턴으로 정의된 버튼 스타일
const buttonVariants = {
  variant: {
    default:     'Primary 버튼 - 주요 행동',
    secondary:   'Secondary 버튼 - 보조 행동',
    outline:     'Outline 버튼 - 중립적 행동',
    ghost:       'Ghost 버튼 - 최소한의 강조',
    destructive: 'Destructive 버튼 - 위험 행동',
    accent:      'Accent 버튼 - 특수 강조',
    link:        'Link 버튼 - 텍스트 링크',
  },
  size: {
    sm:   'h-8 px-3 text-xs',
    md:   'h-10 px-4 text-sm',
    lg:   'h-12 px-6 text-base',
    icon: 'h-9 w-9 p-0',
  }
}
```

#### 사용 예시

```tsx
// ✅ GOOD
<Button variant="default" size="md">저장</Button>
<Button variant="destructive" size="sm">삭제</Button>
<Button variant="ghost" size="icon"><Icon /></Button>

// ❌ BAD
<button style={{ color: 'blue' }}>버튼</button>  // CVA 미사용
<Button>                                         // 기본값 사용
```

#### 상태 표현

| 상태 | 스타일 |
|------|--------|
| **Normal** | 기본 배경색 |
| **Hover** | 배경색 -50 조도 |
| **Active** | 배경색 +50 조도 |
| **Disabled** | 불투명도 50%, 포인터 없음 |
| **Loading** | 스핀 애니메이션 + "처리 중..." 텍스트 |

### 5.2 입력 필드 (Input)

#### 기본 스타일

```tsx
<input
  className="h-10 px-3 rounded-lg
    border border-white/10
    bg-white/5
    text-white
    placeholder:text-gray-500
    focus:outline-none focus:ring-1 focus:ring-primary-500
    transition-all"
  placeholder="입력..."
/>
```

#### 상태 표현

| 상태 | 스타일 |
|------|--------|
| **Normal** | 연한 보더, 투명 배경 |
| **Focus** | Primary 컬러 링, 보더 컬러 변경 |
| **Error** | Red 링 + 에러 메시지 |
| **Disabled** | 불투명도 50% |

### 5.3 카드 (Card)

#### 기본 구조

```tsx
<Card className="glass-dark p-6">
  <CardHeader className="mb-4">
    <h3 className="text-lg font-semibold">제목</h3>
  </CardHeader>
  <CardContent>
    {/* 컨텐츠 */}
  </CardContent>
</Card>
```

#### 스타일 특징

- 배경: `rgba(26, 26, 46, 0.8)` (glass-dark)
- 테두리: `1px solid rgba(255, 255, 255, 0.1)`
- 배경필터: `blur(8px)`
- 모서리: `rounded-lg` (12px)

### 5.4 배지 (Badge)

#### 타입별 사용

```tsx
// ✅ 상태 표시
<Badge variant="success">완료</Badge>
<Badge variant="warning">진행 중</Badge>
<Badge variant="error">오류</Badge>
<Badge variant="info">정보</Badge>

// ✅ 태그
<Badge variant="outline">태그</Badge>
```

### 5.5 커스텀 유틸리티

#### Glass 효과

```css
/* 기본 글래스 */
.glass {
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(4px);
}

/* 어두운 글래스 */
.glass-dark {
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(8px);
}
```

#### 그래디언트 텍스트

```tsx
<h1 className="text-gradient">
  그래디언트 제목
</h1>

// CSS
.text-gradient {
  background: linear-gradient(to right, #a78bfa, #22d3ee);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

---

## 6. 레이아웃

### 6.1 페이지 구조

```
┌─────────────────────────────────┐
│  Header (h-16)                  │  ← 네비게이션, 검색, 알림
├─────────────────────────────────┤
│  Sidebar (w-64)  │   Content    │  ← 사이드바 + 메인 컨텐츠
│                  │              │
│                  │ page-container│ ← max-w-7xl, p-6
└─────────────────────────────────┘
```

### 6.2 페이지 컨테이너

```tsx
<div className="page-container">
  {/* max-w-7xl mx-auto p-6 */}
  <h1 className="section-title">제목</h1>
  <p className="section-desc">설명</p>
  
  {/* 컨텐츠 */}
</div>
```

### 6.3 그리드 시스템

```tsx
// 반응형 그리드
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* 모바일: 1열 */}
  {/* 태블릿: 2열 */}
  {/* 데스크톱: 3열 */}
</div>
```

---

## 7. 애니메이션 & 전환

### 7.1 기본 애니메이션

| 애니메이션 | 지속시간 | 사용처 |
|-----------|---------|--------|
| **transition-all** | 200ms | 상태 변경 |
| **pulse** | 2s | 주의 집중 필요 |
| **pulse-slow** | 3s | 부드러운 호흡 효과 |
| **spin** | 1s | 로딩 (기본) |
| **spin-slow** | 3s | 느린 로딩 |

### 7.2 사용 예시

```tsx
// 버튼 호버
<Button className="hover:shadow-lg transition-all duration-200" />

// 로딩 스피너
<Spinner className="animate-spin" />

// 부드러운 호흡
<Indicator className="animate-pulse-slow" />
```

### 7.3 Transition 규칙

```css
/* ✅ GOOD: 200ms 기본 전환 */
transition-all duration-200

/* ✅ GOOD: 상태별 특정 전환 */
transition-colors duration-150

/* ❌ BAD: 과도한 애니메이션 */
transition-all duration-1000
```

---

## 8. 반응형 디자인

### 8.1 브레이크포인트

| 크기 | 너비 | 용도 |
|------|------|------|
| **sm** | 640px | 스마트폰 가로 |
| **md** | 768px | 태블릿 세로 |
| **lg** | 1024px | 태블릿 가로 |
| **xl** | 1280px | 데스크톱 |
| **2xl** | 1536px | 대형 데스크톱 |

### 8.2 반응형 패턴

```tsx
// 모바일 우선
<div className="
  grid grid-cols-1      // 모바일: 1열
  md:grid-cols-2        // 태블릿: 2열
  lg:grid-cols-3        // 데스크톱: 3열
  gap-4
  md:gap-6
">

// 숨기기/표시
<div className="
  hidden sm:block       // 640px 이상에서 표시
  md:hidden lg:block    // 태블릿에선 숨김, 데스크톱에서 표시
">

// 텍스트 크기
<h1 className="
  text-2xl
  md:text-3xl
  lg:text-4xl
">
```

---

## 9. 접근성 (Accessibility)

### 9.1 색상 대비

- **일반 텍스트**: WCAG AA 표준 이상 (최소 4.5:1)
- **큰 텍스트**: 최소 3:1 대비

### 9.2 포커스 상태

```tsx
// ✅ 모든 상호작용 요소는 포커스 링 포함
className="
  focus-visible:outline-none
  focus-visible:ring-2
  focus-visible:ring-primary-500
  focus-visible:ring-offset-2
  focus-visible:ring-offset-dark-800
"
```

### 9.3 Semantic HTML

```tsx
// ✅ GOOD: 의미있는 마크업
<header>...</header>
<nav>...</nav>
<main>...</main>
<section>...</section>
<button>클릭</button>

// ❌ BAD: div로 모든 것을 구성
<div onClick={}>클릭</div>
```

### 9.4 ARIA 라벨

```tsx
// ✅ 아이콘 버튼 라벨
<button aria-label="메뉴 닫기">
  <X size={24} />
</button>

// ✅ 섹션 라벨
<section aria-labelledby="section-title">
  <h2 id="section-title">제목</h2>
</section>
```

---

## 10. 성능 최적화

### 10.1 이미지 최적화

```tsx
// ✅ 명시적 크기 지정
<img
  src="image.jpg"
  alt="설명"
  width={1200}
  height={600}
  loading="lazy"
/>

// ✅ Next.js Image 컴포넌트
<Image
  src={image}
  alt="설명"
  width={1200}
  height={600}
  priority={false}
/>
```

### 10.2 CSS 최적화

```tsx
// ✅ Tailwind 클래스 사용 (동적 생성 금지)
className="text-lg font-semibold"

// ❌ 동적 스타일 생성 금지
className={`text-${size} font-${weight}`}
```

### 10.3 번들 최적화

```tsx
// ✅ 동적 임포트
const HeavyComponent = dynamic(() => import('./Heavy'), {
  loading: () => <LoadingSpinner />
})

// ✅ 트리 쉐이킹 가능한 임포트
import { Button, Card } from '@/components/ui'
```

---

## 11. 다크 모드

### 11.1 색상 모드 토글

```tsx
// ✅ CSS 변수 기반 (현재 시스템)
:root {
  --background: 15 15 15;
  --foreground: 255 255 255;
}

// Tailwind 지원
className="bg-background text-foreground"
```

### 11.2 절대 금지 사항

```tsx
// ❌ 하드코딩된 색상
<div style={{ backgroundColor: '#ffffff' }}>  // 라이트 모드만 보임
```

---

## 12. 코드 예시

### 12.1 완전한 컴포넌트 예시

```tsx
'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'

interface FeatureCardProps {
  title: string
  description: string
  onAction: () => void
}

export function FeatureCard({
  title,
  description,
  onAction
}: FeatureCardProps) {
  return (
    <Card className="glass-dark">
      <CardHeader className="mb-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-400 mb-6">{description}</p>
        <Button
          variant="primary"
          size="md"
          onClick={onAction}
          className="w-full"
        >
          작업 수행
        </Button>
      </CardContent>
    </Card>
  )
}
```

### 12.2 페이지 레이아웃 예시

```tsx
export default function Page() {
  return (
    <div className="page-container">
      {/* 제목 섹션 */}
      <div className="mb-8">
        <h1 className="section-title">페이지 제목</h1>
        <p className="section-desc">페이지 설명</p>
      </div>

      {/* 컨텐츠 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* 카드들 */}
      </div>
    </div>
  )
}
```

---

## 13. 체크리스트

### 13.1 새로운 UI 개발 시 확인사항

- [ ] 색상이 정의된 팔레트에서 선택되었는가?
- [ ] 타이포그래피가 정의된 스케일을 따르는가?
- [ ] 간격이 정의된 스페이싱 스케일을 사용하는가?
- [ ] 컴포넌트가 존재하는 것을 재사용하는가?
- [ ] 포커스 상태가 명시적으로 정의되었는가?
- [ ] 반응형 디자인이 모든 브레이크포인트에서 작동하는가?
- [ ] 색상 대비가 WCAG 표준을 충족하는가?
- [ ] 애니메이션이 목적을 가지고 있는가?

### 13.2 코드 리뷰 체크리스트

- [ ] 하드코딩된 색상값이 없는가?
- [ ] 일관된 컴포넌트 패턴을 사용했는가?
- [ ] 접근성 요구사항(ARIA, 포커스)을 충족하는가?
- [ ] 성능 최적화 가이드를 따랐는가?
- [ ] 이 디자인이 전체 시스템과 일관성이 있는가?

---

## 14. 참고 파일

- **컴포넌트 구현**: `frontend/src/components/`
- **스타일 설정**: `frontend/src/app/globals.css`
- **Tailwind 설정**: `frontend/tailwind.config.ts`
- **유틸리티 함수**: `frontend/src/lib/utils.ts`

---

## 15. 업데이트 로그

| 날짜 | 버전 | 변경사항 |
|------|------|---------|
| 2026-06-17 | v1.0 | 초기 디자인 시스템 문서 작성 |

---

**작성일**: 2026-06-17
**유지보수**: Claude Code
**상태**: Active
