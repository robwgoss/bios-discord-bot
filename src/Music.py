PROGRAM_NAME = "Music.py"

##########################################################
#                                                        #
#   Program          Music.py                            #
#                                                        #
#   Description      Module for the music related        #
#                    commands                            #
#                                                        #
##########################################################

import discord, yt_dlp, re, Utils, asyncio
from datetime import datetime, date
class Music():
    def __init__(self, args, ctx):
        self.ctx = ctx
        self.args = args
        self.con = Utils.ConnectDB()
        self.cursor = self.con.cursor()

    async def play(self, youtube):
        if not self.ctx.author.voice:
            await self.ctx.send("You need to be in a voice channel")
            return

        if len(self.args) == 0:
            msg = "Here are examples on how to use this command\n`~play Wonderwall`\n`~play https://www.youtube.com/watch?v=6hzrDeceEKc`"
            await self.ctx.send(msg)
            return
        
        songName = " ".join(self.args)

        isUrl = self.checkYtUrl(songName)

        if not isUrl:
            ytUrl = self.ytSearch(youtube, songName)
            if ytUrl is None:
                msg = "Failed to queue " + songName
                await self.ctx.send(msg)
                return
        else:
            ytUrl = self.checkValidUrl(songName)
            if ytUrl is None:
                msg = "Invalid URL, please use a valid YouTube url. Example:\n`~play https://www.youtube.com/watch?v=6hzrDeceEKc`"
                await self.ctx.send(msg)
                return

        if self.ctx.voice_client and self.ctx.voice_client.is_playing():
            self.insertQueue(ytUrl)
            return
     
        queueEmpty = False
        inQueue = False
        while queueEmpty is False:
            musicFile = await asyncio.get_event_loop().run_in_executor(None, self.ytDownload, ytUrl)
            if musicFile is None:
                msg = "Song retrieval failed. Please try again later"
                self.ctx.send(msg)

            played = await self.playMusic(musicFile)
            if not played:
                msg = "Failed to play song"
                await self.ctx.send(msg)
                return

            queueEmpty = self.checkQueue()
            if inQueue:
                res = self.deleteQueue(queueId)
                if res is None:
                    msg = "Failed to remove song from queue"
                    await self.ctx.send(msg)
                    return
            if queueEmpty:
                return
            else:
                queueId = self.getQueueId()
                if queueId is None:
                    msg = "Failed to retrieve song from queue"
                    await self.ctx.send(msg)
                    return
                ytUrl = self.getQueueUrl(queueId)
                if ytUrl is None:
                    msg = "Failed to retrieve song from queue"
                    await self.ctx.send(msg)
                    return


    def checkYtUrl(self, songName):
        pattern = r"(youtube\.com|youtu\.be)"
        return bool(re.search(pattern, songName))

    def checkValidUrl(self, url):
        splitUrl = url.split()
        if len(splitUrl) > 1:
          return None
        pattern = r"(youtube\.com/watch\?v=|youtu\.be/)[\w-]+"
        if re.search(pattern, url):
            return url
        return None     

    def ytSearch(self, youtube, songName):
        try:
            song = youtube.search().list(
                q=songName,
                part="id, snippet",
                type="video",
                maxResults=10
            )
            result = song.execute()

            ytUrl = ""
            for item in result.get("items", []):
                ytVidId = item["id"]["videoId"]
                videoData = youtube.videos().list(
                    part="contentDetails",
                    id=ytVidId
                ).execute()
                contentRating = videoData["items"][0]["contentDetails"].get("contentRating", {})
                if not contentRating.get("ytRating") == "ytAgeRestricted":
                    ytUrl = f"https://www.youtube.com/watch?v={ytVidId}"
                    return ytUrl
            return None
        except Exception as e:
            print(e)
            return None
    
    async def playMusic(self, songPath):
        try:
            voiceChannel = self.ctx.author.voice.channel
            if self.ctx.voice_client:
                await self.ctx.voice_client.move_to(voiceChannel)
                connection = self.ctx.voice_client
            else:
                connection = await voiceChannel.connect()
            source = discord.FFmpegPCMAudio(
                songPath,
                executable="ffmpeg",
                options="-vn"
            )
            connection.play(source)
            while connection.is_playing():
                await asyncio.sleep(1)
            return True
        except Exception as e:
            return False

    def ytDownload(self, url):
        opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'outtmpl': '../data/ytCache/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return f"../data/ytCache/{info['id']}.mp3"
        except Exception as e:
            return None
    
    def checkQueue(self):
        guildId = self.ctx.guild.id
        query = 'SELECT COUNT(*) FROM T_QUEUE WHERE GUILD_ID = ?'
        try:
            result = self.cursor.execute(query, (guildId,)).fetchone()
        except Exception as e:
            msg = "Error in checkQueue executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            return
        count = result[0]
        return count == 0

    def insertQueue(self, url):
        guildId = self.ctx.guild.id
        self.setTime()
        
        query = """
                  INSERT INTO T_QUEUE VALUES(%s,%s,%s,%s)
                """ % (guildId, url, self.day, self.time)
        try:
            self.cursor.execute(query)
        except Exception as e:
            msg = "Error in insertQueue executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            return
        self.con.commit()
    
    def setTime(self):
        today = date.today()
        now = datetime.now()

        self.day = str(today.strftime("%Y%m%d"))
        self.time = str(now.strftime("%H%M%S"))

    def getQueueId(self):
        guildId = self.ctx.guild.id
        query = 'SELECT ID FROM T_QUEUE WHERE GUILD_ID = ? ORDER BY ROWID ASC LIMIT 1'
        result = self.cursor.execute(query, (guildId,)).fetchone()
        if result:
            return result[0]
        return None

    def getQueueUrl(self, queueId):
        query = 'SELECT URL FROM T_QUEUE WHERE ID = ?'
        result = self.cursor.execute(query, (queueId,)).fetchone()
        if result:
            return result[0]
        return None
    
    def deleteQueue(self, queueId):
        query = 'DELETE FROM T_QUEUE WHERE ID = ?'
        try:
            self.cursor.execute(query, (queueId,))
        except Exception as e:
            msg = "Error in deleteQueue executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            return
        self.con.commit()

        