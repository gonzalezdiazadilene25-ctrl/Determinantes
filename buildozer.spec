[app]
title = Determinantes
package.name = determinantes
package.domain = org.matematicas
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = .github,bin,.buildozer
version = 1.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.ndk = 25b
# Version estable de python-for-android (Python 3.11 + Kivy 2.3.0)
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
