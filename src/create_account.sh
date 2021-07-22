#!/usr/bin/expect -f
set account [lindex $argv 0]
set timeout -1
spawn cd ..
spawn export  $(head -2 .env | grep -v '^#' | xargs)
spawn docker exec -ti bostrom-testnet-3 cyber keys add $account
expect "* passphrase:"  {send -- "$env(CYBER_PASS)\r"}
expect {
  "*override the existing name *" {send -- "n\r"}
  "*" {send -- ""}
  }

expect eof