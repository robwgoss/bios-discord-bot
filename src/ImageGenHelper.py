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

import Utils, io, Utils
from PIL import Image, ImageDraw, ImageFont

BIOS_ICON = '../assets/bios_icon.png'
BIOS_FONT = "../assets/terminalFont.ttf"
BIOS_GREEN = (32, 194, 14)

async def generateGenericServerHeader(header, width, height, offset, ctx):
    try:
        x = 145 + offset
        image = Image.new(mode="RGBA", size=(width, height), color = (0, 0, 0))
        draw = ImageDraw.Draw(image)
        #Header
        font = ImageFont.truetype(BIOS_FONT, size=120)
        draw.text((x,100), header, font=font, fill = BIOS_GREEN)
        #Server Text
        font = ImageFont.truetype(BIOS_FONT, size=80)
        guildName = ctx.guild.name
        if len(guildName) > 20:
            guildName = guildName[0:20]
        guildLine = "\nServer Leaderboard\n------------------\n" + guildName + "\n------------------"
        guildLine += "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        draw.text((x + 5, 300), guildLine, font=font, fill = BIOS_GREEN)
        try:
            imageBytes = await ctx.guild.icon.read()
            guildIcon = Image.open(io.BytesIO(imageBytes))
        except:
            guildIcon = Image.open(BIOS_ICON)
        guildIcon = guildIcon.resize((260,260))
        x = 1030 + offset
        y = 310
        draw.rectangle([(x, y), (x + 300, y + 300)], fill = BIOS_GREEN)
        image.paste(guildIcon, (x + 20, y + 20))
        return image
    except Exception as e:
        msg = "Error generating generic server header"
        Utils.logError(msg, PROGRAM_NAME, str(e))

async def generateGenericUserHeader(header, width, height, offset, ctx, userId):
    try:
        x = 145 + offset
        image = Image.new(mode="RGBA", size=(width, height), color = (0, 0, 0))
        draw = ImageDraw.Draw(image)
        #Header
        font = ImageFont.truetype(BIOS_FONT, size=120)
        draw.text((x,100), header, font=font, fill = BIOS_GREEN)
        #Server Text
        font = ImageFont.truetype(BIOS_FONT, size=80)
        member = await ctx.guild.fetch_member(int(userId))
        displayName = member.display_name
        if len(displayName)  > 20:
            displayName = displayName[0:20]
            displayName += '...'    
        memberLine = "\n--------------------\n" + displayName + "\n--------------------"
        memberLine += "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        draw.text((x + 5, 150), memberLine, font=font, fill = BIOS_GREEN)
        try:
            imageBytes = await member.avatar.read()
            memberIcon = Image.open(io.BytesIO(imageBytes))
        except Exception as e:
            print(e)
            memberIcon = Image.open(BIOS_ICON)
        memberIcon = memberIcon.resize((260,260))
        x = 1030 + offset
        y = 120
        draw.rectangle([(x, y), (x + 300, y + 300)], fill = BIOS_GREEN)
        image.paste(memberIcon, (x + 20, y + 20))
        return image
    except Exception as e:
        msg = "Error generating generic server header"
        Utils.logError(msg, PROGRAM_NAME, str(e))

async def drawLeaderboardUser(y, count, image, userId, ctx):
    try:
        x = 50
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(BIOS_FONT, size=60)
        place = str(count) + '.'
        draw.text((x, y), place, font=font, fill = BIOS_GREEN)
        member = await ctx.guild.fetch_member(int(userId))
        try:
            imageBytes = await member.avatar.read()
            authorAvatar = Image.open(io.BytesIO(imageBytes))
        except:
            authorAvatar = Image.open(BIOS_ICON)
        authorAvatar = authorAvatar.resize((80,80))
        draw.rectangle([(x + 110, y - 25), (x + 220, y + 85)], fill = getPlaceColorRgb(count))
        image.paste(authorAvatar, (x + 125, y - 10))
        name = member.display_name
        if len(name) >= 25:
            name = name[0:24]
            name += '-'
        while len(name) < 25 :
            name += ' '
        name = name 
        draw.text((x + 280, y), name, font=font, fill = BIOS_GREEN)
        return image
    except Exception as e:
        msg = "Error generating user leaderboard"
        Utils.logError(msg, PROGRAM_NAME, str(e))

