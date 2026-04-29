# Stage 05 Integration Test Results

**60 tests, 60 passed, 0 failed** (0.12s)

## E2E-01: Basic Defect Detection Flow (17 tests)
- [x] gRPC servicer instantiation (3 tests)
- [x] DetectDefects returns valid proto response, sets UNAVAILABLE without model (3 tests)
- [x] GetModelInfo lists all 5 defect types, correct model name (3 tests)
- [x] HealthCheck returns status, reports unloaded model, tracks uptime (3 tests)
- [x] PSC code mapping for all 5 defect types + unknown fallback (2 tests)
- [x] End-to-end: Detection → proto roundtrip, response construction, timing (3 tests)

## E2E-02: Offline Operation (11 tests)
- [x] Inference engine works without network (3 tests)
- [x] PSC mapping works entirely offline with embedded rules (3 tests)
- [x] Full pipeline offline: detection → violation → storage (2 tests)
- [x] Sync queue priority ordering: critical before normal (1 test)
- [x] Data integrity after offline accumulation and batch sync (2 tests)

## E2E-03: Security Verification (16 tests)
- [x] OT gateway read-only enforcement: no write methods, doc comment, all modules clean (4 tests)
- [x] RBAC role permissions: all 5 roles defined, Captain wildcard, Crew scan-only, ReadOnly no-create, ChiefEngineer defect.review (5 tests)
- [x] Audit event structure: all 6 fields present, all 3 result variants (2 tests)
- [x] Authentication: invalid token rejected, unknown role rejected, authenticate fn exists (3 tests)
- [x] Unidirectional data flow: OT reads only, sync flows edge-to-shore (2 tests)

## E2E-04: Cargo Securing — CIC 2026 (16 tests)
- [x] Cargo detector initialization and empty detect without model (2 tests)
- [x] PSC code 0725 mapping with correct description (1 test)
- [x] Subtype classification: TURNBUCKLE_BROKEN, LASHING_LOOSE, WIRE_CUT, SECURING_MISSING, tiny bbox (5 tests)
- [x] All subtypes produce psc_code "0725" (1 test)
- [x] Severity prioritization: high confidence→CRITICAL, medium→HIGH (2 tests)
- [x] CIC 2026 target flags: 0725, 0726, 0728 all flagged, CARGO_LASHING in related types (5 tests)
