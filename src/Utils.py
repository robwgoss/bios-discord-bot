import sqlite3

def ConnectDB(env):
    try:
        connectStr = "../data/bot" + env + ".db"
        con = sqlite3.connect(connectStr)
        return con.cursor()
    except:
        print("FAILURE")
        return False

def logError(msg, program_name):
    msg = "Error in " + program_name + " - " + msg
    print(msg)

def cleanMember(author):
    return author.replace("\'", "\'\'")