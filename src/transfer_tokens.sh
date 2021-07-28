#!/usr/bin/expect -f
set to_account_address [lindex $argv 0]
set value [lindex $argv 1]
set timeout -1
spawn docker exec -ti bostrom-testnet-3 cyber tx bank send $env(CYBER_KEY_NAME) $to_account_address $value --chain-id bostrom-testnet-3
expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}
expect "* broadcasting *" {send -- "y\r"}

expect eof