#!/usr/bin/expect -f
set to_account_address [lindex $argv 0]
set value [lindex $argv 1]
set timeout -1
spawn cyberdcli tx send $env(CYBERD_KEY_NAME) $to_account_address $value --chain-id euler-6
expect "* passphrase:"  {send -- "$env(CYBERD_PASS)\r"}
expect "* broadcasting *" {send -- "y\r"}
expect "* passphrase:"  {send -- "$env(CYBERD_PASS)\r"}

expect eof