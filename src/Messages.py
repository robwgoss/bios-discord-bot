from Wordle import WordleData
class RouteMessage():
    def __init__(self, bot, message):
        self.bot = bot
        self.message = message
        self.content = message.content
        self.channel = message.channel
        self.reponse = "NULL"
        self.triggerFound = False
        self.findTriggers()

    def wordle(self):
        w = WordleData(self.message)
        valid = w.validateWordle()
        if valid:
            unsolved = w.checkUnsolved()
            if unsolved:
                w.insertWordleData()
                self.triggerFound = True

    def findTriggers(self):
        self.triggers = [
            self.wordle
            ]
        
        for trigger in self.triggers:
            if not self.triggerFound:
                trigger()

    def getResponse(self):
        return self.reponse

