# B-Wave 시스템 아키텍처 & 기술 스택

---

## 1. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              선박 (Vessel)                                   │
│                          *** Offline-First ***                               │
│                                                                             │
│  ┌────────────────┐                          ┌────────────────────────────┐ │
│  │  📱 방수 태블릿  │    802.11s Wi-Fi Mesh    │  🖥  Edge Server (Mini PC) │ │
│  │  (BYOD)        │◄════════════════════════►│                            │ │
│  │                │      < 100ms 지연         │  ┌──────────────────────┐ │ │
│  │  Flutter / Dart │                          │  │  AI Engine (Python)  │ │ │
│  │  ─────────────  │   gRPC :50051            │  │                      │ │ │
│  │  카메라 스캔     │◄─── DetectDefects ──────►│  │  YOLOv8 → ONNX RT   │ │ │
│  │  바운딩박스 오버레이│  image → defects[]     │  │  PSC Code Mapper     │ │ │
│  │  점검 체크리스트  │                          │  │  Cargo Securing      │ │ │
│  │  리포트 뷰어    │                          │  │  (CIC 2026 특화)     │ │ │
│  │  기항지 알림    │                          │  │  < 500ms 추론        │ │ │
│  │                │                          │  └──────────────────────┘ │ │
│  │  Riverpod 상태  │                          │                            │ │
│  │  Hive 로컬 DB   │                          │  ┌──────────────────────┐ │ │
│  │  GoRouter 네비   │                          │  │ Edge Platform (Rust) │ │ │
│  └────────────────┘                          │  │                      │ │ │
│                                               │  │  PSC 룰 엔진 (12규제)│ │ │
│  ┌────────────────┐                          │  │  Sync Manager        │ │ │
│  │  🔧 OT 장비     │   단방향 읽기 전용 ──────►│  │  (SQLite 오프라인)   │ │ │
│  │                │   *** 쓰기 절대 금지 ***   │  │  Runtime Manager     │ │ │
│  │  NMEA 2000     │                          │  │  Security Module     │ │ │
│  │  Modbus TCP    │                          │  │  (mTLS + RBAC)       │ │ │
│  │  OPC-UA        │                          │  │  OT Gateway          │ │ │
│  └────────────────┘                          │  │  (Read-Only Only)    │ │ │
│                                               │  └──────────────────────┘ │ │
│  ┌──────────────────────────────────────────┐│                            │ │
│  │  📡 Mesh Network (802.11s)               ││  Docker + K3s 오케스트레이션 │ │
│  │  Bridge AP ↔ Engine Room AP ↔ Deck AP    ││  PKI 인증서 (mTLS)         │ │
│  │  WPA3-SAE 암호화 · 5GHz/2.4GHz 듀얼     ││  Audit Logging (UR E26/E27)│ │
│  └──────────────────────────────────────────┘│                            │ │
│                                               └────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │  위성 통신 (복구 시)
                                 │  SyncService (gRPC Streaming)
                                 │  우선순위: CRITICAL > HIGH > NORMAL > LOW
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           육상 본사 서버 (Shore)                             │
│                                                                            │
│  ┌────────────────────────┐       ┌──────────────────────────────────────┐ │
│  │  🗄  Fleet Backend      │       │  📊 Fleet Dashboard                  │ │
│  │  FastAPI (Python)       │◄─────►│  React + TypeScript                  │ │
│  │                        │ REST  │                                      │ │
│  │  11 REST 엔드포인트     │  +    │  D3.js 차트 (결함 분포 / 선박 상태)    │ │
│  │  동기화 수신 서버       │  WS   │  SVG Fleet Map (선대 위치)            │ │
│  │  리포트 엔진 (4종)      │       │  Vessel List (정렬/필터/검색)         │ │
│  │  웹훅 매니저           │       │  Inspection Timeline                 │ │
│  │  ERP/SMS 연동 API      │       │  Report Generator                    │ │
│  │                        │       │  Dark Maritime Theme                 │ │
│  └───────────┬────────────┘       └──────────────────────────────────────┘ │
│              │                                                             │
│  ┌───────────▼────────────┐                                               │
│  │  PostgreSQL 16          │                                               │
│  │  + TimescaleDB          │                                               │
│  │  (시계열 결함 데이터)    │                                               │
│  └────────────────────────┘                                               │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 데이터 플로우 — 결함 탐지 E2E

