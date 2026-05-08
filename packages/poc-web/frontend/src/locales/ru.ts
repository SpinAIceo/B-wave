import ko from "./ko";

const ru = {
  // NavBar
  nav_ai_sandbox: "ИИ Песочница",
  nav_psc_risk: "Риск PSC",
  nav_roi_calculator: "Калькулятор ROI",
  nav_fleet_demo: "Демо флота",
  nav_brand_subtitle: "PSC Сканер",
  nav_try_free: "Попробовать бесплатно",

  // Home — hero
  home_badge: "Живая виртуальная PoC — без оборудования",
  home_hero_title1: "Обнаружение дефектов PSC судов",
  home_hero_title2: "за менее чем 500мс",
  home_hero_desc:
    "B-Wave разворачивается на edge-сервере судна. Экипаж направляет камеру планшета на оборудование — коррозия, повреждения, утечки помечаются с кодами нарушений PSC до прибытия инспектора.",
  home_cta_primary: "Загрузить фото судна →",
  home_cta_secondary: "Посмотреть риски",

  // Home — features
  feat_sandbox_title: "ИИ Сканер дефектов",
  feat_sandbox_desc:
    "Загрузите фото судна. Получите мгновенные коды нарушений PSC, наложение ограничивающих рамок и градацию серьёзности — на базе YOLO26s, обученной на 11000+ морских изображениях.",
  feat_sandbox_cta: "Попробовать песочницу →",
  feat_risk_title: "Симулятор риска PSC порта",
  feat_risk_desc:
    "Выберите порт назначения и обнаруженные дефекты. Реальная статистика MOU из Токио, Парижа, USCG и 20+ региональных властей прогнозирует вероятность задержания.",
  feat_risk_cta: "Симулировать риск →",
  feat_roi_title: "Калькулятор стоимости задержания",
  feat_roi_desc:
    "Преобразуйте дефекты в финансовые риски. Сравните дни задержания, штрафы за задержку груза и репутационные потери с инвестициями в систему B-Wave.",
  feat_roi_cta: "Рассчитать ROI →",
  feat_fleet_title: "Демо панели флота",
  feat_fleet_desc:
    "Просмотр в реальном времени 50 судов на мировых судоходных линиях. Зелёный/жёлтый/красный статусы риска PSC обновляются в реальном времени.",
  feat_fleet_cta: "Посмотреть флот →",

  // Home — stats
  stat_latency_label: "p95 задержка вывода",
  stat_map_label: "mAP50-95 (3 класса)",
  stat_images_label: "обучающих изображений",
  stat_sla_label: "сквозной SLA",

  // Home — CTA card
  home_demo_title: "Хотите полное демо?",
  home_demo_desc:
    "Посмотрите, как B-Wave работает на реальном edge-оборудовании. Мы привезём оборудование — вы предоставите судно.",
  home_demo_cta: "Запросить демо оборудования",

  // Sandbox page
  sandbox_title: "ИИ Сканер дефектов",
  sandbox_desc: "Загрузите фото судового оборудования — корпус, трубопроводы, палубные конструкции — и получите мгновенный анализ дефектов PSC.",
  sandbox_vessel_label: "Судно",
  sandbox_sync_hint: "Результаты синхронизируются с панелью флота",
  sandbox_dropzone_title: "Перетащите фото судна сюда",
  sandbox_dropzone_hint: "JPG, PNG, WebP · макс 20МБ",
  sandbox_run_btn: "Запустить анализ PSC",
  sandbox_analyzing: "Анализ...",
  sandbox_reset: "Сброс",
  sandbox_demo_mode: "Демо режим",
  sandbox_result_header: "Анализ завершён",
  sandbox_no_defects: "Нет дефектов",
  sandbox_defects_found_single: "Найдено {n} дефект",
  sandbox_defects_found_plural: "Найдено {n} дефектов",
  sandbox_compliant: "✓ Соответствует PSC",
  sandbox_compliant_desc: "Дефекты не обнаружены. Судно соответствует требованиям в этой области проверки.",
  sandbox_link_risk: "Симулировать риск порта →",
  sandbox_upload_hint: "Загрузите изображение и запустите анализ для просмотра результатов дефектов PSC",

  // Risk page
  risk_title: "Симулятор риска PSC",
  risk_desc: "Прогноз вероятности задержания на основе порта назначения и обнаруженных дефектов, используя исторические данные MOU.",
  risk_label_port: "Порт назначения",
  risk_label_defects: "Обнаруженные дефекты",
  risk_label_age: "Возраст судна",
  risk_defect_rust: "Коррозия",
  risk_defect_damage: "Повреждение",
  risk_defect_leak: "Утечка",
  risk_age_years: "{n} лет",
  risk_calc_btn: "Рассчитать риск",
  risk_calculating: "Расчёт...",
  risk_placeholder: "Установите параметры и нажмите Рассчитать риск",
  risk_detention_prob: "Вероятность задержания",
  risk_breakdown_title: "Разбивка риска",
  risk_base_rate: "Базовая ставка порта",
  risk_avg_duration: "Средняя продолжительность задержания",
  risk_link_roi: "Рассчитать финансовое воздействие →",

  // ROI page
  roi_title: "Калькулятор стоимости задержания",
  roi_desc: "Преобразуйте дефекты в финансовые риски и посмотрите ROI от предотвращения одного задержания.",
  roi_label_defects: "Текущие дефекты",
  roi_label_port: "Порт захода",
  roi_label_vessel_type: "Тип судна",
  roi_label_dwt: "DWT судна",
  roi_vessel_bulk: "Балкер",
  roi_vessel_container: "Контейнеровоз",
  roi_vessel_tanker: "Танкер",
  roi_vessel_roro: "Ro-Ro",
  roi_vessel_gas: "Газовоз",
  roi_vessel_passenger: "Пассажирское",
  roi_vessel_general: "Универсальное",
  roi_calc_btn: "Рассчитать стоимость рисков",
  roi_calculating: "Расчёт...",
  roi_placeholder: "Выберите дефекты и параметры судна для просмотра рисков",
  roi_total_exposure: "Общий финансовый риск (за рейс)",
  roi_detention_days: "{n} дней ожидаемого задержания",
  roi_breakdown_title: "Разбивка стоимости",
  roi_cost_detention: "Стоимость задержания судна",
  roi_cost_cargo: "Стоимость задержки груза",
  roi_cost_repute: "Репутационные/админ. расходы",
  roi_section_title: "ROI B-Wave",
  roi_ratio_label: "Коэффициент ROI",
  roi_payback_label: "Срок окупаемости",
  roi_annual_label: "Годовая стоимость",
  roi_payback_text: "Предотвращение одного задержания покрывает {n} лет B-Wave",
  roi_link_quote: "Получить официальное предложение →",

  // Fleet page
  fleet_title: "Панель флота",
  fleet_desc: "Статус риска PSC в реальном времени для 50 судов на мировых судоходных линиях.",
  fleet_tile_total: "Всего флот",
  fleet_tile_compliant: "Соответствует",
  fleet_tile_monitor: "Мониторинг",
  fleet_tile_at_risk: "Под риском",
  fleet_filter_all: "Все",
  fleet_filter_risk: "Под риском",
  fleet_filter_monitor: "Мониторинг",
  fleet_filter_ok: "Соответствует",
  fleet_loading: "Загрузка данных флота...",
  fleet_detail_risk: "Риск PSC",
  fleet_detail_defects: "Дефекты",
  fleet_detail_inspection: "Последняя проверка",
  fleet_detail_next_port: "Следующий порт",
  fleet_no_defects: "Нет",
  fleet_btn_risk: "Симулировать риск",
  fleet_btn_cost: "Рассчитать стоимость",

  // Footer
  footer_copyright: "© 2026 Spinai — B-Wave Edge Vision AI · Сканер соответствия PSC",
  footer_model_meta: "Модель: YOLO26s-v1 · mAP50-95=0.323 · Задержка p95=9.3ms (RTX4090)",

  // Zones
  zone_bow: "Нос",
  zone_midship: "Мидель",
  zone_stern: "Корма",
  zone_deck: "Палуба",
  zone_hull: "Корпус",
  zone_engine_room: "Машинное отделение",
} as const satisfies Record<keyof typeof ko, string>;

export default ru;
