# Frontend — 기술스택 명세

> React + React Three Fiber 기반. 우주 탐색 뷰(Three.js 씬)와 블로그 UI를 하나의 React 앱에서 구성한다.

---

## 핵심 스택

| 역할 | 기술 | 선택 이유 |
|------|------|----------|
| UI 프레임워크 | **React 19** | 컴포넌트 기반, R3F와 동일 생태계 |
| 빌드 도구 | **Vite** | CRA보다 빠른 HMR, ESM 네이티브 |
| 언어 | **TypeScript** | Three.js 타입 지원, 대형 씬 관리에 필수 |
| 3D 렌더링 | **@react-three/fiber (R3F)** | Three.js를 React 컴포넌트로 선언적 관리 |
| 3D 헬퍼 | **@react-three/drei** | 카메라 컨트롤, 글로우, 텍스트, 파티클 등 |
| 후처리 효과 | **@react-three/postprocessing** | 블룸(Bloom), 글로우 효과 |
| 상태 관리 | **Zustand** | Three.js 렌더 루프와 궁합 좋음, 보일러플레이트 없음 |
| 라우팅 | **React Router v7** | URL 기반 씬 전환 (`/galaxy/:id`, `/stars/:slug`) |
| 스타일링 | **TailwindCSS v4** | 블로그 UI, 오버레이 패널 스타일링 |
| 마크다운 렌더링 | **react-markdown** + **remark-gfm** | 항성 상세 포스트 렌더링 |
| 마크다운 에디터 | **@uiw/react-md-editor** | 분할 뷰 에디터(편집+미리보기) |
| 커맨드 팔레트 | **cmdk** | Cmd+K 항성 검색 → fly-in |
| HTTP 클라이언트 | **TanStack Query v5** + **axios** | API 캐싱, 로딩 상태 관리 |
| 폼 관리 | **React Hook Form** + **zod** | 항성 생성/수정 폼 검증 |
| 애니메이션 | **@react-spring/three** | R3F 내 스프링 기반 트랜지션 |

---

## 렌더링 씬 구조

### URL 라우팅 구조

```
/                          → 랜딩 페이지 (비로그인) or 개인 우주 리다이렉트
/auth/login                → 로그인
/auth/register             → 회원가입
/universe                  → 본인 개인 우주 (로그인 필요)
/galaxy/:id                → 본인 은하 뷰 (로그인 필요)
/:username/stars/:slug     → 공개 스타 페이지 (비로그인 접근 가능)
/explore                   → 공개 우주 (모든 published 스타)
```

### 줌 레벨 3단계

```
[은하단 뷰]  /universe
  ├── 성운 안개로 감싸진 은하 클러스터들 표시
  ├── 항성 미표시
  └── 은하 클릭 → React Router → [은하 뷰] + 진입 애니메이션

[은하 뷰]   /galaxy/:id
  ├── 해당 은하의 항성 전체 표시 (UMAP 2D 좌표 기반, z=0 고정)
  ├── 웜홀 연결선 표시 (임계값 이상 유사도, Phase 2)
  ├── 항성 이름 레이블 (줌 임계값 이상: 항상 표시 / 미만: hover만)
  └── 항성 클릭 → 카메라 fly-in + 우측 패널 오픈

[항성 뷰]   /galaxy/:id + 우측 패널
  ├── 클릭한 항성 중심으로 카메라 스프링 이동
  ├── 인접 항성 + 연결선 하이라이트
  └── 우측 패널: 마크다운 블로그 포스트 + 편집
```

### 카메라 컨트롤
- **MapControls** (drei) — 2D 탑뷰 팬/줌 (Google Maps 방식)
- 터치 지원: 핀치 줌, 단일 터치 팬

---

## 항성 시각 표현

### 생애주기별 색상/크기

| 상태 | 색상 | 크기 | 글로우 |
|------|------|------|--------|
| 주계열성 (Active) | `#A8D8FF` 청백색 | 1.4x | 강함 |
| 황색 왜성 (Normal) | `#FFD580` 노란색 | 1.0x | 중간 |
| 적색 거성 (Fading) | `#FF6B35` 붉은색 | 1.6x (팽창) | 약하고 흐릿 |
| 백색 왜성 (Forgotten) | `#E8E8E8` 흰색 | 0.6x | 거의 없음 |
| 암흑 물질 (Lost) | `#1A1A2E` 거의 검정 | 0.3x | 없음 |

### Nova 애니메이션
- 유효 조회 30초 완료 시 → API 호출 후 연결 항성들 0.5초 반짝임
- `@react-spring/three`로 opacity, scale 스프링 애니메이션

---

## 인증 플로우

```
Access Token → 메모리(Zustand store)에 저장
  - axios 인터셉터로 모든 요청에 자동 첨부
  - 401 응답 시 → /auth/refresh 자동 호출 → Access Token 갱신

Refresh Token → httpOnly 쿠키 (프론트엔드에서 직접 접근 불가)
  - 서버에서 Set-Cookie로 발급

로그인 상태 유지:
  - 페이지 새로고침 시 → /auth/refresh 호출해서 Access Token 복구
  - Refresh Token 만료 시 → 로그인 페이지로 리다이렉트
```

---

## 디렉토리 구조 (예정)

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx              # 라우팅 루트
│   ├── pages/
│   │   ├── UniversePage.tsx  # 은하단 뷰
│   │   ├── GalaxyPage.tsx    # 은하 뷰
│   │   ├── StarPage.tsx      # 항성 상세 (블로그 포스트)
│   │   └── LoginPage.tsx
│   ├── components/
│   │   ├── three/           # R3F 3D 컴포넌트
│   │   │   ├── StarMesh.tsx
│   │   │   ├── GalaxyCluster.tsx
│   │   │   ├── WormholeEdge.tsx
│   │   │   └── ParticleField.tsx  # 배경 별빛
│   │   └── ui/              # Tailwind 일반 UI
│   │       ├── StarPanel.tsx     # 항성 상세 패널
│   │       ├── MarkdownEditor.tsx
│   │       └── Navbar.tsx
│   ├── stores/              # Zustand 스토어
│   │   ├── authStore.ts
│   │   ├── galaxyStore.ts
│   │   └── starStore.ts
│   ├── hooks/               # TanStack Query 훅
│   ├── lib/
│   │   ├── axios.ts         # axios 인스턴스 + 인터셉터
│   │   └── queryClient.ts
│   └── types/               # TypeScript 타입 정의
├── public/
├── index.html
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

---

## 30초 체류 타이머 플로우

```
항성 상세 패널 열림
  → 프론트엔드 타이머 시작 (30초)
  → 30초 완료 & 패널 닫히지 않음
    → POST /stars/:id/view { duration: 30, is_valid: true } 호출
    → 백엔드: 에너지 기록 + 상위 3~5 유사 항성에 Nova 에너지 전파
    → 프론트엔드: Nova 애니메이션 트리거 (연결 항성 0.5초 반짝임)
  → 패널 닫히면 타이머 리셋 (30초 미달 시 조회 미기록)
```

## 스코프 외 (명시적 제외)

- 모바일 우주 탐색 뷰 (데스크탑 전용)
- 블로그 포스트 페이지(`/:username/stars/:slug`)는 최소한의 반응형만
- 행성(Planet) 계층 구조 (Phase 3+)
