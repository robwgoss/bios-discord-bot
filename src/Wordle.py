PROGRAM_NAME = "Wordle.py"

import re, sqlite3, Utils
from datetime import datetime, date


class WordleData():
    def __init__(self, msg):
        self.message = msg
        self.author = Utils.cleanMember(str(msg.author))
        self.authorID = msg.author.id
        self.content = msg.content
        self.splitArr = self.content.splitlines()
        self.con = sqlite3.connect("../data/botProd.db")
        self.cursor = self.con.cursor()
        self.today = date.today()
        self.now = datetime.now()        

    def checkUnsolved(self):
        query = 'SELECT solved FROM T_WORDLE_GAMES WHERE user_id = ' + str(self.authorID) + ' AND wordle_num = ' + str(self.getWordleNum())
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            Utils.logError(str(e), PROGRAM_NAME)
            return False
        if len(res.fetchall()) == 0:
            return True
        else:
            self.cursor.close()
            return False

    def validateWordle(self):
        #Validates Wordle Header format of "Wordle xxx x/6"
        searchString = "^(Wordle)\s\d+\s.[/]{1}(6)\n"
        valid = re.search(searchString, self.content)
        if not valid:
            return False
        
        #Checks the validity of Wordle for potential errors or tampering
        count = 0
        for line in self.splitArr:
            if count == 1 and len(line) != 0:
                return False
            if count > 1 and len(line) != 5:
                return False
            if count > 1:
                for char in line:
                    if char != '🟩' and char != '⬛' and char != '🟨' and char != '⬜':
                        return False
            count += 1
        headLine = self.splitArr[0].rstrip()
        self.attemps = headLine[len(headLine) - 3]
        if self.attemps.lower() != 'x':
            if(len(self.splitArr) - 2 != int(self.attemps)):
                return False
            if(self.splitArr[int(self.attemps) + 1] != "🟩🟩🟩🟩🟩"):
                return False
        else:
            if(len(self.splitArr) != 8):
                return False
        return True
    
    def getWordleNum(self):
        header = self.splitArr[0]
        toggle = 0
        num = ""
        for char in header:
            if toggle == 1:
                num += char
            if char == ' ':
                if toggle == 1:
                    toggle = 0
                else:
                    toggle = 1
        return num.strip()

    def updateGlobalData(self):
        self.globalDteLastGame = str(self.today.strftime("%Y%m%d"))
        #Get user's global stats or add new record
        query = 'SELECT * FROM T_WORDLE_GLOBAL_STAT WHERE user_id = ' + str(self.authorID)
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            Utils.logError(str(e), PROGRAM_NAME)
            exit(1)
        results = res.fetchall()
        if(len(results) == 0):
            self.globalTotalMoves = 0
            self.globalTotalGames = 0
            self.globalTotalGreen = 0
            self.globalTotalYellow = 0
            self.globalTotalMiss = 0
            self.globalAverage = 0
            self.globalTotalSolved = 0
            self.globalWinRate = 0
            query = """
                INSERT INTO T_WORDLE_GLOBAL_STAT VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """ % (self.authorID, self.globalTotalMoves, self.globalTotalGames, self.globalTotalGreen,
                    self.globalTotalYellow, self.globalTotalMiss, self.globalAverage,  self.globalTotalSolved, self.globalWinRate, self.globalDteLastGame)
            try:
                self.cursor.execute(query)
            except Exception as e:
                Utils.logError(str(e), PROGRAM_NAME)
                exit(1)
            self.con.commit()
        else:
            self.globalTotalMoves = int(results[0][1])
            self.globalTotalGames = int(results[0][2])
            self.globalTotalGreen = int(results[0][3])
            self.globalTotalYellow = int(results[0][4])
            self.globalTotalMiss = int(results[0][5])
            self.globalTotalSolved = int(results[0][7])
        #Update global stats with new game data
        self.globalTotalMoves += self.totalMoves
        self.globalTotalGames += 1
        self.globalTotalGreen += self.total_green
        self.globalTotalYellow += self.total_yellow
        self.globalTotalMiss += self.total_miss
        self.globalAverage = self.globalTotalMoves / self.globalTotalGames
        self.globalTotalSolved += self.solved
        self.globalWinRate = self.globalTotalSolved / self.globalTotalGames
        query = """
            UPDATE T_WORDLE_GLOBAL_STAT SET total_moves = %s, total_games = %s, total_green = %s, total_yellow = %s, total_miss = %s, average = %s, total_solved = %s, win_rate = %s, dte_last_game = %s WHERE user_id = %s
        """ % (self.globalTotalMoves, self.globalTotalGames, self.globalTotalGreen, self.globalTotalYellow, self.globalTotalMiss, format(self.globalAverage, '.4f'), self.globalTotalSolved, format(self.globalWinRate, '.4f'),
                self.globalDteLastGame, self.authorID)
        try:
            self.cursor.execute(query)
        except Exception as e:
            Utils.logError(str(e), PROGRAM_NAME)
            exit(1)



    def processWordleData(self):
        self.total_green = 0
        self.total_yellow = 0
        self.total_miss = 0
        self.solved = 0
        count = 0
        #Insertions for individual moves
        for line in self.splitArr:
            if(count > 1):
                green = 0
                yellow = 0
                miss = 0
                for char in line:
                    if char == '🟩':
                        green += 1
                    elif char == '🟨':
                        yellow += 1
                    elif char == '⬛' or char == '⬜':
                        miss += 1
                if green == 5:
                    self.solved = 1
                self.total_green += green
                self.total_yellow += yellow
                self.total_miss += miss
                query = """
                    INSERT INTO T_WORDLE_MOVES VALUES(%s,%s,%s,\'%s\',%s,%s,%s,%s)
                """ % (self.authorID, self.getWordleNum(), count - 1, line, green, yellow, miss, self.solved)
                try:
                    self.cursor.execute(query)
                except Exception as e:
                    Utils.logError(str(e), PROGRAM_NAME)
                    exit(1)
            count += 1
        #Game data and global stat update
        day = str(self.today.strftime("%Y%m%d"))
        time = str(self.now.strftime("%H%M%S"))
        self.totalMoves = count - 2
        query = """
                    INSERT INTO T_WORDLE_GAMES VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """ % (self.authorID, self.getWordleNum(), self.totalMoves, self.total_green, self.total_yellow, self.total_miss, self.solved, day, time)
        try:
            self.cursor.execute(query)
        except Exception as e:
            Utils.logError(str(e), PROGRAM_NAME)
            exit(1)
        self.updateGlobalData()
        self.con.commit()
        self.cursor.close()

