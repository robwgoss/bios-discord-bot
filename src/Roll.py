import random, re
from datetime import datetime
class Roll():
    def __init__(self):
        self.low = 1
        self.high = 21
        self.rolls = 1
        self.results = []

    def setRollCfg(self, args):
        self.args = args
        if len(self.args) == 0:
            return 0
        elif len(self.args) == 1:
            if(self.args[0].lower() == 'help'):
                return 2
            mod = self.args[0]
            searchString = "^\d+[d]\d+"
            valid = re.search(searchString, mod)
            if not valid:
                return 1
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
                return 1
            return 0
        elif len(self.args) == 3:
            for arg in self.args:
                if not arg.isdigit() or int(arg) < 0:
                    return 1
            self.rolls = int(self.args[0])
            self.low = int(self.args[1])
            self.high = int(self.args[2]) + 1
            if self.low > self.high:
                temp = self.low
                self.low = self.high
                self.high = temp
            elif self.low == self.high:
                return 1
            return 0
        else:
            return 1

    def roll(self):
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