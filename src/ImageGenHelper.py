PROGRAM_NAME = 'ImageGenHelper.py'

##########################################################
#                                                        #
#   Program          ImageGenHelper.py                   #
#                                                        #
#   Description      Helper program housing functions    #
#                    that generate generic image         #   
#                    components.                         #
#                                                        #
##########################################################

import Utils, discord, io, Utils
from PIL import Image, ImageDraw, ImageFont

async def generateGenericServerHeader(header, height, ctx):
    try:
        picWidth = 1500
        image = Image.new(mode="RGBA", size=(picWidth, height), color = (0, 0, 0))
        draw = ImageDraw.Draw(image)
        #Header
        font = ImageFont.truetype("../assets/terminalFont.ttf", size=120)
        draw.text((145,100), header, font=font, fill = (32, 194, 14))
        #Server Text
        font = ImageFont.truetype("../assets/terminalFont.ttf", size=80)
        guildName = ctx.guild.name
        if len(guildName) > 20:
            guildName = guildName[0:20]
        guildLine = "\nServer Leaderboard\n------------------\n" + guildName + "\n------------------"
        guildLine += "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        draw.text((150,300), guildLine, font=font, fill = (32, 194, 14))
        #Server Image - Note check if no image
        imageBytes = await ctx.guild.icon.read()
        guildIcon = Image.open(io.BytesIO(imageBytes))
        guildIcon = guildIcon.resize((260,260))
        x = 1030
        y = 310
        draw.rectangle([(x, y), (x + 300, y + 300)], fill = (32, 194, 14))
        image.paste(guildIcon, (x + 20, y + 20))
        return image
    except:
        msg = "Error generating generic server header"
        Utils.logError(msg, PROGRAM_NAME)

async def drawLeaderboardUser(y, count, image, userId, ctx):
    try:
        x = 50
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("../assets/terminalFont.ttf", size=60)
        place = str(count) + '.'
        draw.text((x, y), place, font=font, fill = (32, 194, 14))
        member = await ctx.guild.fetch_member(int(userId))
        imageBytes = await member.avatar.read()
        authorAvatar = Image.open(io.BytesIO(imageBytes))
        authorAvatar = authorAvatar.resize((80,80))
        print("Place: " + str(place))
        draw.rectangle([(x + 110, y - 25), (x + 220, y + 85)], fill = getPlaceColorRgb(count))
        image.paste(authorAvatar, (x + 125, y - 10))
        name = member.display_name
        if len(name) >= 25:
            name = name[0:24]
            name += '-'
        while len(name) < 25 :
            name += ' '
        name = name 
        draw.text((x + 280, y), name, font=font, fill = (32, 194, 14))
        return image
    except:
        msg = "Error generating user leaderboard"
        Utils.logError(msg, PROGRAM_NAME)

def getPlaceColorRgb(place):
    if place == 1:
        color = (239, 169, 0)
    elif place == 2:
        color = (167, 167, 173)
    elif place == 3:
        color = (130, 74, 2)
    else:
        color = (32, 194, 14)
    return color