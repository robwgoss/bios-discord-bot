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

    #Drives message parsing functions to find a "trigger" to react to, and ensures only one trigger per message is hit
    def findTriggers(self):
        self.triggers = [
            self.wordle
            ]
        
        for trigger in self.triggers:
            if not self.triggerFound:
                trigger()