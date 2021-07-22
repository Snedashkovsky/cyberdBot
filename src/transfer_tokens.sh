#!/usr/bin/expect -f
set to_account_address [lindex $argv 0]
set value [lindex $argv 1]
set timeout -1
spawn cd ..
spawn export  $(head -2 .env | grep -v '^#' | xargs)
spawn docker exec -ti bostrom-testnet-3 cyber tx send $env(CYBER_KEY_NAME) $to_account_address $value --chain-id bostrom-testnet-3
expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}
expect "* broadcasting *" {send -- "y\r"}
expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}

expect eof