PROGRAM_NAME = "Wordle.py"

##########################################################
#                                                        #
#   Program          Wordle.py                           #
#                                                        #
#   Description      Generates images for the author's   #
#                    channel based off Wordle data that  #
#                    has been gathered and cleaned by    #
#                    this program.                       #
#                                                        #
##########################################################

import re, Utils, discord, os, ImageGenHelper
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, date

BIOS_GREEN = (32, 194, 14)
TERMINAL_FONT = "../assets/terminalFont.ttf"

##########################################################
#                                                        #
#   Class            WordleData()                        #
#                                                        #
#   Description      Processes Wordle data if message    #
#                    watcher detects a valid Wordle      #
#                                                        #
##########################################################
class WordleData():
    def __init__(self, msg):
        self.message = msg
        self.author = Utils.cleanMember(str(msg.author))
        self.authorID = msg.author.id
        self.content = msg.content
        self.splitArr = self.content.splitlines()
        self.con = Utils.ConnectDB()
        self.cursor = self.con.cursor()
        self.today = date.today()
        self.now = datetime.now()        

    def checkUnsolved(self):
        query = 'SELECT solved FROM T_WORDLE_GAMES WHERE user_id = ' + str(self.authorID) + ' AND wordle_num = ' + str(self.getWordleNum())
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            msg = "Error in checkUnsolved executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            return False
        if len(res.fetchall()) == 0:
            return True
        else:
            self.cursor.close()
            return False

    def validateWordle(self):
        #Validates Wordle Header format of "Wordle xxx x/6"
        searchString = "^(Wordle)\s\d+(,\d+)?\s.[/]{1}(6)\n"
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
        return num.replace(",", "").strip()

    def updateGlobalData(self):
        globalDteLastGame = str(self.today.strftime("%Y%m%d"))
        #Get user's global stats or add new record
        query = 'SELECT * FROM T_WORDLE_GLOBAL_STAT WHERE user_id = ' + str(self.authorID)
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            msg = "Error in updateGlobalData executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            exit(1)
        results = res.fetchall()
        globalTotalMoves = 0
        globalTotalGames = 0
        globalTotalGreen = 0
        globalTotalYellow = 0
        globalTotalMiss = 0
        globalAverage = 0
        globalTotalSolved = 0
        globalWinRate = 0
        if(len(results) == 0):
            query = """
                INSERT INTO T_WORDLE_GLOBAL_STAT VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """ % (self.authorID, globalTotalMoves, globalTotalGames, globalTotalGreen,
                    globalTotalYellow, globalTotalMiss, globalAverage,  globalTotalSolved, globalWinRate, globalDteLastGame)
            try:
                self.cursor.execute(query)
            except Exception as e:
                msg = "Error in updateGlobalData executing:\n" + query
                Utils.logError(msg, PROGRAM_NAME, str(e))
                exit(1)
            self.con.commit()
        else:
            globalTotalMoves = int(results[0][1])
            globalTotalGames = int(results[0][2])
            globalTotalGreen = int(results[0][3])
            globalTotalYellow = int(results[0][4])
            globalTotalMiss = int(results[0][5])
            globalTotalSolved = int(results[0][7])
        #Update global stats with new game data
        globalTotalMoves += self.totalMoves
        globalTotalGames += 1
        globalTotalGreen += self.total_green
        globalTotalYellow += self.total_yellow
        globalTotalMiss += self.total_miss
        globalAverage = globalTotalMoves / globalTotalGames
        globalTotalSolved += self.solved
        globalWinRate = globalTotalSolved / globalTotalGames
        query = """
            UPDATE T_WORDLE_GLOBAL_STAT SET total_moves = %s, total_games = %s, total_green = %s, total_yellow = %s, total_miss = %s, average = %s, total_solved = %s, win_rate = %s, dte_last_game = %s WHERE user_id = %s
        """ % (globalTotalMoves, globalTotalGames, globalTotalGreen, globalTotalYellow, globalTotalMiss, format(globalAverage, '.4f'), globalTotalSolved, format(globalWinRate, '.4f'),
                globalDteLastGame, self.authorID)
        try:
            self.cursor.execute(query)
        except Exception as e:
            msg = "Error in updateGlobalData executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
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
                    msg = "Error in processWordleData executing:\n" + query
                    Utils.logError(msg, PROGRAM_NAME, str(e))
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
            msg = "Error in processWordleData executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            exit(1)
        self.updateGlobalData()
        self.con.commit()
        self.cursor.close()
