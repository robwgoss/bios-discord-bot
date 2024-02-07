PROGRAM_NAME = "Utils.py"

##########################################################
#                                                        #
#   Program          Utils.py                            #
#                                                        #
#   Description      Server utilities and general use    #
#                    functions for the bot.              #
##########################################################

import sqlite3

def ConnectDB(env):
    try:
        connectStr = "../data/bot" + env + ".db"
        con = sqlite3.connect(connectStr)
        return con.cursor()
    except:
        print("FAILURE")
        return False

def logError(msg, program_name, exception):
    msg = "Error in " + program_name + " - " + msg
    msg += '\n------------------------------------\n'
    msg += 'Exception\n==========\n' + exception
    print(msg)

def cleanMember(author):
    return author.replace("\'", "\'\'")