```
  태블릿                  Mesh              Edge Server                  태블릿
┌─────────┐          ┌─────────┐       ┌──────────────────┐         ┌─────────┐
│ ① 촬영   │  JPEG    │ ② 전송   │ gRPC  │ ③ AI 추론         │ 결과    │ ⑤ 표시   │
│ 카메라   │─────────►│ 802.11s │──────►│ YOLOv8 → NMS     │────────►│ 오버레이 │
│ 1280x720 │  ~200KB  │ <100ms  │       │ <500ms           │         │ BBox +  │
└─────────┘          └─────────┘       └────────┬─────────┘         │ PSC코드 │
                                                │                    └─────────┘
                                                ▼
                                       ┌──────────────────┐
                                       │ ④ PSC 코드 매핑    │
                                       │                    │
                                       │ 부식  → 0615      │
                                       │ 파손  → 0630      │
                                       │ 누수  → 0950      │
                                       │ 라벨  → 1320      │
                                       │ 고박  → 0725 (CIC)│
                                       └────────┬─────────┘
                                                │
                                    ┌───────────▼──────────┐
                                    │ ⑥ 오프라인 저장        │
                                    │ SQLite + Sync Queue   │
                                    │ 위성 복구 시 자동 동기화│
                                    └──────────────────────┘
```

---

## 3. 기술 스택

### 패키지별 기술 스택

| 패키지 | 언어 | 핵심 프레임워크 | DB | 통신 |
|--------|------|----------------|-----|------|
| **ai-engine** | Python 3.11 | PyTorch, ONNX Runtime, YOLOv8 | — | gRPC (server) |
| **edge-platform** | Rust (2021) | Tokio, Tonic, Serde | SQLite (rusqlite) | gRPC (server) |
| **mobile-app** | Dart | Flutter 3.22+, Riverpod, GoRouter | Hive | gRPC (client) |
| **fleet-view backend** | Python 3.11 | FastAPI, Pydantic v2, SQLAlchemy | PostgreSQL + TimescaleDB | REST + WebSocket |
| **fleet-view frontend** | TypeScript | React 19, D3.js, Mapbox GL | — | REST + WebSocket |
| **deploy** | Bash, Python | Docker, K3s, OpenSSL | — | OTA (HTTP) |
| **mesh-network** | Bash | 802.11s, iw, iperf3 | — | Wi-Fi Mesh |

### 계층별 기술 스택

```
┌──────────────────────────────────────────────────────────────────┐
│                     인터페이스 계층 (Shared)                       │
│  Protocol Buffers · gRPC · 4 proto 파일 · Python/Rust/Dart 스텁   │
└──────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐  ┌────────────────┐  ┌────────────────────┐
│  AI 추론 계층  │  │  엣지 서비스 계층 │  │  프레젠테이션 계층    │
│              │  │                │  │                    │
│  Python 3.11 │  │  Rust + Tokio  │  │  Flutter (Dart)    │
│  PyTorch 2.x │  │  Tonic (gRPC)  │  │  camera 패키지     │
│  ONNX Runtime│  │  rusqlite      │  │  CustomPainter     │
│  YOLOv8      │  │  Serde JSON    │  │  Riverpod          │
│  OpenCV      │  │  Tracing       │  │  Hive (오프라인)    │
│  NumPy       │  │  Anyhow        │  │  GoRouter          │
│  gRPC Server │  │  Chrono + UUID │  │  gRPC Client       │
└──────────────┘  └────────────────┘  └────────────────────┘
        │                    │
        ▼                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                     저장 계층 (Persistence)                        │
│                                                                  │
│  선박: SQLite (엣지, 오프라인)   │   육상: PostgreSQL + TimescaleDB │
│  모바일: Hive (로컬 캐시)       │   시계열 결함 데이터              │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     육상 관제 계층 (Shore)                         │
│                                                                  │
│  FastAPI (Python)  ·  React 19 (TypeScript)  ·  D3.js  ·  Mapbox │
│  Pydantic v2  ·  SQLAlchemy  ·  Vite 6  ·  Dark Maritime Theme   │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     인프라 계층 (Infrastructure)                   │
│                                                                  │
│  Docker + Docker Compose  ·  K3s (엣지 오케스트레이션)              │
│  GitHub Actions (CI/CD)   ·  OTA 업데이트 (delta + rollback)      │
│  802.11s Wi-Fi Mesh       ·  PKI (CA + mTLS 인증서)              │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     보안 계층 (Security · UR E26/E27)              │
│                                                                  │
│  TLS 1.3 전 구간  ·  mTLS (엣지↔태블릿)  ·  AES-256 저장 암호화   │
│  RBAC 5개 역할 (Captain/ChiefEngineer/Officer/Crew/ReadOnly)     │
│  Audit Trail Logging  ·  Data Diode (OT 단방향)  ·  CRL 인증 폐기 │
└──────────────────────────────────────────────────────────────────┘
```

