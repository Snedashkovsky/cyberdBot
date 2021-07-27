#!/usr/bin/expect -f
set account_address [lindex $argv 0]
set value [lindex $argv 1]
set target_token [lindex $argv 2]
set timeout -1
spawn cd ..
spawn export  $(head -2 .env | grep -v '^#' | xargs)
spawn docker exec -ti bostrom-testnet-3 cyber tx resources investmint $value $target_token 86400 --from $account_address --chain-id bostrom-testnet-3 --gas 160000 --gas-prices 0.01boot --yes
expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}
expect "* broadcasting *" {send -- "y\r"}

expect eof