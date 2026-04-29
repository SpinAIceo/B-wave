# AGENTS.md — B-Wave Agent 운영 가이드

> **목적:** AI Agent 팀 구성, Harness 기법, 협업 프로토콜 정의  
> **최종 수정:** 2026-04-29  
> **관련 문서:**  
> - [PRD.md](./PRD.md) — 제품 요구사항  
> - [AGENTS_PROMPTS_BUILD.md](./AGENTS_PROMPTS_BUILD.md) — Stage 1~4 프롬프트 (빌드)  
> - [AGENTS_PROMPTS_OPS.md](./AGENTS_PROMPTS_OPS.md) — Stage 5~7 프롬프트 (통합/배포)  
> - [AGENT_CHEATSHEET.md](./AGENT_CHEATSHEET.md) — 일일 운영 빠른 참조  
> - [init-harness.sh](./init-harness.sh) — 프로젝트 초기화 스크립트

---

## 1. 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                    🎯 Orchestrator Agent                        │
│              (프로젝트 총괄 / Harness Controller)                │
└───────┬──────────┬──────────┬──────────┬──────────┬─────────────┘
        │          │          │          │          │
   ┌────▼───┐ ┌───▼────┐ ┌──▼───┐ ┌───▼────┐ ┌───▼────┐
   │ Team-A │ │ Team-B │ │Team-C│ │ Team-D │ │ Team-E │
   │ Vision │ │  Edge  │ │Mobile│ │ Fleet  │ │  Infra │
   │   AI   │ │Platform│ │  App │ │  View  │ │  Mesh  │
   └────────┘ └────────┘ └──────┘ └────────┘ └────────┘
```

### Agent Team 구성표

| Team | 역할 | 사용 Tool | 핵심 산출물 |
|------|------|-----------|-------------|
| **Orchestrator** | 총괄 조율, Harness 관리, 인터페이스 정의 | Claude Code | manifest.yaml, API_CONTRACTS.md, HANDOFF.md |
| **Team-A: Vision AI** | 결함 탐지 모델 학습, 경량화, 추론 서버 | Cursor Composer + Claude Code | 학습 파이프라인, ONNX 모델, gRPC 추론 서버 |
| **Team-B: Edge Platform** | 엣지 런타임, 룰 엔진, OT 데이터 수집 | Claude Code | Edge 서비스, 룰 엔진, 단방향 API 게이트웨이 |
| **Team-C: Mobile App** | 뷰어 앱 (카메라 스캔, 오버레이) | Cursor Composer | Flutter 앱, 카메라 모듈, UX |
| **Team-D: Fleet View** | 육상 대시보드, 동기화, 리포트 | Cursor Composer + Claude Code | React 대시보드, REST API, 리포트 엔진 |
| **Team-E: Infra & Mesh** | 메쉬 네트워크, 배포, 보안 | Claude Code | 네트워크 설정, Docker/K3s, PKI |

### 권장 도구 조합

| 작업 유형 | 추천 도구 | 이유 |
|-----------|-----------|------|
| 아키텍처 설계, Protobuf | **Claude Code** (터미널) | 파일 생성/수정, 프로젝트 컨텍스트 파악 |
| AI 모델, 학습 파이프라인 | **Cursor Composer** + Claude | 다중 파일 동시 편집, 자동완성 |
| Flutter 모바일 앱 | **Cursor Composer** | Widget 트리, 실시간 프리뷰 |
| Rust 엣지 서비스 | **Claude Code** | 시스템 프로그래밍, 컴파일 에러 해결 |
| React 대시보드 | **Cursor Composer** | 컴포넌트 기반 개발, CSS |
| DevOps, Docker, 배포 | **Claude Code** (터미널) | 쉘 스크립트, 설정 파일 |
| 문서 작성 (Harness) | **Claude Chat** (claude.ai) | 긴 문서 작성, 의사결정 |

---

## 2. Harness 기법: 단계 보존 시스템

### Harness란?

장기 프로젝트에서 AI Agent의 컨텍스트 유실을 방지하고, 각 개발 단계의 결정·산출물·상태를 구조적으로 보존하여 언제든 이어서 작업할 수 있게 하는 기법입니다.

### 디렉토리 구조

```
bwave-project/
├── .harness/                          # ← 단계 보존 저장소
│   ├── manifest.yaml                  # 프로젝트 상태 매니페스트
│   ├── stages/
│   │   ├── stage-01-foundation/
│   │   │   ├── STAGE_BRIEF.md         # 목표·범위·완료 기준
│   │   │   ├── DECISIONS.md           # 기술 결정과 근거
│   │   │   ├── HANDOFF.md             # 다음 단계 인수인계서
│   │   │   ├── ARTIFACTS.md           # 산출물 목록
│   │   │   └── TESTS.md              # 통과해야 할 테스트
│   │   ├── stage-02 ~ stage-07/       # (동일 구조)
│   └── context/
│       ├── ARCHITECTURE.md            # 확정 아키텍처
│       ├── API_CONTRACTS.md           # 팀 간 인터페이스 계약
│       ├── DATA_MODELS.md             # 공유 데이터 모델
│       ├── TECH_STACK.md              # 확정 기술 스택
│       └── GLOSSARY.md               # 도메인 용어 사전
├── docs/
│   ├── PRD.md                         # 제품 요구사항
│   ├── AGENTS.md                      # ← 이 문서
│   ├── AGENTS_PROMPTS_BUILD.md        # Stage 1~4 프롬프트
│   ├── AGENTS_PROMPTS_OPS.md          # Stage 5~7 프롬프트
│   └── AGENT_CHEATSHEET.md            # 일일 운영 빠른 참조
├── packages/
│   ├── ai-engine/                     # Team-A
│   ├── edge-platform/                 # Team-B
│   ├── mobile-app/                    # Team-C
│   ├── fleet-view/                    # Team-D
│   └── mesh-network/                  # Team-E
└── shared/
    ├── proto/                         # gRPC/Protobuf 정의
    ├── types/                         # 공유 타입
    └── test-fixtures/                 # 테스트 데이터
