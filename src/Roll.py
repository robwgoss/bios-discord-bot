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

import random, re, Utils
from datetime import datetime, date
class Roll():
    def __init__(self, ctx):
        self.low = 1
        self.high = 21
        self.rolls = 1
        self.results = []
        self.ctx = ctx
        self.authorID = ctx.author.id
        self.con = Utils.ConnectDB()
        self.cursor = self.con.cursor()

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
        newSeed = getSeed()
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

    async def setFlipCfg(self, args):
        if len(args) == 0:
            return self.setFlipData()
        elif len(args) == 1:
            if 'stat' in args[0].lower()  or args[0].lower() == 's':
                await self.getFlipData()
                return 2
        else:
            return 1

    def setFlipData(self):
        query = 'SELECT heads, tails, dte_last_flip FROM T_FLIP WHERE user_id = ' + str(self.authorID)
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            msg = "Error in setFlipData executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            return 1
        results = res.fetchall()
        if len(results) == 0:
            query = 'INSERT INTO T_FLIP VALUES(' + str(self.authorID) + ', 0, 0, 0)'
            try:
                res = self.cursor.execute(query)
            except Exception as e:
                msg = "Error in setFlipData executing:\n" + query
                Utils.logError(msg, PROGRAM_NAME, str(e))
                return 1
            self.totalHeads = 0
            self.totalTails = 0
            self.lastFlip = 0
            self.con.commit()
        else:
            self.totalHeads = int(results[0][0])
            self.totalTails = int(results[0][1])
            self.lastFlip =   int(results[0][2])
        return 0

    async def getFlipData(self):
        res = self.setFlipData()
        if res == 1:
            msg = 'Critical error getting Flip data!'
            self.ctx.send(msg)
            return 2
        if self.lastFlip == 0:
            msg = 'You have never flipped before! Try now with command: *~flip*'
            self.ctx.send(msg)
            return 2
        total = self.totalHeads + self.totalTails
        msg = 'You have a total of **' + str(total) + '** flips!\nYour total number of **HEADS** is **' + str(self.totalHeads) + '**, and total number of **TAILS** is **' + str(self.totalTails) + '**!\n'
        headsPercent = (self.totalHeads / total) * 100
        tailsPercent = (self.totalTails / total) * 100
        msg += 'Flips by Percentage:   Heads - ' + str(format(headsPercent, '.1f')) + '%       Tails - ' + str(format(tailsPercent, '.1f'))  + '%'
        await self.ctx.send(msg)
        self.cursor.close()
        return 2

    def updateFlipData(self, roll):
        if roll == 1:
            self.totalHeads += 1
        elif roll == 2:
            self.totalTails += 1
        today = date.today()
        dteLastFlip = str(today.strftime("%Y%m%d"))
        query = 'UPDATE T_FLIP SET HEADS = ' + str(self.totalHeads) + ', TAILS = ' + str(self.totalTails) + ', DTE_LAST_FLIP = ' + dteLastFlip + ' WHERE USER_ID = ' + str(self.authorID)
        try:
            self.cursor.execute(query)
        except Exception as e:
            msg = "Error in updateFlipData executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
        self.con.commit()

    async def flip(self):
        newSeed = getSeed()
        random.seed(newSeed)
        self.high = 3
        roll = random.randrange(self.low, self.high)

        msg = self.ctx.message.author.mention + "'s coin has flipped "
        if roll == 1:
            msg += "**HEADS!!**"
        else:
            msg += "**TAILS!!**"
        self.updateFlipData(roll)
        await self.ctx.send(msg)
        self.cursor.close()

def getSeed():
    dt = datetime.now()
    dt.strftime("%Y%d%H%M%S")
    newSeed = ""
    for char in str(dt):
        if char.isdigit():
            newSeed += char
    return newSeed