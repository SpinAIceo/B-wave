const ko = {
  // NavBar
  nav_ai_sandbox: "AI 샌드박스",
  nav_psc_risk: "PSC 위험",
  nav_roi_calculator: "ROI 계산기",
  nav_fleet_demo: "선단 데모",
  nav_brand_subtitle: "PSC 스캐너",
  nav_try_free: "무료 체험",

  // Home — hero
  home_badge: "라이브 가상 PoC — 하드웨어 불필요",
  home_hero_title1: "선박 PSC 결함 탐지",
  home_hero_title2: "500ms 이내",
  home_hero_desc:
    "B-Wave는 선박의 엣지 서버에 배포됩니다. 승무원이 장비에 태블릿 카메라를 겨누면 — 부식, 손상, 누수가 검사관이 도착하기 전에 PSC 위반 코드와 함께 표시됩니다.",
  home_cta_primary: "선박 사진 업로드 →",
  home_cta_secondary: "비용 노출 확인",

  // Home — features
  feat_sandbox_title: "AI 결함 탐지기",
  feat_sandbox_desc:
    "선박 사진을 업로드하세요. 즉각적인 PSC 위반 코드, 바운딩 박스 오버레이, 심각도 등급을 제공합니다 — 11,000개 이상의 해상 이미지로 학습된 YOLO26s 기반.",
  feat_sandbox_cta: "샌드박스 체험 →",
  feat_risk_title: "항구 PSC 위험 시뮬레이터",
  feat_risk_desc:
    "목적지 항구와 감지된 결함을 선택하세요. 도쿄, 파리, USCG 및 20개 이상의 지역 당국의 실제 MOU 통계를 사용하여 억류 확률을 예측합니다.",
  feat_risk_cta: "위험 시뮬레이션 →",
  feat_roi_title: "억류 비용 계산기",
  feat_roi_desc:
    "결함을 비용 노출로 환산합니다. 억류 일수, 화물 지연 위약금, 평판 손실 비용을 B-Wave 시스템 투자 비용과 비교 분석합니다.",
  feat_roi_cta: "ROI 계산 →",
  feat_fleet_title: "선단 대시보드 데모",
  feat_fleet_desc:
    "전 세계 해상 항로에 걸친 50척의 실시간 시각화. 녹색/노란색/빨간색 PSC 위험 상태가 실시간으로 업데이트됩니다.",
  feat_fleet_cta: "선단 보기 →",

  // Home — stats
  stat_latency_label: "p95 추론 지연 시간",
  stat_map_label: "mAP50-95 (3클래스)",
  stat_images_label: "학습 이미지 수",
  stat_sla_label: "엔드투엔드 SLA",

  // Home — CTA card
  home_demo_title: "전체 데모를 원하시나요?",
  home_demo_desc:
    "실제 엣지 하드웨어로 B-Wave가 실행되는 모습을 직접 확인하세요. 장비는 저희가 가져갑니다. 선박만 준비해 주세요.",
  home_demo_cta: "하드웨어 데모 신청",

  // Sandbox page
  sandbox_title: "AI 결함 탐지기",
  sandbox_desc: "선박 장비 사진을 업로드하세요 — 선체, 배관, 갑판 구조물 — 즉각적인 PSC 결함 분석을 받으세요.",
  sandbox_vessel_label: "선박",
  sandbox_sync_hint: "결과가 선단 대시보드와 동기화됩니다",
  sandbox_dropzone_title: "선박 사진을 여기에 드롭하세요",
  sandbox_dropzone_hint: "JPG, PNG, WebP · 최대 20MB",
  sandbox_run_btn: "PSC 분석 실행",
  sandbox_analyzing: "분석 중...",
  sandbox_reset: "초기화",
  sandbox_demo_mode: "데모 모드",
  sandbox_result_header: "분석 완료",
  sandbox_no_defects: "결함 없음",
  sandbox_defects_found_single: "결함 {n}개 발견",
  sandbox_defects_found_plural: "결함 {n}개 발견",
  sandbox_compliant: "✓ PSC 적합",
  sandbox_compliant_desc: "결함이 감지되지 않았습니다. 이 검사 구역에서 선박은 적합한 것으로 보입니다.",
  sandbox_link_risk: "항구 위험 시뮬레이션 →",
  sandbox_upload_hint: "이미지를 업로드하고 분석을 실행하여 PSC 결함 결과를 확인하세요",

  // Risk page
  risk_title: "PSC 위험 시뮬레이터",
  risk_desc: "MOU 역사 데이터를 사용하여 목적지 항구와 감지된 결함에 따라 억류 확률을 예측합니다.",
  risk_label_port: "목적지 항구",
  risk_label_defects: "감지된 결함",
  risk_label_age: "선박 연령",
  risk_defect_rust: "부식",
  risk_defect_damage: "손상",
  risk_defect_leak: "누수",
  risk_age_years: "{n}년",
  risk_calc_btn: "위험 계산",
  risk_calculating: "계산 중...",
  risk_placeholder: "파라미터를 설정하고 위험 계산을 클릭하세요",
  risk_detention_prob: "억류 확률",
  risk_breakdown_title: "위험 분석",
  risk_base_rate: "기본 항구 비율",
  risk_avg_duration: "평균 억류 기간",
  risk_link_roi: "재정적 노출 계산 →",

  // ROI page
  roi_title: "억류 비용 계산기",
  roi_desc: "결함을 비용 노출로 환산하고 단 한 번의 억류 예방으로 얻는 ROI를 확인하세요.",
  roi_label_defects: "현재 결함",
  roi_label_port: "기항지",
  roi_label_vessel_type: "선박 유형",
  roi_label_dwt: "선박 DWT",
  roi_vessel_bulk: "벌크선",
  roi_vessel_container: "컨테이너선",
  roi_vessel_tanker: "탱커",
  roi_vessel_roro: "로로선",
  roi_vessel_gas: "가스선",
  roi_vessel_passenger: "여객선",
  roi_vessel_general: "일반화물선",
  roi_calc_btn: "노출 비용 계산",
  roi_calculating: "계산 중...",
  roi_placeholder: "결함과 선박 파라미터를 선택하여 비용 노출을 확인하세요",
  roi_total_exposure: "총 재정적 노출 (항해당)",
  roi_detention_days: "{n}일 예상 억류",
  roi_breakdown_title: "비용 내역",
  roi_cost_detention: "선박 억류 비용",
  roi_cost_cargo: "화물 지연 비용",
  roi_cost_repute: "평판/행정 비용",
  roi_section_title: "B-Wave ROI",
  roi_ratio_label: "ROI 비율",
  roi_payback_label: "투자 회수 기간",
  roi_annual_label: "연간 비용",
  roi_payback_text: "억류 한 번 예방으로 B-Wave {n}년치 비용이 충당됩니다",
  roi_link_quote: "공식 견적 받기 →",

  // Fleet page
  fleet_title: "선단 대시보드",
  fleet_desc: "전 세계 해상 항로에 걸친 50척의 실시간 PSC 위험 현황.",
  fleet_tile_total: "전체 선단",
  fleet_tile_compliant: "적합",
  fleet_tile_monitor: "관찰",
  fleet_tile_at_risk: "위험",
  fleet_filter_all: "전체",
  fleet_filter_risk: "위험",
  fleet_filter_monitor: "관찰",
  fleet_filter_ok: "적합",
  fleet_loading: "선단 데이터 로딩 중...",
  fleet_detail_risk: "PSC 위험",
  fleet_detail_defects: "결함",
  fleet_detail_inspection: "최근 점검",
  fleet_detail_next_port: "다음 항구",
  fleet_no_defects: "없음",
  fleet_btn_risk: "위험 시뮬레이션",
  fleet_btn_cost: "비용 계산",

  // Footer
  footer_copyright: "© 2026 Spinai — B-Wave Edge Vision AI · PSC 준수 스캐너",
  footer_model_meta: "모델: YOLO26s-v1 · mAP50-95=0.323 · 지연 p95=9.3ms (RTX4090)",

  // Zones
  zone_bow: "선수",
  zone_midship: "중앙",
  zone_stern: "선미",
  zone_deck: "갑판",
  zone_hull: "선체",
  zone_engine_room: "기관실",
} as const;

export default ko;