### 언어 비중

```
  Python   ████████████████████████░░░░░░  45%  AI Engine + Fleet Backend + OTA
  Rust     ████████████░░░░░░░░░░░░░░░░░░  22%  Edge Platform
  Dart     ████████████░░░░░░░░░░░░░░░░░░  20%  Mobile App
  TypeScript████████░░░░░░░░░░░░░░░░░░░░░  10%  Fleet Dashboard
  Bash     ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░   3%  Deploy Scripts + Mesh Tools
```

---

## 4. 보안 아키텍처

```
                    ┌─────────────────────────┐
                    │   PKI Certificate Chain  │
                    │                         │
                    │   Root CA (RSA-4096)    │
                    │         │               │
                    │   Intermediate CA       │
                    │      │        │         │
                    │   Server    Client      │
                    │   Certs     Certs       │
                    │  (Vessel)  (Tablet)     │
                    └─────────────────────────┘
                           │           │
              ┌────────────▼───┐  ┌────▼────────────┐
              │  Edge Server    │  │  BYOD Tablet     │
              │  vessel-XX.pem  │  │  tablet-XX.p12   │
              │                 │◄─┤                  │
              │  mTLS 상호 인증  │  │  클라이언트 인증서 │
              └────────┬────────┘  └─────────────────┘
                       │
          ┌────────────▼────────────┐
          │     RBAC 권한 매트릭스    │
          ├─────────┬───────────────┤
          │ Captain │ 전체 권한      │
          │ Chief   │ 점검+결함+리포트│
          │ Officer │ 점검+리포트 열람│
          │ Crew    │ 스캔+본인 결과 │
          │ ReadOnly│ 열람 전용      │
          └─────────┴───────────────┘
                       │
          ┌────────────▼────────────┐
          │     Audit Trail         │
          │  모든 접근 기록          │
          │  UR E26/E27 충족        │
          │  위성 복구 시 육상 전송   │
          └─────────────────────────┘

  OT 네트워크 격리:
  ┌──────────┐      ┌──────────┐
  │ OT 장비   │─────►│ Edge     │     *** 단방향 ***
  │ (운항 제어)│ READ │ Server   │     OT → Edge (읽기만)
  │          │ ONLY │          │     Edge → OT (차단)
  └──────────┘      └──────────┘
```

---

## 5. 배포 토폴로지

```
  선박 A                    선박 B                    선박 C
┌──────────┐            ┌──────────┐            ┌──────────┐
│Edge Server│            │Edge Server│            │Edge Server│
│Docker x3  │            │Docker x3  │            │Docker x3  │
│- ai-engine│            │- ai-engine│            │- ai-engine│
│- edge-plat│            │- edge-plat│            │- edge-plat│
│- mesh-mon │            │- mesh-mon │            │- mesh-mon │
└─────┬─────┘            └─────┬─────┘            └─────┬─────┘
      │ 위성                   │ 위성                   │ 위성
      └────────────┬───────────┴───────────┬────────────┘
                   │                       │
                   ▼                       ▼
          ┌────────────────────────────────────────┐
          │            육상 서버 (Shore)              │
          │  Docker Compose                        │
          │  ┌──────────┐  ┌──────────┐            │
          │  │fleet-back│  │fleet-front│            │
          │  │ :8000    │  │ :80/:443 │            │
          │  └────┬─────┘  └──────────┘            │
          │       │                                │
          │  ┌────▼─────┐                          │
          │  │PostgreSQL │                          │
          │  │TimescaleDB│                          │
          │  └──────────┘                          │
          └────────────────────────────────────────┘
                   │
                   ▼  OTA 업데이트 (역방향)
          ┌────────────────────┐
          │ OTA Update Server  │
          │ SHA-256 + GPG 서명  │
          │ Delta 업데이트      │
          │ 자동 Rollback       │
          └────────────────────┘
```
