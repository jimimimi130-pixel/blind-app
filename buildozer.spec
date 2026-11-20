[app]

title = Blind Assistant
package.name = blindapp
package.domain = org.blind.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

version = 1.0

requirements = python3,kivy,pyjnius



orientation = portrait
fullscreen = 0

android.permissions = INTERNET,VIBRATE,CAMERA 

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]

log_level = 1
warn_on_root = 1
