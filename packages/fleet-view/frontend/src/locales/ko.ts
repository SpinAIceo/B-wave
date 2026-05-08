const ko = {
  // App / Navigation
  appSubtitle: '선단 뷰 대시보드',
  navDashboard: '대시보드',
  navFleetMap: '선단 지도',
  navVessels: '선박',
  navReports: '보고서',

  // Dashboard — stat cards
  totalVessels: '전체 선박',
  activeInspections: '활성 점검',
  criticalDefects: '위험 결함',
  detentionRisk: '억류 위험',
  trendThisMonth: '+2 이번 달',
  trendOngoing: '진행 중',
  trendVsLastWeek: '-3 지난 주 대비',
  trendScoreOf100: '점수 / 100',

  // Dashboard — chart titles
  defectDistribution: '결함 분포',
  fleetStatus: '선단 상태',
  recentInspections: '최근 점검',

  // Dashboard — table headers
  vessel: '선박',
  port: '항구',
  date: '날짜',
  result: '결과',
  critical: '위험',

  // Result badges
  pass: '합격',
  fail: '불합격',

  // Loading
  loading: '불러오는 중...',

  // Fleet Map — tooltip labels
  status: '상태',
  lastInspection: '최근 점검',
  criticalDefectsLabel: '위험 결함',

  // Fleet Map — legend
  legendNoIssues: '이상 없음',
  legendWarnings: '경고',
  legendCritical: '위험',

  // Vessel List — search
  searchPlaceholder: '선박 검색...',
  vesselCount: '{n}척',

  // Vessel List — table headers
  colName: '선박명',
  colType: '종류',
  colFlag: '국기',
  colStatus: '상태',
  colLastInspection: '최근 점검',
  colCritical: '위험',
  colDetentionRisk: '억류 위험',

  // Vessel statuses
  statusSailing: '항해 중',
  statusPort: '입항',
  statusAnchor: '정박',
  statusMaintenance: '정비 중',

  // Defect types
  defectRust: '부식',
  defectDamage: '손상',
  defectLeak: '누수',
  defectMissingLabel: '라벨 누락',
  defectCargoLashing: '화물 결박',

  // Vessel Detail
  backToFleet: '← 선단으로 돌아가기',
  flagLabel: '국기',
  detentionRiskLabel: '억류 위험',
  inspectionHistory: '점검 이력',
  noInspectionsRecorded: '점검 기록 없음',
  passLabel: '합격',
  failLabel: '불합격',
  criticalLabel: '위험',
  mouSuffix: 'MoU',
  quickActions: '빠른 작업',
  generatePscReport: '📋 PSC 준비 상태 보고서 생성',
  viewLastInspection: '🔍 최근 점검 보기',
  scheduleInspection: '📅 점검 예약',
  vesselInfo: '선박 정보',
  infoPosition: '위치',
  infoLastInspection: '최근 점검',
  infoCriticalDefects: '위험 결함',
  infoDetentionRisk: '억류 위험',
  reportGenerated: '보고서 생성됨',
  openingLastInspection: '최근 점검을 여는 중...',
  schedulingInspection: '점검 예약 중...',

  // Log Viewer
  navLogs: '오류 로그',
  logsTitle: '오류 로그 검토',
  logsDesc: '백엔드 WARNING/ERROR 로그를 X-Request-ID 기준으로 일괄 조회합니다.',
  logsFilterLevel: '레벨 필터',
  logsFilterReqId: 'Request-ID 검색',
  logsFilterAll: '전체 (WARNING+ERROR)',
  logsBtnRefresh: '새로고침',
  logsBtnClear: '전체 삭제',
  logsColTs: '발생 시각',
  logsColLevel: '레벨',
  logsColReqId: 'Request-ID',
  logsColModule: '모듈',
  logsColMessage: '메시지',
  logsEmpty: '조건에 맞는 오류 로그가 없습니다.',
  logsLoading: '로그 불러오는 중...',
  logsClearConfirm: '전체 오류 로그를 삭제하시겠습니까?',

  // Reports
  generateReport: '보고서 생성',
  vesselLabel: '선박',
  reportTypeLabel: '보고서 유형',
  selectVessel: '선박 선택...',
  generateBtn: '생성',
  selectVesselAlert: '선박을 선택하세요',
  generatedReports: '생성된 보고서',
  colReportId: '보고서 ID',
  colVessel: '선박',
  rptColType: '유형',
  colGenerated: '생성일',
  rptColStatus: '상태',
  colAction: '작업',
  downloadPdf: 'PDF 다운로드',
  statusReady: '완료',
  statusGenerating: '생성 중',
  downloading: '{id} 다운로드 중...',

  // Report types
  reportPscReadiness: 'PSC 준비 상태 보고서',
  reportClassSurvey: '선급 검사 보고서',
  reportSecurityAudit: '보안 감사 (UR E26/E27)',
  reportCicCompliance: 'CIC 2026 준수 (화물 결박)',

  // Zones
  zone_bow: '선수',
  zone_midship: '중앙',
  zone_stern: '선미',
  zone_deck: '갑판',
  zone_hull: '선체',
  zone_engine_room: '기관실',

  // Vessel diagram
  defectMap: '결함 위치 지도',
  clickZoneToFilter: '구역을 클릭해서 결함을 필터하세요',
  clearFilter: '전체 보기',
  defectsInZone: '{zone}의 결함',
  noDefectsInZone: '이 구역에 결함 없음',

  // Auth
  loginUsername: '사용자명',
  loginPassword: '비밀번호',
  loginSubmit: '로그인',
  loginSubmitting: '로그인 중...',
  loginRequired: '사용자명과 비밀번호를 입력하세요',
  loginInvalidCredentials: '사용자명 또는 비밀번호가 올바르지 않습니다',
  loginGenericError: '로그인 실패',
  loginRolesHint: '권한별 데모 계정: admin · operator · viewer',
  logout: '로그아웃',
} as const;

export default ko;
