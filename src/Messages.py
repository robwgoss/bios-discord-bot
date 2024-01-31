PROGRAM_NAME = "Messages.py"

##########################################################
#                                                        #
#   Program          Messages.py                         #
#                                                        #
#   Description      All new messages from any channel   #
#                    the bot can read are processed here.#
#                    Each message is put through         #
#                    functions to find "triggers" to     #
#                    take action on. Does nothing if no  #
#                    trigger is found.                   #
#                                                        #
##########################################################

from Wordle import WordleData
class RouteMessage():
    def __init__(self, bot, message):
        self.bot = bot
        self.message = message
        self.content = message.content
        self.channel = message.channel
        self.responseCode = -1
        self.responseMsg = ""
        self.triggerFound = False
        self.findTriggers()

    def getResponseCode(self):
        return self.responseCode

    def getResponseMsg(self):
        return self.responseMsg

    def wordle(self):
        w = WordleData(self.message)
        valid = w.validateWordle()
        if valid:
            self.responseCode = 1
            self.responseMsg = '❌'
            unsolved = w.checkUnsolved()
            if unsolved:
                w.processWordleData()
                self.triggerFound = True
                self.responseMsg = '✅'

    def findTriggers(self):
        self.triggers = [
            self.wordle
            ]
        
        for trigger in self.triggers:
            if not self.triggerFound:
                trigger()