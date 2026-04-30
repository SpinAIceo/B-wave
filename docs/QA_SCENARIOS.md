# B-Wave QA 테스트 시나리오

> **Version:** 1.0  
> **Last Updated:** 2026-04-30  
> **Total Scenarios:** 62  
> **Automated:** 45 / Manual: 10 / Partial: 7

---

## SC-01: 결함 탐지 정확도

| ID | 설명 | 사전 조건 | 실행 단계 | 기대 결과 | 우선순위 | 자동화 |
|---|---|---|---|---|---|---|
| SC-01-01 | 부식(Rust) 탐지 | AI Engine 가동, 모델 로드 | 부식 이미지를 DetectDefects RPC 전송 | BBox 반환, defect_type=RUST, PSC 0615 | P0 | Yes |
| SC-01-02 | 파손(Damage) 탐지 | AI Engine 가동 | 파손 이미지 전송 | defect_type=DAMAGE, PSC 0630 | P0 | Yes |
| SC-01-03 | 누수(Leak) 탐지 | AI Engine 가동 | 누수 이미지 전송 | defect_type=LEAK, PSC 0950 | P0 | Yes |
| SC-01-04 | 라벨 누락 탐지 | AI Engine 가동 | 라벨 누락 이미지 전송 | defect_type=MISSING_LABEL, PSC 1320 | P0 | Yes |
| SC-01-05 | 화물 고박 탐지 (CIC 2026) | AI Engine + Cargo 모듈 | 고박 결함 이미지 전송 | defect_type=CARGO_LASHING, PSC 0725 | P0 | Yes |
| SC-01-06 | 정상 이미지 (결함 없음) | AI Engine 가동 | 정상 이미지 전송 | defects=[], 탐지 0건 | P0 | Yes |
| SC-01-07 | 다중 결함 동시 탐지 | AI Engine 가동 | 복합 결함 이미지 전송 | 결함별 개별 BBox, 각각 PSC 코드 매핑 | P0 | Yes |
| SC-01-08 | 저해상도/흐린 이미지 | AI Engine 가동 | 320x240 흐린 이미지 전송 | 에러 없이 처리, confidence 낮은 결과 또는 빈 결과 | P1 | Yes |

---

## SC-02: 실시간 성능

| ID | 설명 | 사전 조건 | 실행 단계 | 기대 결과 | 우선순위 | 자동화 |
|---|---|---|---|---|---|---|
| SC-02-01 | 추론 응답 시간 | Edge 서버 가동, 모델 로드 | 1280x720 이미지 전송 | inference_time_ms < 500ms | P0 | Yes |
| SC-02-02 | 메쉬 전송 지연 | 메쉬 네트워크 구성 | 태블릿→엣지 이미지 전송 | 전송 지연 < 100ms | P0 | Manual |
| SC-02-03 | 연속 스캔 안정성 | 스캔 모드 활성 | 10회 연속 프레임 전송 | 응답 시간 편차 < 20%, 메모리 누수 없음 | P0 | Partial |
| SC-02-04 | 동시 접속 처리 | 3대 태블릿 연결 | 동시에 DetectDefects 호출 | 모든 요청 정상 응답, 지연 < 1000ms | P1 | Partial |
| SC-02-05 | 고부하 graceful degradation | CPU 90% 인위 부하 | 추론 요청 전송 | 타임아웃 에러 대신 느린 응답, 서버 크래시 없음 | P1 | Manual |

---

## SC-03: 오프라인 동작

