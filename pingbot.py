import socket
import os
import sys
import random
import time
import configparser
import urllib.request
import bs4



COMMANDS = ('!ping', '!pony', '!dice', '!whatis', '!now', '!uptime'
    , '!hex', '!isprime', '!wwwtitle')
    #please update this tuple everytime you add a new command unless 
    # you don't want to show that command in !help
START_TIME = time.time() # startup time in seconds
PING_MSGS = ( # answers of !ping
"PONG",
"tail -n 10",
"Linux != Windows",
"#include<stdio.h> main() { while (1) fork(); }",
"Hey there is a cool site: http://example.com",
"su -c \'cat /dev/urandom >> /dev/dsp\'",
"while true; do eject -T; done",
"Hey don\'t ping me!", 
"cat /dev/urandom | tr -dc \'A-Za-z0-9!-)\' | fold -w 10 | head -n 3",
"sed s/.//g", 
"DING DOONG DONG",
"PING PONG POONG",
"rm -rf /",
"I\'m under GPL!",
"GNU = gnu's not unix",
"Play Supertux!",
"Play LiquidWar!",
"DDOS IT!",
"GTK = GIMP Tool Kit",
"MICRO$OFT THE ROBBER!",
"C# = Java.clone()",
"C => C++ => C++++ => C#",
"Free as freedom",
"aafire",
"MINIX...LINUX...HERD...????...",
"MOV BX, AX",
"by gcc when generating a far command line debuggers available for the java language specification demands that",
"gcc, this is useful when precompiling a c header file used, in the far option",
time.ctime(),
'There are 10 types of people: who know binary and who don\'t',
'Hey! someone is being drowned! ~~~ ~~~\o/~~~ ~ ~~',
'Beep...Beep...Beep...BOOM',
'BaghBaghoo!',
'shangul',
'do you like to be op\'ed?',
hex(int(START_TIME)),
'try !help for a list of my useless commands!',
'Chitty Chitty Bang Bang',
'tuxdude!',
'rm -rf /',
'sudo dd if=/dev/urandom >> of=/dev/sda',
'Nooooooo!Don\'t Interrupt me by CtrlC!',
'try C--',
'+[++++-,[+-.].',
'try Digger!',
hex(random.randint(100, 1000)),
'Do you want Pizza?',
'Hey there is a cool site: http://grahamdowney.com/',
'Hey a cool site: http://0.0.0.0/',
'NULL',
"dd if=/dev/urandom of=/dev/sda",
"dd if=/dev/zero of=./big_file",
"int a[1] = {0}; a[10] = 100;",
"Seg fault!",
"I\'m PingBot!",
"My glasses: -O_O-",
"Whoo Whoo!",
"Visit my website: http://example.com",
"don\'t let me ping you when you ping me and ping is the pinger pong!",
"ping the pong when pong is ping pong and do not pong the ping when poong is sleeping!"
"The Burrows Wheeler transform (BWT, also called block-sorting compression) rearranges a character string into runs of similar characters.",
"Error! File not found!",
"CommandNotFoundError: [Errno 2] Command \'!ping\' not found!",
":{}{}:{}{}|[]",
"Thanks for pinging ping bot!",
"Thanks for pinging The Pinger Bot! You won $3000 dollars!",
"Wanna get some bitcoins?yes?ok get some bitcoins!",
"   (null)",
"man is the woman's husband. Each page argument given to man is rarely the gcc of a torvalds, stallman or gates."
)

if len(sys.argv) == 1 or '-h' in sys.argv:
    print('Usage: pingbot.py <config_file>')
    sys.exit()

global Config
Config = configparser.ConfigParser()


try:
    with open(sys.argv[1]) as fs:
        Config.read_file(fs)
except FileNotFoundError:
    print('Error! File not Found!')
    sys.exit(1)


global server
global clogfile


def privmsg(target, msg) -> None:
    """ Sends msg to target."""
    if server:
        server.send(bytes("PRIVMSG " + target + 
            " :" + msg + "\r\n", 'utf-8'))


def quit(qmsg='') -> None:
    """Sends QUIT command to server"""
    print("Quiting!")
    print("Quit Message:", qmsg)
    if qmsg:
        server.send(bytes('QUIT :' + qmsg + '\r\n', 'utf-8'))
    else:
        server.send(bytes("QUIT\r\n", "utf-8"))
    server.close()
    clogfile.write("===============================================")
    clogfile.close()
    sys.exit()


def reply(msg_dict, message) -> None:
    """ Replys a highlighted message to sender of message if it\'s """
    """ in a channel otherwise sends raw message to sender"""
    if msg_dict['channel'] == Config['DEFAULT']['nick']:
        privmsg(msg_dict['nick'], message)
    else:
        privmsg(msg_dict['channel'], msg_dict['nick'] + ': ' + message)


