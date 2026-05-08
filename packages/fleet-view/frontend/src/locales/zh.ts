import ko from './ko';

const zh = {
  // App / Navigation
  appSubtitle: '船队视图仪表板',
  navDashboard: '仪表板',
  navFleetMap: '船队地图',
  navVessels: '船舶',
  navReports: '报告',

  // Dashboard — stat cards
  totalVessels: '船舶总数',
  activeInspections: '进行中的检验',
  criticalDefects: '严重缺陷',
  detentionRisk: '滞留风险',
  trendThisMonth: '本月 +2',
  trendOngoing: '进行中',
  trendVsLastWeek: '较上周 -3',
  trendScoreOf100: '分数 / 100',

  // Dashboard — chart titles
  defectDistribution: '缺陷分布',
  fleetStatus: '船队状态',
  recentInspections: '最近检验',

  // Dashboard — table headers
  vessel: '船舶',
  port: '港口',
  date: '日期',
  result: '结果',
  critical: '严重',

  // Result badges
  pass: '合格',
  fail: '不合格',

  // Loading
  loading: '加载中...',

  // Fleet Map — tooltip labels
  status: '状态',
  lastInspection: '最近检验',
  criticalDefectsLabel: '严重缺陷',

  // Fleet Map — legend
  legendNoIssues: '无异常',
  legendWarnings: '警告',
  legendCritical: '严重',

  // Vessel List — search
  searchPlaceholder: '搜索船舶...',
  vesselCount: '{n} 艘',

  // Vessel List — table headers
  colName: '船名',
  colType: '类型',
  colFlag: '船旗',
  colStatus: '状态',
  colLastInspection: '最近检验',
  colCritical: '严重',
  colDetentionRisk: '滞留风险',

  // Vessel statuses
  statusSailing: '航行中',
  statusPort: '在港',
  statusAnchor: '锚泊',
  statusMaintenance: '维护中',

  // Defect types
  defectRust: '锈蚀',
  defectDamage: '损伤',
  defectLeak: '泄漏',
  defectMissingLabel: '标签缺失',
  defectCargoLashing: '货物绑扎',

  // Vessel Detail
  backToFleet: '← 返回船队',
  flagLabel: '船旗',
  detentionRiskLabel: '滞留风险',
  inspectionHistory: '检验历史',
  noInspectionsRecorded: '无检验记录',
  passLabel: '合格',
  failLabel: '不合格',
  criticalLabel: '严重',
  mouSuffix: 'MoU',
  quickActions: '快捷操作',
  generatePscReport: '📋 生成 PSC 准备报告',
  viewLastInspection: '🔍 查看最近检验',
  scheduleInspection: '📅 预约检验',
  vesselInfo: '船舶信息',
  infoPosition: '位置',
  infoLastInspection: '最近检验',
  infoCriticalDefects: '严重缺陷',
  infoDetentionRisk: '滞留风险',
  reportGenerated: '报告已生成',
  openingLastInspection: '正在打开最近检验...',
  schedulingInspection: '正在预约检验...',

  // Log Viewer
  navLogs: '错误日志',
  logsTitle: '错误日志审查',
  logsDesc: '按 X-Request-ID 筛选后端 WARNING/ERROR 日志。',
  logsFilterLevel: '级别筛选',
  logsFilterReqId: '搜索 Request-ID',
  logsFilterAll: '全部 (WARNING+ERROR)',
  logsBtnRefresh: '刷新',
  logsBtnClear: '全部清除',
  logsColTs: '时间戳',
  logsColLevel: '级别',
  logsColReqId: 'Request-ID',
  logsColModule: '模块',
  logsColMessage: '消息',
  logsEmpty: '没有符合筛选条件的错误日志。',
  logsLoading: '正在加载日志...',
  logsClearConfirm: '确定要清除全部错误日志吗?',

  // Reports
  generateReport: '生成报告',
  vesselLabel: '船舶',
  reportTypeLabel: '报告类型',
  selectVessel: '选择船舶...',
  generateBtn: '生成',
  selectVesselAlert: '请选择船舶',
  generatedReports: '已生成的报告',
  colReportId: '报告 ID',
  colVessel: '船舶',
  rptColType: '类型',
  colGenerated: '生成时间',
  rptColStatus: '状态',
  colAction: '操作',
  downloadPdf: '下载 PDF',
  statusReady: '已完成',
  statusGenerating: '生成中',
  downloading: '正在下载 {id}...',

  // Report types
  reportPscReadiness: 'PSC 准备状态报告',
  reportClassSurvey: '船级检验报告',
  reportSecurityAudit: '安全审计 (UR E26/E27)',
  reportCicCompliance: 'CIC 2026 合规 (货物绑扎)',

  // Zones
  zone_bow: '船首',
  zone_midship: '中部',
  zone_stern: '船尾',
  zone_deck: '甲板',
  zone_hull: '船体',
  zone_engine_room: '机舱',

  // Vessel diagram
  defectMap: '缺陷位置图',
  clickZoneToFilter: '点击区域以筛选缺陷',
  clearFilter: '显示全部',
  defectsInZone: '{zone} 的缺陷',
  noDefectsInZone: '此区域无缺陷',

  // Auth
  loginUsername: '用户名',
  loginPassword: '密码',
  loginSubmit: '登录',
  loginSubmitting: '登录中...',
  loginRequired: '请输入用户名和密码',
  loginInvalidCredentials: '用户名或密码无效',
  loginGenericError: '登录失败',
  loginRolesHint: '按角色的演示账户: admin · operator · viewer',
  logout: '退出登录',
} as const satisfies Record<keyof typeof ko, string>;

export default zh;
