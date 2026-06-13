PROGRAM_NAME = "Music.py"

##########################################################
#                                                        #
#   Program          Music.py                            #
#                                                        #
#   Description      Module for the music related        #
#                    commands                            #
#                                                        #
##########################################################

import ffmpeg, discord, yt_dlp, re
class Music():
    def __init__(self, args, ctx):
        self.ctx = ctx
        self.args = args

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
                msg = "Failed to play " + songName
                await self.ctx.send(msg)
                return
        else:
            ytUrl = self.checkValidUrl(songName)
            print(ytUrl)
            if ytUrl is None:
                msg = "Invalid URL, please use a valid YouTube url. Example:\n`~play https://www.youtube.com/watch?v=6hzrDeceEKc`"
                await self.ctx.send(msg)
                return

        print(ytUrl)
        musicFile = self.ytDownload(ytUrl)
        print(musicFile)
        played = await self.playMusic(musicFile)
        if not played:
            msg = "Failed to play song"
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
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return f"../data/ytCache/{info['id']}.mp3"