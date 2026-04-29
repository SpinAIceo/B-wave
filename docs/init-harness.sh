#!/bin/bash
# B-Wave Project Harness Initialization Script
# 위치: docs/init-harness.sh
# 실행: 프로젝트 루트(B-Wave/)에서 bash docs/init-harness.sh

set -e
echo "🚢 B-Wave Harness 초기화: $(pwd)"

# ── 1. 디렉토리 구조 ──
mkdir -p packages/{ai-engine,edge-platform,mobile-app,fleet-view,mesh-network}
mkdir -p shared/{proto,types,test-fixtures}
mkdir -p deploy docs

# ── 2. .harness 구조 ──
mkdir -p .harness/stages/{stage-01-foundation,stage-02-ai-engine,stage-03-edge-platform,stage-04-mobile-app,stage-05-integration,stage-06-fleet-view,stage-07-poc-deploy}
mkdir -p .harness/context

# ── 3. manifest.yaml ──
cat > .harness/manifest.yaml << 'EOF'
project: bwave-psc-scanner
version: "1.0"
current_stage: stage-01-foundation
status: in_progress
created: "2026-04-29"

stages:
  stage-01-foundation:
    status: in_progress
    owner: orchestrator
    started: "2026-04-29"
    completed: null
    blockers: []
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
  team-e-infra: [mesh-network, deploy]
EOF

# ── 4. Context 파일들 ──
cat > .harness/context/TECH_STACK.md << 'EOF'
# B-Wave 확정 기술 스택

| 영역 | 기술 | 비고 |
|------|------|------|
| Vision AI 학습 | PyTorch 2.x | 전이 학습 |
| Vision AI 추론 | ONNX Runtime / TensorRT | 엣지 경량 추론 |
| 엣지 서비스 | Rust + Tokio | 성능 크리티컬 |
| AI-Edge 연동 | Python + gRPC | 추론 서버 |
| 모바일 앱 | Flutter (Dart) | Android/iOS |
| 육상 백엔드 | FastAPI (Python) | REST + WebSocket |
| 육상 프론트엔드 | React + TypeScript | 대시보드 |
| DB (엣지) | SQLite + LevelDB | 오프라인 저장 |
| DB (육상) | PostgreSQL + TimescaleDB | 시계열 |
| 인터페이스 정의 | Protocol Buffers (gRPC) | 팀 간 계약 |
| 컨테이너 | Docker + K3s | 엣지 오케스트레이션 |
| CI/CD | GitHub Actions | 자동 빌드/배포 |
| 보안 | mTLS, AES-256, RBAC | UR E26/E27 |
EOF

cat > .harness/context/GLOSSARY.md << 'EOF'
# B-Wave 도메인 용어 사전

| 용어 | 약어 | 설명 |
|------|------|------|
| Port State Control | PSC | 항만국통제 — 기항지에서 외국 선박을 검사하는 제도 |
| Detention | — | 출항 정지 — PSC에서 심각한 결함 발견 시 선박 억류 |
| Maintenance, Repair, Overhaul | MRO | 선박 유지보수 활동 전반 |
| Capital Expenditure | CAPEX | 초기 설비 투자 비용 |
| Operational Expenditure | OPEX | 운영 비용 (구독료 등) |
| Bring Your Own Device | BYOD | 선원 소유 범용 태블릿/스마트폰 활용 |
| Hardware as a Service | HaaS | 장비를 구매 대신 월 구독으로 제공 |
| Unified Requirement E26/E27 | UR E26/E27 | IACS 사이버 보안 통합 규정 |
| Operational Technology | OT | 선박 운항·기관 제어 네트워크 |
| Concentrated Inspection Campaign | CIC | MoU 체제 특정 항목 집중 단속 기간 |
| Memorandum of Understanding | MoU | PSC 지역 협력 기구 (Tokyo/Paris MoU) |
| Proof of Concept | PoC | 현장 실증 |
| Annual Recurring Revenue | ARR | 연간 반복 매출 |
| Letter of Intent | LOI | 구매 의향서 |
| Commercial Off-The-Shelf | COTS | 범용 기성품 |
| Edge Computing | — | 현장 단말에서 데이터 처리 |
| Cargo Securing | — | 화물 고박 — 선적 화물 고정 |
EOF

cat > .harness/context/API_CONTRACTS.md << 'EOF'
# B-Wave 팀 간 인터페이스 계약

> 이 문서는 팀 간 gRPC/REST 인터페이스의 Single Source of Truth입니다.
> 변경 시 반드시 Orchestrator를 통해 ICR(Interface Change Request)을 거칩니다.

## 1. EdgeInferenceService (Team-A ↔ Team-C)

```protobuf
service EdgeInferenceService {
  rpc DetectDefects(DetectRequest) returns (DetectResponse);
  rpc GetModelInfo(Empty) returns (ModelInfo);
  rpc HealthCheck(Empty) returns (HealthStatus);
}

message DetectRequest {
  bytes image_data = 1;
  int32 image_width = 2;
  int32 image_height = 3;
  string inspection_id = 4;
}

message DetectResponse {
  repeated Defect defects = 1;
  float inference_time_ms = 2;
  string model_version = 3;
}

message Defect {
  BoundingBox bbox = 1;
  string defect_type = 2;       // RUST, DAMAGE, LEAK, MISSING_LABEL
  float confidence = 3;
  string psc_code = 4;
  string severity = 5;          // LOW, MEDIUM, HIGH, CRITICAL
}

message BoundingBox {
  float x_min = 1;
  float y_min = 2;
  float x_max = 3;
  float y_max = 4;
}
```

## 2. RuleEngineService (Team-A ↔ Team-B)

