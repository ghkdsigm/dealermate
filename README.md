# DealerMate (딜러/상사용 AI 업무 에이전트) - PoC

기존 **상사시스템/종사원 시스템**이 이미 제공하는 기능(매입차량조회, 원부/정비이력, 매물검색, 시세, 판매현황, 상담내역 등)을
**MCP 툴**로 래핑해서, 판매자(딜러/상사) 업무 흐름에서 바로 쓰는 형태로 만든 실무형 PoC 입니다.

- 추천: 고객 조건 입력 → 매물검색 호출 → 3개 정제 추천
- 비교표: 후보 매물 비교표 자동 생성
- 리스크: 원부/정비이력 기반 리스크 고지 멘트 생성
- 가격/협상: 시세 밴드 근거 제시 + 협상 스크립트
- 팔로업: 카톡/문자 문구 자동 생성

> 이 PoC는 **LLM을 실제로 호출하지 않고**, “의도(Intent) 분류 → MCP 툴 호출 → 템플릿 생성” 구조만 구현했습니다.
> 운영에서는 `services/api`에서 LLM을 붙이면 됩니다.

---

## 아키텍처 (Docker Compose)

- Postgres: 업무/로그 저장
- Redis: MCP 오케스트레이터 로그 저장(데모)
- FastAPI API: 인증/JWT, 상담(Deal) 관리, Assistant 엔드포인트
- MCP Orchestrator: 도구 라우팅, 마스킹, 호출 로그
- MCP Inventory/History/Pricing: 원천 도메인 연동용 툴 서버(현재는 데모 데이터)
- Nuxt 3 Frontend: 한 화면에서 Deal + Chat 기반 업무 수행

---

## 실행

```bash
cd dealermate
cp .env.example .env
docker compose up --build
```

- 프론트: `http://localhost:3000`
- API: `http://localhost:8001/docs`
- Orchestrator: `http://localhost:8002/docs`

### 데모 계정

- 딜러: `D001 / pass1234`
- 상사관리자: `M001 / pass1234`
- 어드민: `A001 / pass1234`

---

## MCP 툴 목록 (오케스트레이터 기준)

오케스트레이터가 제공하는 호출 방식:

- `POST /tool/call`  body: `{ "tool": "inventory.search_listings", "args": {...} }`

등록된 툴:

- `inventory.get_car_by_plate` : 차량번호로 내/매입 차량 조회(데모)
- `inventory.search_listings` : 조건 검색 후 top_k개 정제 추천(데모)
- `inventory.compare_listings` : 비교표(데모)
- `inventory.get_monthly_sales_stats` : 판매현황 시리즈(데모)
- `history.get_vehicle_registry_summary` : 원부 요약(데모)
- `history.get_maintenance_history` : 정비이력 요약(데모)
- `pricing.get_market_price` : 시세 밴드(데모)

---

## 개인정보/동의(실서비스 설계 포인트)

- 이 PoC는 고객 실명/연락처를 저장하지 않습니다. `customer_token`은 내부 토큰입니다.
- 실서비스에서 고객 연락처(카톡/문자) 등 PII 저장이 필요하다면:
  - 동의 UI/약관/보관기간/파기정책
  - 마스킹/암호화(PII Vault)
  - 접근권한(딜러/상사/관리자) + 감사로그
  - 외부 발송 채널(알림톡/문자) 연동 시 위수탁/계약 범위 정리

---

## 다음 단계 (운영급으로 올릴 때)

- 기존 상사/종사원 도메인 분리 환경(SSO, API Gateway) 연동
- MCP 서버별 인증(서비스 간 JWT/mTLS) + RBAC/ABAC
- Tool schema(versioning)와 승인 플로우(상사 승인/점검)
- LLM 연결(의도 분류 고도화, 템플릿 생성 품질 개선)
- 관제/지표: 상담 전환율, 응답시간, 툴 실패율, 추천 클릭률


## 프로젝트 구조도

