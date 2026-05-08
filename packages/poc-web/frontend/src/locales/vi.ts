import ko from "./ko";

const vi = {
  // NavBar
  nav_ai_sandbox: "Hộp cát AI",
  nav_psc_risk: "Rủi ro PSC",
  nav_roi_calculator: "Máy tính ROI",
  nav_fleet_demo: "Demo đội tàu",
  nav_brand_subtitle: "Máy quét PSC",
  nav_try_free: "Dùng thử miễn phí",

  // Home — hero
  home_badge: "PoC ảo trực tiếp — Không cần phần cứng",
  home_hero_title1: "Phát hiện khuyết tật PSC tàu",
  home_hero_title2: "Dưới 500ms",
  home_hero_desc:
    "B-Wave triển khai trên máy chủ edge của tàu. Thuyền viên hướng camera máy tính bảng vào thiết bị — rỉ sét, hư hỏng, rò rỉ được đánh dấu với mã vi phạm PSC trước khi thanh tra viên đến.",
  home_cta_primary: "Tải lên ảnh tàu →",
  home_cta_secondary: "Xem tổn thất chi phí",

  // Home — features
  feat_sandbox_title: "Máy quét khuyết tật AI",
  feat_sandbox_desc:
    "Tải lên ảnh tàu. Nhận ngay mã vi phạm PSC, lớp phủ bounding-box và phân loại mức độ nghiêm trọng — được hỗ trợ bởi YOLO26s đào tạo trên 11.000+ ảnh hàng hải.",
  feat_sandbox_cta: "Thử Hộp cát →",
  feat_risk_title: "Trình mô phỏng rủi ro PSC cảng",
  feat_risk_desc:
    "Chọn cảng đích và khuyết tật phát hiện. Số liệu MOU thực từ Tokyo, Paris, USCG và 20+ cơ quan khu vực dự đoán xác suất bắt giữ.",
  feat_risk_cta: "Mô phỏng rủi ro →",
  feat_roi_title: "Máy tính chi phí bắt giữ",
  feat_roi_desc:
    "Chuyển đổi khuyết tật thành rủi ro tài chính. So sánh ngày bắt giữ, phạt chậm trễ hàng hóa và chi phí danh tiếng với khoản đầu tư hệ thống B-Wave.",
  feat_roi_cta: "Tính ROI →",
  feat_fleet_title: "Demo bảng điều khiển đội tàu",
  feat_fleet_desc:
    "Xem trực tiếp 50 tàu trên các tuyến vận tải toàn cầu. Trạng thái rủi ro PSC xanh/vàng/đỏ cập nhật trực tiếp.",
  feat_fleet_cta: "Xem đội tàu →",

  // Home — stats
  stat_latency_label: "độ trễ suy luận p95",
  stat_map_label: "mAP50-95 (3 lớp)",
  stat_images_label: "ảnh huấn luyện",
  stat_sla_label: "SLA đầu cuối",

  // Home — CTA card
  home_demo_title: "Muốn demo đầy đủ?",
  home_demo_desc:
    "Xem B-Wave chạy trên phần cứng edge thực. Chúng tôi mang thiết bị — bạn cung cấp tàu.",
  home_demo_cta: "Yêu cầu demo phần cứng",

  // Sandbox page
  sandbox_title: "Máy quét khuyết tật AI",
  sandbox_desc: "Tải lên ảnh thiết bị tàu — vỏ tàu, đường ống, kết cấu boong — và nhận phân tích khuyết tật PSC tức thì.",
  sandbox_vessel_label: "Tàu",
  sandbox_sync_hint: "Kết quả đồng bộ với bảng đội tàu",
  sandbox_dropzone_title: "Thả ảnh tàu vào đây",
  sandbox_dropzone_hint: "JPG, PNG, WebP · tối đa 20MB",
  sandbox_run_btn: "Chạy phân tích PSC",
  sandbox_analyzing: "Đang phân tích...",
  sandbox_reset: "Đặt lại",
  sandbox_demo_mode: "Chế độ Demo",
  sandbox_result_header: "Phân tích hoàn tất",
  sandbox_no_defects: "Không có khuyết tật",
  sandbox_defects_found_single: "Tìm thấy {n} khuyết tật",
  sandbox_defects_found_plural: "Tìm thấy {n} khuyết tật",
  sandbox_compliant: "✓ Tuân thủ PSC",
  sandbox_compliant_desc: "Không phát hiện khuyết tật. Tàu có vẻ tuân thủ trong khu vực kiểm tra này.",
  sandbox_link_risk: "Mô phỏng rủi ro cảng →",
  sandbox_upload_hint: "Tải ảnh lên và chạy phân tích để xem kết quả khuyết tật PSC",

  // Risk page
  risk_title: "Trình mô phỏng rủi ro PSC",
  risk_desc: "Dự đoán xác suất bắt giữ dựa trên cảng đích và khuyết tật phát hiện, sử dụng dữ liệu MOU lịch sử.",
  risk_label_port: "Cảng đích",
  risk_label_defects: "Khuyết tật phát hiện",
  risk_label_age: "Tuổi tàu",
  risk_defect_rust: "Rỉ sét",
  risk_defect_damage: "Hư hỏng",
  risk_defect_leak: "Rò rỉ",
  risk_age_years: "{n} năm",
  risk_calc_btn: "Tính rủi ro",
  risk_calculating: "Đang tính...",
  risk_placeholder: "Đặt tham số và nhấp Tính rủi ro",
  risk_detention_prob: "Xác suất bắt giữ",
  risk_breakdown_title: "Phân tích rủi ro",
  risk_base_rate: "Tỷ lệ cơ sở của cảng",
  risk_avg_duration: "Thời gian bắt giữ trung bình",
  risk_link_roi: "Tính tổn thất tài chính →",

  // ROI page
  roi_title: "Máy tính chi phí bắt giữ",
  roi_desc: "Chuyển đổi khuyết tật thành rủi ro chi phí và xem ROI từ việc ngăn chặn một lần bắt giữ.",
  roi_label_defects: "Khuyết tật hiện tại",
  roi_label_port: "Cảng ghé",
  roi_label_vessel_type: "Loại tàu",
  roi_label_dwt: "DWT tàu",
  roi_vessel_bulk: "Tàu hàng rời",
  roi_vessel_container: "Tàu container",
  roi_vessel_tanker: "Tàu chở dầu",
  roi_vessel_roro: "Ro-Ro",
  roi_vessel_gas: "Tàu chở khí",
  roi_vessel_passenger: "Tàu khách",
  roi_vessel_general: "Hàng tổng hợp",
  roi_calc_btn: "Tính tổn thất tài chính",
  roi_calculating: "Đang tính...",
  roi_placeholder: "Chọn khuyết tật và tham số tàu để xem rủi ro chi phí",
  roi_total_exposure: "Tổng tổn thất tài chính (mỗi chuyến)",
  roi_detention_days: "{n} ngày bắt giữ dự kiến",
  roi_breakdown_title: "Phân tích chi phí",
  roi_cost_detention: "Chi phí bắt giữ tàu",
  roi_cost_cargo: "Chi phí chậm trễ hàng hóa",
  roi_cost_repute: "Chi phí danh tiếng/hành chính",
  roi_section_title: "ROI B-Wave",
  roi_ratio_label: "Tỷ lệ ROI",
  roi_payback_label: "Thời gian hoàn vốn",
  roi_annual_label: "Chi phí hàng năm",
  roi_payback_text: "Ngăn chặn một lần bắt giữ trang trải {n} năm B-Wave",
  roi_link_quote: "Nhận báo giá chính thức →",

  // Fleet page
  fleet_title: "Bảng điều khiển đội tàu",
  fleet_desc: "Trạng thái rủi ro PSC thời gian thực cho 50 tàu trên các tuyến vận tải toàn cầu.",
  fleet_tile_total: "Tổng đội tàu",
  fleet_tile_compliant: "Tuân thủ",
  fleet_tile_monitor: "Theo dõi",
  fleet_tile_at_risk: "Có rủi ro",
  fleet_filter_all: "Tất cả",
  fleet_filter_risk: "Có rủi ro",
  fleet_filter_monitor: "Theo dõi",
  fleet_filter_ok: "Tuân thủ",
  fleet_loading: "Đang tải dữ liệu đội tàu...",
  fleet_detail_risk: "Rủi ro PSC",
  fleet_detail_defects: "Khuyết tật",
  fleet_detail_inspection: "Kiểm tra cuối",
  fleet_detail_next_port: "Cảng tiếp theo",
  fleet_no_defects: "Không",
  fleet_btn_risk: "Mô phỏng rủi ro",
  fleet_btn_cost: "Tính chi phí",

  // Footer
  footer_copyright: "© 2026 Spinai — B-Wave Edge Vision AI · Máy quét tuân thủ PSC",
  footer_model_meta: "Mô hình: YOLO26s-v1 · mAP50-95=0.323 · Độ trễ p95=9.3ms (RTX4090)",

  // Zones
  zone_bow: "Mũi tàu",
  zone_midship: "Giữa tàu",
  zone_stern: "Đuôi tàu",
  zone_deck: "Boong",
  zone_hull: "Thân tàu",
  zone_engine_room: "Phòng máy",
} as const satisfies Record<keyof typeof ko, string>;

export default vi;
