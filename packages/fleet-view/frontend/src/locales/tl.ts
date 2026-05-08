import ko from './ko';

const tl = {
  // App / Navigation
  appSubtitle: 'Fleet View Dashboard',
  navDashboard: 'Dashboard',
  navFleetMap: 'Fleet Map',
  navVessels: 'Mga Barko',
  navReports: 'Mga Ulat',

  // Dashboard — stat cards
  totalVessels: 'Kabuuang Barko',
  activeInspections: 'Aktibong Inspeksyon',
  criticalDefects: 'Kritikal na Depekto',
  detentionRisk: 'Panganib ng Pagpigil',
  trendThisMonth: '+2 ngayong buwan',
  trendOngoing: 'Nagpapatuloy',
  trendVsLastWeek: '-3 vs nakaraang linggo',
  trendScoreOf100: 'iskor / 100',

  // Dashboard — chart titles
  defectDistribution: 'Distribusyon ng Depekto',
  fleetStatus: 'Estado ng Fleet',
  recentInspections: 'Pinakahuling Inspeksyon',

  // Dashboard — table headers
  vessel: 'Barko',
  port: 'Daungan',
  date: 'Petsa',
  result: 'Resulta',
  critical: 'Kritikal',

  // Result badges
  pass: 'Pasado',
  fail: 'Bagsak',

  // Loading
  loading: 'Naglo-load...',

  // Fleet Map — tooltip labels
  status: 'Estado',
  lastInspection: 'Huling Inspeksyon',
  criticalDefectsLabel: 'Kritikal na Depekto',

  // Fleet Map — legend
  legendNoIssues: 'Walang Isyu',
  legendWarnings: 'Babala',
  legendCritical: 'Kritikal',

  // Vessel List — search
  searchPlaceholder: 'Maghanap ng barko...',
  vesselCount: '{n} barko',

  // Vessel List — table headers
  colName: 'Pangalan',
  colType: 'Uri',
  colFlag: 'Bandila',
  colStatus: 'Estado',
  colLastInspection: 'Huling Inspeksyon',
  colCritical: 'Kritikal',
  colDetentionRisk: 'Panganib Pagpigil',

  // Vessel statuses
  statusSailing: 'Naglalayag',
  statusPort: 'Nasa Daungan',
  statusAnchor: 'Naka-angkla',
  statusMaintenance: 'Pinapanatili',

  // Defect types
  defectRust: 'Kalawang',
  defectDamage: 'Pinsala',
  defectLeak: 'Tagas',
  defectMissingLabel: 'Walang Etiketa',
  defectCargoLashing: 'Pagtali ng Kargada',

  // Vessel Detail
  backToFleet: '← Bumalik sa Fleet',
  flagLabel: 'Bandila',
  detentionRiskLabel: 'Panganib Pagpigil',
  inspectionHistory: 'Kasaysayan ng Inspeksyon',
  noInspectionsRecorded: 'Walang naitalang inspeksyon',
  passLabel: 'Pasado',
  failLabel: 'Bagsak',
  criticalLabel: 'Kritikal',
  mouSuffix: 'MoU',
  quickActions: 'Mabilisang Aksyon',
  generatePscReport: '📋 Gumawa ng PSC Readiness Report',
  viewLastInspection: '🔍 Tingnan ang Huling Inspeksyon',
  scheduleInspection: '📅 Mag-iskedyul ng Inspeksyon',
  vesselInfo: 'Impormasyon ng Barko',
  infoPosition: 'Posisyon',
  infoLastInspection: 'Huling Inspeksyon',
  infoCriticalDefects: 'Kritikal na Depekto',
  infoDetentionRisk: 'Panganib Pagpigil',
  reportGenerated: 'Naka-generate ang ulat',
  openingLastInspection: 'Binubuksan ang huling inspeksyon...',
  schedulingInspection: 'Iniiskedyul ang inspeksyon...',

  // Log Viewer
  navLogs: 'Error Logs',
  logsTitle: 'Pagsusuri ng Error Log',
  logsDesc: 'Tingnan ang backend WARNING/ERROR logs ayon sa X-Request-ID.',
  logsFilterLevel: 'Filter ng Level',
  logsFilterReqId: 'Hanapin ang Request-ID',
  logsFilterAll: 'Lahat (WARNING+ERROR)',
  logsBtnRefresh: 'I-refresh',
  logsBtnClear: 'Burahin Lahat',
  logsColTs: 'Timestamp',
  logsColLevel: 'Level',
  logsColReqId: 'Request-ID',
  logsColModule: 'Module',
  logsColMessage: 'Mensahe',
  logsEmpty: 'Walang error log na tumutugma sa filter.',
  logsLoading: 'Naglo-load ng mga log...',
  logsClearConfirm: 'Sigurado ka bang gusto mong burahin lahat ng error logs?',

  // Reports
  generateReport: 'Gumawa ng Ulat',
  vesselLabel: 'Barko',
  reportTypeLabel: 'Uri ng Ulat',
  selectVessel: 'Pumili ng barko...',
  generateBtn: 'Gumawa',
  selectVesselAlert: 'Mangyaring pumili ng barko',
  generatedReports: 'Mga Nagawang Ulat',
  colReportId: 'Report ID',
  colVessel: 'Barko',
  rptColType: 'Uri',
  colGenerated: 'Nagawa noong',
  rptColStatus: 'Estado',
  colAction: 'Aksyon',
  downloadPdf: 'I-download ang PDF',
  statusReady: 'Handa na',
  statusGenerating: 'Ginagawa',
  downloading: 'Dina-download ang {id}...',

  // Report types
  reportPscReadiness: 'PSC Readiness Report',
  reportClassSurvey: 'Class Survey Report',
  reportSecurityAudit: 'Security Audit (UR E26/E27)',
  reportCicCompliance: 'CIC 2026 Compliance (Cargo Lashing)',

  // Zones
  zone_bow: 'Bow',
  zone_midship: 'Gitna',
  zone_stern: 'Stern',
  zone_deck: 'Kubyerta',
  zone_hull: 'Hull',
  zone_engine_room: 'Silid Makina',

  // Vessel diagram
  defectMap: 'Mapa ng Depekto',
  clickZoneToFilter: 'I-click ang zone para mag-filter ng depekto',
  clearFilter: 'Ipakita Lahat',
  defectsInZone: 'Mga depekto sa {zone}',
  noDefectsInZone: 'Walang depekto sa zone na ito',

  // Auth
  loginUsername: 'Username',
  loginPassword: 'Password',
  loginSubmit: 'Mag-Login',
  loginSubmitting: 'Nagla-login...',
  loginRequired: 'Pakilagay ang username at password',
  loginInvalidCredentials: 'Mali ang username o password',
  loginGenericError: 'Nabigo ang pag-login',
  loginRolesHint: 'Demo accounts ayon sa role: admin · operator · viewer',
  logout: 'Mag-Logout',
} as const satisfies Record<keyof typeof ko, string>;

export default tl;
