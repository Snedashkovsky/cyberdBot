#!/usr/bin/expect -f
set timeout -1
spawn cyberdcli tx slashing unjail --from=$env(CYBERD_KEY_NAME) --chain-id bostrom-testnet-3
expect "* passphrase:"  {send -- "$env(CYBERD_PASS)\r"}
expect "* broadcasting *" {send -- "y\r"}
expect "* passphrase:"  {send -- "$env(CYBERD_PASS)\r"}

expect eof