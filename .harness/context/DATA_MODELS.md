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
