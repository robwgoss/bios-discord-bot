import discord
from discord.ext import commands
from Messages import RouteMessage
from configparser import ConfigParser
from Roll import Roll


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

@bot.command(
    name='roll',
    description='Roll a dice!',
    pass_context=True,
)    
async def rollTwenty(ctx, *args):
    r = Roll(args)
    results = r.roll()
    try:  
        if results == -1:
            msg = "Your arguments are not valid. Here are examples on how to use this command\n\`~roll` - A 1d20 roll.\n`~roll 3d5 - Rolls 3 5 sided dice\n~roll 5 10 3 - Rolls 3 random numbers between 5 and 10"
            await ctx.send(msg)
    except:
        print("Critical error occured. Results passed - " + str(results))
    index = 0
    for r in results:
        if(len(results) == 1):
            msg = "Your roll was " + str(r) + "!"
            await ctx.send(msg)
        elif(len(results) > 1):
            msg = "Results of roll number " + str(index) + ":    " + str(r)
            await ctx.send(msg)
        else:
            await ctx.send("The bot critically missed rolling! How did that happen?")
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
