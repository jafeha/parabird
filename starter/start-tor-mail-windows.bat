@echo off

set GNUPGHOME=%CD%\data\gpg\
echo user_pref("extensions.enigmail.agentPath", "%CD%apps\linux\gpg4usb\bin\gpg.exe"); > %CD%conf\user-win.js
copy /y %CD%conf\user-win.js %CD%data\profile\user.js
start /D "%CD%\apps\win\Tor Browser" /NORMAL call "Start Tor Browser.exe"
"%CD%apps\win\thunderbird\core\thunderbird.exe" -profile %CD%data\profile\
