import random, re
from datetime import datetime
class Roll():
    def __init__(self):
        self.low = 1
        self.high = 21
        self.rolls = 1
        self.results = []
        self.validArgs = True

    def setRollCfg(self, args):
        self.args = args
        if len(self.args) == 0:
            return
        elif len(self.args) == 1:
            mod = self.args[0]
            searchString = "^\d+[d]\d+"
            valid = re.search(searchString, mod)
            if not valid:
                return -1
            dIndex = 0
            modChar = ''
            while modChar != 'd':
                modChar = mod[dIndex]
                if(modChar != 'd'):
                    dIndex += 1
            self.low = 1
            self.rolls = int(mod[0:dIndex])
            self.high = int(mod[dIndex+1:len(mod)]) + 1
            if self.rolls > 100 or self.high > 999999999999999:
                return -1
        else:
            return

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