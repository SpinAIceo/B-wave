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
