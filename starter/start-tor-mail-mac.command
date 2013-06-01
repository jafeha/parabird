#!/bin/bash

cd `dirname $0`

open $PWD/apps/mac/Thunderbird/TorBrowser.app

sleep 5 

export DYLD_LIBRARY_PATH=$PWD/apps/mac/gpg4mac/MacGPG2/lib/

export GNUPGHOME=$PWD/data/gpg/

sed '/agentPath/d' -i $PWD"/data/profile/user.js"

echo user_pref\(\"extensions.enigmail.agentPath\", \"$PWD/apps/mac/gpg4mac/MacGPG2/bin/gpg2\"\)\; >> $PWD"/data/profile/user.js"

open $PWD/apps/mac/Thunderbird.app --args -no-remote --profile $PWD/data/profile
