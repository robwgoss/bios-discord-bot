import random
from datetime import datetime
class Roll():
    def __init__(self, args):
        self.args = args
        self.low = 1
        self.high = 20
        self.rolls = 1
        self.results = []
        self.validArgs = True
        self.checkArgs()

    def checkArgs(self):
        if len(self.args) != 0:
            self.validArgs = False #TODO: Check either 1d20 stye format or low, high, and numrolls(optional) for args. Can call this check in Main and intercept roll() logic
    
    def roll(self):
        if not self.validArgs:
            return -1
        dt = datetime.now()
        dt.strftime("%Y%d%H%M%S")
        newSeed = ""
        for char in str(dt):
            if char.isdigit():
                newSeed += char
        random.seed(newSeed)
        while self.rolls > 0:
            self.results.append(random.randrange(self.low, self.high))
            self.rolls -= 1 
        return self.results
