from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


TEXTS = {
    "ar": {
        "title": "تطبيق المساعد الذكي (Blind App)",
        "ready": "جاهز. اضغط على أي زر للقراءة أو التنبيه.",
        "time_btn": "الوقت والحالة",
        "alert_btn": "تنبيه سريع",
        "lang_btn": "اللغة: العربية",
        "status_msg": "الساعة الآن {time}. النظام يعمل بنجاح.",
        "alert_msg": "تم تفعيل التنبيه السريع.",
        "lang_changed": "تم التبديل إلى اللغة العربية.",
    },
    "ku": {
        "title": "Alîkarê Jîr (Blind App)",
        "ready": "Amade ye. Ji bo xwendin an hişyariyê bişkojkeyekê bitikîne.",
        "time_btn": "Dem û Rewş",
        "alert_btn": "Hişyariya Lezgîn",
        "lang_btn": "Ziman: Kurmancî",
        "status_msg": "Dem niha {time} e. Sîstem bi rêkûpêk dixebite.",
        "alert_msg": "Hişyariya lezgîn hate çalakkirin.",
        "lang_changed": "Ziman hate guhertin bo Kurmancî.",
    },
    "en": {
        "title": "Blind App Assistant",
        "ready": "Ready. Tap any button for spoken feedback or alert.",
        "time_btn": "Time & Status",
        "alert_btn": "Quick Alert",
        "lang_btn": "Language: English",
        "status_msg": "Current time is {time}. System is running normally.",
        "alert_msg": "Quick alert triggered.",
        "lang_changed": "Switched to English.",
    },
}


class DeviceAccessibility:
    def __init__(self):
        self._tts = None
        self._vibrator = None
        self._setup_android()

    def _setup_android(self):
        if platform != "android":
            return
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")

            activity = PythonActivity.mActivity
            self._tts = TextToSpeech(activity, None)
            self._vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
        except Exception:
            self._tts = None
            self._vibrator = None

    def set_lang(self, lang_code):
        if platform != "android" or not self._tts:
            return
        try:
            from jnius import autoclass

            Locale = autoclass("java.util.Locale")
            if lang_code == "ar":
                self._tts.setLanguage(Locale("ar"))
            elif lang_code == "ku":
                self._tts.setLanguage(Locale("ku"))
            else:
                self._tts.setLanguage(Locale.US)
        except Exception:
            pass

    def speak(self, text):
        if platform == "android" and self._tts:
            try:
                from jnius import autoclass

                TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
                self._tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, "blind_app_msg")
                return
            except Exception:
                pass
        print(f"[TTS]: {text}")

    def vibrate(self, duration_ms=120):
        if platform == "android" and self._vibrator:
            try:
                if self._vibrator.hasVibrator():
                    self._vibrator.vibrate(duration_ms)
                return
            except Exception:
                pass
        print(f"[VIBRATE]: {duration_ms}ms")


class BlindRootScreen(BoxLayout):
    def __init__(self, device, **kwargs):
        super().__init__(orientation="vertical", padding=18, spacing=14, **kwargs)
        self.device = device
        self.languages = ["ar", "ku", "en"]
        self.current_idx = 0

        self.lbl_title = Label(
            font_size="24sp",
            bold=True,
            size_hint=(1, 0.18),
            halign="center",
            valign="middle",
        )
        self.lbl_title.bind(size=self.lbl_title.setter("text_size"))

        self.lbl_status = Label(
            font_size="21sp",
            size_hint=(1, 0.28),
            halign="center",
            valign="middle",
        )
        self.lbl_status.bind(size=self.lbl_status.setter("text_size"))

        self.btn_time = Button(
            font_size="22sp",
            size_hint=(1, 0.18),
            background_color=(0.15, 0.45, 0.75, 1),
        )
        self.btn_time.bind(on_press=self.handle_time)

        self.btn_alert = Button(
            font_size="22sp",
            size_hint=(1, 0.18),
            background_color=(0.75, 0.25, 0.2, 1),
        )
        self.btn_alert.bind(on_press=self.handle_alert)

        self.btn_lang = Button(
            font_size="20sp",
            size_hint=(1, 0.18),
            background_color=(0.2, 0.55, 0.35, 1),
        )
        self.btn_lang.bind(on_press=self.handle_language)

        self.add_widget(self.lbl_title)
        self.add_widget(self.lbl_status)
        self.add_widget(self.btn_time)
        self.add_widget(self.btn_alert)
        self.add_widget(self.btn_lang)

        self.apply_language(announce=False)
        Clock.schedule_once(lambda dt: self.device.speak(self.strings()["ready"]), 0.8)

    @property
    def lang_code(self):
        return self.languages[self.current_idx]

    def strings(self):
        return TEXTS[self.lang_code]

    def apply_language(self, announce=True):
        s = self.strings()
        self.lbl_title.text = s["title"]
        self.lbl_status.text = s["ready"]
        self.btn_time.text = s["time_btn"]
        self.btn_alert.text = s["alert_btn"]
        self.btn_lang.text = s["lang_btn"]
        self.device.set_lang(self.lang_code)
        if announce:
            self.device.speak(s["lang_changed"])

    def handle_time(self, instance):
        self.device.vibrate(100)
        now = datetime.now().strftime("%H:%M")
        msg = self.strings()["status_msg"].format(time=now)
        self.lbl_status.text = msg
        self.device.speak(msg)

    def handle_alert(self, instance):
        self.device.vibrate(250)
        msg = self.strings()["alert_msg"]
        self.lbl_status.text = msg
        self.device.speak(msg)

    def handle_language(self, instance):
        self.device.vibrate(80)
        self.current_idx = (self.current_idx + 1) % len(self.languages)
        self.apply_language(announce=True)


class BlindApp(App):
    def build(self):
        Window.clearcolor = (0.06, 0.06, 0.08, 1)
        self.device = DeviceAccessibility()
        return BlindRootScreen(self.device)

    def on_stop(self):
        if hasattr(self, "device") and self.device._tts:
            try:
                self.device._tts.stop()
                self.device._tts.shutdown()
            except Exception:
                pass


if __name__ == "__main__":
    BlindApp().run()
