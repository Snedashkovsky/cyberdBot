#!/usr/bin/expect -f
set timeout -1
spawn docker exec -ti bostrom-testnet-3 cyber tx slashing unjail --from=$env(CYBER_KEY_NAME) --chain-id bostrom-testnet-3
expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}
expect "* broadcasting *" {send -- "y\r"}

expect eof