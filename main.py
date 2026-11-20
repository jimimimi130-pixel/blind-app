from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

# محاولة استيراد أدوات أندرويد عند التشغيل على الهاتف
if platform == "android":
    try:
        from jnius import autoclass
        from android.permissions import request_permissions, Permission
    except Exception:
        autoclass = None
        request_permissions = None
        Permission = None
else:
    autoclass = None
    request_permissions = None
    Permission = None


TEXTS = {
    "en": {
        "title": "Blind App Assistant",
        "ready": "Ready. Camera walk mode available.",
        "time_btn": "Time & Status",
        "alert_btn": "Quick Alert",
        "cam_on_btn": "Camera Walk: ON",
        "cam_off_btn": "Camera Walk: OFF",
        "lang_btn": "Language: English",
        "spoken_time": "Current time is {time}. Camera walk is {cam_state}.",
        "cam_state_on": "active",
        "cam_state_off": "off",
        "alert_msg": "Quick alert activated.",
        "cam_started": "Camera walk mode started. Moving carefully.",
        "cam_stopped": "Camera walk mode stopped.",
        "cam_perm_needed": "Camera permission is required for walk mode.",
        "walk_scan_tip": "Scanning path ahead.",
    },
    "ar": {
        "title": "مساعد المكفوفين الذكي",
        "ready": "جاهز. وضع المشي بالكاميرا متاح.",
        "time_btn": "الوقت والحالة",
        "alert_btn": "تنبيه سريع",
        "cam_on_btn": "المشي بالكاميرا: يعمل",
        "cam_off_btn": "المشي بالكاميرا: متوقف",
        "lang_btn": "اللغة: العربية",
        "spoken_time": "الوقت الآن {time}. وضع المشي بالكاميرا {cam_state}.",
        "cam_state_on": "يعمل",
        "cam_state_off": "متوقف",
        "alert_msg": "تم تفعيل التنبيه السريع.",
        "cam_started": "تم تشغيل وضع المشي بالكاميرا. انتبه للطريق.",
        "cam_stopped": "تم إيقاف وضع المشي بالكاميرا.",
        "cam_perm_needed": "يلزم منح صلاحية الكاميرا لتشغيل وضع المشي.",
        "walk_scan_tip": "جاري فحص المسار أمامك.",
    },
    "ku": {
        "title": "Alîkarê Kor û Kêmdîtinê",
        "ready": "Amade ye. Moda meşê ya bi kamerayê heye.",
        "time_btn": "Dem û Rewş",
        "alert_btn": "Hişyariya Bilez",
        "cam_on_btn": "Meşa bi Kamerayê: Çalak e",
        "cam_off_btn": "Meşa bi Kamerayê: Rawestiyaye",
        "lang_btn": "Ziman: Kurmancî",
        "spoken_time": "Dem niha {time} e. Moda meşa kamerayê {cam_state} ye.",
        "cam_state_on": "çalak",
        "cam_state_off": "rawestiyaye",
        "alert_msg": "Hişyariya bilez hate çalakkirin.",
        "cam_started": "Moda meşa bi kamerayê dest pê kir. Li rê hişyar be.",
        "cam_stopped": "Moda meşa bi kamerayê hate rawestandin.",
        "cam_perm_needed": "Ji bo moda meşê destûra kamerayê pêwîst e.",
        "walk_scan_tip": "Riya li pêş tê kontrolkirin.",
    },
}

LANG_ORDER = ["en", "ar", "ku"]


class BlindAppRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=24, spacing=16, **kwargs)
        Window.clearcolor = (0.06, 0.07, 0.09, 1)

        self.lang_index = 0
        self.camera_walk_active = False
        self._scan_event = None
        self._tts = None
        self._init_android_tts()

        self.title_label = Label(
            text=self._t("title"),
            font_size="28sp",
            bold=True,
            size_hint_y=0.16,
            halign="center",
            valign="middle",
        )
        self.title_label.bind(size=self._update_label_text_size)

        self.status_label = Label(
            text=self._t("ready"),
            font_size="20sp",
            size_hint_y=0.20,
            halign="center",
            valign="middle",
        )
        self.status_label.bind(size=self._update_label_text_size)

        self.time_btn = Button(
            text=self._t("time_btn"),
            font_size="22sp",
            background_normal="",
            background_color=(0.11, 0.24, 0.42, 1),
        )
        self.time_btn.bind(on_press=self.on_time_press)

        self.cam_btn = Button(
            text=self._t("cam_off_btn"),
            font_size="22sp",
            background_normal="",
            background_color=(0.12, 0.36, 0.32, 1),
        )
        self.cam_btn.bind(on_press=self.on_camera_walk_toggle)

        self.alert_btn = Button(
            text=self._t("alert_btn"),
            font_size="22sp",
            background_normal="",
            background_color=(0.45, 0.12, 0.12, 1),
        )
        self.alert_btn.bind(on_press=self.on_alert_press)

        self.lang_btn = Button(
            text=self._t("lang_btn"),
            font_size="22sp",
            background_normal="",
            background_color=(0.13, 0.33, 0.18, 1),
        )
        self.lang_btn.bind(on_press=self.on_lang_press)

        self.add_widget(self.title_label)
        self.add_widget(self.status_label)
        self.add_widget(self.time_btn)
        self.add_widget(self.cam_btn)
        self.add_widget(self.alert_btn)
        self.add_widget(self.lang_btn)

        Clock.schedule_once(lambda dt: self.speak(self._t("ready")), 0.6)

    def _update_label_text_size(self, instance, value):
        instance.text_size = (instance.width - 20, None)

    @property
    def current_lang(self):
        return LANG_ORDER[self.lang_index]

    def _t(self, key):
        return TEXTS[self.current_lang][key]

    def _refresh_ui_texts(self):
        self.title_label.text = self._t("title")
        self.status_label.text = self._t("ready")
        self.time_btn.text = self._t("time_btn")
        self.alert_btn.text = self._t("alert_btn")
        self.lang_btn.text = self._t("lang_btn")
        self._refresh_cam_btn()

    def _refresh_cam_btn(self):
        if self.camera_walk_active:
            self.cam_btn.text = self._t("cam_on_btn")
            self.cam_btn.background_color = (0.16, 0.52, 0.24, 1)
        else:
            self.cam_btn.text = self._t("cam_off_btn")
            self.cam_btn.background_color = (0.12, 0.36, 0.32, 1)

    def _init_android_tts(self):
        if platform != "android" or autoclass is None:
            return
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
            activity = PythonActivity.mActivity
            self._tts = TextToSpeech(activity, None)
        except Exception:
            self._tts = None

    def speak(self, message):
        self.status_label.text = message
        if platform == "android" and self._tts is not None and autoclass is not None:
            try:
                TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
                self._tts.speak(message, TextToSpeech.QUEUE_FLUSH, None, None)
            except Exception:
                pass

    def vibrate(self, duration_ms=250):
        if platform != "android" or autoclass is None:
            return
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            activity = PythonActivity.mActivity
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
            if vibrator is not None and vibrator.hasVibrator():
                vibrator.vibrate(duration_ms)
        except Exception:
            pass

    def _has_camera_permission(self):
        if platform != "android" or autoclass is None or Permission is None:
            return True
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            ContextCompat = autoclass("androidx.core.content.ContextCompat")
            PackageManager = autoclass("android.content.pm.PackageManager")
            activity = PythonActivity.mActivity
            result = ContextCompat.checkSelfPermission(activity, Permission.CAMERA)
            return result == PackageManager.PERMISSION_GRANTED
        except Exception:
            return True

    def _request_camera_permission(self, on_granted):
        if platform != "android" or request_permissions is None or Permission is None:
            on_granted()
            return

        def callback(permissions, grants):
            if grants and all(grants):
                Clock.schedule_once(lambda dt: on_granted(), 0)
            else:
                Clock.schedule_once(
                    lambda dt: self.speak(self._t("cam_perm_needed")), 0
                )

        request_permissions([Permission.CAMERA], callback)

    def on_camera_walk_toggle(self, instance):
        if not self.camera_walk_active:
            if not self._has_camera_permission():
                self._request_camera_permission(self._enable_camera_walk)
            else:
                self._enable_camera_walk()
        else:
            self._disable_camera_walk()

    def _enable_camera_walk(self):
        self.camera_walk_active = True
        self._refresh_cam_btn()
        self.vibrate(200)
        self.speak(self._t("cam_started"))
        if self._scan_event is None:
            self._scan_event = Clock.schedule_interval(self._periodic_walk_check, 6.0)

    def _disable_camera_walk(self):
        self.camera_walk_active = False
        if self._scan_event is not None:
            self._scan_event.cancel()
            self._scan_event = None
        self._refresh_cam_btn()
        self.vibrate(150)
        self.speak(self._t("cam_stopped"))

    def _periodic_walk_check(self, dt):
        if self.camera_walk_active:
            self.vibrate(100)
            self.speak(self._t("walk_scan_tip"))

    def on_time_press(self, instance):
        now_str = datetime.now().strftime("%I:%M %p")
        cam_state = self._t("cam_state_on") if self.camera_walk_active else self._t("cam_state_off")
        msg = self._t("spoken_time").format(time=now_str, cam_state=cam_state)
        self.vibrate(150)
        self.speak(msg)

    def on_alert_press(self, instance):
        self.vibrate(500)
        self.speak(self._t("alert_msg"))

    def on_lang_press(self, instance):
        self.lang_index = (self.lang_index + 1) % len(LANG_ORDER)
        self._refresh_ui_texts()
        self.vibrate(120)
        self.speak(self._t("ready"))


class BlindApp(App):
    def build(self):
        return BlindAppRoot()


if __name__ == "__main__":
    BlindApp().run()