```

### manifest.yaml

```yaml
project: bwave-psc-scanner
version: "1.0"
current_stage: stage-01-foundation
status: in_progress

stages:
  stage-01-foundation:
    status: in_progress
    owner: orchestrator
    depends_on: []
  stage-02-ai-engine:
    status: not_started
    owner: team-a-vision
    depends_on: [stage-01-foundation]
  stage-03-edge-platform:
    status: not_started
    owner: team-b-edge
    depends_on: [stage-01-foundation]
  stage-04-mobile-app:
    status: not_started
    owner: team-c-mobile
    depends_on: [stage-02-ai-engine, stage-03-edge-platform]
  stage-05-integration:
    status: not_started
    owner: orchestrator
    depends_on: [stage-02-ai-engine, stage-03-edge-platform, stage-04-mobile-app]
  stage-06-fleet-view:
    status: not_started
    owner: team-d-fleet
    depends_on: [stage-03-edge-platform]
  stage-07-poc-deploy:
    status: not_started
    owner: all
    depends_on: [stage-05-integration, stage-06-fleet-view]

team_assignments:
  team-a-vision: [ai-engine]
  team-b-edge: [edge-platform]
  team-c-mobile: [mobile-app]
  team-d-fleet: [fleet-view]
  team-e-infra: [mesh-network]
```

### HANDOFF.md 템플릿

```markdown
# Stage N → Stage N+1 Handoff

## 완료된 작업
- [ ] 항목 1

## 핵심 결정 사항
| 결정 | 근거 | 기각된 대안 |
|------|------|-------------|

## 다음 단계에서 알아야 할 것
## 미해결 이슈 (Carry-over)
## 산출물 경로
## 테스트 통과 현황
```

---

## 3. 세션 복구 프롬프트 (Harness Resumption)

개발을 이어서 할 때 Agent에게 주는 **세션 시작 프롬프트**입니다.

```markdown
# Session Resumption Prompt (모든 Agent 공용)