| ID | 설명 | 사전 조건 | 실행 단계 | 기대 결과 | 우선순위 | 자동화 |
|---|---|---|---|---|---|---|
| SC-03-01 | 완전 오프라인 파이프라인 | 위성 통신 차단, 엣지+태블릿만 | 결함 스캔 수행 | 추론+PSC매핑+오버레이 정상 동작 | P0 | Yes |
| SC-03-02 | 로컬 DB 저장 | 오프라인 상태 | 점검 완료 | SQLite에 InspectionRecord 저장 확인 | P0 | Yes |
| SC-03-03 | 자동 동기화 트리거 | 오프라인 데이터 축적 후 | 위성 통신 복구 시뮬레이션 | SyncService 자동 호출, 데이터 전송 | P0 | Yes |
| SC-03-04 | 동기화 우선순위 | 다양한 우선순위 데이터 축적 | 동기화 큐 조회 | CRITICAL > HIGH > NORMAL > LOW 순서 | P0 | Yes |
| SC-03-05 | 충돌 해결 (LWW) | 동일 ID 데이터 엣지+육상 존재 | 동기화 수행 | Last-Write-Wins: 최신 타임스탬프 데이터 유지 | P1 | Yes |
| SC-03-06 | 장기 오프라인 대량 동기화 | 7일 오프라인 데이터 축적 | 통신 복구 후 전체 동기화 | 데이터 손실 없이 전량 전송, 순서 보장 | P1 | Partial |

---

## SC-04: 보안 (UR E26/E27)

| ID | 설명 | 사전 조건 | 실행 단계 | 기대 결과 | 우선순위 | 자동화 |
|---|---|---|---|---|---|---|
| SC-04-01 | 미인증 태블릿 차단 | mTLS 활성, 인증서 미설치 태블릿 | gRPC 연결 시도 | TLS 핸드셰이크 실패, 연결 거부 | P0 | Partial |
| SC-04-02 | 만료 인증서 거부 | 만료된 클라이언트 인증서 | gRPC 연결 시도 | 인증서 검증 실패, 접근 거부 | P0 | Manual |
| SC-04-03 | Captain 전체 권한 | Captain 역할 인증 | 모든 API 호출 | 전체 기능 접근 가능 | P0 | Yes |
| SC-04-04 | Crew 제한 접근 | Crew 역할 인증 | 스캔 + 리포트 열람 시도 | 스캔 허용, 다른 사용자 결과 접근 차단 | P0 | Yes |
| SC-04-05 | ReadOnly 수정 불가 | ReadOnly 역할 인증 | 데이터 수정 API 호출 | 403 Forbidden 응답 | P0 | Yes |
| SC-04-06 | OT 쓰기 차단 | Edge Platform 가동 | OT 네트워크 방향 쓰기 시도 | 쓰기 메서드 미존재, 물리적 차단 | P0 | Yes |
| SC-04-07 | 감사 로그 기록 | 보안 모듈 활성 | 다양한 작업 수행 | 모든 접근 AuditEvent 기록 (timestamp, user, action, result) | P0 | Yes |
| SC-04-08 | TLS 1.3 검증 | mTLS 설정 완료 | 연결 후 TLS 버전 확인 | TLS 1.3 사용 확인 | P1 | Manual |

---

## SC-05: 모바일 앱 UX

