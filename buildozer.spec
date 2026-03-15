[app]
title = Student Starter Pack
package.name = studentstarterpack
package.domain = com.asiatech.student
source.dir = .
source.include_exts = py,png,jpg,kv,json
source.exclude_dirs = tests,bin,.buildozer
version = 1.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
