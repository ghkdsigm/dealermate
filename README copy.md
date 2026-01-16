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
