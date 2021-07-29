#!/usr/bin/expect -f

set account [lindex $argv 0]
set timeout 3
spawn docker exec -ti bostrom-testnet-3 cyber keys add $account
expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}
expect {
  "*override the existing name *" {send -- "N\r"}
  "*" {send -- ""}
  }

expect eof