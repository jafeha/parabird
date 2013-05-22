#!/bin/bash
cd `dirname $0`
open $PWD/apps/mac/TorBrowser.app
sleep 5 

export GNUPGHOME=$PWD/data/gpg/
sed '/agentPath/d' -i $PWD"/data/profile/user.js"
echo user_pref\(\"extensions.enigmail.agentPath\", \"$PWD/apps/mac/gpg/gpg\"\)\; >> $PWD"/data/profile/user.js"
open $PWD/apps/mac/Thunderbird.app --args -no-remote --profile $PWD/data/profile
