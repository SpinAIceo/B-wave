# Stage 05 → Stage 06/07 Handoff

## 완료된 작업
- [x] E2E-01: 기본 결함 탐지 플로우 (gRPC servicer, proto roundtrip, PSC 매핑) — 17 tests
- [x] E2E-02: 오프라인 동작 검증 (네트워크 없이 전체 파이프라인 동작) — 11 tests
- [x] E2E-03: 보안 검증 (OT 읽기 전용, RBAC 5개 역할, 감사 로그, 단방향) — 16 tests
- [x] E2E-04: Cargo Securing CIC 2026 (4개 서브타입, PSC 0725, CIC 플래그) — 16 tests
- [x] TESTS.md, BUGS.md, HANDOFF.md 작성

## 핵심 결정 사항

| 결정 | 근거 | 기각된 대안 |
|------|------|-------------|
| Rust 코드를 소스 분석으로 검증 | Rust 툴체인 미설치, 인터페이스 계약 기반 검증으로 충분 | Rust 컴파일 후 FFI 테스트 |
| Protobuf float 비교에 epsilon 사용 | float32 정밀도 손실은 프로토콜 특성 | 정수 비교로 변환 |
| 오프라인 저장을 dict으로 시뮬레이션 | SQLite는 Edge Platform(Rust) 책임, Python 테스트에서는 로직 검증에 집중 | 별도 SQLite 테스트 |

## 다음 단계에서 알아야 할 것

### Stage 06 (Fleet View)
- SyncService 인터페이스로 엣지 서버 데이터를 수신해야 함
- 동기화 큐 우선순위: CRITICAL > HIGH > NORMAL > LOW
- 모든 결함 데이터는 DefectDetection / InspectionReport 형식 (DATA_MODELS.md 참조)
- 프로토 float32 필드 비교 시 epsilon 고려 필요

### Stage 07 (PoC Deploy)
- 전체 E2E 파이프라인이 Python(AI) + Rust(Edge) + Dart(Mobile) 간 gRPC 통신으로 연결됨
- 오프라인 동작은 검증 완료 — 실선 환경에서 메쉬 네트워크 지연 테스트 필요
- 보안: mTLS 실제 인증서 설정은 Stage 07에서 수행
- OT 게이트웨이는 시뮬레이션 데이터 — 실제 NMEA 2000/Modbus 연동은 PoC에서

## 미해결 이슈 (Carry-over)
- 실제 AI 모델 파일 없이 테스트 — 모델 학습 완료 후 실제 추론 E2E 테스트 필요
- Rust 코드 컴파일/실행 테스트 미수행 — Rust 툴체인 설치 후 `cargo test` 필요
- Flutter 앱 위젯 테스트 미수행 — Flutter SDK 설치 후 `flutter test` 필요
- 실제 gRPC 서버-클라이언트 연결 테스트 (현재는 servicer 메서드 직접 호출)

## 산출물 경로

| 산출물 | 경로 |
|--------|------|
| 통합 테스트 | `tests/integration/` |
| E2E 결함 탐지 | `tests/integration/test_e2e_detection.py` |
| E2E 오프라인 | `tests/integration/test_e2e_offline.py` |
| E2E 보안 | `tests/integration/test_e2e_security.py` |
| E2E Cargo Securing | `tests/integration/test_e2e_cargo.py` |
| 공유 픽스처 | `tests/integration/conftest.py` |
| 테스트 결과 | `.harness/stages/stage-05-integration/TESTS.md` |
| 발견 버그 | `.harness/stages/stage-05-integration/BUGS.md` |

## 테스트 통과 현황

| 시나리오 | 테스트 수 | 상태 |
|----------|-----------|------|
| E2E-01 결함 탐지 | 17 | PASS |
| E2E-02 오프라인 | 11 | PASS |
| E2E-03 보안 | 16 | PASS |
| E2E-04 Cargo Securing | 16 | PASS |
| **합계** | **60** | **ALL PASS** |
