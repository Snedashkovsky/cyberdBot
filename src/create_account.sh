#!/usr/bin/expect -f
set account [lindex $argv 0]
set timeout -1
spawn cyberdcli keys add $account
expect "* passphrase:"  {send -- "$env(CYBERD_PASS)\r"}
expect {
  "*override the existing name *" {send -- "n\r"}
  "*" {send -- ""}
  }

expect eof