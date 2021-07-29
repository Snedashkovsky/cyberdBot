#!/usr/bin/expect -f
set account_address [lindex $argv 0]
set value [lindex $argv 1]
set investmint_token [lindex $argv 2]
set timeout -1
set investmint_period 604800
spawn docker exec -ti bostrom-testnet-3 cyber tx resources investmint $value investmint_token $investmint_period --from $account_address --chain-id bostrom-testnet-3 --gas 160000 --gas-prices 0.01boot --yes
expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}
expect "* broadcasting *" {send -- "y\r"}

expect eof