##########################################################
#                                                        #
#   Class            Wordle()                            #
#                                                        #
#   Description      Drives the ~wordle command based    #
#                    off the args passed from the client #
#                    and through the command on main.    #
#                                                        #
#   Command Options                                      #
#                                                        #
#   ~wordle x        Wordle option to generate an image  #
#                    that's sent to the author's channel #
#                    with a guild leaderboard for the    #
#                    day.                                #
#                    Client Command Ex. ~wordle 952      #
#                                                        #
#   ~wordle help     Displays available Wordle commands  #
#                    in the author's channel.            #
#                                                        #
##########################################################
class Wordle():
    async def processArgs(self, args, ctx):
        if len(args) == 0:
            ws = WordleStat(0, ctx, 0)
            return await ws.routeCommand()
        elif len(args) > 0:
            option = args[0]
            if option.lower() == 'help':
                return 2
            elif 'stat' in option.lower():
                mod = 0
                if len(args) == 2:
                    mod = args[1]
                ws = WordleStat(0, ctx, mod)
                return await ws.routeCommand()
            elif option.lower() == 'server':
                mod = 1
                if len(args) == 2:
                    #Check if number is after 'server'
                    if not args[1].isnumeric():
                        return 3
                    mod = int(args[1])
                    #verify number greater than or equal to 1
                    if mod < 1:
                        return 3
                    #Accept only one number for arg
                elif len(args) > 2:
                    return 3
                ws = WordleStat(1, ctx, mod)
                return await ws.routeCommand()
            elif option.isnumeric():
                wordleNum = int(option)
                if wordleNum < 1 or wordleNum > 9999:
                    return 3
                else:
                    ws = WordleStat(2, ctx, wordleNum)
                    return await ws.routeCommand()
            #Option for weighted average
            elif option.lower() == 'weighted':
                mod = 1
                if len(args) == 2:
                    if not args[1].isnumeric():
                        return 3
                    mod = int(args[1])
                    if mod < 1:
                        return 3
                elif len(args) > 2:
                    return 3
                ws = WordleStat(3, ctx, mod)
                return await ws.routeCommand()
            else:
                return 3
