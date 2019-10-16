:: Date Created: 2019-07-11
:: Date last modified: 2019-07-29
:: author: Jared Spaulding - WEST, Inc.
:: Sets R_HOME and R_LIBS_USER environment variables according to lastest installed R version

@ECHO off
ECHO Please wait...

:: Set R Home environment variable
FOR /f %%i in ('DIR "C:\Program Files\R\" /b/a:d/od/t:c') do SET VERSION=%%i
SET a=C:\Program Files\R\%VERSION%\bin\x64
SETX R_HOME "%a%"

:: Get R library directory from user
setlocal
set "psCommand="(new-object -COM 'Shell.Application')^
.BrowseForFolder(0,'Choose writable R library.',0,0).self.path""
for /f "usebackq delims=" %%I in (`powershell %psCommand%`) do set "r_libs_user_dir=%%I"
setlocal enabledelayedexpansion

:: Set R_LIBS_USER environment variable
SETX R_LIBS_USER "%r_libs_user_dir%"
endlocal

