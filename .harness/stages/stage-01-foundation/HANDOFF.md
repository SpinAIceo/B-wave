# Stage 01 → Stage 02/03 Handoff

## 완료된 작업
- [x] 모노레포 디렉토리 구조 생성 (packages/, shared/, .harness/)
- [x] manifest.yaml 작성
- [x] TECH_STACK.md 확정
- [x] GLOSSARY.md 작성
- [x] API_CONTRACTS.md 초안 (4개 서비스 인터페이스)
- [x] DATA_MODELS.md 초안 (4개 모델)
- [x] Protobuf 파일 생성 및 컴파일 테스트 통과
- [x] 각 팀 패키지 스캐폴딩
- [x] CI/CD 기초 파이프라인 (GitHub Actions)
- [x] HANDOFF.md 작성

## 핵심 결정 사항

| 결정 | 근거 | 기각된 대안 |
|------|------|-------------|
| 모노레포 구조 | 팀 간 인터페이스 공유 용이, protobuf 단일 소스 | 멀티레포 |
| gRPC 팀 간 통신 | 강타입, 코드 생성, 바이너리 스트리밍 최적 | REST, GraphQL |
| Flutter 모바일 앱 | 크로스 플랫폼, 카메라 실시간 처리 성능 | React Native, Native |
| Rust + Python 엣지 | 성능 크리티컬(Rust) + AI 연동(Python) | Go, 순수 Python |
| Proto 패키지 구조 bwave/v1/ | 버전닝 지원, 언어별 codegen 호환 | 플랫 구조 |

## 다음 단계에서 알아야 할 것

### Team-A (AI Engine — Stage 02)
- `shared/proto/bwave/v1/inference.proto`의 EdgeInferenceService 인터페이스 준수
- `packages/ai-engine/src/ai_engine/inference/server.py`에 gRPC 서버 스켈레톤이 준비됨
- Python protobuf 스텁: `shared/gen/python/bwave/v1/` (proto-gen.sh로 재생성)
- 모델 추론 결과는 반드시 `Defect` 메시지 형식으로 반환
- `train/` 디렉토리에 학습 파이프라인 구현

### Team-B (Edge Platform — Stage 03)
- `shared/proto/bwave/v1/rule_engine.proto`의 RuleEngineService 인터페이스 준수
- `shared/proto/bwave/v1/sync.proto`의 SyncService 인터페이스 준수
- `packages/edge-platform/`에 Rust 프로젝트 스켈레톤 준비됨 (Cargo.toml + 모듈 구조)
- 5개 서브모듈: gateway, rule_engine, sync_manager, runtime, security
- OT 네트워크는 **읽기 전용** — 절대 쓰기 금지

### Team-C (Mobile App — Stage 04, Stage 02/03 완료 후)
- `packages/mobile-app/`에 Flutter 스켈레톤 준비됨
- EdgeInferenceService의 DetectDefects RPC로 카메라 프레임 전송
- `Defect` 메시지의 `bbox` 좌표로 오버레이 렌더링
- 오프라인 모드: 엣지 서버 로컬 통신만으로 동작

### Team-D (Fleet View — Stage 06, Stage 03 이후)
- `packages/fleet-view/backend/`에 FastAPI 스켈레톤 준비됨
- `packages/fleet-view/frontend/`에 React+Vite 스켈레톤 준비됨
- SyncService를 통해 엣지 서버 데이터 수신
- REST API 엔드포인트는 API_CONTRACTS.md §4 참조

## 미해결 이슈 (Carry-over)
- Dart용 protobuf codegen은 Flutter 환경 설정 후 추가 필요
- Rust용 tonic codegen (build.rs)은 Stage 03에서 설정
- 엣지 서버 하드웨어 벤치마크 미수행 (Stage 03에서 수행)

## 산출물 경로

| 산출물 | 경로 |
|--------|------|
| Protobuf 정의 | `shared/proto/bwave/v1/*.proto` |
| Python gRPC 스텁 | `shared/gen/python/bwave/v1/` |
| Proto 빌드 스크립트 | `scripts/proto-gen.sh` |
| AI Engine 패키지 | `packages/ai-engine/` |
| Edge Platform 패키지 | `packages/edge-platform/` |
| Mobile App 패키지 | `packages/mobile-app/` |
| Fleet View 패키지 | `packages/fleet-view/` |
| Mesh Network 패키지 | `packages/mesh-network/` |
| CI/CD 워크플로우 | `.github/workflows/ci.yml` |
| 아키텍처 컨텍스트 | `.harness/context/` |

## 테스트 통과 현황

| 테스트 | 상태 |
|--------|------|
| protoc 컴파일 (4 proto 파일) | PASS |
| Python gRPC 스텁 생성 (12 파일) | PASS |
| ai-engine ruff lint | PASS |
| ai-engine pytest (1 test) | PASS |
| fleet-backend ruff lint | PASS |
| fleet-backend pytest (1 test) | PASS |
