# main.py - تطبيق مساعد المكفوفين APK
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.clock import Clock
import cv2

try:
    from plyer import tts, vibrator
    HAS_PLYER = True
except:
    HAS_PLYER = False

class BlindAppLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 12
        self.add_widget(Label(text='مساعد المكفوفين الذكي', font_size='28sp', size_hint=(1, 0.12)))
        self.camera = Camera(resolution=(640, 480), play=True)
        self.camera.size_hint = (1, 0.52)
        self.add_widget(self.camera)
        self.status = Label(text='اضغط تشغيل للبدء', font_size='22sp', size_hint=(1, 0.16), color=(0, 1, 0, 1))
        self.add_widget(self.status)
        self.btn_start = Button(text='تشغيل المساعد', font_size='24sp', size_hint=(1, 0.12), background_color=(0, 0.8, 0, 1))
        self.btn_start.bind(on_press=self.toggle)
        self.add_widget(self.btn_start)
        self.btn_detect = Button(text='كشف الآن', font_size='22sp', size_hint=(1, 0.12), background_color=(0, 0.5, 1, 1))
        self.btn_detect.bind(on_press=self.detect_now)
        self.add_widget(self.btn_detect)
        self.is_running = False
        self.event = None
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def speak(self, text):
        self.status.text = text
        if HAS_PLYER:
            try:
                tts.speak(text)
            except:
                pass
        if "انتبه" in text:
            try:
                vibrator.vibrate(time=0.8)
            except:
                pass

    def toggle(self, instance):
        if not self.is_running:
            self.is_running = True
            self.btn_start.text = 'ايقاف المساعد'
            self.btn_start.background_color = (1, 0, 0, 1)
            self.speak("تم تشغيل المساعد الذكي، امشي بأمان")
            self.event = Clock.schedule_interval(self.auto_detect, 2.0)
        else:
            self.is_running = False
            self.btn_start.text = 'تشغيل المساعد'
            self.btn_start.background_color = (0, 0.8, 0, 1)
            if self.event:
                self.event.cancel()
            self.speak("تم ايقاف المساعد")

    def auto_detect(self, dt):
        self.detect_now(None)

    def detect_now(self, instance):
        try:
            img_path = "/sdcard/blind_temp.png"
            self.camera.export_to_png(img_path)
        except:
            img_path = "blind_temp.png"
            try:
                self.camera.export_to_png(img_path)
            except:
                self.speak("لا استطيع التقاط صورة")
                return
        img = cv2.imread(img_path)
        if img is None:
            self.speak("حاول مرة اخرى")
            return
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        boxes, _ = self.hog.detectMultiScale(img, winStride=(8, 8))
        person_count = len(boxes)
        person_close = False
        for (x, y, ww, hh) in boxes:
            if ww * hh > (w * h * 0.15):
                person_close = True
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        center = gray[int(h*0.3):int(h*0.9), int(w*0.3):int(w*0.7)]
        edges = cv2.Canny(center, 50, 150)
        edge_density = (edges > 0).mean()
        if person_close:
            self.status.color = (1, 0, 0, 1)
            self.speak("انتبه، شخص قريب جدا امامك")
        elif person_count > 0:
            self.status.color = (1, 1, 0, 1)
            self.speak(f"يوجد {person_count} شخص امامك")
        elif len(faces) > 0:
            self.speak("يوجد شخص ينظر اليك امامك")
        elif edge_density > 0.18:
            self.status.color = (1, 0, 0, 1)
            self.speak("انتبه، عائق كبير امامك، توقف")
        elif edge_density > 0.10:
            self.speak("يوجد شيء امامك، امشي بحذر")
        else:
            self.status.color = (0, 1, 0, 1)
            self.speak("الطريق آمن، اكمل المشي")

class BlindAssistantApp(App):
    def build(self):
        return BlindAppLayout()
    def on_pause(self):
        return True

if __name__ == '__main__':
    BlindAssistantApp().run()
