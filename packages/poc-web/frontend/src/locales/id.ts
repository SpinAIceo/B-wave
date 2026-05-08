import ko from "./ko";

const id = {
  // NavBar
  nav_ai_sandbox: "AI Sandbox",
  nav_psc_risk: "Risiko PSC",
  nav_roi_calculator: "Kalkulator ROI",
  nav_fleet_demo: "Demo Armada",
  nav_brand_subtitle: "Pemindai PSC",
  nav_try_free: "Coba Gratis",

  // Home — hero
  home_badge: "PoC Virtual Langsung — Tanpa Perangkat Keras",
  home_hero_title1: "Deteksi Cacat PSC Kapal",
  home_hero_title2: "Dalam 500ms",
  home_hero_desc:
    "B-Wave digunakan pada server edge kapal. Kru mengarahkan kamera tablet ke peralatan — korosi, kerusakan, kebocoran ditandai dengan kode pelanggaran PSC sebelum inspektur tiba.",
  home_cta_primary: "Unggah Foto Kapal →",
  home_cta_secondary: "Lihat Risiko Biaya",

  // Home — features
  feat_sandbox_title: "Pemindai Cacat AI",
  feat_sandbox_desc:
    "Unggah foto kapal. Dapatkan kode pelanggaran PSC instan, overlay bounding-box, dan grading tingkat keparahan — didukung oleh YOLO26s yang dilatih dengan 11.000+ gambar maritim.",
  feat_sandbox_cta: "Coba Sandbox →",
  feat_risk_title: "Simulator Risiko PSC Pelabuhan",
  feat_risk_desc:
    "Pilih pelabuhan tujuan dan cacat yang terdeteksi. Statistik MOU asli dari Tokyo, Paris, USCG, dan 20+ otoritas regional memprediksi probabilitas penahanan.",
  feat_risk_cta: "Simulasikan Risiko →",
  feat_roi_title: "Kalkulator Biaya Penahanan",
  feat_roi_desc:
    "Konversi cacat menjadi paparan finansial. Bandingkan hari penahanan, denda keterlambatan kargo, dan biaya reputasi terhadap investasi sistem B-Wave.",
  feat_roi_cta: "Hitung ROI →",
  feat_fleet_title: "Demo Dasbor Armada",
  feat_fleet_desc:
    "Tampilan real-time 50 kapal di seluruh jalur pelayaran global. Status risiko PSC hijau/kuning/merah diperbarui langsung.",
  feat_fleet_cta: "Lihat Armada →",

  // Home — stats
  stat_latency_label: "latensi inferensi p95",
  stat_map_label: "mAP50-95 (3 kelas)",
  stat_images_label: "gambar pelatihan",
  stat_sla_label: "SLA end-to-end",

  // Home — CTA card
  home_demo_title: "Ingin demo lengkap?",
  home_demo_desc:
    "Lihat B-Wave berjalan pada perangkat edge nyata. Kami bawa peralatan — Anda sediakan kapal.",
  home_demo_cta: "Minta Demo Hardware",

  // Sandbox page
  sandbox_title: "Pemindai Cacat AI",
  sandbox_desc: "Unggah foto peralatan kapal — lambung, perpipaan, struktur dek — dan dapatkan analisis cacat PSC instan.",
  sandbox_vessel_label: "Kapal",
  sandbox_sync_hint: "Hasil tersinkronisasi ke dasbor Armada",
  sandbox_dropzone_title: "Letakkan foto kapal di sini",
  sandbox_dropzone_hint: "JPG, PNG, WebP · maks 20MB",
  sandbox_run_btn: "Jalankan Analisis PSC",
  sandbox_analyzing: "Menganalisis...",
  sandbox_reset: "Reset",
  sandbox_demo_mode: "Mode Demo",
  sandbox_result_header: "Analisis Selesai",
  sandbox_no_defects: "Tidak ada cacat",
  sandbox_defects_found_single: "{n} cacat ditemukan",
  sandbox_defects_found_plural: "{n} cacat ditemukan",
  sandbox_compliant: "✓ PSC Sesuai",
  sandbox_compliant_desc: "Tidak ada cacat terdeteksi. Kapal tampak sesuai pada area inspeksi ini.",
  sandbox_link_risk: "Simulasikan Risiko Pelabuhan →",
  sandbox_upload_hint: "Unggah gambar dan jalankan analisis untuk melihat hasil cacat PSC",

  // Risk page
  risk_title: "Simulator Risiko PSC",
  risk_desc: "Prediksi probabilitas penahanan berdasarkan pelabuhan tujuan dan cacat yang terdeteksi, menggunakan data historis MOU.",
  risk_label_port: "Pelabuhan Tujuan",
  risk_label_defects: "Cacat Terdeteksi",
  risk_label_age: "Usia Kapal",
  risk_defect_rust: "Karat",
  risk_defect_damage: "Kerusakan",
  risk_defect_leak: "Bocor",
  risk_age_years: "{n} tahun",
  risk_calc_btn: "Hitung Risiko",
  risk_calculating: "Menghitung...",
  risk_placeholder: "Atur parameter dan klik Hitung Risiko",
  risk_detention_prob: "Probabilitas Penahanan",
  risk_breakdown_title: "Rincian Risiko",
  risk_base_rate: "Tingkat Dasar Pelabuhan",
  risk_avg_duration: "Rata-rata Durasi Penahanan",
  risk_link_roi: "Hitung Paparan Finansial →",

  // ROI page
  roi_title: "Kalkulator Biaya Penahanan",
  roi_desc: "Konversi cacat menjadi paparan biaya dan lihat ROI dari pencegahan satu penahanan.",
  roi_label_defects: "Cacat Saat Ini",
  roi_label_port: "Pelabuhan Singgah",
  roi_label_vessel_type: "Jenis Kapal",
  roi_label_dwt: "DWT Kapal",
  roi_vessel_bulk: "Kapal Curah",
  roi_vessel_container: "Kapal Kontainer",
  roi_vessel_tanker: "Tanker",
  roi_vessel_roro: "Ro-Ro",
  roi_vessel_gas: "Kapal Gas",
  roi_vessel_passenger: "Penumpang",
  roi_vessel_general: "Kargo Umum",
  roi_calc_btn: "Hitung Paparan",
  roi_calculating: "Menghitung...",
  roi_placeholder: "Pilih cacat dan parameter kapal untuk melihat paparan biaya",
  roi_total_exposure: "Total Paparan Finansial (per pelayaran)",
  roi_detention_days: "{n} hari penahanan diperkirakan",
  roi_breakdown_title: "Rincian Biaya",
  roi_cost_detention: "Biaya Penahanan Kapal",
  roi_cost_cargo: "Biaya Keterlambatan Kargo",
  roi_cost_repute: "Biaya Reputasi/Administrasi",
  roi_section_title: "ROI B-Wave",
  roi_ratio_label: "Rasio ROI",
  roi_payback_label: "Periode Pengembalian",
  roi_annual_label: "Biaya Tahunan",
  roi_payback_text: "Mencegah satu penahanan menutupi {n} tahun B-Wave",
  roi_link_quote: "Dapatkan Penawaran Resmi →",

  // Fleet page
  fleet_title: "Dasbor Armada",
  fleet_desc: "Status risiko PSC real-time untuk 50 kapal di jalur pelayaran global.",
  fleet_tile_total: "Total Armada",
  fleet_tile_compliant: "Sesuai",
  fleet_tile_monitor: "Pantau",
  fleet_tile_at_risk: "Berisiko",
  fleet_filter_all: "Semua",
  fleet_filter_risk: "Berisiko",
  fleet_filter_monitor: "Pantau",
  fleet_filter_ok: "Sesuai",
  fleet_loading: "Memuat data armada...",
  fleet_detail_risk: "Risiko PSC",
  fleet_detail_defects: "Cacat",
  fleet_detail_inspection: "Inspeksi Terakhir",
  fleet_detail_next_port: "Pelabuhan Berikutnya",
  fleet_no_defects: "Tidak Ada",
  fleet_btn_risk: "Simulasikan Risiko",
  fleet_btn_cost: "Hitung Biaya",

  // Footer
  footer_copyright: "© 2026 Spinai — B-Wave Edge Vision AI · Pemindai Kepatuhan PSC",
  footer_model_meta: "Model: YOLO26s-v1 · mAP50-95=0.323 · Latensi p95=9.3ms (RTX4090)",

  // Zones
  zone_bow: "Haluan",
  zone_midship: "Tengah",
  zone_stern: "Buritan",
  zone_deck: "Geladak",
  zone_hull: "Lambung",
  zone_engine_room: "Kamar Mesin",
} as const satisfies Record<keyof typeof ko, string>;

export default id;
