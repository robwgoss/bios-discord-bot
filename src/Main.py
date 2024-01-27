import discord
from discord.ext import commands
from Messages import RouteMessage
from configparser import ConfigParser
from Roll import Roll
from Wordle import Wordle


#=====================================================================
#=                         Initialization                            =
#=====================================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix = "~", intents=intents)
config = ConfigParser()
config.read('../config/bot.cfg')


#=====================================================================
#=                          Commands                                 =
#=====================================================================
@bot.command(
    name='wordle',
    description='Wordle stats for a given user',
    pass_context=True,
)
async def wordle(ctx, *args):
    ws = Wordle()
    response = await ws.processArgs(args, ctx)


@bot.command(
    name='roll',
    description='Roll a dice!',
    pass_context=True,
)    
async def rollTwenty(ctx, *args):
    r = Roll(ctx)
    results = r.setRollCfg(args)
    if results == 0:
        await r.roll()
    elif results == 2:
        msg = "Here are examples on how to use this command\n`~roll` *A 1d20 roll*\n`~roll 3d5`* Rolls 3 5 sided dice*\n`~roll 3 5 10` *Rolls 3 random numbers between 5 and 10*"
        await ctx.send(msg)
        return
    try:  
        if results == 1:
            msg = "Your arguments are not valid. Here are examples on how to use this command\n`~roll` *A 1d20 roll*\n`~roll 3d5` *Rolls 3 5 sided dice*\n`~roll 3 5 10` *Rolls 3 random numbers between 5 and 10*"
            await ctx.send(msg)
            return
    except:
        print("Critical error occured. Results passed - " + str(results))

#=====================================================================
#=                          Events                                   =
#=====================================================================
@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return 
    rm = RouteMessage(bot, message)
    #Change response to tuple with [0] being response code. Base response off of this code
    responseCode = rm.getResponseCode()
    if responseCode == 0:
        await message.channel.send(rm.getResponseMsg())
    elif responseCode == 1:
        await message.add_reaction(rm.getResponseMsg())
    if message.content == "test":
        await message.channel.send("response")


#=====================================================================
#=                          Entry                                    =
#=====================================================================
bot.run(config.get('discord', 'key'))