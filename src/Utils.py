PROGRAM_NAME = "Utils.py"

##########################################################
#                                                        #
#   Program          Utils.py                            #
#                                                        #
#   Description      Server utilities and general use    #
#                    functions for the bot.              #
##########################################################

import sqlite3
from configparser import ConfigParser

def ConnectDB():
    try:
        config = ConfigParser()
        config.read('../config/bot.cfg')
        connectStr = config.get('discord', 'DB_PATH')
        return sqlite3.connect(connectStr)
    except Exception as e:
        msg = "Failed to connect to database"
        logError(msg, PROGRAM_NAME, str(e))
        return False

def logError(msg, program_name, exception):
    msg = "Error in " + program_name + " - " + msg
    msg += '\n------------------------------------\n'
    msg += 'Exception\n==========\n' + exception
    print(msg)

def cleanMember(author):
    return author.replace("\'", "\'\'")