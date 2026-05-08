import ko from "./ko";

const en = {
  // NavBar
  nav_ai_sandbox: "AI Sandbox",
  nav_psc_risk: "PSC Risk",
  nav_roi_calculator: "ROI Calculator",
  nav_fleet_demo: "Fleet Demo",
  nav_brand_subtitle: "PSC Scanner",
  nav_try_free: "Try Free",

  // Home — hero
  home_badge: "Live Virtual PoC — No Hardware Required",
  home_hero_title1: "Ship PSC Defect Detection",
  home_hero_title2: "in Under 500ms",
  home_hero_desc:
    "B-Wave deploys on the vessel's edge server. Crew points the tablet camera at any equipment — corrosion, damage, leaks are flagged with PSC violation codes before the inspector arrives.",
  home_cta_primary: "Upload Vessel Photo →",
  home_cta_secondary: "See Cost Exposure",

  // Home — features
  feat_sandbox_title: "AI Defect Scanner",
  feat_sandbox_desc:
    "Upload a vessel photo. Get instant PSC violation codes, bounding-box overlays, and severity grading — powered by YOLO26s trained on 11,000+ maritime images.",
  feat_sandbox_cta: "Try the Sandbox →",
  feat_risk_title: "Port PSC Risk Simulator",
  feat_risk_desc:
    "Pick a destination port and detected defects. Real MOU statistics from Tokyo, Paris, USCG, and 20+ regional authorities forecast detention probability.",
  feat_risk_cta: "Simulate Risk →",
  feat_roi_title: "Detention Cost Calculator",
  feat_roi_desc:
    "Convert defects into financial exposure. Compare detention days, cargo-delay penalties, and reputational cost against the B-Wave system investment.",
  feat_roi_cta: "Calculate ROI →",
  feat_fleet_title: "Fleet Dashboard Demo",
  feat_fleet_desc:
    "Real-time view of 50 vessels across global shipping lanes. Green/yellow/red PSC risk states update live.",
  feat_fleet_cta: "View Fleet →",

  // Home — stats
  stat_latency_label: "p95 inference latency",
  stat_map_label: "mAP50-95 (3 classes)",
  stat_images_label: "training images",
  stat_sla_label: "end-to-end SLA",

  // Home — CTA card
  home_demo_title: "Want a full demo?",
  home_demo_desc:
    "See B-Wave running on real edge hardware. We bring the gear — you bring the vessel.",
  home_demo_cta: "Request Hardware Demo",

  // Sandbox page
  sandbox_title: "AI Defect Scanner",
  sandbox_desc: "Upload a photo of vessel equipment — hull, piping, deck structures — and get instant PSC defect analysis.",
  sandbox_vessel_label: "Vessel",
  sandbox_sync_hint: "Results sync to the Fleet dashboard",
  sandbox_dropzone_title: "Drop vessel photos here",
  sandbox_dropzone_hint: "JPG, PNG, WebP · max 20MB",
  sandbox_run_btn: "Run PSC Analysis",
  sandbox_analyzing: "Analyzing...",
  sandbox_reset: "Reset",
  sandbox_demo_mode: "Demo Mode",
  sandbox_result_header: "Analysis Complete",
  sandbox_no_defects: "No defects",
  sandbox_defects_found_single: "{n} defect found",
  sandbox_defects_found_plural: "{n} defects found",
  sandbox_compliant: "✓ PSC Compliant",
  sandbox_compliant_desc: "No defects detected. The vessel appears compliant in this inspection area.",
  sandbox_link_risk: "Simulate Port Risk →",
  sandbox_upload_hint: "Upload an image and run analysis to see PSC defect results",

  // Risk page
  risk_title: "PSC Risk Simulator",
  risk_desc: "Predict detention probability based on destination port and detected defects, using historical MOU data.",
  risk_label_port: "Destination Port",
  risk_label_defects: "Detected Defects",
  risk_label_age: "Vessel Age",
  risk_defect_rust: "Rust",
  risk_defect_damage: "Damage",
  risk_defect_leak: "Leak",
  risk_age_years: "{n} years",
  risk_calc_btn: "Calculate Risk",
  risk_calculating: "Calculating...",
  risk_placeholder: "Set parameters and click Calculate Risk",
  risk_detention_prob: "Detention Probability",
  risk_breakdown_title: "Risk Breakdown",
  risk_base_rate: "Base Port Rate",
  risk_avg_duration: "Avg. Detention Duration",
  risk_link_roi: "Calculate Financial Exposure →",

  // ROI page
  roi_title: "Detention Cost Calculator",
  roi_desc: "Convert defects into cost exposure and see ROI from preventing a single detention.",
  roi_label_defects: "Current Defects",
  roi_label_port: "Port of Call",
  roi_label_vessel_type: "Vessel Type",
  roi_label_dwt: "Vessel DWT",
  roi_vessel_bulk: "Bulk Carrier",
  roi_vessel_container: "Container Ship",
  roi_vessel_tanker: "Tanker",
  roi_vessel_roro: "Ro-Ro",
  roi_vessel_gas: "Gas Carrier",
  roi_vessel_passenger: "Passenger",
  roi_vessel_general: "General Cargo",
  roi_calc_btn: "Calculate Exposure",
  roi_calculating: "Calculating...",
  roi_placeholder: "Select defects and vessel parameters to see cost exposure",
  roi_total_exposure: "Total Financial Exposure (per voyage)",
  roi_detention_days: "{n} days expected detention",
  roi_breakdown_title: "Cost Breakdown",
  roi_cost_detention: "Vessel Detention Cost",
  roi_cost_cargo: "Cargo Delay Cost",
  roi_cost_repute: "Reputation/Admin Cost",
  roi_section_title: "B-Wave ROI",
  roi_ratio_label: "ROI Ratio",
  roi_payback_label: "Payback Period",
  roi_annual_label: "Annual Cost",
  roi_payback_text: "Preventing a single detention covers {n} years of B-Wave",
  roi_link_quote: "Get Official Quote →",

  // Fleet page
  fleet_title: "Fleet Dashboard",
  fleet_desc: "Real-time PSC risk status for 50 vessels across global shipping lanes.",
  fleet_tile_total: "Total Fleet",
  fleet_tile_compliant: "Compliant",
  fleet_tile_monitor: "Monitor",
  fleet_tile_at_risk: "At Risk",
  fleet_filter_all: "All",
  fleet_filter_risk: "At Risk",
  fleet_filter_monitor: "Monitor",
  fleet_filter_ok: "Compliant",
  fleet_loading: "Loading fleet data...",
  fleet_detail_risk: "PSC Risk",
  fleet_detail_defects: "Defects",
  fleet_detail_inspection: "Last Inspection",
  fleet_detail_next_port: "Next Port",
  fleet_no_defects: "None",
  fleet_btn_risk: "Simulate Risk",
  fleet_btn_cost: "Calculate Cost",

  // Footer
  footer_copyright: "© 2026 Spinai — B-Wave Edge Vision AI · PSC Compliance Scanner",
  footer_model_meta: "Model: YOLO26s-v1 · mAP50-95=0.323 · Latency p95=9.3ms (RTX4090)",

  // Zones
  zone_bow: "Bow",
  zone_midship: "Midship",
  zone_stern: "Stern",
  zone_deck: "Deck",
  zone_hull: "Hull",
  zone_engine_room: "Engine Room",
} as const satisfies Record<keyof typeof ko, string>;

export default en;
