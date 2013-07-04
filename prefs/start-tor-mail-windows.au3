; this is the autoit script for building an exe to start the tor mailer

; messy thing to do: delete the old config and create a new one
FileDelete(@WorkingDir & "conf\user-win.js")
$newfile = @WorkingDir & "conf\user-win.js"

; Check if i can read $newfile
If $newfile = -1 Then
    MsgBox(0, "Error", "Unable to open file.")
    Exit
 EndIf
 
 FileOpen( "$newfile", 1 )

; set path to gpg binary and write it to a file
$gpgbin = @WorkingDir & "apps\linux\gpg4usb\bin\gpg.exe"
FileWrite( $newfile, 'user_pref("extensions.enigmail.agentPath", ' & '"' & $gpgbin & '"' &');')
FileClose( "$newfile" )

; define where to copy the file and copy it
$userjs = @WorkingDir & "data\profile\user.js"
FileCopy( $newfile, $userjs, 1)

; set env vars for GNUPGHOME
$gpgdir = @WorkingDir & "data\gpg\"
EnvSet ( "GNUPGHOME", $gpgdir )

; start the applications
Run ( "apps/win/Tor Browser/Start Tor Browser.exe", "apps/win/Tor Browser/" )
$runcommand = "apps/win/thunderbird/core/thunderbird.exe -no-remote --profile " & @WorkingDir & "data\profile\"
Run ( $runcommand, "apps\win\thunderbird\core\")
