@echo off
rem adb shell push
rem adb shell push
if "%1" == "" call adb shell /data/local/tmp/ppinject 14427 /data/local/tmp/libppdvm.so HookJdwpProcessRequest
if not "%1" == "" call adb shell /data/local/tmp/ppinject "%1" /data/local/tmp/libppdvm.so HookJdwpProcessRequest 