[app]
title = مساعد المكفوفين
package.name = blindapp
package.domain = org.blind.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,opencv,plyer,cmake
orientation = portrait
fullscreen = 0
android.permissions = CAMERA,RECORD_AUDIO,INTERNET,VIBRATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
p4a.branch = master
[buildozer]
log_level = 2
warn_on_root = 1
