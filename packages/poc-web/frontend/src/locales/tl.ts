import ko from "./ko";

const tl = {
  // NavBar
  nav_ai_sandbox: "AI Sandbox",
  nav_psc_risk: "PSC Risk",
  nav_roi_calculator: "ROI Calculator",
  nav_fleet_demo: "Fleet Demo",
  nav_brand_subtitle: "PSC Scanner",
  nav_try_free: "Subukan nang Libre",

  // Home — hero
  home_badge: "Live Virtual PoC — Walang Hardware na Kailangan",
  home_hero_title1: "Pagtukoy ng Depekto sa PSC",
  home_hero_title2: "Sa ilalim ng 500ms",
  home_hero_desc:
    "Naka-deploy ang B-Wave sa edge server ng barko. Kapag itinuro ng tripulante ang tablet camera sa kagamitan — kalawang, pinsala, tagas ay flagged na may PSC violation codes bago dumating ang inspector.",
  home_cta_primary: "Mag-upload ng Larawan ng Barko →",
  home_cta_secondary: "Tingnan ang Cost Exposure",

  // Home — features
  feat_sandbox_title: "AI Defect Scanner",
  feat_sandbox_desc:
    "Mag-upload ng larawan ng barko. Makakuha ng instant PSC violation codes, bounding-box overlays, at severity grading — pinapagana ng YOLO26s na sinanay sa 11,000+ maritime images.",
  feat_sandbox_cta: "Subukan ang Sandbox →",
  feat_risk_title: "Port PSC Risk Simulator",
  feat_risk_desc:
    "Pumili ng destinasyong daungan at natuklasang depekto. Real MOU statistics mula sa Tokyo, Paris, USCG, at 20+ regional authorities ay nagpapakita ng detention probability.",
  feat_risk_cta: "I-simulate ang Risk →",
  feat_roi_title: "Detention Cost Calculator",
  feat_roi_desc:
    "I-convert ang depekto sa financial exposure. Ihambing ang detention days, cargo-delay penalties, at reputational cost laban sa B-Wave system investment.",
  feat_roi_cta: "Kalkulahin ang ROI →",
  feat_fleet_title: "Fleet Dashboard Demo",
  feat_fleet_desc:
    "Real-time view ng 50 barko sa mga global shipping lanes. Berde/dilaw/pula PSC risk states ay live na nag-uupdate.",
  feat_fleet_cta: "Tingnan ang Fleet →",

  // Home — stats
  stat_latency_label: "p95 inference latency",
  stat_map_label: "mAP50-95 (3 klase)",
  stat_images_label: "training images",
  stat_sla_label: "end-to-end SLA",

  // Home — CTA card
  home_demo_title: "Gusto ng buong demo?",
  home_demo_desc:
    "Tingnan ang B-Wave sa real edge hardware. Dadalhin namin ang gear — dalhin mo ang barko.",
  home_demo_cta: "Humiling ng Hardware Demo",

  // Sandbox page
  sandbox_title: "AI Defect Scanner",
  sandbox_desc: "Mag-upload ng larawan ng kagamitan ng barko — hull, piping, deck structures — at makakuha ng instant PSC defect analysis.",
  sandbox_vessel_label: "Barko",
  sandbox_sync_hint: "Nag-sync ang resulta sa Fleet dashboard",
  sandbox_dropzone_title: "I-drop ang larawan ng barko dito",
  sandbox_dropzone_hint: "JPG, PNG, WebP · max 20MB",
  sandbox_run_btn: "Patakbuhin ang PSC Analysis",
  sandbox_analyzing: "Sinusuri...",
  sandbox_reset: "I-reset",
  sandbox_demo_mode: "Demo Mode",
  sandbox_result_header: "Tapos na ang Pagsusuri",
  sandbox_no_defects: "Walang depekto",
  sandbox_defects_found_single: "{n} depekto na natuklasan",
  sandbox_defects_found_plural: "{n} depekto na natuklasan",
  sandbox_compliant: "✓ PSC Compliant",
  sandbox_compliant_desc: "Walang natuklasang depekto. Mukhang compliant ang barko sa inspection area na ito.",
  sandbox_link_risk: "I-simulate ang Port Risk →",
  sandbox_upload_hint: "Mag-upload ng larawan at patakbuhin ang analysis upang makita ang PSC defect results",

  // Risk page
  risk_title: "PSC Risk Simulator",
  risk_desc: "Hulaan ang detention probability batay sa destinasyong daungan at natuklasang depekto, gamit ang historical MOU data.",
  risk_label_port: "Destinasyong Daungan",
  risk_label_defects: "Natuklasang Depekto",
  risk_label_age: "Edad ng Barko",
  risk_defect_rust: "Kalawang",
  risk_defect_damage: "Pinsala",
  risk_defect_leak: "Tagas",
  risk_age_years: "{n} taon",
  risk_calc_btn: "Kalkulahin ang Risk",
  risk_calculating: "Kinakalkula...",
  risk_placeholder: "Itakda ang mga parameter at i-click ang Kalkulahin ang Risk",
  risk_detention_prob: "Detention Probability",
  risk_breakdown_title: "Risk Breakdown",
  risk_base_rate: "Base Port Rate",
  risk_avg_duration: "Average Detention Duration",
  risk_link_roi: "Kalkulahin ang Financial Exposure →",

  // ROI page
  roi_title: "Detention Cost Calculator",
  roi_desc: "I-convert ang depekto sa cost exposure at tingnan ang ROI mula sa pag-iwas sa isang detention.",
  roi_label_defects: "Kasalukuyang Depekto",
  roi_label_port: "Port of Call",
  roi_label_vessel_type: "Uri ng Barko",
  roi_label_dwt: "Vessel DWT",
  roi_vessel_bulk: "Bulk Carrier",
  roi_vessel_container: "Container Ship",
  roi_vessel_tanker: "Tanker",
  roi_vessel_roro: "Ro-Ro",
  roi_vessel_gas: "Gas Carrier",
  roi_vessel_passenger: "Passenger",
  roi_vessel_general: "General Cargo",
  roi_calc_btn: "Kalkulahin ang Exposure",
  roi_calculating: "Kinakalkula...",
  roi_placeholder: "Pumili ng depekto at vessel parameters upang makita ang cost exposure",
  roi_total_exposure: "Kabuuang Financial Exposure (kada paglalayag)",
  roi_detention_days: "{n} araw na inaasahang detention",
  roi_breakdown_title: "Cost Breakdown",
  roi_cost_detention: "Vessel Detention Cost",
  roi_cost_cargo: "Cargo Delay Cost",
  roi_cost_repute: "Reputation/Admin Cost",
  roi_section_title: "B-Wave ROI",
  roi_ratio_label: "ROI Ratio",
  roi_payback_label: "Payback Period",
  roi_annual_label: "Annual Cost",
  roi_payback_text: "Ang pag-iwas sa isang detention ay sumasaklaw sa {n} taon ng B-Wave",
  roi_link_quote: "Kumuha ng Opisyal na Quote →",

  // Fleet page
  fleet_title: "Fleet Dashboard",
  fleet_desc: "Real-time PSC risk status para sa 50 barko sa mga global shipping lanes.",
  fleet_tile_total: "Total Fleet",
  fleet_tile_compliant: "Compliant",
  fleet_tile_monitor: "Monitor",
  fleet_tile_at_risk: "May Panganib",
  fleet_filter_all: "Lahat",
  fleet_filter_risk: "May Panganib",
  fleet_filter_monitor: "Monitor",
  fleet_filter_ok: "Compliant",
  fleet_loading: "Naglo-load ng fleet data...",
  fleet_detail_risk: "PSC Risk",
  fleet_detail_defects: "Mga Depekto",
  fleet_detail_inspection: "Huling Inspeksyon",
  fleet_detail_next_port: "Susunod na Daungan",
  fleet_no_defects: "Wala",
  fleet_btn_risk: "I-simulate ang Risk",
  fleet_btn_cost: "Kalkulahin ang Cost",

  // Footer
  footer_copyright: "© 2026 Spinai — B-Wave Edge Vision AI · PSC Compliance Scanner",
  footer_model_meta: "Model: YOLO26s-v1 · mAP50-95=0.323 · Latency p95=9.3ms (RTX4090)",

  // Zones
  zone_bow: "Bow",
  zone_midship: "Gitna",
  zone_stern: "Stern",
  zone_deck: "Kubyerta",
  zone_hull: "Hull",
  zone_engine_room: "Silid Makina",
} as const satisfies Record<keyof typeof ko, string>;

export default tl;
