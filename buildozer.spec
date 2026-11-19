[app]
title = Blind Assistant
package.name = blindapp
package.domain = org.blind.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,opencv,plyer
orientation = portrait
fullscreen = 0
android.permissions = CAMERA,RECORD_AUDIO
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
