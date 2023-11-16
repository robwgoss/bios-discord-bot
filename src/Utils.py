import sqlite3

def ConnectDB(env):
    try:
        connectStr = "/home/bot/data/bot" + env + ".db"
        return sqlite3.connect(connectStr)
    except:
        print("FAILURE")
        return False

# def logError(msg, ):
