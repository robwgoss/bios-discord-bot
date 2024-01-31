PROGRAM_NAME = "Roll.py"

##########################################################
#                                                        #
#   Program          Roll.py                             #
#                                                        #
#   Description      Responds to the ~roll command based #
#                    off the following options:          #
#                                                        #
#   ~roll            Rolls a single 20 sided dice        #
#                                                        #
#   ~roll xdy        Roll option where x is the number   #
#                    of rolls, d is a constant character,#
#                    and y is the max roll.              #
#                    Client Command Ex. ~roll 5d15       #
#                                                        #
#  ~roll x y z       Roll option where x is the number   #
#                    of rolls, y is the min roll, and z  #
#                    is the max roll.                    #
#                    Client Command Ex. ~roll 2 4 6      #
#                                                        #
#  ~roll help        Displays available commands in the  #
#                    client.                             #
#                                                        #                
##########################################################

import random, re
from datetime import datetime
class Roll():
    def __init__(self, ctx):
        self.low = 1
        self.high = 21
        self.rolls = 1
        self.results = []
        self.ctx = ctx

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

    async def roll(self):
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
        index = 0
        sum = 0
        multi = False
        highRoll = False
        msg = ""
        for r in self.results:
            if(len(self.results) == 1):
                msg = "Your roll was " + str(r) + "!"
                await self.ctx.send(msg)
            elif(len(self.results) > 10):
                if not multi:
                    msg = "Result of your rolls\n===========================\n"
                    multi = True
                    highRoll = True
                sum += r
                msg += str(r) + ", "
            elif(len(self.results) > 1):
                if not multi:
                    multi = True
                sum += r
                index += 1
                msg = "Result of roll number " + str(index) + " :    " + str(r)
                await self.ctx.send(msg)
            else:
                await self.ctx.send("The bot critically missed rolling! How did that happen?")
        if multi:
            if highRoll:
                msg = msg[0:len(msg) - 2]
                await self.ctx.send(msg)
            msg = "===========================\nThe sum of your rolls was " + str(sum) + "!\n==========================="
            await self.ctx.send(msg)