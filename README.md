# pingbot
## An IRC utility bot

PingBot is a simple IRC utility bot written in Python3.4!

Usage: `python3.4 pingbot.py <config_file>`
To learn how to make a config file see def.conf

### Commands
Pingbot has 2 groups of commands: User Commands and Admin Commands

User Commands can be used by everyone:

!ping : pings the bot

!hex \<decimal_number\> : converts a decimal to hex format

!uptime : uptime of the bot

!whatis \<prog_name\> : Unix whatis command

!pony : Will return plot or head

!dice : Will return a random number 1-6

!now : returns current time

!isprime \<num\> : says num is prime or not

Admin Commands can be used just by admins:

!quit : disconnects bot from IRC

!say \<channel|person\> \<msg\> : sends \<msg\> to \<channel|person\>

!part \<channel\> : parts \<channel\>

!join \<channel\> : joins \<channel\>

!add\_admin \<nick\> : adds \<nick\> to admins list

!remove\_admin \<nick\> : removes \<nick\> from admins list

!op \<nick\> : give OP to \<nick\>

!deop \<nick\> : takes OP from \<nick\>

!voice \<nick\> : give Voice to \<nick\>

!devoice \<nick\> : takes Voice from \<nick\>

!kick \<nick\> : Kicks \<nick\>


# Raw Pingbot
raw\_ping.py is a version of Pingbot without any command except !ping and !help

You may use it to make your own pingbot. if you did please send me a version of it! Thanks!
