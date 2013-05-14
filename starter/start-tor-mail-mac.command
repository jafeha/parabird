#!/bin/bash
cd `dirname $0`
open $PWD/apps/mac/TorBrowser.app
sleep 5 

export GNUPGHOME=$PWD/data/gpg/
echo user_pref\(\"extensions.enigmail.agentPath\", \"$PWD/apps/mac/gpg/gpg\"\)\; > $PWD"/conf/user-mac.js"
cp $PWD"/conf/user-mac.js $PWD"/data/profile/user.js
open $PWD/apps/mac/Thunderbird.app --args -no-remote --profile $PWD/data/profile
