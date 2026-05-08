import ko from './ko';

const ru = {
  // App / Navigation
  appSubtitle: 'Панель управления флотом',
  navDashboard: 'Панель',
  navFleetMap: 'Карта флота',
  navVessels: 'Суда',
  navReports: 'Отчёты',

  // Dashboard — stat cards
  totalVessels: 'Всего судов',
  activeInspections: 'Активные проверки',
  criticalDefects: 'Критические дефекты',
  detentionRisk: 'Риск задержания',
  trendThisMonth: '+2 в этом месяце',
  trendOngoing: 'В процессе',
  trendVsLastWeek: '-3 к прошлой неделе',
  trendScoreOf100: 'балл / 100',

  // Dashboard — chart titles
  defectDistribution: 'Распределение дефектов',
  fleetStatus: 'Состояние флота',
  recentInspections: 'Недавние проверки',

  // Dashboard — table headers
  vessel: 'Судно',
  port: 'Порт',
  date: 'Дата',
  result: 'Результат',
  critical: 'Критич.',

  // Result badges
  pass: 'Пройдено',
  fail: 'Не пройдено',

  // Loading
  loading: 'Загрузка...',

  // Fleet Map — tooltip labels
  status: 'Статус',
  lastInspection: 'Последняя проверка',
  criticalDefectsLabel: 'Критические дефекты',

  // Fleet Map — legend
  legendNoIssues: 'Без замечаний',
  legendWarnings: 'Предупреждения',
  legendCritical: 'Критич.',

  // Vessel List — search
  searchPlaceholder: 'Поиск судна...',
  vesselCount: '{n} судов',

  // Vessel List — table headers
  colName: 'Название',
  colType: 'Тип',
  colFlag: 'Флаг',
  colStatus: 'Статус',
  colLastInspection: 'Последняя проверка',
  colCritical: 'Критич.',
  colDetentionRisk: 'Риск задержания',

  // Vessel statuses
  statusSailing: 'В пути',
  statusPort: 'В порту',
  statusAnchor: 'На якоре',
  statusMaintenance: 'На ремонте',

  // Defect types
  defectRust: 'Коррозия',
  defectDamage: 'Повреждение',
  defectLeak: 'Утечка',
  defectMissingLabel: 'Отсутствует маркировка',
  defectCargoLashing: 'Крепление груза',

  // Vessel Detail
  backToFleet: '← Назад к флоту',
  flagLabel: 'Флаг',
  detentionRiskLabel: 'Риск задержания',
  inspectionHistory: 'История проверок',
  noInspectionsRecorded: 'Проверки не зарегистрированы',
  passLabel: 'Пройдено',
  failLabel: 'Не пройдено',
  criticalLabel: 'Критич.',
  mouSuffix: 'MoU',
  quickActions: 'Быстрые действия',
  generatePscReport: '📋 Создать отчёт о готовности к PSC',
  viewLastInspection: '🔍 Посмотреть последнюю проверку',
  scheduleInspection: '📅 Запланировать проверку',
  vesselInfo: 'Информация о судне',
  infoPosition: 'Позиция',
  infoLastInspection: 'Последняя проверка',
  infoCriticalDefects: 'Критические дефекты',
  infoDetentionRisk: 'Риск задержания',
  reportGenerated: 'Отчёт создан',
  openingLastInspection: 'Открытие последней проверки...',
  schedulingInspection: 'Планирование проверки...',

  // Log Viewer
  navLogs: 'Журнал ошибок',
  logsTitle: 'Просмотр журнала ошибок',
  logsDesc: 'Просмотр серверных логов WARNING/ERROR по X-Request-ID.',
  logsFilterLevel: 'Фильтр уровня',
  logsFilterReqId: 'Поиск Request-ID',
  logsFilterAll: 'Все (WARNING+ERROR)',
  logsBtnRefresh: 'Обновить',
  logsBtnClear: 'Очистить всё',
  logsColTs: 'Время',
  logsColLevel: 'Уровень',
  logsColReqId: 'Request-ID',
  logsColModule: 'Модуль',
  logsColMessage: 'Сообщение',
  logsEmpty: 'Нет логов, соответствующих фильтру.',
  logsLoading: 'Загрузка логов...',
  logsClearConfirm: 'Удалить все логи ошибок?',

  // Reports
  generateReport: 'Создать отчёт',
  vesselLabel: 'Судно',
  reportTypeLabel: 'Тип отчёта',
  selectVessel: 'Выберите судно...',
  generateBtn: 'Создать',
  selectVesselAlert: 'Пожалуйста, выберите судно',
  generatedReports: 'Созданные отчёты',
  colReportId: 'ID отчёта',
  colVessel: 'Судно',
  rptColType: 'Тип',
  colGenerated: 'Создано',
  rptColStatus: 'Статус',
  colAction: 'Действие',
  downloadPdf: 'Скачать PDF',
  statusReady: 'Готово',
  statusGenerating: 'Создаётся',
  downloading: 'Загрузка {id}...',

  // Report types
  reportPscReadiness: 'Отчёт о готовности к PSC',
  reportClassSurvey: 'Отчёт о классификационном осмотре',
  reportSecurityAudit: 'Аудит безопасности (UR E26/E27)',
  reportCicCompliance: 'Соответствие CIC 2026 (крепление груза)',

  // Zones
  zone_bow: 'Нос',
  zone_midship: 'Мидель',
  zone_stern: 'Корма',
  zone_deck: 'Палуба',
  zone_hull: 'Корпус',
  zone_engine_room: 'Машинное отделение',

  // Vessel diagram
  defectMap: 'Карта дефектов',
  clickZoneToFilter: 'Нажмите на зону для фильтрации дефектов',
  clearFilter: 'Показать все',
  defectsInZone: 'Дефекты в зоне {zone}',
  noDefectsInZone: 'В этой зоне нет дефектов',

  // Auth
  loginUsername: 'Имя пользователя',
  loginPassword: 'Пароль',
  loginSubmit: 'Войти',
  loginSubmitting: 'Вход...',
  loginRequired: 'Введите имя пользователя и пароль',
  loginInvalidCredentials: 'Неверное имя пользователя или пароль',
  loginGenericError: 'Ошибка входа',
  loginRolesHint: 'Демо-аккаунты по ролям: admin · operator · viewer',
  loginDemoAccounts: 'Демо-аккаунты (нажмите для автозаполнения)',
  logout: 'Выйти',
} as const satisfies Record<keyof typeof ko, string>;

export default ru;
