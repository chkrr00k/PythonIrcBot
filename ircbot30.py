
    #############################################################
    #                                                           #
    #   This program is relased in the GNU GPL v3.0 licence     #
    #   you can modify/use this program as you wish. Please     #
    #   link the original distribution of this software. If     #
    #   you plan to redistribute your modified/copied copy      #
    #   you need to relased the in GNU GPL v3.0 licence too     #
    #   according to the overmentioned licence.                 #
    #                                                           #
    #   "PROUDLY" MADE BY chkrr00k (i'm not THAT proud tbh)     #
    #                                                           #
    #############################################################
    #                                                           #
    #   I have tried to use a good mvc modelling while let-     #
    #   letting the maximum usability, modularity and mode-     #
    #   lling                                                   #
    #                                                           #
    #############################################################

import sys
import socket
import string

HOST = "ayy.lmao"
NICK = "nickName"
IDENT = "ident"
REALNAME = "realname"

##MODEL
class Server:
    #private sock
    #private stringBuffer
    def __init__(self, server, port=6667):
        self.sock = socket.socket( )
        self.sock.connect((server, port))
        self.stringBuffer = ""
        
    def write(self, message):
        self.sock.send(bytes(message, "UTF-8"))
    
    def read(self):
        #old string + string just read.
        self.stringBuffer = self.stringBuffer + self.sock.recv(1024).decode("UTF-8")
        #split the string in corrispondence of "\n" to have a list of message ("\r" is still there)
        tmp = self.stringBuffer.split("\n")
        #
        self.stringBuffer = tmp.pop()
        return tmp

class Irc:
    #private ServerObj
    def __init__(self, server, port=6667):
        self.ServerObj = Server(server, port);
        self.lastString = ""
        self.messages = []
    
    def pingHandler(self, line):
        self.ServerObj.write("PONG " + (line.split() [1]) + "\r\n")

    def messageHandler(self, line):
        tokLine = line.split()
        nickName = ((tokLine[0]).split("!")[0]).strip()[1:]
        channel = (tokLine[2]).strip()
        message = line.split(" :")[1]
        return nickName, channel, message

    def sendMessage(self, channel, message):
        self.ServerObj.write("PRIVMSG " + channel + " :" + message +"\r\n")

    def sendNotice(self, channel, message):
        self.ServerObj.write("NOTICE " + channel + " :" + message +"\r\n")

    def modeHandler(self, line):
        pass

    def quitHandler(self, line):
        tokLine = line.split()
        nickName = ((tokLine[0]).split("!")[0]).strip()[1:]
        return nickName

    def partHandler(self, line):
        tokLine = line.split()
        nickName = ((tokLine[0]).split("!")[0]).strip()[1:]
        channel = tokLine[2]
        return nickName, channel

    def joinHandler(self, line):
        tokLine = line.split()
        nickName = ((tokLine[0]).split("!")[0]).strip()[1:]
        channel = line.split(" :")[1]
        return nickName, channel

    def inviteHandler(self, line):
        return (line.split(" ")[3])[1:]

    def setMode(self, channel, moded, mode):
        self.ServerObj.write("MODE " + channel + " " + mode + " " + moded + "\r\n")

    def readline(self):
        return self.ServerObj.read()

    def joinChannel(self, channel):
        self.ServerObj.write("JOIN " + channel + "\r\n")
	
    def connect(self):
        self.ServerObj.write("NICK " + NICK + "\r\n")
        self.ServerObj.write("USER " + IDENT + " " + HOST + " ayy :" + REALNAME + "\r\n")

    def kick(self, channel, kicked, message=""):
        self.ServerObj.write("KICK " + channel + " " + kicked + " :" + message + "\r\n")

    def ban(self, channel, banned, message=""):
        self.setMode(channel, "+b", banned)

    def kickAndBan(self, channel, banned, message=""):
        self.kick(channel, banned, message)
        self.ban(channel, banned, message)

##CONTROLLER

irc = Irc("server.name")
print("connecting")
irc.connect()
auth = 0
number = 0
channels = ["#chan", "#chan2"] #list of channels to join
#TODO add multiple channel permissions
instructionsOP = {".op" : "+o", ".deop" : "-o", ".protect" : "+a", ".deprotect" : "-a", ".voice" : "+v", ".devoice" : "-v", ".hop" : "+h", ".dehop" : "-h"} #possible commands form chat line (command : mode)
instructionsPR = {".k" : irc.kick, ".kb" : irc.kickAndBan, ".b" : irc.ban}
authorized = {"#chan" : {"authNickName" : [".op", ".deop", ".hop", ".dehop", ".voice",".devoice", ".k"]}} #authorized users + list of commands they can use
while 1:
    msgList = irc.readline()
    for msg in msgList:
        if msg.startswith("PING"):
            irc.pingHandler(msg.rstrip())
            print("PONGED")
            
        if msg.find("PRIVMSG") > -1:
            nick, chan, messS = irc.messageHandler(msg)
            print(nick, chan, messS)
#	    bot behaviour at messages promotion for user
            mess = messS.split(" ")
            if mess[0].strip() in instructionsOP and chan.strip().lower() in authorized :
                if nick in authorized[chan.strip().lower()]:
                    for mode in (authorized[chan.strip()])[nick.strip()]:
                        if mess[0].strip() == mode:
                            if len(mess) > 1:
                                irc.setMode(chan, mess[1], instructionsOP[mess[0].strip()])
                            else:
                                irc.setMode(chan, nick, instructionsOP[mess[0].strip()])

                            
            if mess[0].strip() in instructionsPR and chan.strip() in authorized :
                if nick in authorized[chan.strip()]:
                    for command in (authorized[chan.strip()])[nick.strip()]:
                        if mess[0].strip() == command:
                            if len(mess) > 1:
                                instructionsPR[mess[0]](chan, mess[1])

        if msg.find("NOTICE") > -1:
            nick, chan, mess = irc.messageHandler(msg)
            print(nick, chan, mess)

        if msg.find("INVITE") > -1:
            irc.joinChannel(irc.inviteHandler(msg))

        if msg.find("MODE") > -1:
            irc.modeHandler(msg)

        if msg.find("QUIT") > -1:
            nick = irc.quitHandler(msg)
            print(nick, " has quit")

        if msg.find("PART") > -1:
            nick, chan = irc.partHandler(msg)
            print(nick, " has left ", chan)

        if msg.find("JOIN") > -1:
            nick, chan = irc.joinHandler(msg)
            print(nick, " has join ", chan)
            
        if (number == 6) and not auth:
            auth = 1
            for chan in channels:
                irc.joinChannel(chan)
        number += 1

#    print(msg)
