import ko from './ko';

const en = {
  // App / Navigation
  appSubtitle: 'Fleet View Dashboard',
  navDashboard: 'Dashboard',
  navFleetMap: 'Fleet Map',
  navVessels: 'Vessels',
  navReports: 'Reports',

  // Dashboard — stat cards
  totalVessels: 'Total Vessels',
  activeInspections: 'Active Inspections',
  criticalDefects: 'Critical Defects',
  detentionRisk: 'Detention Risk',
  trendThisMonth: '+2 this month',
  trendOngoing: 'Ongoing',
  trendVsLastWeek: '-3 vs last week',
  trendScoreOf100: 'score / 100',

  // Dashboard — chart titles
  defectDistribution: 'Defect Distribution',
  fleetStatus: 'Fleet Status',
  recentInspections: 'Recent Inspections',

  // Dashboard — table headers
  vessel: 'Vessel',
  port: 'Port',
  date: 'Date',
  result: 'Result',
  critical: 'Critical',

  // Result badges
  pass: 'Pass',
  fail: 'Fail',

  // Loading
  loading: 'Loading...',

  // Fleet Map — tooltip labels
  status: 'Status',
  lastInspection: 'Last Inspection',
  criticalDefectsLabel: 'Critical Defects',

  // Fleet Map — legend
  legendNoIssues: 'No Issues',
  legendWarnings: 'Warnings',
  legendCritical: 'Critical',

  // Vessel List — search
  searchPlaceholder: 'Search vessels...',
  vesselCount: '{n} vessels',

  // Vessel List — table headers
  colName: 'Name',
  colType: 'Type',
  colFlag: 'Flag',
  colStatus: 'Status',
  colLastInspection: 'Last Inspection',
  colCritical: 'Critical',
  colDetentionRisk: 'Detention Risk',

  // Vessel statuses
  statusSailing: 'Sailing',
  statusPort: 'In Port',
  statusAnchor: 'At Anchor',
  statusMaintenance: 'Maintenance',

  // Defect types
  defectRust: 'Rust',
  defectDamage: 'Damage',
  defectLeak: 'Leak',
  defectMissingLabel: 'Missing Label',
  defectCargoLashing: 'Cargo Lashing',

  // Vessel Detail
  backToFleet: '← Back to Fleet',
  flagLabel: 'Flag',
  detentionRiskLabel: 'Detention Risk',
  inspectionHistory: 'Inspection History',
  noInspectionsRecorded: 'No inspections recorded',
  passLabel: 'Passed',
  failLabel: 'Failed',
  criticalLabel: 'Critical',
  mouSuffix: 'MoU',
  quickActions: 'Quick Actions',
  generatePscReport: '📋 Generate PSC Readiness Report',
  viewLastInspection: '🔍 View Last Inspection',
  scheduleInspection: '📅 Schedule Inspection',
  vesselInfo: 'Vessel Information',
  infoPosition: 'Position',
  infoLastInspection: 'Last Inspection',
  infoCriticalDefects: 'Critical Defects',
  infoDetentionRisk: 'Detention Risk',
  reportGenerated: 'Report generated',
  openingLastInspection: 'Opening last inspection...',
  schedulingInspection: 'Scheduling inspection...',

  // Log Viewer
  navLogs: 'Error Logs',
  logsTitle: 'Error Log Review',
  logsDesc: 'View backend WARNING/ERROR logs filtered by X-Request-ID.',
  logsFilterLevel: 'Level Filter',
  logsFilterReqId: 'Search Request-ID',
  logsFilterAll: 'All (WARNING+ERROR)',
  logsBtnRefresh: 'Refresh',
  logsBtnClear: 'Clear All',
  logsColTs: 'Timestamp',
  logsColLevel: 'Level',
  logsColReqId: 'Request-ID',
  logsColModule: 'Module',
  logsColMessage: 'Message',
  logsEmpty: 'No error logs match the filter.',
  logsLoading: 'Loading logs...',
  logsClearConfirm: 'Are you sure you want to clear all error logs?',

  // Reports
  generateReport: 'Generate Report',
  vesselLabel: 'Vessel',
  reportTypeLabel: 'Report Type',
  selectVessel: 'Select vessel...',
  generateBtn: 'Generate',
  selectVesselAlert: 'Please select a vessel',
  generatedReports: 'Generated Reports',
  colReportId: 'Report ID',
  colVessel: 'Vessel',
  rptColType: 'Type',
  colGenerated: 'Generated',
  rptColStatus: 'Status',
  colAction: 'Action',
  downloadPdf: 'Download PDF',
  statusReady: 'Ready',
  statusGenerating: 'Generating',
  downloading: 'Downloading {id}...',

  // Report types
  reportPscReadiness: 'PSC Readiness Report',
  reportClassSurvey: 'Class Survey Report',
  reportSecurityAudit: 'Security Audit (UR E26/E27)',
  reportCicCompliance: 'CIC 2026 Compliance (Cargo Lashing)',

  // Zones
  zone_bow: 'Bow',
  zone_midship: 'Midship',
  zone_stern: 'Stern',
  zone_deck: 'Deck',
  zone_hull: 'Hull',
  zone_engine_room: 'Engine Room',

  // Vessel diagram
  defectMap: 'Defect Map',
  clickZoneToFilter: 'Click a zone to filter defects',
  clearFilter: 'Show All',
  defectsInZone: 'Defects in {zone}',
  noDefectsInZone: 'No defects in this zone',

  // Auth
  loginUsername: 'Username',
  loginPassword: 'Password',
  loginSubmit: 'Sign In',
  loginSubmitting: 'Signing in...',
  loginRequired: 'Please enter both username and password',
  loginInvalidCredentials: 'Invalid username or password',
  loginGenericError: 'Login failed',
  loginRolesHint: 'Demo accounts by role: admin · operator · viewer',
  loginDemoAccounts: 'Demo accounts (click to auto-fill)',
  logout: 'Sign Out',
} as const satisfies Record<keyof typeof ko, string>;

export default en;
