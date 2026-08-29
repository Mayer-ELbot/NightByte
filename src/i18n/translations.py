"""
NightByte AI - Localization & Internationalization (i18n)
Complete bilingual support (العربية & English) with dynamic switching.
"""

TRANSLATIONS = {
    "ar": {
        # App Title & Navigation
        "app_name": "NightByte AI",
        "app_tagline": "المساعد الذكي لإيقاف التشغيل وإدارة التحميلات",
        "tab_dashboard": "الرئيسية",
        "tab_downloads": "التحميلات",
        "tab_logs": "السجل والشرح",
        "tab_settings": "الإعدادات",
        
        # Main Dashboard Cards & Status
        "status_idle": "جاهز - اضغط على الزر للبدء",
        "status_monitoring": "المراقبة الذكية نشطة...",
        "status_downloading": "جاري التحميل بسرعة عالية",
        "status_patching": "تثبيت وتحديث ملفات اللعبة على القرص",
        "status_below_threshold": "التحميل منخفض / متوقف (المؤقت يعمل)",
        "status_countdown": "⚠️ سيبدأ إيقاف التشغيل قريباً!",
        "status_paused_network": "⚠️ متوقف مؤقتاً لحماية التحميل - انقطع الإنترنت",
        "status_paused_afk": "⏸️ متوقف مؤقتاً - تم اكتشاف استخدامك للجهاز",
        "status_action_executing": "جاري تنفيذ الإجراء الآن...",
        "status_completed": "تم الانتهاء بنجاح!",
        
        # Metrics
        "metric_download_speed": "سرعة التحميل",
        "metric_disk_write": "كتابة القرص",
        "metric_total_downloaded": "إجمالي المستلم",
        "metric_active_items": "العناصر النشطة",
        "metric_network_status": "حالة الإنترنت",
        "net_online": "متصل",
        "net_offline": "الإنترنت منقطع!",
        "net_reconnecting": "إعادة الاتصال...",
        "awake_active": "حماية وضع النوم نشطة",
        
        # Controls & Buttons
        "btn_enable": "بدء المراقبة الذكية",
        "btn_disable": "إيقاف المراقبة",
        "btn_settings": "الإعدادات",
        "btn_cancel_countdown": "إلغاء الإطفاء فوراً",
        "btn_snooze_5m": "+5 د",
        "btn_snooze_15m": "+15 د",
        "btn_snooze_30m": "+30 د",
        "btn_snooze_1h": "+1 س",
        "btn_test_action": "تجربة الإجراء",
        "btn_clear_logs": "مسح السجل",
        "btn_save": "حفظ الإعدادات",
        "btn_reset": "استعادة الافتراضيات",
        "btn_apply": "تطبيق",
        "btn_close": "إغلاق",
        
        # Update checker
        "update_available_banner": "✨ يتوفر تحديث جديد ({version})! اضغط هنا للتحميل",
        "update_btn_check": "فحص التحديثات من GitHub",
        "update_status_checking": "جاري فحص GitHub...",
        "update_status_latest": "أنت تستخدم أحدث إصدار ({version})",
        "update_status_found": "تم العثور على إصدار جديد: {version}",
        "update_status_error": "تعذر فحص التحديثات: {error}",
        
        # Actions List
        "action_shutdown": "إيقاف التشغيل (Shutdown)",
        "action_restart": "إعادة التشغيل (Restart)",
        "action_sleep": "وضع السكون (Sleep)",
        "action_hibernate": "وضع الإسبات (Hibernate)",
        "action_lock": "قفل الشاشة (Lock)",
        "action_logoff": "تسجيل الخروج (Log Off)",
        "action_close_launchers": "إغلاق ستيم والمنصات فقط",
        "action_monitors_off": "إطفاء الشاشات فقط",
        
        # Action selector label
        "label_select_action": "عند انتهاء التحميل:",
        "label_timer_countdown": "الوقت المتبقي:",
        
        # Countdown Window
        "countdown_title": "⚠️ اكتملت التحميلات!",
        "countdown_desc": "سيتم تنفيذ الإجراء بعد انتهاء العد التنازلي. يمكنك الإلغاء أو التأجيل الآن.",
        "countdown_remaining": "متبقي",
        "countdown_seconds": "ثانية",
        
        # Settings Groups
        "settings_group_general": "عام واللغة",
        "settings_group_guardian": "حارس الإنترنت",
        "settings_group_triggers": "السرعة والمؤقت",
        "settings_group_protection": "حماية المستخدم والأنشطة",
        "settings_group_platforms": "المنصات المراقبة",
        "settings_group_notifications": "التنبيهات والتحديثات",
        
        # Settings Fields
        "setting_lang": "لغة البرنامج:",
        "setting_autostart": "تشغيل تلقائي مع بدء ويندوز",
        "setting_min_tray": "تصغير لشريط المهام",
        "setting_close_tray": "إغلاق النافذة يرسلها لشريط المهام",
        
        "setting_guardian_enable": "تفعيل حماية انقطاع الإنترنت (تجميد الإطفاء إذا انقطع النت)",
        "setting_guardian_pause": "تجميد المؤقت فوراً عند انقطاع الاتصال",
        "setting_guardian_resume": "استئناف المراقبة تلقائياً بمجرد عودة الإنترنت",
        "setting_guardian_max_wait": "أقصى مهلة لانتظار عودة النت (ثانية، 0 = دائماً):",
        
        "setting_threshold_speed": "الحد الأدنى لسرعة التحميل (KB/s):",
        "setting_threshold_speed_hint": "إذا انخفضت السرعة عن هذا الحد، يعتبر التحميل منتهياً ويبدأ المؤقت.",
        "setting_inactivity_time": "مهلة الانتظار بعد انخفاض السرعة (بالثواني):",
        "setting_countdown_time": "مدة شاشة التحذير التنازلية (بالثواني):",
        
        "setting_anti_afk": "حماية المستخدم النشط (تأجيل الإطفاء لو كنت تستخدم الماوس أو الكيبورد)",
        "setting_afk_timeout": "مهلة اعتبار المستخدم خاملاً (بالثواني):",
        "setting_gaming_mode": "وضع الألعاب (عدم الإطفاء إذا كانت لعبة نشطة بملء الشاشة)",
        "setting_prevent_sleep": "منع ويندوز من النوم أثناء التحميل (Awake Lock)",
        
        "setting_mon_steam": "Steam (فحص ملفات التثبيت والتحميل)",
        "setting_mon_epic": "Epic Games Launcher",
        "setting_mon_ea": "EA App / Origin",
        "setting_mon_battlenet": "Battle.net",
        "setting_mon_xbox": "Xbox / Microsoft Store",
        "setting_mon_ubisoft": "Ubisoft Connect",
        "setting_mon_torrents": "برامج التورنت (qBittorrent, etc.)",
        "setting_mon_idm": "برامج التحميل والمتصفحات (IDM, Chrome, etc.)",
        "setting_mon_system_io": "المراقبة الشاملة لحركة الشبكة والقرص (Universal)",
        
        "setting_sound_enable": "تفعيل الأصوات والتنبيهات",
        "setting_sound_ticks": "دقات في الثواني الأخيرة للعد التنازلي",
        "setting_tray_notif": "إشعارات ويندوز المنبثقة",
        "setting_auto_check_updates": "فحص التحديثات تلقائياً من GitHub عند بدء التشغيل",
        "setting_webhook_url": "رابط Webhook (ديسكورد / تليجرام للإشعار عن بعد):",
        "btn_test_webhook": "إرسال إشعار تجريبي",
        
        # Tray Menu
        "tray_open": "فتح NightByte",
        "tray_status": "الحالة:",
        "tray_enable": "بدء المراقبة",
        "tray_disable": "إيقاف المراقبة",
        "tray_cancel_shutdown": "إلغاء الإطفاء",
        "tray_exit": "خروج",
        
        # Cards & Empty state
        "no_active_downloads": "لا توجد تنزيلات نشطة حالياً في المنصات المحددة",
        "waiting_for_steam": "بانتظار بدء تحميل جديد في ستيم أو المنصات...",
        "eta_unknown": "الوقت المتبقي: غير محدد",
        "eta_calculating": "الوقت المتبقي: جاري الحساب...",
        "eta_format": "الوقت المتبقي: {time}",
    },
    
    "en": {
        # App Title & Navigation
        "app_name": "NightByte AI",
        "app_tagline": "Smart Auto-Shutdown & Download Guardian",
        "tab_dashboard": "Dashboard",
        "tab_downloads": "Downloads",
        "tab_logs": "Live Log & Guide",
        "tab_settings": "Settings",
        
        # Main Dashboard Cards & Status
        "status_idle": "Ready - Click Start to begin monitoring",
        "status_monitoring": "Smart monitoring active...",
        "status_downloading": "Downloading at high speed",
        "status_patching": "Allocating / Patching files on disk",
        "status_below_threshold": "Download finished / low (Timer running)",
        "status_countdown": "⚠️ Shutdown countdown in progress!",
        "status_paused_network": "⚠️ Paused to protect download - Internet disconnected",
        "status_paused_afk": "⏸️ Paused - User activity detected",
        "status_action_executing": "Executing selected action...",
        "status_completed": "Completed successfully!",
        
        # Metrics
        "metric_download_speed": "Download Speed",
        "metric_disk_write": "Disk Write",
        "metric_total_downloaded": "Session Received",
        "metric_active_items": "Active Items",
        "metric_network_status": "Internet Status",
        "net_online": "Online",
        "net_offline": "Offline!",
        "net_reconnecting": "Reconnecting...",
        "awake_active": "Awake Lock Active",
        
        # Controls & Buttons
        "btn_enable": "Start Smart Monitor",
        "btn_disable": "Stop Monitor",
        "btn_settings": "Settings",
        "btn_cancel_countdown": "Cancel Shutdown Immediately",
        "btn_snooze_5m": "+5m",
        "btn_snooze_15m": "+15m",
        "btn_snooze_30m": "+30m",
        "btn_snooze_1h": "+1h",
        "btn_test_action": "Test Action",
        "btn_clear_logs": "Clear Log",
        "btn_save": "Save Settings",
        "btn_reset": "Reset Defaults",
        "btn_apply": "Apply",
        "btn_close": "Close",
        
        # Update checker
        "update_available_banner": "✨ New update available ({version})! Click here to download",
        "update_btn_check": "Check for Updates from GitHub",
        "update_status_checking": "Checking GitHub...",
        "update_status_latest": "You are on the latest version ({version})",
        "update_status_found": "New version found: {version}",
        "update_status_error": "Could not check updates: {error}",
        
        # Actions List
        "action_shutdown": "Shutdown PC",
        "action_restart": "Restart PC",
        "action_sleep": "Sleep PC",
        "action_hibernate": "Hibernate PC",
        "action_lock": "Lock Workstation",
        "action_logoff": "Log Off User",
        "action_close_launchers": "Close Steam & Launchers",
        "action_monitors_off": "Turn Off Displays",
        
        # Action selector label
        "label_select_action": "When downloads finish:",
        "label_timer_countdown": "Remaining time:",
        
        # Countdown Window
        "countdown_title": "⚠️ Downloads Completed!",
        "countdown_desc": "The selected action will execute when countdown reaches zero. You can cancel or snooze now.",
        "countdown_remaining": "Remaining",
        "countdown_seconds": "sec",
        
        # Settings Groups
        "settings_group_general": "General & Language",
        "settings_group_guardian": "Network Guardian",
        "settings_group_triggers": "Speed & Timers",
        "settings_group_protection": "User Activity & Safety",
        "settings_group_platforms": "Monitored Platforms",
        "settings_group_notifications": "Notifications & Updates",
        
        # Settings Fields
        "setting_lang": "Language:",
        "setting_autostart": "Start with Windows automatically",
        "setting_min_tray": "Minimize to System Tray",
        "setting_close_tray": "Closing window minimizes to tray",
        
        "setting_guardian_enable": "Enable Internet Guardian (Freeze timer on disconnect)",
        "setting_guardian_pause": "Freeze countdown immediately if internet disconnects",
        "setting_guardian_resume": "Automatically resume monitoring when back online",
        "setting_guardian_max_wait": "Max offline wait timeout (seconds, 0 = indefinite):",
        
        "setting_threshold_speed": "Minimum download threshold speed (KB/s):",
        "setting_threshold_speed_hint": "If speed drops below this value, inactivity timer begins.",
        "setting_inactivity_time": "Inactivity wait time before countdown (seconds):",
        "setting_countdown_time": "On-screen warning countdown duration (seconds):",
        
        "setting_anti_afk": "Anti-AFK Protection (Pause if user is using mouse/keyboard)",
        "setting_afk_timeout": "User idle threshold before allowing action (seconds):",
        "setting_gaming_mode": "Gaming Mode Protection (Don't shutdown if full-screen game is running)",
        "setting_prevent_sleep": "Prevent Windows sleep mode during active downloads",
        
        "setting_mon_steam": "Steam (Manifest, VDF & Downloading folders)",
        "setting_mon_epic": "Epic Games Launcher",
        "setting_mon_ea": "EA App / Origin",
        "setting_mon_battlenet": "Battle.net",
        "setting_mon_xbox": "Xbox / Microsoft Store App",
        "setting_mon_ubisoft": "Ubisoft Connect",
        "setting_mon_torrents": "Torrent Clients (qBittorrent, etc.)",
        "setting_mon_idm": "Download Managers & Browsers (IDM, Chrome, etc.)",
        "setting_mon_system_io": "Universal Network & Disk I/O Fallback Engine",
        
        "setting_sound_enable": "Enable audio sound alerts",
        "setting_sound_ticks": "Ticking sound during final countdown seconds",
        "setting_tray_notif": "Windows native toast notifications",
        "setting_auto_check_updates": "Check for updates from GitHub on startup",
        "setting_webhook_url": "Webhook URL (Discord / Telegram remote notifications):",
        "btn_test_webhook": "Send Test Webhook",
        
        # Tray Menu
        "tray_open": "Open NightByte",
        "tray_status": "Status:",
        "tray_enable": "Start Monitor",
        "tray_disable": "Stop Monitor",
        "tray_cancel_shutdown": "Cancel Shutdown",
        "tray_exit": "Exit",
        
        # Cards & Empty state
        "no_active_downloads": "No active downloads detected across monitored platforms",
        "waiting_for_steam": "Waiting for new downloads in Steam or other platforms...",
        "eta_unknown": "ETA: Unknown",
        "eta_calculating": "ETA: Calculating...",
        "eta_format": "ETA: {time}",
    }
}


def tr(key: str, lang: str = "ar", **kwargs) -> str:
    """Translate a key to the requested language with optional formatting."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["ar"])
    text = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
