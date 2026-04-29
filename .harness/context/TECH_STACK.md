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
