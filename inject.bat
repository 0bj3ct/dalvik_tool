@echo off
rem adb.exe push libppdvm.so /data/local/tmp/
rem adb.exe push ppinject /data/local/tmp
@adb.exe shell < inject.txt
adb.exe shell