import discord
from discord.ext import commands
from Messages import RouteMessage
from configparser import ConfigParser


#=====================================================================
#=                         Initialization                            =
#=====================================================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = "~", intents=intents)
config = ConfigParser()
config.read('../config/bot.cfg')


#=====================================================================
#=                          Commands                                 =
#=====================================================================
@bot.command(
    name='wordleStats',
    description='Wordle stats for a given user',
    pass_context=True,
)
async def wordleStats(ctx, *args):
    await ctx.send("Success")
    

#=====================================================================
#=                          Events                                   =
#=====================================================================
@bot.listen()
async def on_message(message):
    if message.author == bot.user:
            return 
    rm = RouteMessage(bot, message)
    response = rm.getResponse()
    if response != "NULL":
        await message.channel.send(response)
    
    if message.content == "test":
         await message.channel.send("response")


#=====================================================================
#=                          Entry                                    =
#=====================================================================
bot.run(config.get('discord', 'key'))
