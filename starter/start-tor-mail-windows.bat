@echo off

set GNUPGHOME="%CD%\data\gpg\"
COPY "%CD%\conf\user-win.js" "%CD%\profile\user.js"
start /D "%CD%\apps\win\Tor Browser" /NORMAL call "Start Tor Browser.exe"
"%CD%\apps\win\thunderbird\core\thunderbird.exe" -profile \data\profile\