def init() -> None:
    """ Something that bot should do when connecting to server """
    """ like sending USER and NICK commands and sending Password """
    bot_nick = Config['DEFAULT']['nick']
    server.send(bytes("USER " + bot_nick + ' ' + bot_nick + ' ' 
        + bot_nick + ' '
        + ":" + Config['DEFAULT']['realname'] + "\r\n", "utf-8"))
    server.send(bytes("NICK " + bot_nick + "\r\n", "utf-8"))

    privmsg("NickServ", "identify " + Config['DEFAULT']['password'])
    for c in Config['DEFAULT']['channels'].split():
        server.send(bytes("JOIN " + c + "\r\n", "utf-8"))
    server.recv(10000)
    # to clear buffer.irc networks send something that we don't need


def irc_msg(raw_irc_msg) -> dict:
    """ Extracts nick, message and channel from raw_irc_msg """
    """ returns None if raw_irc_msg is not an irc message """
    if not raw_irc_msg: return None
    raw_irc_msg = raw_irc_msg.split()
    raw_irc_msg[3:] = [' '.join(raw_irc_msg[3:])]
    msg = dict()
    try:
        msg['nick'] = raw_irc_msg[0].split('!')[0].replace(':', '', 1)
        msg['channel'] = raw_irc_msg[2]
        msg['msg'] = raw_irc_msg[-1].replace(':', '', 1).replace('\r\n', '')
       
        clogfile.write('[' + msg['channel'] + ']' + ' ' + '<' + msg['nick'] +
                       '>' + ' ' + msg['msg'] + '\n')
            
        
        if not msg['channel'].startswith('#') and msg['channel'] != Config['DEFAULT']['nick']:
            return None
    except IndexError: return None
    return msg


def is_admin(nick) -> bool:
    """ Checnks nick is nick of an admin or not """
    return (nick in Config['DEFAULT']['admins'].split()) or (nick == Config['DEFAULT']['main_admin'])


def part(channel) -> None:
    """ Leaves a channel """
    server.send(bytes('PART ' + channel + '\r\n', 'utf-8'))


def join(channel) -> None:
    """ Joins a channel """
    server.send(bytes("JOIN " + channel + "\r\n", 'utf-8'))


def kick(channel, nick) -> None:
    """ Kicks someone with <nick> in channel <channel> """
    server.send(bytes('KICK ' + channel + ' ' + nick + '\r\n', 'utf-8'))


def op(channel, nick) -> None:
    """ Gives OP status to <nick> in <channel> """
    server.send(bytes('MODE ' + channel + ' +o ' + nick + '\r\n', 'utf-8'))


def deop(channel, nick) -> None:
    """ Takes OP status from <nick> in <channel>"""
    server.send(bytes('MODE ' + channel + ' -o ' + nick + '\r\n', 'utf-8'))


def voice(channel, nick) -> None:
    """ Gives Voice to <nick> in <channel>"""
    server.send(bytes('MODE ' + channel + ' +v ' + nick + '\r\n', 'utf-8'))


def devoice(channel, nick) -> None:
    """ Takess Voice to <nick> in <channel>"""
    server.send(bytes('MODE ' + channel + ' -v ' + nick + '\r\n', 'utf-8'))

def write_conf() -> None:
    """ Writes data to config file """
    with open(sys.argv[1], 'w') as fp:
        Config.write(fp)


server = socket.socket()
HOST = Config['DEFAULT']['host']
PORT = int(Config['DEFAULT']['port'])
server.connect((HOST, PORT))
print("Connected!")
init()
print("Initialized!")
clogfile = open("clog.txt", "a")


