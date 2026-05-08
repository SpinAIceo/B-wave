import ko from './ko';

const id = {
  // App / Navigation
  appSubtitle: 'Dasbor Tampilan Armada',
  navDashboard: 'Dasbor',
  navFleetMap: 'Peta Armada',
  navVessels: 'Kapal',
  navReports: 'Laporan',

  // Dashboard — stat cards
  totalVessels: 'Total Kapal',
  activeInspections: 'Inspeksi Aktif',
  criticalDefects: 'Cacat Kritis',
  detentionRisk: 'Risiko Penahanan',
  trendThisMonth: '+2 bulan ini',
  trendOngoing: 'Berlangsung',
  trendVsLastWeek: '-3 vs minggu lalu',
  trendScoreOf100: 'skor / 100',

  // Dashboard — chart titles
  defectDistribution: 'Distribusi Cacat',
  fleetStatus: 'Status Armada',
  recentInspections: 'Inspeksi Terbaru',

  // Dashboard — table headers
  vessel: 'Kapal',
  port: 'Pelabuhan',
  date: 'Tanggal',
  result: 'Hasil',
  critical: 'Kritis',

  // Result badges
  pass: 'Lulus',
  fail: 'Gagal',

  // Loading
  loading: 'Memuat...',

  // Fleet Map — tooltip labels
  status: 'Status',
  lastInspection: 'Inspeksi Terakhir',
  criticalDefectsLabel: 'Cacat Kritis',

  // Fleet Map — legend
  legendNoIssues: 'Tidak Ada Masalah',
  legendWarnings: 'Peringatan',
  legendCritical: 'Kritis',

  // Vessel List — search
  searchPlaceholder: 'Cari kapal...',
  vesselCount: '{n} kapal',

  // Vessel List — table headers
  colName: 'Nama',
  colType: 'Jenis',
  colFlag: 'Bendera',
  colStatus: 'Status',
  colLastInspection: 'Inspeksi Terakhir',
  colCritical: 'Kritis',
  colDetentionRisk: 'Risiko Penahanan',

  // Vessel statuses
  statusSailing: 'Berlayar',
  statusPort: 'Di Pelabuhan',
  statusAnchor: 'Berlabuh',
  statusMaintenance: 'Pemeliharaan',

  // Defect types
  defectRust: 'Karat',
  defectDamage: 'Kerusakan',
  defectLeak: 'Bocor',
  defectMissingLabel: 'Label Hilang',
  defectCargoLashing: 'Pengikat Muatan',

  // Vessel Detail
  backToFleet: '← Kembali ke Armada',
  flagLabel: 'Bendera',
  detentionRiskLabel: 'Risiko Penahanan',
  inspectionHistory: 'Riwayat Inspeksi',
  noInspectionsRecorded: 'Tidak ada inspeksi tercatat',
  passLabel: 'Lulus',
  failLabel: 'Gagal',
  criticalLabel: 'Kritis',
  mouSuffix: 'MoU',
  quickActions: 'Aksi Cepat',
  generatePscReport: '📋 Buat Laporan Kesiapan PSC',
  viewLastInspection: '🔍 Lihat Inspeksi Terakhir',
  scheduleInspection: '📅 Jadwalkan Inspeksi',
  vesselInfo: 'Informasi Kapal',
  infoPosition: 'Posisi',
  infoLastInspection: 'Inspeksi Terakhir',
  infoCriticalDefects: 'Cacat Kritis',
  infoDetentionRisk: 'Risiko Penahanan',
  reportGenerated: 'Laporan dibuat',
  openingLastInspection: 'Membuka inspeksi terakhir...',
  schedulingInspection: 'Menjadwalkan inspeksi...',

  // Log Viewer
  navLogs: 'Log Kesalahan',
  logsTitle: 'Tinjauan Log Kesalahan',
  logsDesc: 'Lihat log WARNING/ERROR backend berdasarkan X-Request-ID.',
  logsFilterLevel: 'Filter Level',
  logsFilterReqId: 'Cari Request-ID',
  logsFilterAll: 'Semua (WARNING+ERROR)',
  logsBtnRefresh: 'Segarkan',
  logsBtnClear: 'Hapus Semua',
  logsColTs: 'Waktu',
  logsColLevel: 'Level',
  logsColReqId: 'Request-ID',
  logsColModule: 'Modul',
  logsColMessage: 'Pesan',
  logsEmpty: 'Tidak ada log kesalahan yang sesuai filter.',
  logsLoading: 'Memuat log...',
  logsClearConfirm: 'Yakin ingin menghapus semua log kesalahan?',

  // Reports
  generateReport: 'Buat Laporan',
  vesselLabel: 'Kapal',
  reportTypeLabel: 'Jenis Laporan',
  selectVessel: 'Pilih kapal...',
  generateBtn: 'Buat',
  selectVesselAlert: 'Silakan pilih kapal',
  generatedReports: 'Laporan Dihasilkan',
  colReportId: 'ID Laporan',
  colVessel: 'Kapal',
  rptColType: 'Jenis',
  colGenerated: 'Dibuat',
  rptColStatus: 'Status',
  colAction: 'Aksi',
  downloadPdf: 'Unduh PDF',
  statusReady: 'Siap',
  statusGenerating: 'Membuat',
  downloading: 'Mengunduh {id}...',

  // Report types
  reportPscReadiness: 'Laporan Kesiapan PSC',
  reportClassSurvey: 'Laporan Survei Klas',
  reportSecurityAudit: 'Audit Keamanan (UR E26/E27)',
  reportCicCompliance: 'Kepatuhan CIC 2026 (Pengikat Muatan)',

  // Zones
  zone_bow: 'Haluan',
  zone_midship: 'Tengah',
  zone_stern: 'Buritan',
  zone_deck: 'Geladak',
  zone_hull: 'Lambung',
  zone_engine_room: 'Kamar Mesin',

  // Vessel diagram
  defectMap: 'Peta Cacat',
  clickZoneToFilter: 'Klik zona untuk memfilter cacat',
  clearFilter: 'Tampilkan Semua',
  defectsInZone: 'Cacat di {zone}',
  noDefectsInZone: 'Tidak ada cacat di zona ini',

  // Auth
  loginUsername: 'Nama Pengguna',
  loginPassword: 'Kata Sandi',
  loginSubmit: 'Masuk',
  loginSubmitting: 'Sedang masuk...',
  loginRequired: 'Masukkan nama pengguna dan kata sandi',
  loginInvalidCredentials: 'Nama pengguna atau kata sandi tidak valid',
  loginGenericError: 'Gagal masuk',
  loginRolesHint: 'Akun demo per peran: admin · operator · viewer',
  logout: 'Keluar',
} as const satisfies Record<keyof typeof ko, string>;

export default id;
