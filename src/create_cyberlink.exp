#!/usr/bin/expect -f

set account  [lindex $argv 0]
set from [lindex $argv 1]
set to [lindex $argv 2]
set timeout -1
spawn docker exec -ti bostrom-testnet-3 cyber tx graph cyberlink $from $to --from=$account --chain-id=bostrom-testnet-3 --yes
expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}

expect eof