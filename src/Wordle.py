import re, sqlite3
class WordleData():
    def __init__(self, msg):
        self.message = msg
        self.content = msg.content
        self.splitArr = self.content.splitlines()
        self.con = sqlite3.connect("/home/bot/data/botProd.db")
        self.cursor = self.con.cursor()

    def checkUnsolved(self):
        query = 'SELECT solved FROM t_wordle_games where user_id = \'' + str(self.message.author) + '\' AND wordle_num = ' + str(self.getWordleNum())
        res = self.cursor.execute(query)
        return len(res.fetchall()) == 0

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

    def insertWordleData(self):
        total_green = 0
        total_yellow = 0
        total_miss = 0
        count = 0
        for line in self.splitArr:
            if(count > 1):
                green = 0
                yellow = 0
                miss = 0
                solved = 0
                for char in line:
                    if char == '🟩':
                        green += 1
                    elif char == '🟨':
                        yellow += 1
                    elif char == '⬛' or char == '⬜':
                        miss += 1
                if green == 5:
                    solved = 1
                total_green += green
                total_yellow += yellow
                total_miss += miss
                query = """
                    INSERT INTO T_WORDLE_MOVES VALUES(\'%s\',%s,%s,\'%s\',%s,%s,%s,%s,datetime('now', 'localtime'))
                """ % (str(self.message.author), self.getWordleNum(), str(count - 1), line, str(green), str(yellow), str(miss), str(solved))
                self.cursor.execute(query)
                self.con.commit()
            count += 1
        query = """
                    INSERT INTO T_WORDLE_GAMES VALUES(\'%s\',%s,%s,%s,%s,%s,%s,datetime('now', 'localtime'))
        """ % (str(self.message.author), self.getWordleNum(), str(count - 2), str(total_green), str(total_yellow), str(total_miss), str(solved))
        self.cursor.execute(query)
        self.con.commit()
        self.cursor.close()