async def drawUserMatchHist(ctx, image, matchHist):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(BIOS_FONT, size=60)

    header = "Game History"
    draw.text((600,525), header, font=font, fill = BIOS_GREEN)

    if matchHist == -1:
        text = "No Data Found"
        draw.text((600,900), text, font=font, fill = BIOS_GREEN)
        return image

    x = 173
    px = 0
    py = 0
    heightIncrease = 50
    pNumMoves = 1000
    for game in reversed(matchHist):
        y = 975
        offset = 30
        numMoves = game[0]
        dteGame = str(game[1])
        y -= heightIncrease * numMoves
        draw.circle((x,y), 15, BIOS_GREEN, BIOS_GREEN, 0)
        if numMoves > pNumMoves:
            offset = -60
        font = ImageFont.truetype(BIOS_FONT, size=40)
        draw.text((x - 8, y + offset), str(numMoves), font=font, fill = BIOS_GREEN)
        if px != 0:
            line = [(px,py),(x,y)]
            draw.line(line, BIOS_GREEN, 8, joint=None)
        drawDate = dteGame[4:6] + '/' + dteGame[6:8]
        font = ImageFont.truetype(BIOS_FONT, size=45)
        draw.text((x - 45, 1000), drawDate, font=font, fill = BIOS_GREEN)
        px = x
        py = y
        pNumMoves = numMoves
        x += 133
    return image

async def drawUserStats(ctx, image, userStats, currMonth, prevMonth):
    if userStats == -1:
        return image

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(BIOS_FONT, size=60)
    x = 180
    y = 1100

    text = "Total Average"
    totalGames = int(userStats[0])
    totalScore = int(userStats[1])
    totalAvg = str(format(totalScore / totalGames, '.2f'))
    draw.text((x - 20, y), text, font=font, fill = BIOS_GREEN)
    draw.text((x + 75, y + 80), totalAvg, font=font, fill = BIOS_GREEN)

    x += 430
    text = "Current Month"
    if currMonth != -1:
        print('test')
        currGames = int(currMonth[0])
        currScore = int(currMonth[1])
        currAvg = str(format(currScore / currGames, '.2f'))
    else:
        currAvg = 'N/A'
    draw.text((x, y), text, font=font, fill = BIOS_GREEN)
    draw.text((x + 100, y + 80), currAvg, font=font, fill = BIOS_GREEN)

    x += 470
    text = "Previous Month"
    if prevMonth != -1:
        prevGames = int(prevMonth[0])
        prevScore = int(prevMonth[1])
        prevAvg = str(format(prevScore / prevGames, '.2f'))
    else:
        prevAvg = 'N/A'
    draw.text((x, y), text, font=font, fill = BIOS_GREEN)
    draw.text((x + 120, y + 80), prevAvg, font=font, fill = BIOS_GREEN)

    x = 180
    y += 175

    text = "Total Games"
    totalGames = str(userStats[0])
    draw.text((x, y), text, font=font, fill = BIOS_GREEN)
    draw.text((x + 100, y + 80), totalGames, font=font, fill = BIOS_GREEN)

    x += 450
    text = "Total Solved"
    totalSolved = str(userStats[2])
    draw.text((x, y), text, font=font, fill = BIOS_GREEN)
    draw.text((x + 100, y + 80), totalSolved, font=font, fill = BIOS_GREEN)

    x += 450
    text = "Percent Solved"
    totalGames = int(userStats[0])
    totalSolved = int(userStats[2])
    totalPercent = str(format((totalSolved / totalGames) * 100, '.2f')) + '%'
    draw.text((x, y), text, font=font, fill = BIOS_GREEN)
    draw.text((x + 100, y + 80), totalPercent, font=font, fill = BIOS_GREEN)

    return image

def getPlaceColorRgb(place):
    if place == 1:
        color = (239, 169, 0)
    elif place == 2:
        color = (167, 167, 173)
    elif place == 3:
        color = (130, 74, 2)
    else:
        color = BIOS_GREEN
    return color