| ID | 설명 | 사전 조건 | 실행 단계 | 기대 결과 | 우선순위 | 자동화 |
|---|---|---|---|---|---|---|
| SC-05-01 | 스캔 시작/중지 | 앱 실행, 엣지 연결 | FAB 버튼 탭 | 스캔 시작 (빨간 정지 버튼), 재탭 시 중지 | P0 | Manual |
| SC-05-02 | 오버레이 색상 정확도 | 스캔 중 결함 탐지 | 다양한 결함 발생 | Rust=주황, Damage=빨강, Leak=파랑, Label=노랑, Cargo=보라 | P0 | Manual |
| SC-05-03 | CRITICAL 펄스 애니메이션 | CRITICAL 결함 탐지 | 오버레이 관찰 | CRITICAL BBox 테두리 펄스 효과 (opacity 0.6~1.0) | P1 | Manual |
| SC-05-04 | 체크리스트 상태 변경 | 체크리스트 화면 진입 | 항목 상태 버튼 탭 | Pass(초록)/Fail(빨강)/Not Checked(회색) 전환, 진행률 업데이트 | P0 | Manual |
| SC-05-05 | PDF 리포트 생성 | 점검 완료 | 리포트 화면 PDF 버튼 | "PDF export coming soon" 스낵바 (placeholder) | P2 | Manual |
| SC-05-06 | 기항지 알림 표시 | 알림 화면 진입 | 알림 목록 확인 | 기항지별 MoU 지역 + CIC 집중 항목 + 도착 예정일 | P1 | Manual |
| SC-05-07 | 대형 터치 타깃 | 장갑 착용 | 모든 인터랙션 요소 탭 | 최소 48dp 터치 타깃, 오작동 없음 | P0 | Partial |
| SC-05-08 | 테마 전환 | 설정 화면 진입 | Light/Dark/High Contrast 전환 | 즉시 적용, 대비 충분, 가독성 유지 | P1 | Manual |
| SC-05-09 | 연결 끊김 표시 | 엣지 서버 연결 중 | 엣지 서버 중단 | 연결 표시 빨간색 "Offline"으로 전환, 캐시 데이터 표시 | P0 | Partial |
| SC-05-10 | 다국어 전환 | 설정 화면 진입 | 한/영/중/타갈로그 선택 | UI 언어 즉시 전환 (placeholder 상태) | P2 | Manual |

---

## SC-06: Fleet View API

| ID | 설명 | 사전 조건 | 실행 단계 | 기대 결과 | 우선순위 | 자동화 |
|---|---|---|---|---|---|---|
| SC-06-01 | Health Check | 백엔드 가동 | GET /health | 200, {"status": "ok"} | P0 | Yes |
| SC-06-02 | 선박 목록 | 백엔드 가동 | GET /api/v1/vessels | 200, 5개 선박, 각각 id/name/type/flag/status 포함 | P0 | Yes |
| SC-06-03 | 선박 상세 | V-001 존재 | GET /api/v1/vessels/V-001 | 200, "MV Pacific Star" 데이터 | P0 | Yes |
| SC-06-04 | 선박 점검 이력 | V-001 점검 2건 | GET /api/v1/vessels/V-001/inspections | 200, 2건 반환 | P0 | Yes |
| SC-06-05 | 결함 목록 | INS-001에 결함 2건 | GET /api/v1/vessels/V-001/inspections/INS-001/detections | 200, 2건 (DET-001, DET-002) | P0 | Yes |
| SC-06-06 | 대시보드 통계 | 전체 데이터 존재 | GET /api/v1/dashboard/overview | 200, total_vessels=5, 각 필드 합리적 | P0 | Yes |
| SC-06-07 | 동기화 수신 | 유효한 데이터 | POST /api/v1/sync/receive | 200, SyncEvent 반환, records_received > 0 | P0 | Yes |
| SC-06-08 | 리포트 생성 (4종) | V-001 존재 | POST /api/v1/reports/generate (각 타입) | 200, report_id 발급, file_path 포함 | P0 | Yes |
| SC-06-09 | 웹훅 설정 | — | POST /api/v1/webhooks/configure | 200, webhook_id 반환 | P1 | Yes |
| SC-06-10 | 존재하지 않는 선박 | — | GET /api/v1/vessels/INVALID | 404 | P0 | Yes |
| SC-06-11 | 잘못된 동기화 데이터 | — | POST /api/v1/sync/receive (빈 vessel_id) | SyncEvent status=FAILED 또는 validation 오류 | P1 | Yes |

---

## SC-07: Cargo Securing (CIC 2026)

