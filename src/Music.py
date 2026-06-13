PROGRAM_NAME = "Music.py"

##########################################################
#                                                        #
#   Program          Music.py                            #
#                                                        #
#   Description      Module for the music related        #
#                    commands                            #
#                                                        #
##########################################################

import ffmpeg, discord
class Music():
    def __init__(self, args, ctx):
        self.ctx = ctx
        self.args = args

    async def play(self):
        if not self.ctx.author.voice:
            await self.ctx.send("You need to be in a voice channel")
            return

        voiceChannel = self.ctx.author.voice.channel
        connection = await voiceChannel.connect()
        source = discord.FFmpegPCMAudio(
            "/home/bot/test/data/test.mp3",
            executable="ffmpeg",
            options="-vn"
        )
        connection.play(source)
        await self.ctx.send("🎵 Can't put down the cup! 🎵")