while 1:
    try:
        buf = server.recv(1024).decode()
        uptime = int(time.time() - START_TIME)
        random.seed(uptime)
        for m in buf.split('\n'):
            if not m: continue
            # the PING PONG game between server and client. if you don't answer
            # server, your connection will be closed by server after about 270s
            if m.split()[0] == "PING": 
                server.send(bytes('PONG ' + m.split()[1] + '\r\n', 'utf-8'))
                continue

            m = irc_msg(m)
            if not m: continue
            args = m['msg'].split()
            if not len(args): continue

            if args[0] == '!ping':
                result = random.choice(PING_MSGS)
                reply(m, result)

            if args[0] == '!whatis' and len(args) >= 2:
                os.system('whatis ' + args[1] + ' > /tmp/faf')
                with open('/tmp/faf') as fs:
                    result = fs.read()
                reply(m, result)
            
            if args[0] == '!quit' and is_admin(m['nick']):
                quit(Config['DEFAULT']['QUIT_MSG_ON_ADMIN'])

            if args[0] == '!now':
                reply(m, time.ctime())

            if args[0] == '!say' and is_admin(m['nick']) and len(args)>2:
                privmsg(args[1], ' '.join(args[2:]))

            if args[0] == '!join' and is_admin(m['nick']) and len(args)>1:
                join(args[1])

            if args[0] == '!part' and is_admin(m['nick']) and len(args)>1:
                part(args[1])
                
            if args[0] == '!dice':
                result = str(random.randint(1, 6))
                reply(m, result)

            if args[0] == '!pony':
                result = 'plot' if random.randint(0, 1) else 'head'
                reply(m, result)

            if args[0] == '!help': 
                result = 'User Commands: ' + ' '.join(COMMANDS)
                reply(m, result)

            if args[0] == '!add_admin' and is_admin(m['nick']) and len(args)>1:
                Config['DEFAULT']['admins'] += ' ' + args[1]
                reply(m, 'Added ' + args[1] + ' to admins list')
                write_conf()

            if args[0] == '!remove_admin' and is_admin(m['nick']) and len(args)>1:
                try:
                    admins = Config['DEFAULT']['admins'].split()
                    admins.remove(args[1])
                    Config['DEFAULT']['admins'] = ' '.join(admins)
                except ValueError:
                    reply(m, args[1] + ' is not in admins list.')
                else:
                    reply(m, args[1] + ' removed from list')
                    write_conf()

            if args[0] == '!kick' and is_admin(m['nick']):
                if m['channel'] == Config['DEFAULT']['nick'] and len(args) > 2:
                    kick(args[1], args[2])
                elif m['channel'].startswith('#') and len(args) > 1:
                    kick(m['channel'], args[1])

            if args[0] == '!op' and is_admin(m['nick']):
                if m['channel'] == Config['DEFAULT']['nick'] and len(args) > 2:
                    op(args[1], args[2])
                elif m['channel'].startswith('#') and len(args) > 1:
                    op(m['channel'], args[1])
            
            if args[0] == '!deop' and is_admin(m['nick']):
                if m['channel'] == Config['DEFAULT']['nick'] and len(args) > 2:
                    deop(args[1], args[2])
                elif m['channel'].startswith('#') and len(args) > 1:
                    deop(m['channel'], args[1])

            if args[0] == '!voice' and is_admin(m['nick']):
                if m['channel'] == Config['DEFAULT']['nick'] and len(args) > 2:
                    voice(args[1], args[2])
                elif m['channel'].startswith('#') and len(args) > 1:
                    voice(m['channel'], args[1])
            
            if args[0] == '!devoice' and is_admin(m['nick']):
                if m['channel'] == Config['DEFAULT']['nick'] and len(args) > 2:
                    devoice(args[1], args[2])
                elif m['channel'].startswith('#') and len(args) > 1:
                    devoice(m['channel'], args[1])
            
            if args[0] == '!uptime':
                days = uptime // 86400
                b = uptime % 86400
                hours = b // 3600
                b = b % 3600
                mins = b // 60
                b = b % 60
                result =  (str(days) + 'd ' + str(hours) + 'h ' 
                    + str(mins) + 'm ' + str(b) + 's')
                reply(m, result)

            if args[0] == '!hex' and len(args) > 1:
                try:
                    result = hex(int(args[1])).replace('0x', '')
                    reply(m, result)
                except ValueError:
                    reply(m, 'ValueError! Are you sure it\'s an integer?')

            if args[0] == '!isprime' and len(args) > 1:
                try:
                    if len(args[1]) > 6:
                        raise ValueError
                    n = int(args[1])
                    if n < 2:
                        reply(m, str(n) + ' is not prime!')
                    isprime = True
                    for i in range(2, n):
                        if (n % i) == 0:
                           isprime = False 
                    reply(m, str(n) + (' is prime!' if isprime else ' is not prime!'))

                except ValueError:
                   reply(m, 'ValueError! Are you sure ' +
                       'it\'s an integer?')

            if args[0] == "!wwwtitle" and len(args) > 1:
                try:
                    page = urllib.request.urlopen(args[1])
                    tags = bs4.BeautifulSoup(page, "html.parser")
                    reply(m, tags.find_all("title")[0].get_text())
                except urllib.error.HTTPError and urllib.error.URLError:
                    reply(m, "Page Not Found!")
                except IndexError:
                    reply(m, "No title found in page!")
                except ValueError:
                    reply(m, "Are you sure it\'s a url?")
                    

    except KeyboardInterrupt:
        quit(Config['DEFAULT']['QUIT_MSG_ON_INTERRUPT'])
    except UnicodeEncodeError:
        pass