| ID | 설명 | 사전 조건 | 실행 단계 | 기대 결과 | 우선순위 | 자동화 |
|---|---|---|---|---|---|---|
| SC-07-01 | LASHING_LOOSE 분류 | CargoSecuringDetector | aspect_ratio < 0.4, confidence ≤ 0.7 | subtype=LASHING_LOOSE | P0 | Yes |
| SC-07-02 | TURNBUCKLE_BROKEN 분류 | CargoSecuringDetector | aspect_ratio < 0.4, confidence > 0.7 | subtype=TURNBUCKLE_BROKEN | P0 | Yes |
| SC-07-03 | WIRE_CUT 분류 | CargoSecuringDetector | aspect_ratio > 2.5 | subtype=WIRE_CUT | P0 | Yes |
| SC-07-04 | SECURING_MISSING 분류 | CargoSecuringDetector | area > 0.05, square-ish | subtype=SECURING_MISSING | P0 | Yes |
| SC-07-05 | CIC 2026 플래그 | 룰 엔진 PSC 규제 DB | cargo_lashing 결함 매핑 | cic_target_2026=true in rule engine | P0 | Yes |
| SC-07-06 | 체크리스트 CIC 배지 | 모바일 앱 체크리스트 | Cargo Securing 항목 확인 | "CIC" 오렌지 배지 표시 | P1 | Manual |

---

## SC-08: 배포/인프라

| ID | 설명 | 사전 조건 | 실행 단계 | 기대 결과 | 우선순위 | 자동화 |
|---|---|---|---|---|---|---|
| SC-08-01 | 엣지 Docker 기동 | Docker 설치, 이미지 빌드 | docker compose up -d (edge) | ai-engine, edge-platform, mesh-monitor 3개 서비스 healthy | P0 | Partial |
| SC-08-02 | 육상 Docker 기동 | Docker 설치, 이미지 빌드 | docker compose up -d (shore) | fleet-backend, fleet-frontend, postgres, timescaledb 4개 healthy | P0 | Partial |
| SC-08-03 | OTA 무결성 검증 | 업데이트 패키지 생성 | create-update.sh → ota-client.sh 적용 | SHA-256 해시 일치, 서명 검증 통과 | P0 | Yes |
| SC-08-04 | OTA 롤백 | 업데이트 적용 후 | 헬스체크 실패 시뮬레이션 | 5분 내 이전 버전 자동 복구 | P0 | Partial |
| SC-08-05 | PKI 인증서 발급/폐기 | CA 초기화 완료 | issue-vessel-cert.sh → revoke-cert.sh | 인증서 발급 성공, CRL 업데이트 | P0 | Yes |
| SC-08-06 | 메쉬 토폴로지 검증 | 메쉬 네트워크 구성 | validate-topology.sh 실행 | 7개 체크 항목 PASS (인터페이스, mesh ID, 암호화, 피어, DNS, gRPC) | P0 | Yes |
| SC-08-07 | 엣지 프로비저닝 | 클린 Ubuntu 서버 | provision-edge.sh --vessel-id V-001 | 시스템 요구사항 체크, 인증서 설치, Docker 기동, 헬스체크 통과 | P0 | Partial |

---

## 요약

| 카테고리 | 시나리오 수 | P0 | P1 | P2 | 자동화 |
|----------|-----------|----|----|----|----|
| SC-01 결함 탐지 | 8 | 7 | 1 | 0 | 8 Yes |
| SC-02 실시간 성능 | 5 | 2 | 3 | 0 | 1 Yes, 2 Partial, 2 Manual |
| SC-03 오프라인 | 6 | 4 | 2 | 0 | 5 Yes, 1 Partial |
| SC-04 보안 | 8 | 7 | 1 | 0 | 5 Yes, 1 Partial, 2 Manual |
| SC-05 모바일 UX | 10 | 4 | 4 | 2 | 2 Partial, 8 Manual |
| SC-06 Fleet API | 11 | 9 | 2 | 0 | 11 Yes |
| SC-07 Cargo CIC | 6 | 5 | 1 | 0 | 5 Yes, 1 Manual |
| SC-08 배포/인프라 | 7 | 7 | 0 | 0 | 2 Yes, 5 Partial |
| **합계** | **61** | **45** | **14** | **2** | **37 Yes / 11 Partial / 13 Manual** |
