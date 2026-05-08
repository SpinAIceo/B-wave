import ko from './ko';

const vi = {
  // App / Navigation
  appSubtitle: 'Bảng điều khiển đội tàu',
  navDashboard: 'Bảng điều khiển',
  navFleetMap: 'Bản đồ đội tàu',
  navVessels: 'Tàu',
  navReports: 'Báo cáo',

  // Dashboard — stat cards
  totalVessels: 'Tổng số tàu',
  activeInspections: 'Kiểm tra đang diễn ra',
  criticalDefects: 'Khuyết tật nghiêm trọng',
  detentionRisk: 'Rủi ro bắt giữ',
  trendThisMonth: '+2 tháng này',
  trendOngoing: 'Đang diễn ra',
  trendVsLastWeek: '-3 so với tuần trước',
  trendScoreOf100: 'điểm / 100',

  // Dashboard — chart titles
  defectDistribution: 'Phân bố khuyết tật',
  fleetStatus: 'Trạng thái đội tàu',
  recentInspections: 'Kiểm tra gần đây',

  // Dashboard — table headers
  vessel: 'Tàu',
  port: 'Cảng',
  date: 'Ngày',
  result: 'Kết quả',
  critical: 'Nghiêm trọng',

  // Result badges
  pass: 'Đạt',
  fail: 'Không đạt',

  // Loading
  loading: 'Đang tải...',

  // Fleet Map — tooltip labels
  status: 'Trạng thái',
  lastInspection: 'Kiểm tra gần nhất',
  criticalDefectsLabel: 'Khuyết tật nghiêm trọng',

  // Fleet Map — legend
  legendNoIssues: 'Không vấn đề',
  legendWarnings: 'Cảnh báo',
  legendCritical: 'Nghiêm trọng',

  // Vessel List — search
  searchPlaceholder: 'Tìm tàu...',
  vesselCount: '{n} tàu',

  // Vessel List — table headers
  colName: 'Tên',
  colType: 'Loại',
  colFlag: 'Cờ',
  colStatus: 'Trạng thái',
  colLastInspection: 'Kiểm tra gần nhất',
  colCritical: 'Nghiêm trọng',
  colDetentionRisk: 'Rủi ro bắt giữ',

  // Vessel statuses
  statusSailing: 'Đang chạy',
  statusPort: 'Tại cảng',
  statusAnchor: 'Neo đậu',
  statusMaintenance: 'Bảo trì',

  // Defect types
  defectRust: 'Rỉ sét',
  defectDamage: 'Hư hỏng',
  defectLeak: 'Rò rỉ',
  defectMissingLabel: 'Thiếu nhãn',
  defectCargoLashing: 'Chằng buộc hàng',

  // Vessel Detail
  backToFleet: '← Quay lại đội tàu',
  flagLabel: 'Cờ',
  detentionRiskLabel: 'Rủi ro bắt giữ',
  inspectionHistory: 'Lịch sử kiểm tra',
  noInspectionsRecorded: 'Không có ghi nhận kiểm tra',
  passLabel: 'Đạt',
  failLabel: 'Không đạt',
  criticalLabel: 'Nghiêm trọng',
  mouSuffix: 'MoU',
  quickActions: 'Thao tác nhanh',
  generatePscReport: '📋 Tạo báo cáo sẵn sàng PSC',
  viewLastInspection: '🔍 Xem kiểm tra gần nhất',
  scheduleInspection: '📅 Đặt lịch kiểm tra',
  vesselInfo: 'Thông tin tàu',
  infoPosition: 'Vị trí',
  infoLastInspection: 'Kiểm tra gần nhất',
  infoCriticalDefects: 'Khuyết tật nghiêm trọng',
  infoDetentionRisk: 'Rủi ro bắt giữ',
  reportGenerated: 'Đã tạo báo cáo',
  openingLastInspection: 'Đang mở kiểm tra gần nhất...',
  schedulingInspection: 'Đang đặt lịch kiểm tra...',

  // Log Viewer
  navLogs: 'Nhật ký lỗi',
  logsTitle: 'Xem nhật ký lỗi',
  logsDesc: 'Xem nhật ký WARNING/ERROR backend theo X-Request-ID.',
  logsFilterLevel: 'Lọc cấp độ',
  logsFilterReqId: 'Tìm Request-ID',
  logsFilterAll: 'Tất cả (WARNING+ERROR)',
  logsBtnRefresh: 'Làm mới',
  logsBtnClear: 'Xóa tất cả',
  logsColTs: 'Thời gian',
  logsColLevel: 'Cấp độ',
  logsColReqId: 'Request-ID',
  logsColModule: 'Module',
  logsColMessage: 'Thông điệp',
  logsEmpty: 'Không có nhật ký lỗi phù hợp bộ lọc.',
  logsLoading: 'Đang tải nhật ký...',
  logsClearConfirm: 'Bạn có chắc muốn xóa tất cả nhật ký lỗi không?',

  // Reports
  generateReport: 'Tạo báo cáo',
  vesselLabel: 'Tàu',
  reportTypeLabel: 'Loại báo cáo',
  selectVessel: 'Chọn tàu...',
  generateBtn: 'Tạo',
  selectVesselAlert: 'Vui lòng chọn tàu',
  generatedReports: 'Báo cáo đã tạo',
  colReportId: 'ID báo cáo',
  colVessel: 'Tàu',
  rptColType: 'Loại',
  colGenerated: 'Đã tạo',
  rptColStatus: 'Trạng thái',
  colAction: 'Thao tác',
  downloadPdf: 'Tải PDF',
  statusReady: 'Sẵn sàng',
  statusGenerating: 'Đang tạo',
  downloading: 'Đang tải {id}...',

  // Report types
  reportPscReadiness: 'Báo cáo sẵn sàng PSC',
  reportClassSurvey: 'Báo cáo khảo sát đăng kiểm',
  reportSecurityAudit: 'Kiểm toán an ninh (UR E26/E27)',
  reportCicCompliance: 'Tuân thủ CIC 2026 (Chằng buộc hàng)',

  // Zones
  zone_bow: 'Mũi tàu',
  zone_midship: 'Giữa tàu',
  zone_stern: 'Đuôi tàu',
  zone_deck: 'Boong',
  zone_hull: 'Thân tàu',
  zone_engine_room: 'Phòng máy',

  // Vessel diagram
  defectMap: 'Bản đồ khuyết tật',
  clickZoneToFilter: 'Nhấp vào khu vực để lọc khuyết tật',
  clearFilter: 'Hiện tất cả',
  defectsInZone: 'Khuyết tật ở {zone}',
  noDefectsInZone: 'Không có khuyết tật ở khu vực này',

  // Auth
  loginUsername: 'Tên đăng nhập',
  loginPassword: 'Mật khẩu',
  loginSubmit: 'Đăng nhập',
  loginSubmitting: 'Đang đăng nhập...',
  loginRequired: 'Vui lòng nhập tên đăng nhập và mật khẩu',
  loginInvalidCredentials: 'Tên đăng nhập hoặc mật khẩu không đúng',
  loginGenericError: 'Đăng nhập thất bại',
  loginRolesHint: 'Tài khoản demo theo vai trò: admin · operator · viewer',
  logout: 'Đăng xuất',
} as const satisfies Record<keyof typeof ko, string>;

export default vi;
