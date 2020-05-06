#!/usr/bin/expect -f
set from [lindex $argv 0]
set to [lindex $argv 1]
set timeout -1
spawn cyberdcli link --from=$env(CYBERD_KEY_NAME) --cid-from=$from --cid-to=$to --chain-id=euler-6
expect "* passphrase:"  {send -- "$env(CYBERD_PASS)\r"}
expect "* broadcasting *" {send -- "y\r"}
expect "* passphrase:"  {send -- "$env(CYBERD_PASS)\r"}

expect eof