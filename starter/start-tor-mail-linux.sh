#!/bin/bash
"$PWD/apps/linux/tor-browser_de/start-tor-browser" &
sleep 5

export GNUPGHOME=$PWD/data/gpg/
sed '/agentPath/d' -i $PWD"/data/profile/user.js"
echo user_pref\(\"extensions.enigmail.agentPath\", \"$PWD/apps/linux/gpg4usb/bin/gpg\"\)\; >> $PWD"/data/profile/user.js"
"$PWD/apps/linux/thunderbird/thunderbird" --no-remote -profile "$PWD/data/profile/"
