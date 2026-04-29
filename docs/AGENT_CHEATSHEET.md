# B-Wave Agent 운영 치트시트

> 즉시 사용 가능한 명령어 모음 — 상세 내용은 [AGENTS.md](./AGENTS.md) 참조  
> **관련 문서:** [AGENTS.md](./AGENTS.md) · [AGENTS_PROMPTS_BUILD.md](./AGENTS_PROMPTS_BUILD.md) · [AGENTS_PROMPTS_OPS.md](./AGENTS_PROMPTS_OPS.md) · [PRD.md](./PRD.md)

---

## 🚀 매일 세션 시작 시 (모든 Agent 공용)

```bash
# 1. 상태 확인
cat .harness/manifest.yaml | head -20

# 2. 현재 Stage 목표 확인
cat .harness/stages/$(grep current_stage .harness/manifest.yaml | awk '{print $2}')/STAGE_BRIEF.md

# 3. 최근 결정 사항 확인
cat .harness/stages/$(grep current_stage .harness/manifest.yaml | awk '{print $2}')/DECISIONS.md
```

---

## 📋 Agent별 빠른 시작 프롬프트

### Orchestrator (총괄)
```
.harness/manifest.yaml, .harness/context/ARCHITECTURE.md,
.harness/context/API_CONTRACTS.md를 읽고
현재 프로젝트 상태를 파악한 뒤
[오늘 할 작업]을 수행해주세요.
```

### Team-A: Vision AI
```
.harness/manifest.yaml, .harness/context/API_CONTRACTS.md,
.harness/stages/stage-01-foundation/HANDOFF.md를 읽고
packages/ai-engine/에서
[결함 탐지 모델 학습 파이프라인 / 추론 서버 / 모델 경량화]
작업을 이어서 해주세요.
```

### Team-B: Edge Platform
```
.harness/manifest.yaml, .harness/context/API_CONTRACTS.md,
.harness/stages/stage-01-foundation/HANDOFF.md를 읽고
packages/edge-platform/에서
[룰 엔진 / 데이터 게이트웨이 / 동기화 / 보안 모듈]
작업을 이어서 해주세요.
```

### Team-C: Mobile App
```
.harness/manifest.yaml, .harness/context/API_CONTRACTS.md,
.harness/stages/stage-02-ai-engine/HANDOFF.md,
.harness/stages/stage-03-edge-platform/HANDOFF.md를 읽고
packages/mobile-app/에서
[카메라 스캔 화면 / 체크리스트 / 리포트 뷰어]
작업을 이어서 해주세요.
```

### Team-D: Fleet View
```
.harness/manifest.yaml, .harness/context/API_CONTRACTS.md,
.harness/stages/stage-03-edge-platform/HANDOFF.md를 읽고
packages/fleet-view/에서
[대시보드 / 동기화 수신 서버 / 리포트 엔진]
작업을 이어서 해주세요.
```

---

## 🔄 Stage 전환 체크리스트

```bash
# 1. 현재 Stage 완료 확인
cat .harness/stages/stage-XX/STAGE_BRIEF.md  # 체크리스트 모두 완료?

# 2. HANDOFF.md 작성 (Agent에게 요청)
# "현재 Stage의 HANDOFF.md를 작성해주세요"

# 3. 커밋 & 태그
git add .harness/
git commit -m "harness: complete stage-XX"
git tag stage-XX-complete

# 4. manifest 업데이트
# current_stage를 다음 단계로 변경
# 이전 stage의 status를 completed로 변경

# 5. 다음 Stage의 STAGE_BRIEF.md 작성
```

---

## 🚨 블로커 발생 시

```bash
# 1. 기록
echo "## $(date +%Y-%m-%d) - [블로커 제목]" >> .harness/stages/stage-XX/BLOCKERS.md
echo "- 문제: ..." >> .harness/stages/stage-XX/BLOCKERS.md
echo "- 영향: ..." >> .harness/stages/stage-XX/BLOCKERS.md

# 2. manifest에 반영
# blockers: ["블로커 설명"]

# 3. Orchestrator에게 에스컬레이션
```

---

## 📊 프로젝트 현황 한눈에 보기

```bash
echo "=== B-Wave Project Status ==="
grep -A1 "status:" .harness/manifest.yaml | grep -v "^--$"
echo ""
echo "=== Current Stage ==="
grep "current_stage" .harness/manifest.yaml
echo ""
echo "=== Recent Decisions ==="
for d in .harness/stages/*/DECISIONS.md; do
  [ -s "$d" ] && echo "--- $d ---" && tail -3 "$d"
done
```

---

## 🏷️ Git 태그 컨벤션

```
stage-01-start          # Stage 시작
stage-01-complete       # Stage 완료
stage-02-ai-v0.1        # 중간 마일스톤
integration-e2e-pass    # E2E 테스트 통과
poc-ready               # PoC 배포 준비 완료
```