```protobuf
service RuleEngineService {
  rpc MapToRegulation(DefectList) returns (ViolationReport);
  rpc GetPortInspectionFocus(PortInfo) returns (InspectionChecklist);
}
```

## 3. SyncService (Team-B ↔ Team-D)

```protobuf
service SyncService {
  rpc PushInspectionData(stream InspectionRecord) returns (SyncAck);
  rpc PullUpdates(UpdateRequest) returns (stream UpdatePackage);
}
```

## 4. Fleet REST API (Team-D)

```
GET    /api/v1/vessels
GET    /api/v1/vessels/{id}/inspections
GET    /api/v1/dashboard/overview
POST   /api/v1/reports/generate
WS     /api/v1/ws/live
```
EOF

cat > .harness/context/DATA_MODELS.md << 'EOF'
# B-Wave 공유 데이터 모델

## DefectDetection (결함 탐지 결과)
```
{
  id: UUID,
  inspection_id: UUID,
  vessel_id: string,
  timestamp: ISO8601,
  image_ref: string,
  defects: [{
    bbox: {x_min, y_min, x_max, y_max},
    defect_type: enum(RUST, DAMAGE, LEAK, MISSING_LABEL, CARGO_LASHING),
    confidence: float,
    psc_code: string,
    severity: enum(LOW, MEDIUM, HIGH, CRITICAL)
  }],
  model_version: string,
  inference_time_ms: float
}
```

## InspectionReport (점검 보고서)
```
{
  id: UUID,
  vessel_id: string,
  vessel_name: string,
  inspector_id: string,
  port_of_inspection: string,
  mou_region: enum(TOKYO, PARIS, ...),
  started_at: ISO8601,
  completed_at: ISO8601,
  checklist_items: [{
    item_id: string,
    category: string,
    description: string,
    status: enum(PASS, FAIL, NOT_CHECKED),
    detections: [DefectDetection.id],
    notes: string
  }],
  summary: { total_items, passed, failed, critical_defects },
  synced: boolean,
  synced_at: ISO8601 | null
}
```

## VesselProfile (선박 프로필)
```
{
  id: string,
  name: string,
  type: enum(BULK, CONTAINER, TANKER, ...),
  flag: string,
  management_company: string,
  fleet_size: int,
  edge_server_id: string,
  last_psc_inspection: ISO8601,
  detention_history: [{date, port, defects}],
  subscription_tier: enum(BASIC, STANDARD, ENTERPRISE)
}
```

## PSCRuleViolation (규제 위반 항목)
```
{
  psc_code: string,
  category: string,
  description: string,
  severity: enum(LOW, MEDIUM, HIGH, CRITICAL),
  cic_target_2026: boolean,
  mou_regions: [string],
  related_defect_types: [string],
  recommended_action: string
}
```
EOF

# ── 5. Stage 01 ──
cat > .harness/stages/stage-01-foundation/STAGE_BRIEF.md << 'EOF'
# Stage 01: Foundation (기반 구축)

## 목표
프로젝트 골격, 공유 인터페이스, 개발 환경을 확립합니다.

## 범위
- [x] 모노레포 디렉토리 구조 생성
- [x] manifest.yaml 작성
- [x] TECH_STACK.md 확정
- [x] GLOSSARY.md 작성
- [x] API_CONTRACTS.md 초안 (Protobuf 인터페이스)
- [x] DATA_MODELS.md 초안 (4개 모델)
- [ ] Protobuf 파일 생성 및 컴파일 테스트
- [ ] 각 팀 패키지 스캐폴딩 (빌드 성공)
- [ ] CI/CD 기초 파이프라인 (lint + build)
- [ ] HANDOFF.md 작성

## 완료 기준
- [ ] protoc 컴파일 통과
- [ ] 각 패키지 빈 프로젝트 빌드 성공
- [ ] CI 파이프라인에서 lint 통과
EOF

cat > .harness/stages/stage-01-foundation/DECISIONS.md << 'EOF'
# Stage 01 기술 결정 기록

| 일자 | 결정 | 근거 | 기각된 대안 |
|------|------|------|-------------|
| 2026-04-29 | 모노레포 구조 채택 | 팀 간 인터페이스 공유 용이 | 멀티레포 |
| 2026-04-29 | gRPC 기반 팀 간 통신 | 강타입, 코드 생성, 스트리밍 | REST, GraphQL |
| 2026-04-29 | Flutter 모바일 앱 | 크로스 플랫폼, 카메라 성능 | React Native, Native |
| 2026-04-29 | Rust + Python 엣지 | 성능(Rust) + AI(Python) | Go, 순수 Python |
EOF

# ── 6. 각 Stage 빈 파일 ──
for stage in .harness/stages/stage-*/; do
  [ -d "$stage" ] || continue
  touch "$stage/DECISIONS.md" "$stage/HANDOFF.md" "$stage/TESTS.md" "$stage/ARTIFACTS.md" 2>/dev/null
done

# ── 7. .gitignore + Git 초기화 ──
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
node_modules/
.dart_tool/
build/
dist/
*.onnx
*.trt
*.pt
.env
EOF

git init
git add .
git commit -m "harness: initialize B-Wave project with Harness framework"
git tag stage-01-start

echo ""
echo "✅ B-Wave Harness 초기화 완료!"
echo ""
echo "📋 현재 Stage: stage-01-foundation"
echo ""
echo "Agent 세션 시작:"
echo '  claude "cat docs/AGENTS.md; cat .harness/manifest.yaml; cat .harness/stages/stage-01-foundation/STAGE_BRIEF.md 를 읽고 Stage 01 작업을 시작해주세요."'