당신은 B-Wave 프로젝트의 [{팀명}] Agent입니다.
이전 세션에서 중단된 작업을 이어서 수행합니다.

## 복귀 절차 (반드시 순서대로)
1. .harness/manifest.yaml → 현재 프로젝트 상태 파악
2. 현재 Stage의 STAGE_BRIEF.md → 이번 단계 목표 확인
3. 이전 Stage의 HANDOFF.md → 인수인계 사항 확인
4. 현재 Stage의 DECISIONS.md → 이미 내려진 결정 확인
5. .harness/context/ 하위 파일 → 아키텍처/인터페이스 확인
6. git log --oneline -20 && git status → 코드 상태 확인

## 작업 완료 시 반드시 수행
- DECISIONS.md에 새로운 결정 추가
- STAGE_BRIEF.md 체크리스트에 진행 반영
- 중단 시 TODO.md에 다음 할 일 기록
- manifest.yaml status 업데이트

## 현재 컨텍스트
- 팀: [{팀명}]
- Stage: [{현재 Stage}]
- 마지막 작업: [{간단 기술}]
```

---

## 4. Agent 간 협업 프로토콜

### 4.1 인터페이스 변경 요청 (ICR)

```markdown
현재 API_CONTRACTS.md의 [{인터페이스명}]에 변경이 필요합니다.

### 변경 내용
- 변경 전: [현재 인터페이스]
- 변경 후: [원하는 인터페이스]
- 변경 사유: [이유]

### 영향 범위
- 영향받는 팀: [Team-A, Team-C 등]
- 하위 호환성: [유지/불가]

→ Orchestrator가 검토 후 API_CONTRACTS.md 업데이트 → 영향받는 팀에 전파
```

### 4.2 블로커 에스컬레이션

```markdown
[{팀명}]에서 블로커가 발생했습니다.

- 문제: [상세 설명]
- 원인 추정: [...]
- 시도한 해결: [...]
- 필요한 도움: [다른 팀 또는 결정 필요]

→ Orchestrator가 manifest.yaml blockers에 기록 → 관련 팀과 조율
```

---

## 5. 실전 워크플로우

### Cursor Composer

```
1. 프로젝트 루트에서 @file .harness/manifest.yaml 참조
2. @file .harness/context/API_CONTRACTS.md 참조
3. @file .harness/stages/stage-XX/HANDOFF.md 참조
4. "XXX를 구현해주세요" 요청
```

### Claude Code (터미널)

```bash
claude "cat .harness/manifest.yaml && cat .harness/stages/stage-02-ai-engine/HANDOFF.md
그리고 packages/ai-engine/inference/server.py의 gRPC 추론 서버 구현을 이어서 진행해주세요."
```

### 병렬 팀 운영 (Tmux)

```
┌─────────────────────────┬─────────────────────────┐
│  Terminal 1: Team-A     │  Terminal 2: Team-B     │
│  claude --profile ai    │  claude --profile edge  │
├─────────────────────────┼─────────────────────────┤
│  Terminal 3: Team-C     │  Terminal 4: Orchestrator│
│  cursor (Mobile App)    │  claude --profile orch  │
└─────────────────────────┴─────────────────────────┘
```

---

## 6. Harness 체크포인트 명령어

```bash
# Stage 완료
git add .harness/ && git commit -m "harness: complete stage-XX"
git tag stage-XX-complete

# 일일 스냅샷
git add .harness/ && git commit -m "harness: daily snapshot $(date +%Y-%m-%d)"

# Stage 전환
sed -i 's/current_stage: .*/current_stage: stage-XX/' .harness/manifest.yaml
git add .harness/ && git commit -m "harness: advance to stage-XX"

# 전체 상태 조회
cat .harness/manifest.yaml | grep -A2 "status:"
```