PROGRAM_NAME = "Music.py"

##########################################################
#                                                        #
#   Program          Music.py                            #
#                                                        #
#   Description      Module for the music related        #
#                    commands                            #
#                                                        #
##########################################################

import ffmpeg, discord, yt_dlp
class Music():
    def __init__(self, args, ctx):
        self.ctx = ctx
        self.args = args

    async def play(self, youtube):
        if not self.ctx.author.voice:
            await self.ctx.send("You need to be in a voice channel")
            return

        if len(self.args) == 0:
            msg = "Here are examples on how to use this command\n`~play Wonderwall`\n~play https://www.youtube.com/watch?v=6hzrDeceEKc"
            await self.ctx.send(msg)
            return
        
        songName = " ".join(self.args)

        ytUrl = self.ytSearch(youtube, songName)
        print(ytUrl)
        musicFile = self.ytDownload(ytUrl)
        print(musicFile)
        await self.playMusic(musicFile)

        

    def ytSearch(self, youtube, songName):
        try:
            song = youtube.search().list(
                q=songName,
                part="id, snippet",
                type="video",
                maxResults=1
            )
            result = song.execute()

            for item in result.get("items", []):
                ytVidId = item["id"]["videoId"]
                ytUrl = f"https://www.youtube.com/watch?v={ytVidId}"
                return ytUrl
        except Exception as e:
            print(f"YouTube search failed: {e}")
            return None
    
    async def playMusic(self, songPath):
        voiceChannel = self.ctx.author.voice.channel
        connection = await voiceChannel.connect()
        source = discord.FFmpegPCMAudio(
            songPath,
            executable="ffmpeg",
            options="-vn"
        )
        
        connection.play(source)
        await self.ctx.send("🎵 Can't put down the cup! 🎵")

    def ytDownload(self, url):
        opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'outtmpl': '../data/ytCache/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return f"../data/ytCache/{info['title']}.mp3"