class Wordle():
    def processArgs(self, args, ctx):
        if len(args) == 0:
            return WordleStat(0, ctx)
        elif len(args) == 1:
            arg = args[0]
            if arg.lower() == 'help':
                return 2
            elif arg.lower() == 'practice':
                practice = WordlePractice()
            elif arg.lower() == 'guild':
                return WordleStat(1, ctx)
            elif arg.isnumeric():
                wordleNum = int(arg)
                if wordleNum < 1 or wordleNum > 2000:
                    return 1
                else:
                    return WordleStat(2, ctx, wordleNum)
        else:
            return 1

class WordleStat():
    def __init__(self, commandInd, ctx, wordleNum=''):
        self.commandInd = commandInd
        self.ctx = ctx
        self.wordleNum = wordleNum
        self.con = sqlite3.connect("../data/botProd.db")
        self.cursor = self.con.cursor()
        self.routeCommand()

    def routeCommand(self):
        if self.commandInd == 0:
            print("Default user stats")
        elif self.commandInd == 1:
            print("Wordle stats for users in channel")
        elif self.commandInd == 2:
            self.wordleNumStat(self.wordleNum)
        else:
            msg = 'WordleStat recieved bad arguments'
            Utils.logError(msg, PROGRAM_NAME)
            return 1
        return 0
    
    def guildLeaderboard(self):
        query = ''

    def wordleNumStat(self, wordleNum):
        query = 'SELECT * FROM T_WORDLE_GAMES WHERE wordle_num = ' + str(wordleNum) + ' AND user_id in ( ' + self.getGuildMembers() + ') ORDER BY num_moves ASC, dte_game ASC, time_game ASC LIMIT 5'
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            Utils.logError(str(e), PROGRAM_NAME)
            exit(1)
        results = res.fetchall()
        for result in results:
            print(self.ctx.guild.get_member(result[0]))

    def getGuildMembers(self):
        memberStr = ''
        for member in self.ctx.guild.members:
            memberStr += '' + str(member.id) + ','
        return memberStr[0:len(memberStr) - 1]


class WordlePractice():
    def __init__(self):
        print("test")