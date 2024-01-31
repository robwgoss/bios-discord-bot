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

import re, sqlite3, Utils, discord, io, os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, date

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
            return WordleStat(0, ctx)
        elif len(args) == 1:
            arg = args[0]
            if arg.lower() == 'help':
                return 2
            elif arg.lower() == 'guild':
                ws = WordleStat(1, ctx)
                return await ws.routeCommand()
            elif arg.isnumeric():
                wordleNum = int(arg)
                if wordleNum < 1 or wordleNum > 2000:
                    return 3
                else:
                    ws = WordleStat(2, ctx, wordleNum)
                    return await ws.routeCommand()
            else:
                return 3
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
    def __init__(self, commandInd, ctx, wordleNum=''):
        self.commandInd = commandInd
        self.ctx = ctx
        self.wordleNum = wordleNum
        self.con = sqlite3.connect("../data/botProd.db")
        self.cursor = self.con.cursor()

    async def routeCommand(self):
        if self.commandInd == 0:
            print("Default user stats")
        elif self.commandInd == 1:
            print("Wordle stats for users in channel")
        elif self.commandInd == 2:
            return await self.wordleNumStat()
        else:
            msg = 'WordleStat recieved bad arguments'
            Utils.logError(msg, PROGRAM_NAME)
            return 1
        return 0

    async def wordleNumStat(self):
        query = 'SELECT * FROM T_WORDLE_GAMES WHERE wordle_num = ' + str(self.wordleNum) + ' AND user_id in ( ' + self.getGuildMembers() + ') AND SOLVED = 1 ORDER BY num_moves ASC, dte_game ASC, time_game ASC LIMIT 5'
        try:
            res = self.cursor.execute(query)
        except Exception as e:
            Utils.logError(str(e), PROGRAM_NAME)
            exit(1)
        self.results = res.fetchall()
        if await self.generateWordleNumStatImg():
            return 0
        return 1

    async def generateWordleNumStatImg(self):
        try:
            picWidth = 1500
            picHeight = 1600 - (170 * (5 - len(self.results)))
            image = Image.new(mode="RGBA", size=(picWidth, picHeight), color = (0, 0, 0))
            draw = ImageDraw.Draw(image)
            #Header
            font = ImageFont.truetype("../assets/terminalFont.ttf", size=120)
            header = "> Stats for Wordle [" + str(self.wordleNum) + "]\n========================="
            draw.text((145,100), header, font=font, fill = (32, 194, 14))
            #Server Text
            font = ImageFont.truetype("../assets/terminalFont.ttf", size=80)
            guildName = self.ctx.guild.name
            if len(guildName) > 20:
                guildName = guildName[0:20]
            guildLine = "\nServer Leaderboard\n------------------\n" + guildName + "\n------------------"
            guildLine += "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            draw.text((150,300), guildLine, font=font, fill = (32, 194, 14))

            #Server Image - Note check if no image
            imageBytes = await self.ctx.guild.icon.read()
            guildIcon = Image.open(io.BytesIO(imageBytes))
            guildIcon = guildIcon.resize((260,260))
            x = 1030
            y = 310
            draw.rectangle([(x, y), (x + 300, y + 300)], fill = (32, 194, 14))
            image.paste(guildIcon, (x + 20, y + 20))
            #Stats
            if len(self.results) == 0:
                font = ImageFont.truetype("../assets/terminalFont.ttf", size=120)
                noData = "- NO DATA FOUND -"
                draw.text((325,800), noData, font=font, fill = (32, 194, 14))
            else:
                y = 775
                count = 1
                font = ImageFont.truetype("../assets/terminalFont.ttf", size=60)
                for result in self.results:
                    #Generate place, avatar, and name for user
                    x = 50
                    place = str(count) + '.'
                    draw.text((x, y), place, font=font, fill = (32, 194, 14))
                    userId = result[0]
                    member = await self.ctx.guild.fetch_member(int(userId))
                    imageBytes = await member.avatar.read()
                    authorAvatar = Image.open(io.BytesIO(imageBytes))
                    authorAvatar = authorAvatar.resize((80,80))
                    draw.rectangle([(x + 110, y - 25), (x + 220, y + 85)], fill = self.getPlaceColorRgb(count))
                    image.paste(authorAvatar, (x + 125, y - 10))
                    name = member.display_name
                    if len(name) >= 25:
                        name = name[0:24]
                        name += '-'
                    while len(name) < 25 :
                        name += ' '
                    name = name + ' ' + str(result[2]) + '/6'
                    draw.text((x + 280, y), name, font=font, fill = (32, 194, 14))
                    #Visualized stats
                    x = 1075
                    green = int(result[3])
                    yellow = int(result[4])
                    red = int(result[5])
                    maxMoves = max(green, yellow, red)
                    green = int(80 - (80 * (green / maxMoves)))
                    yellow = int(80 - (80 * (yellow / maxMoves)))
                    red = int(80 - (80 * (red / maxMoves)))
                    statY = y - 20

                    draw.rectangle([(x, statY + green), (x + 20, statY + 80)], fill = (32, 194, 14))
                    draw.rectangle([(x + 21, statY + yellow), (x + 40, statY + 80)], fill = (255, 234, 0))
                    draw.rectangle([(x + 41, statY + red), (x + 60, statY + 80)], fill = (255, 0, 30))
                    #Time
                    x += 100
                    dateRaw = str(result[7])
                    dateStr = dateRaw[0:4] + '/' + dateRaw[4:6] + '/' + dateRaw[6:8]
                    timeStr = dateStr + '\n' + self.formatTime(str(result[8]))
                    font = ImageFont.truetype("../assets/terminalFont.ttf", size=60)
                    draw.text((x, y - 30), timeStr, font=font, fill = (32, 194, 14))
                    #Increment
                    y += 170
                    count += 1
            #Send picture to ctx channel
            statImgName = '../tmp/' + str(self.ctx.guild.id) + '_wordleNumStat' + '_' + str(self.wordleNum) + '.png'
            image.save(statImgName)
            await self.ctx.channel.send(file=discord.File(statImgName))
            os.remove(statImgName)
            return True
        except:
            msg = 'WordleStat failed to generate image'
            Utils.logError(msg, PROGRAM_NAME)
            return False
        
    def getPlaceColorRgb(self, place):
        if place == 1:
            color = (239, 169, 0)
        elif place == 2:
            color = (167, 167, 173)
        elif place == 3:
            color = (130, 74, 2)
        else:
            color = (32, 194, 14)
        return color

    def getGuildMembers(self):
        memberStr = ''
        for member in self.ctx.guild.members:
            memberStr += '' + str(member.id) + ','
        return memberStr[0:len(memberStr) - 1]


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
                if hours >= 12:
                    hours -= 12
                    timeStr = str(hours) + ':' + rawTime[2:4] + ':' + rawTime[4:6] + ' PM'
                elif hours < 12:
                    timeStr = str(hours) + ':' + rawTime[2:4] + ':' + rawTime[4:6] + ' AM'
                else:
                    msg = "Error in formatTime - Bad string passed."
                    Utils.logError(msg, PROGRAM_NAME)
            return timeStr 
