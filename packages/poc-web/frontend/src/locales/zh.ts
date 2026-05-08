import ko from "./ko";

const zh = {
  // NavBar
  nav_ai_sandbox: "AI 沙盒",
  nav_psc_risk: "PSC 风险",
  nav_roi_calculator: "ROI 计算器",
  nav_fleet_demo: "船队演示",
  nav_brand_subtitle: "PSC 扫描仪",
  nav_try_free: "免费试用",

  // Home — hero
  home_badge: "实时虚拟 PoC — 无需硬件",
  home_hero_title1: "船舶 PSC 缺陷检测",
  home_hero_title2: "500ms 内完成",
  home_hero_desc:
    "B-Wave 部署在船舶的边缘服务器上。船员只需将平板相机对准设备 — 在检查员到达之前,锈蚀、损伤、泄漏即可显示并附带 PSC 违规代码。",
  home_cta_primary: "上传船舶照片 →",
  home_cta_secondary: "查看成本风险",

  // Home — features
  feat_sandbox_title: "AI 缺陷扫描仪",
  feat_sandbox_desc:
    "上传船舶照片。即可获得 PSC 违规代码、边界框叠加和严重性分级 — 基于 11,000+ 海上图像训练的 YOLO26s。",
  feat_sandbox_cta: "试用沙盒 →",
  feat_risk_title: "港口 PSC 风险模拟器",
  feat_risk_desc:
    "选择目的地港口和检测到的缺陷。使用东京、巴黎、USCG 及 20+ 区域机构的真实 MOU 统计数据预测滞留概率。",
  feat_risk_cta: "模拟风险 →",
  feat_roi_title: "滞留成本计算器",
  feat_roi_desc:
    "将缺陷转换为成本风险。比较滞留天数、货物延误罚金、声誉损失成本与 B-Wave 系统投资。",
  feat_roi_cta: "计算 ROI →",
  feat_fleet_title: "船队仪表板演示",
  feat_fleet_desc:
    "全球航线上 50 艘船舶的实时可视化。绿/黄/红 PSC 风险状态实时更新。",
  feat_fleet_cta: "查看船队 →",

  // Home — stats
  stat_latency_label: "p95 推理延迟",
  stat_map_label: "mAP50-95 (3 类)",
  stat_images_label: "训练图像数",
  stat_sla_label: "端到端 SLA",

  // Home — CTA card
  home_demo_title: "想要完整演示?",
  home_demo_desc:
    "在真实边缘硬件上亲自体验 B-Wave。我们带设备 — 您只需提供船舶。",
  home_demo_cta: "申请硬件演示",

  // Sandbox page
  sandbox_title: "AI 缺陷扫描仪",
  sandbox_desc: "上传船舶设备照片 — 船体、管道、甲板结构 — 立即获得 PSC 缺陷分析。",
  sandbox_vessel_label: "船舶",
  sandbox_sync_hint: "结果同步到船队仪表板",
  sandbox_dropzone_title: "将船舶照片拖放至此",
  sandbox_dropzone_hint: "JPG, PNG, WebP · 最大 20MB",
  sandbox_run_btn: "运行 PSC 分析",
  sandbox_analyzing: "分析中...",
  sandbox_reset: "重置",
  sandbox_demo_mode: "演示模式",
  sandbox_result_header: "分析完成",
  sandbox_no_defects: "无缺陷",
  sandbox_defects_found_single: "发现 {n} 个缺陷",
  sandbox_defects_found_plural: "发现 {n} 个缺陷",
  sandbox_compliant: "✓ PSC 合规",
  sandbox_compliant_desc: "未检测到缺陷。该检验区域船舶看起来合规。",
  sandbox_link_risk: "模拟港口风险 →",
  sandbox_upload_hint: "上传图像并运行分析以查看 PSC 缺陷结果",

  // Risk page
  risk_title: "PSC 风险模拟器",
  risk_desc: "使用历史 MOU 数据,根据目的地港口和检测到的缺陷预测滞留概率。",
  risk_label_port: "目的地港口",
  risk_label_defects: "检测到的缺陷",
  risk_label_age: "船龄",
  risk_defect_rust: "锈蚀",
  risk_defect_damage: "损伤",
  risk_defect_leak: "泄漏",
  risk_age_years: "{n} 年",
  risk_calc_btn: "计算风险",
  risk_calculating: "计算中...",
  risk_placeholder: "设置参数并点击计算风险",
  risk_detention_prob: "滞留概率",
  risk_breakdown_title: "风险分解",
  risk_base_rate: "港口基础滞留率",
  risk_avg_duration: "平均滞留时间",
  risk_link_roi: "计算财务风险 →",

  // ROI page
  roi_title: "滞留成本计算器",
  roi_desc: "将缺陷转换为成本风险,查看预防一次滞留所获得的 ROI。",
  roi_label_defects: "当前缺陷",
  roi_label_port: "停靠港口",
  roi_label_vessel_type: "船舶类型",
  roi_label_dwt: "船舶载重吨",
  roi_vessel_bulk: "散货船",
  roi_vessel_container: "集装箱船",
  roi_vessel_tanker: "油轮",
  roi_vessel_roro: "滚装船",
  roi_vessel_gas: "液化气船",
  roi_vessel_passenger: "客船",
  roi_vessel_general: "杂货船",
  roi_calc_btn: "计算成本风险",
  roi_calculating: "计算中...",
  roi_placeholder: "选择缺陷和船舶参数以查看成本风险",
  roi_total_exposure: "总财务风险 (每航次)",
  roi_detention_days: "预计滞留 {n} 天",
  roi_breakdown_title: "成本分解",
  roi_cost_detention: "船舶滞留成本",
  roi_cost_cargo: "货物延误成本",
  roi_cost_repute: "声誉/行政成本",
  roi_section_title: "B-Wave ROI",
  roi_ratio_label: "ROI 比率",
  roi_payback_label: "投资回收期",
  roi_annual_label: "年度成本",
  roi_payback_text: "预防一次滞留可覆盖 {n} 年的 B-Wave 费用",
  roi_link_quote: "获取正式报价 →",

  // Fleet page
  fleet_title: "船队仪表板",
  fleet_desc: "全球航线上 50 艘船舶的实时 PSC 风险状态。",
  fleet_tile_total: "总船队",
  fleet_tile_compliant: "合规",
  fleet_tile_monitor: "监控",
  fleet_tile_at_risk: "有风险",
  fleet_filter_all: "全部",
  fleet_filter_risk: "有风险",
  fleet_filter_monitor: "监控",
  fleet_filter_ok: "合规",
  fleet_loading: "加载船队数据中...",
  fleet_detail_risk: "PSC 风险",
  fleet_detail_defects: "缺陷",
  fleet_detail_inspection: "最近检验",
  fleet_detail_next_port: "下一个港口",
  fleet_no_defects: "无",
  fleet_btn_risk: "模拟风险",
  fleet_btn_cost: "计算成本",

  // Footer
  footer_copyright: "© 2026 Spinai — B-Wave Edge Vision AI · PSC 合规扫描仪",
  footer_model_meta: "模型: YOLO26s-v1 · mAP50-95=0.323 · 延迟 p95=9.3ms (RTX4090)",

  // Zones
  zone_bow: "船首",
  zone_midship: "中部",
  zone_stern: "船尾",
  zone_deck: "甲板",
  zone_hull: "船体",
  zone_engine_room: "机舱",
} as const satisfies Record<keyof typeof ko, string>;

export default zh;
