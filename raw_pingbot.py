import socket
import os
import sys
import random
import time
import configparser


COMMANDS = ('!ping')
    #please update this tuple everytime you add a new command unless 
    # you don't want to show that command in !help
START_TIME = time.time() # startup time in seconds

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


def privmsg(target, msg) -> None:
    """ Sends msg to target."""
    if server:
        server.send(bytes("PRIVMSG " + target + 
            " :" + msg + "\r\n", 'utf-8'))


def quit(qmsg=''):
    """Sends QUIT command to server"""
    print("Quiting!")
    print("Quit Message:", qmsg)
    if qmsg:
        server.send(bytes('QUIT :' + qmsg + '\r\n', 'utf-8'))
    else:
        server.send(bytes("QUIT\r\n", "utf-8"))
    server.close()
    sys.exit()


def replay(msg_dict, message):
    """ Replays a highlighted message to sender of message if it\'s """
    """ in a channel otherwise sends raw message to sender"""
    if msg_dict['channel'] == Config['DEFAULT']['nick']:
        privmsg(msg_dict['nick'], message)
    else:
        privmsg(msg_dict['channel'], msg_dict['nick'] + ': ' + message)


def init():
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


def irc_msg(raw_irc_msg):
    """ Extracts nick, message and channel from raw_irc_msg """
    """ returns None if raw_irc_msg is not an irc message """
    if not raw_irc_msg: return None
    raw_irc_msg = raw_irc_msg.split(maxsplit=3)
    msg = dict()
    try:
        msg['nick'] = raw_irc_msg[0].split('!')[0].replace(':', '', 1)
        msg['channel'] = raw_irc_msg[2]
        msg['msg'] = raw_irc_msg[-1].replace(':', '', 1).replace('\r\n', '')
        if not msg['channel'].startswith('#') and msg['channel'] != Config['DEFAULT']['nick']:
            return None
    except IndexError: return None
    return msg


def is_admin(nick):
    """ Checnks nick is nick of an admin or not """
    return (nick in Config['DEFAULT']['admins'].split()) or (nick == Config['DEFAULT']['main_admin'])


def part(channel):
    """ Leaves a channel """
    server.send(bytes('PART ' + channel + '\r\n', 'utf-8'))


def join(channel):
    """ Joins a channel """
    server.send(bytes("JOIN " + channel + "\r\n", 'utf-8'))


def kick(channel, nick):
    """ Kicks someone with <nick> in channel <channel> """
    server.send(bytes('KICK ' + channel + ' ' + nick + '\r\n', 'utf-8'))


def op(channel, nick):
    """ Gives OP status to <nick> in <channel> """
    server.send(bytes('MODE ' + channel + ' +o ' + nick + '\r\n', 'utf-8'))


def deop(channel, nick):
    """ Takes OP status from <nick> in <channel>"""
    server.send(bytes('MODE ' + channel + ' -o ' + nick + '\r\n', 'utf-8'))


def voice(channel, nick):
    """ Gives Voice to <nick> in <channel>"""
    server.send(bytes('MODE ' + channel + ' +v ' + nick + '\r\n', 'utf-8'))


def devoice(channel, nick):
    """ Takess Voice to <nick> in <channel>"""
    server.send(bytes('MODE ' + channel + ' -v ' + nick + '\r\n', 'utf-8'))

def write_conf():
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


while 1:
    try:
        buf = server.recv(1024).decode()
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

            if args[0] == '!ping':
                replay(m, 'pong')

            if args[0] == "!help":
                replay(m, ' '.join(COMMANDS))

            if args[0] == '!quit' and is_admin(m['nick']):
                quit(Config['DEFAULT']['QUIT_MSG_ON_ADMIN'])

    except KeyboardInterrupt:
        quit(Config['DEFAULT']['QUIT_MSG_ON_INTERRUPT'])
    except UnicodeEncodeError:
        pass