```text
dealermate/                                   # 리포지토리 루트
├─ docker-compose.yml                          # 전체 서비스(프론트/API/MCP/DB/Redis) 로컬 오케스트레이션
├─ infra/                                      # 인프라 초기화/설정(컨테이너 마운트용)
│  └─ postgres/
│     └─ init/
│        └─ 001_extensions.sql                 # Postgres 확장/초기 설정(초기화 스크립트)
├─ frontend/                                   # Nuxt 3 프론트엔드(딜러/상사 업무 UI)
│  ├─ Dockerfile                               # 프론트 컨테이너 빌드 정의
│  ├─ package.json                             # 프론트 의존성/스크립트
│  ├─ nuxt.config.ts                           # Nuxt 설정(모듈/라우팅/런타임 설정 등)
│  ├─ tailwind.config.ts                       # Tailwind 설정
│  ├─ app.vue                                  # 앱 루트 엔트리/레이아웃
│  ├─ assets/
│  │  └─ css/
│  │     └─ tailwind.css                       # 글로벌 스타일/Tailwind 엔트리
│  ├─ pages/                                   # 파일 기반 라우팅
│  │  ├─ index.vue                             # 진입(로그인/랜딩)
│  │  └─ dashboard.vue                         # Deal + Chat 기반 업무 화면
│  ├─ components/                              # 화면 구성 컴포넌트
│  │  ├─ ChatPanel.vue                         # Assistant 채팅/응답 패널
│  │  ├─ DealList.vue                          # 상담(Deal) 목록/선택 UI
│  │  ├─ LoginForm.vue                         # 로그인 폼 UI
│  │  └─ TopBar.vue                            # 상단 바(상태/네비게이션)
│  ├─ composables/
│  │  └─ useApi.ts                             # API 호출 래퍼(인증 토큰 포함 등)
│  └─ stores/
│     └─ auth.ts                               # 인증 상태/토큰 스토어(Pinia)
├─ services/                                   # 백엔드 서비스 모음(API + MCP 툴 서버)
│  ├─ api/                                     # 메인 FastAPI API(인증/JWT, Deal, Assistant)
│  │  ├─ Dockerfile                            # API 컨테이너 빌드 정의
│  │  ├─ requirements.txt                      # API Python 의존성
│  │  └─ app/
│  │     ├─ main.py                            # FastAPI 엔트리(라우터/미들웨어 등록)
│  │     ├─ core/
│  │     │  └─ config.py                       # 환경변수/설정 로딩
│  │     ├─ db/
│  │     │  ├─ base.py                         # SQLAlchemy Base/메타데이터
│  │     │  └─ session.py                      # DB 엔진/세션 생성
│  │     ├─ models/                            # DB 모델(테이블 정의)
│  │     │  ├─ __init__.py                     # 모델 패키지 초기화
│  │     │  ├─ artifact.py                     # 생성물(추천/비교표/멘트 등) 저장 모델
│  │     │  ├─ audit_log.py                    # 감사/행위 로그 모델
│  │     │  ├─ deal.py                         # 상담(Deal) 모델
│  │     │  └─ user.py                         # 사용자(딜러/상사/어드민) 모델
│  │     ├─ routers/                           # API 라우터(엔드포인트)
│  │     │  ├─ __init__.py                     # 라우터 패키지 초기화
│  │     │  ├─ assist.py                       # Assistant 엔드포인트(의도→툴→템플릿)
│  │     │  ├─ auth.py                         # 인증(로그인/JWT)
│  │     │  ├─ deals.py                        # Deal CRUD
│  │     │  └─ health.py                       # 헬스체크
│  │     ├─ schemas/                           # Pydantic 스키마(요청/응답)
│  │     │  ├─ assist.py                       # Assistant 요청/응답 스키마
│  │     │  └─ auth.py                         # 로그인/JWT 스키마
│  │     ├─ services/                          # 비즈니스 로직 레이어
│  │     │  ├─ assistant_service.py            # Assistant 처리 오케스트레이션
│  │     │  ├─ intent_router.py                # 의도(Intent) 분류/라우팅
│  │     │  └─ mcp_client.py                   # MCP Orchestrator 호출 클라이언트
│  │     └─ utils/
│  │        ├─ deps.py                         # FastAPI DI(인증/DB 세션 주입 등)
│  │        └─ security.py                     # 보안 유틸(JWT/해시 등)
│  ├─ mcp-orchestrator/                        # MCP 오케스트레이터(툴 라우팅/로그/마스킹)
│  │  ├─ Dockerfile                            # Orchestrator 컨테이너 빌드 정의
│  │  ├─ requirements.txt                      # Orchestrator Python 의존성
│  │  └─ app/
│  │     └─ main.py                            # Orchestrator 엔트리(`/tool/call` 제공)
│  ├─ mcp-inventory/                           # 매물/재고 도메인 MCP 서버(데모)
│  │  ├─ Dockerfile                            # Inventory 컨테이너 빌드 정의
│  │  ├─ requirements.txt                      # Inventory Python 의존성
│  │  └─ app/
│  │     └─ main.py                            # inventory 툴 구현
│  ├─ mcp-history/                             # 원부/정비이력 도메인 MCP 서버(데모)
│  │  ├─ Dockerfile                            # History 컨테이너 빌드 정의
│  │  ├─ requirements.txt                      # History Python 의존성
│  │  └─ app/
│  │     └─ main.py                            # history 툴 구현
│  └─ mcp-pricing/                             # 시세/가격 도메인 MCP 서버(데모)
│     ├─ Dockerfile                            # Pricing 컨테이너 빌드 정의
│     ├─ requirements.txt                      # Pricing Python 의존성
│     └─ app/
│        └─ main.py                            # pricing 툴 구현
└─ README copy.md                              # README 초안/백업(동일 내용 복사본)
```


## 플젝 압축 명령어
tar -a -c -f dealermate.zip `
  --exclude=".env" `
  --exclude=".gitignore" `
  --exclude="README.md" `
  --exclude="README copy.md" `
  --exclude="frontend/node_modules" `
  .