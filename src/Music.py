PROGRAM_NAME = "Music.py" 

##########################################################
#                                                        #
#   Program          Music.py                            #
#                                                        #
#   Description      Module for the music related        #
#                    commands                            #
#                                                        #
##########################################################

import discord, yt_dlp, re, Utils, asyncio, os
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
            res = await self.insertQueue(ytUrl)
            if not res:
                msg = "Failed to add song to queue"
                await self.ctx.send(msg)
                return
            musicFile = await asyncio.get_event_loop().run_in_executor(None, self.ytDownload, ytUrl)
            if musicFile is None:
                msg = "Failed to pre-cache queued song"
                await self.ctx.send(msg)
            return
     
        queueEmpty = False
        inQueue = False
        while queueEmpty is False:
            if inQueue:
                res = self.deleteQueue(queueId)
                if not res:
                    msg = "Failed to remove song from queue"
                    await self.ctx.send(msg)
                    return

            musicFile = await asyncio.get_event_loop().run_in_executor(None, self.ytDownload, ytUrl)
            if musicFile is None:
                msg = "Song retrieval failed. Please try again later"
                await self.ctx.send(msg)

            played = await self.playMusic(musicFile)
            if not played:
                msg = "Failed to play song"
                await self.ctx.send(msg)


            queueCount = self.checkQueue()

            if queueCount == 0:
                await self.goodbyeBot()
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
                inQueue = True
        await self.goodbyeBot()
        return

    async def showQueue(self):
        guildId = self.ctx.guild.id
        query = 'SELECT URL FROM T_QUEUE WHERE GUILD_ID = ? ORDER BY ROWID ASC LIMIT 5'
        result = self.cursor.execute(query, (guildId,)).fetchall()
        if not result:
            msg = "There are no songs in the queue"
            await self.ctx.send(msg)
            return
        queueCount = self.checkQueue()
        count = 1
        msg = f"There are currently **{queueCount}** songs in queue. Upcoming:\n`"
        for res in result:
            self.setYtInfo(res[0])
            minutes = self.songDuration // 60
            seconds = self.songDuration % 60
            msg += f"{count}. {self.songTitle} | {self.songChannel} | {minutes}:{seconds:02d}\n"
            count += 1
        msg += '`'
        await self.ctx.send(msg)
        return

    async def skipSong(self):
        if not self.ctx.voice_client or not self.ctx.voice_client.is_playing():
            await self.ctx.send("No song is playing")
            return
        self.ctx.voice_client.stop()
        await self.ctx.send("Skipped the current song")
        return

    async def stopMusic(self):
        if not self.ctx.voice_client:
            await self.ctx.send("Not currently in a voice channel")
            return
        guildId = self.ctx.guild.id
        query = 'DELETE FROM T_QUEUE WHERE GUILD_ID = ?'
        self.cursor.execute(query, (guildId,))
        self.con.commit()
        await self.goodbyeBot()
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
            cleanUrl = re.search(r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+)", url)
            if cleanUrl:
                return cleanUrl.group(1)
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
            await self.nowPlayingMsg()
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
            'no_warnings': True,
            'outtmpl': '../data/ytCache/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.songTitle = info['title']
                self.songChannel = info['uploader']
                self.songDuration = info['duration']
                cachedFile = f"../data/ytCache/{info['id']}.mp3"
                if not os.path.exists(cachedFile):
                    ydl.download([url])
                return cachedFile
        except Exception as e:
            return None

    def setYtInfo(self, url):
        opts = {'quiet': True, 'no_warnings': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.songTitle = info['title']
                self.songChannel = info['uploader']
                self.songDuration = info['duration']
        except Exception as e:
            return None
        
    async def nowPlayingMsg(self):
        try:
            minutes = self.songDuration // 60
            seconds = self.songDuration % 60
            msg = f"**Now playing:**\n`>{self.songTitle}\n>{self.songChannel} | {minutes}:{seconds:02d}`"
            await self.ctx.send(msg)
        except Exception as e:
            await self.ctx.send("Failed to retrieve song info")
    
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
        return count

    async def insertQueue(self, url):
        guildId = self.ctx.guild.id
        self.setTime()
        self.setYtInfo(url)

        query = "INSERT INTO T_QUEUE (GUILD_ID, URL, DTE_ADDED, TIME_ADDED) VALUES(?,?,?,?)"
        try:
            self.cursor.execute(query, (guildId, url, self.day, self.time))
        except Exception as e:
            msg = "Error in insertQueue executing:\n" + query
            Utils.logError(msg, PROGRAM_NAME, str(e))
            return False

        self.con.commit()

        minutes = self.songDuration // 60
        seconds = self.songDuration % 60
        count = self.checkQueue()
        msg = f"**Added in queue to position {count}:**\n`>{self.songTitle}\n>{self.songChannel} | {minutes}:{seconds:02d}`"
        await self.ctx.send(msg)
    
        return True
    
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
            return False
        self.con.commit()
        return True

    async def goodbyeBot(self):
        if not self.ctx.voice_client:
            return
        await self.ctx.voice_client.disconnect()
        msg = 'Bye bye! ._.'
        await self.ctx.send(msg)
        return
