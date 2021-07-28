#!/usr/bin/expect -f
set account_address [lindex $argv 0]
set validator [lindex $argv 1]
set value [lindex $argv 2]
set timeout -1
spawn docker exec -ti bostrom-testnet-3 cyber tx staking delegate $validator $value --from $account_address --chain-id bostrom-testnet-3 --gas 261000 --gas-prices 0.01boot --yes

expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}
expect "* broadcasting *" {send -- "y\r"}

expect eof