##########################################################
#                                                        #
#   Class            WordleStat()                        #
#                                                        #
#   Description      Generates visualized Wordle data    #
#                    gathered from WordleData() class.   #
#                                                        #
##########################################################
class WordleStat():
    def __init__(self, commandInd, ctx, modifier):
        self.commandInd = commandInd
        self.ctx = ctx
        self.modifier = modifier
        self.wordleNum = modifier
        self.authorID = ctx.author.id
        self.con = Utils.ConnectDB()
        self.cursor = self.con.cursor()

    async def routeCommand(self):
        if self.commandInd == 0:
            return await self.wordleUserStat()
        elif self.commandInd == 1:
            return await self.wordleServerStat()
        elif self.commandInd == 2:
            return await self.wordleNumStat()
        elif self.commandInd == 3:
            return await self.wordleWeightedAvg()
        else:
            msg = 'WordleStat recieved bad arguments'
            Utils.logError(msg, PROGRAM_NAME, 'None')
            return 1
        return 0

    async def wordleUserStat(self):
        userId = str(self.authorID)
        if self.modifier != 0:
            tempId = self.modifier[2:len(self.modifier) - 1]
            if len(str(tempId)) >= 17 and len(str(tempId)) <= 20:
                userId = tempId
        query = "SELECT NUM_MOVES, DTE_GAME FROM T_WORDLE_GAMES WHERE user_id = " + userId + " ORDER BY dte_game desc, time_game desc LIMIT 10"
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            msg = "Error in wordleUserStat executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            exit(1)
        self.matchHist = res.fetchall()
        if len(self.matchHist) == 0:
            self.matchHist = -1
        query = "SELECT COUNT(WORDLE_NUM), SUM(NUM_MOVES), SUM(SOLVED) FROM T_WORDLE_GAMES WHERE user_id = "  
        query += str(userId)
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            msg = "Error in wordleUserStat executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            exit(1)
        self.userStats = res.fetchone()
        if str(self.userStats[0]) == '0':
            self.userStats = -1
        today = date.today()
        month = str(today.strftime("%Y%m"))
        self.currMonth = self.getMonthData(month, userId)
        self.prevMonth = self.getMonthData(str(int(month) - 1), userId)
        if await self.generateWordleUserStatImg(userId):
            return 0
        return 1

    
    async def wordleServerStat(self):
        query = 'SELECT * FROM T_WORDLE_GLOBAL_STAT WHERE user_id in ( ' + self.getGuildMembers() + ') ORDER BY average ASC LIMIT 5'
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            msg = "Error in wordleServerStat executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            exit(1)
        self.results = res.fetchall()
        if await self.generateWordleServerStatImg(True, 1):
            return 0
        return 1

    async def wordleNumStat(self):
        query = 'SELECT * FROM T_WORDLE_GAMES WHERE wordle_num = ' + str(self.wordleNum) + ' AND user_id in ( ' + self.getGuildMembers() + ') AND SOLVED = 1 ORDER BY num_moves ASC, dte_game ASC, time_game ASC LIMIT 5'
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            msg = "Error in wordleNumStat executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            exit(1)
        self.results = res.fetchall()
        if await self.generateWordleNumStatImg():
            return 0
        return 1

    async def wordleWeightedAvg(self):
        queryMax = 'SELECT MAX(total_games) FROM T_WORDLE_GLOBAL_STAT where user_id in ( ' + self.getGuildMembers() + ')'
        try:
            resMax = self.cursor.execute(queryMax)
        except Exception as e:
            msg = "Unable to get who played the most games:\n" + queryMax
            Utils.logError(msg, PROGRAM_NAME, str(e))
            exit(1)
        maxGamesList = resMax.fetchall()
        maxGames = maxGamesList[0][0]
        query = 'SELECT * FROM T_WORDLE_GLOBAL_STAT WHERE user_id in ( ' + self.getGuildMembers() + ') ORDER BY average ASC'
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            msg = "Unable to fetch data from T_WORDLE_GLOBAL_STAT in wordleWeightedAvg:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            exit(1)
        wordleData = res.fetchall()
        for entry,col in enumerate(wordleData):
            if col[2] < maxGames:
                diff = maxGames - col[2]
                addMoves = diff * 6
                temp = list(wordleData[entry])
                temp[1] = temp[1] + addMoves
                temp[6] = format(temp[1] / maxGames, '.4f')
                wordleData[entry] = tuple(temp)
        sort_by_avg = sorted(wordleData, key=lambda tup: float(tup[6]))
        topFive = sort_by_avg[:5]
        self.results = topFive
        if await self.generateWordleServerStatImg(False, 1):
            return 0
        return 1

    async def generateWordleUserStatImg(self, userId):
        try:
            picWidth = 1500
            picHeight = 1500
            header = "User stats"
            image = await ImageGenHelper.generateGenericUserHeader(header, picWidth, picHeight, 0, self.ctx, userId)
            image = await ImageGenHelper.drawUserMatchHist(self.ctx, image, self.matchHist)
            image = await ImageGenHelper.drawUserStats(self.ctx, image, self.userStats, self.currMonth, self.prevMonth)
            draw = ImageDraw.Draw(image)
            statImgName = '../tmp/' + str(self.ctx.guild.id) + '_wordleUsereStat' + '.png'
            image.save(statImgName)
            await self.ctx.channel.send(file=discord.File(statImgName))
            os.remove(statImgName)
            return True
        except Exception as e:
            msg = 'WordleStat failed to generate image'
            Utils.logError(msg, PROGRAM_NAME, str(e))
            return False

    async def generateWordleNumStatImg(self):
        try:
            picWidth = 1500
            picHeight = 1600 - (170 * (5 - len(self.results)))
            header = "> Stats for Wordle [" + str(self.wordleNum) + "]\n========================="
            image = await ImageGenHelper.generateGenericServerHeader(header, picWidth, picHeight, 0, self.ctx)
            draw = ImageDraw.Draw(image)
            #Stats
            if len(self.results) == 0:
                font = ImageFont.truetype(TERMINAL_FONT, size=120)
                noData = "- NO DATA FOUND -"
                draw.text((325,800), noData, font=font, fill = BIOS_GREEN)
            else:
                y = 775
                count = 1
                font = ImageFont.truetype(TERMINAL_FONT, size=60)
                for result in self.results:
                    #Draw user placement, user info and score
                    x = 975
                    image = await ImageGenHelper.drawLeaderboardUser(y, count, image, result[0], self.ctx)
                    score = str(result[2]) + "/6"
                    draw.text((x, y), score, font=font, fill = BIOS_GREEN)
                    #Visualized colors
                    x += 100
                    green = int(result[3])
                    yellow = int(result[4])
                    red = int(result[5])
                    maxMoves = max(green, yellow, red)
                    green = int(80 - (80 * (green / maxMoves)))
                    yellow = int(80 - (80 * (yellow / maxMoves)))
                    red = int(80 - (80 * (red / maxMoves)))
                    statY = y - 20

                    draw.rectangle([(x, statY + green), (x + 20, statY + 80)], fill = BIOS_GREEN)
                    draw.rectangle([(x + 21, statY + yellow), (x + 40, statY + 80)], fill = (255, 234, 0))
                    draw.rectangle([(x + 41, statY + red), (x + 60, statY + 80)], fill = (255, 0, 30))
                    #Time
                    x += 100
                    dateRaw = str(result[7])
                    dateStr = dateRaw[0:4] + '/' + dateRaw[4:6] + '/' + dateRaw[6:8]
                    timeStr = dateStr + '\n' + self.formatTime(str(result[8]))
                    font = ImageFont.truetype(TERMINAL_FONT, size=60)
                    draw.text((x, y - 30), timeStr, font=font, fill = BIOS_GREEN)
                    #Increment
                    y += 170
                    count += 1
            #Send picture to ctx channel
            statImgName = '../tmp/' + str(self.ctx.guild.id) + '_wordleNumStat' + '_' + str(self.wordleNum) + '.png'
            image.save(statImgName)
            await self.ctx.channel.send(file=discord.File(statImgName))
            os.remove(statImgName)
            return True
        except Exception as e:
            msg = 'WordleStat failed to generate image'
            Utils.logError(msg, PROGRAM_NAME, str(e))
            return False

    async def generateWordleServerStatImg(self, server, page):
        try:
            picWidth = 1800
            picHeight = 1650 - (170 * (5 - len(self.results)))
            header = "> All Time Wordle Stats\n========================="
            image = await ImageGenHelper.generateGenericServerHeader(header, picWidth, picHeight, 125, self.ctx)
            draw = ImageDraw.Draw(image)
            #Stats
            if len(self.results) == 0:
                font = ImageFont.truetype(TERMINAL_FONT, size=120)
                noData = "- NO DATA FOUND -"
                draw.text((325,800), noData, font=font, fill = BIOS_GREEN)
            else:
                x = 980
                y = 730
                index = 1

                font = ImageFont.truetype(TERMINAL_FONT, size=45)
                if server:
                    dataHeader = "Average    Colors    Solved    Last Game"
                else:
                    dataHeader = "Weighted    Colors    Solved    Last Game"
                draw.text((x, y), dataHeader, font=font, fill = BIOS_GREEN)

                font = ImageFont.truetype(TERMINAL_FONT, size=60)
                y += 100
                for result in self.results:
                    #Draw user placement, user info and score
                    x = 975
                    image = await ImageGenHelper.drawLeaderboardUser(y, index+(5*(page - 1)), image, result[0], self.ctx)
                    average = result[6]
                    draw.text((x, y), str(average), font=font, fill = BIOS_GREEN)

                    #Visualized colors
                    x += 240
                    green = int(result[3])
                    yellow = int(result[4])
                    red = int(result[5])
                    maxMoves = max(green, yellow, red)
                    green = int(80 - (80 * (green / maxMoves)))
                    yellow = int(80 - (80 * (yellow / maxMoves)))
                    red = int(80 - (80 * (red / maxMoves)))
                    statY = y - 20

                    draw.rectangle([(x, statY + green), (x + 20, statY + 80)], fill = BIOS_GREEN)
                    draw.rectangle([(x + 21, statY + yellow), (x + 40, statY + 80)], fill = (255, 234, 0))
                    draw.rectangle([(x + 41, statY + red), (x + 60, statY + 80)], fill = (255, 0, 30))
                    #Remaining Data
                    x += 185
                    solved = result[7]
                    draw.text((x, y), str(solved), font=font, fill = BIOS_GREEN)

                    x += 120
                    date = self.formatDate(result[9])
                    draw.text((x, y), date, font=font, fill = BIOS_GREEN)
                    #Increment
                    y += 170
                    index += 1
            #Send picture to ctx channel
            statImgName = '../tmp/' + str(self.ctx.guild.id) + '_wordleServerStat.png'
            image.save(statImgName)
            await self.ctx.channel.send(file=discord.File(statImgName))
            os.remove(statImgName)
            return True
        except Exception as e:
            msg = 'WordleServerStat failed to generate image'
            Utils.logError(msg, PROGRAM_NAME, str(e))
            return False

    def getGuildMembers(self):
        memberStr = ''
        for member in self.ctx.guild.members:
            memberStr += '' + str(member.id) + ','
        return memberStr[0:len(memberStr) - 1]
    
    def formatDate(self, rawDate):
        rawDate = str(rawDate)
        newDate = rawDate[4:6] + "/" + rawDate[6:8] + "/" + rawDate[0:4]
        return newDate

    def formatTime(self, rawTime):
            timeStr = ''
            if len(rawTime) < 5:
                charCount = 4 - len(rawTime)
                zeroStr = ''
                for x in range(charCount):
                    zeroStr += '0'
                rawTime = zeroStr + rawTime
                timeStr = '12:' + rawTime[0:2] + ':' + rawTime[2:4] + ' AM'
            elif len(rawTime) == 5:
                timeStr = '0' + rawTime[0] + ':' + rawTime[1:3] + ':' + rawTime[3:5] + ' AM'
            else:
                hours = int(rawTime[0:2])
                if hours > 12:
                    hours -= 12
                    timeStr = str(hours) + ':' + rawTime[2:4] + ':' + rawTime[4:6] + ' PM'
                elif hours <= 12:
                    timeStr = str(hours) + ':' + rawTime[2:4] + ':' + rawTime[4:6] + ' AM'
                else:
                    msg = "Error in formatTime - Bad string passed."
                    Utils.logError(msg, PROGRAM_NAME, 'None')
            return timeStr 

    def getMonthData(self, month, userId):
        query = "SELECT COUNT(WORDLE_NUM), SUM(NUM_MOVES) FROM T_WORDLE_GAMES WHERE user_id = " + str(userId) + " AND DTE_GAME LIKE '" + month + "%'"
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            msg = "Error in wordleUserStat executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            exit(1)
        stats = res.fetchone()
        if str(stats[0]) == '0':
            stats = -1
        return stats

