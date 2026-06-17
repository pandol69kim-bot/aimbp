# UI/UX 빠른 참고 가이드

> `DESIGN_SYSTEM.md`의 핵심 요소를 빠르게 참고할 수 있는 체크리스트입니다.

---

## 🎨 색상 팔레트 (Color Palette)

### 빠른 참고

```typescript
// Primary Actions (주요 행동)
bg-primary-600    // Purple #7c3aed - Button, Links, Highlights
text-primary-500  // Lighter purple - Hover state

// Secondary (보조 행동)
bg-secondary-600  // Blue #3b82f6
text-secondary-500

// Accent (강조)
bg-accent-600     // Cyan #06b6d4 - Status indicators
text-accent-500

// Destructive (위험)
bg-red-600        // Red #ef4444 - Delete, Error, Warning
text-red-500

// Text & Background
bg-[#0f0f0f]      // Page background (darkest)
bg-dark-900       // Section background
text-white        // Primary text
text-gray-400     // Secondary text
text-gray-500     // Muted text
border-white/10   // Border color (1px)
```

---

## 🔤 타이포그래피 (Typography)

### 사용 패턴

```html
<!-- Page Title -->
<h1 class="text-3xl font-bold text-white">제목</h1>

<!-- Section Title -->
<h2 class="section-title">섹션 제목</h2>

<!-- Section Description -->
<p class="section-desc">섹션 설명</p>

<!-- Body Text -->
<p class="text-base text-white">본문 텍스트</p>

<!-- Secondary Text -->
<span class="text-sm text-gray-400">보조 텍스트</span>

<!-- Small Label -->
<label class="text-xs font-medium text-gray-500">라벨</label>
```

### 텍스트 크기 빠른 맵

| HTML | Size | 사용처 |
|------|------|--------|
| h1 | 2.25rem (36px) | 페이지 제목 |
| h2 | 1.875rem (30px) | 섹션 제목 |
| h3 | 1.5rem (24px) | 서브 제목 |
| p | 1rem (16px) | 본문 |
| span | 0.875rem (14px) | 보조 텍스트 |
| label | 0.75rem (12px) | 라벨 |

---

## 🎯 버튼 (Buttons)

### 기본 패턴

```tsx
// 주요 행동 (기본)
<Button>기본 버튼</Button>

// 보조 행동
<Button variant="secondary">보조 버튼</Button>

// 중립 행동
<Button variant="outline">중립 버튼</Button>

// 최소 강조
<Button variant="ghost">유령 버튼</Button>

// 위험 행동
<Button variant="destructive">삭제</Button>

// 링크 스타일
<Button variant="link">링크</Button>

// 아이콘만
<Button variant="ghost" size="icon">
  <Icon size={24} />
</Button>
```

### 크기별

```tsx
<Button size="sm">작음 (h-8)</Button>
<Button size="md">기본 (h-10)</Button>
<Button size="lg">큼 (h-12)</Button>
<Button size="icon">아이콘 (h-9)</Button>
```

### 로딩 상태

```tsx
<Button isLoading>로딩 중...</Button>  // 스핀 애니메이션 자동
```

---

## 📦 카드 (Cards)

### 기본 구조

```tsx
<Card className="glass-dark">
  <CardHeader>
    <h3>제목</h3>
  </CardHeader>
  <CardContent>
    {/* 내용 */}
  </CardContent>
</Card>
```

### 커스텀 스타일

```tsx
// Glass effect (투명)
<div className="glass p-6">내용</div>

// Glass Dark (어둡고 투명)
<div className="glass-dark p-6">내용</div>
```

---

## 🎨 유틸리티 클래스 (Utilities)

### Glass 효과

```html
<!-- 기본 글래스 (밝음) -->
<div class="glass">...</div>

<!-- 어두운 글래스 (권장) -->
<div class="glass-dark">...</div>
```

### 그래디언트 텍스트

```html
<h1 class="text-gradient">그래디언트 제목</h1>
<!-- Gradient: Purple → Cyan -->
```

### 페이지 컨테이너

```html
<div class="page-container">
  <!-- max-w-7xl, mx-auto, p-6 -->
</div>
```

---

## 📏 간격 (Spacing)

### 기본 단위: 4px

```tsx
// Padding
<div class="p-6">  {/* 24px all sides */}
  <div class="px-4 py-2">  {/* 16px horizontal, 8px vertical */}
```

### 마진

```tsx
<h2 class="mb-1">제목</h2>      {/* margin-bottom: 4px */}
<p class="mb-6">설명</p>        {/* margin-bottom: 24px */}
<div class="space-y-4">        {/* gap: 16px between children */}
```

---

## 📱 반응형 디자인 (Responsive)

### 브레이크포인트 빠른 참고

```tsx
// 모바일 우선
<div class="
  text-lg                    // 모바일 기본
  md:text-xl                 // 768px+: 더 크게
  lg:text-2xl                // 1024px+: 더욱 크게
">

// 숨기기/표시
<div class="hidden md:block">  {/* 모바일 숨김, 768px+에서 표시 */}

// 그리드 레이아웃
<div class="
  grid grid-cols-1           // 모바일: 1열
  md:grid-cols-2             // 768px+: 2열
  lg:grid-cols-3             // 1024px+: 3열
  gap-6
">
```

---

## ✨ 애니메이션 (Animations)

### 기본 전환

```tsx
<Button class="hover:shadow-lg transition-all duration-200">
  마우스 오버 시 부드러운 효과
</Button>
```

### 로딩 애니메이션

```tsx
// 기본 스핀 (1초)
<div class="animate-spin">
  <svg>...</svg>
</div>

// 느린 스핀 (3초)
<div class="animate-spin-slow">
  <svg>...</svg>
</div>

// 호흡 효과 (3초)
<div class="animate-pulse-slow">
  상태 표시기
</div>
```

---

## ♿ 접근성 (Accessibility)

### 포커스 상태 필수

```tsx
className="
  focus-visible:outline-none
  focus-visible:ring-2
  focus-visible:ring-primary-500
  focus-visible:ring-offset-2
  focus-visible:ring-offset-dark-800
"
```

### ARIA 라벨 (아이콘 버튼)

```tsx
<button aria-label="메뉴 닫기">
  <X size={24} />
</button>
```

### Semantic HTML

```html
<!-- ✅ GOOD -->
<header>...</header>
<nav>...</nav>
<main>...</main>
<section>...</section>
<button>클릭</button>

<!-- ❌ BAD -->
<div onClick={}>클릭</div>
```

---

## ⚡ 성능 최적화 (Performance)

### 이미지 크기 필수

```tsx
<img
  src="image.jpg"
  width={1200}
  height={600}
  loading="lazy"
/>
```

### 동적 CSS 금지

```tsx
// ✅ GOOD
className="text-lg font-semibold"

// ❌ BAD (Tailwind가 감지 못함)
className={`text-${size} font-${weight}`}
```

---

## 🚫 금지사항 (Do NOT)

| ❌ 금지 | ✅ 대신 |
|--------|--------|
| 하드코딩된 색상 (`#fff`) | 정의된 색상 클래스 사용 |
| 임의의 간격 값 | 4px 배수 사용 |
| 모든 것을 div로 구성 | Semantic HTML 사용 |
| 포커스 상태 생략 | focus-visible 링 추가 |
| 과도한 애니메이션 | 200ms 전환 사용 |

---

## 📋 개발 체크리스트

### UI 개발 시작 전

- [ ] `DESIGN_SYSTEM.md` 읽음
- [ ] 색상 선택 (정의된 팔레트에서)
- [ ] 레이아웃 스케치 (반응형 고려)

### 개발 중

- [ ] 기존 컴포넌트 재사용 확인
- [ ] 포커스 상태 구현
- [ ] 반응형 테스트 (3 브레이크포인트 이상)

### 완성 후

- [ ] 색상 대비 확인
- [ ] 마우스/키보드 네비게이션 테스트
- [ ] 모든 상태 확인 (정상, 호버, 포커스, 비활성화)
- [ ] 이미지 크기 명시
- [ ] 애니메이션 목적성 확인

---

## 🔗 주요 파일 위치

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                    # 기본 컴포넌트
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
│   │   ├── layout/                # 레이아웃
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   └── common/                # 공통 컴포넌트
│   ├── app/
│   │   └── globals.css            # 글로벌 스타일 & 커스텀 유틸
│   └── lib/
│       └── utils.ts               # 유틸리티 함수
├── tailwind.config.ts             # Tailwind 설정
└── next.config.ts
```

---

## 💡 팁

1. **재사용 먼저**: 새 컴포넌트 만들기 전에 기존 것 확인
2. **반응형 먼저**: 모바일 우선으로 개발
3. **접근성**: 포커스 상태는 필수 (기능 요소)
4. **성능**: 큰 이미지는 lazy loading 사용
5. **일관성**: 이 가이드를 따르는 것이 유지보수를 쉽게 함

---

**최종 업데이트**: 2026-06-17
**참고**: `DESIGN_SYSTEM.md` 전체 버전 참고
