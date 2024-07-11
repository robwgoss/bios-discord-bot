# BIOS DISCORD BOT
A multipurpose Discord bot that supports features like:
- Command free Wordle score tracking, leaderboards, and data visualization
- DND style dice rolling and coin flips with stat tracking
## WORDLE
The bot reads each message that comes into a channel that it is in, and will detect if a Wordle result was posted like:

Wordle 1,118 3/6

⬛⬛⬛🟨🟨</br>
🟨🟨🟨⬛⬛</br>
🟩🟩🟩🟩🟩

The bot will then store the invidual score for the user, along with calclulating their lifetime stats and tracking each "color". If the Wordle is tampered with and not a pure copy-paste, the Worlde result is rejected.

### COMMAND EXAMPLES
`~wordle server` Generates a visual server leaderboard for all time stats on the channel this command was ran in </br>
`~wordle weighted` This is the same as above, however its weighted on the user with the highest number of games to eliminate low sample sizes taking over the average leaderboard </br>
`~wordle 951`  Generates a visual server leaderboard for a specific Wordle number on the channel this command was ran in
## ROLL/FLIP
Commands to play odds
### COMMANDS EXAMPLES
`~flip` Flips a coin and tracks total heads/tails</br>
`~roll` Rolls a 1d20 dice</br>
`~roll 3d5` Rolls a 3d5 dice</br>

## Running locally
To run locally, a config file is needed with the following format: </br>
[discord]
key = PLACE-DISCORD-API-KEY-HERE
DB_PATH = PATH-TO-DB

On the DB_PATH, an sqlite3 DB is needed for the following tables:</br>

`T_WORDLE_GLOBAL_STAT (USER_ID INTEGER PRIMARY KEY, TOTAL_MOVES INTEGER, TOTAL_GAMES INTEGER, TOTAL_GREEN INTEGER, TOTAL_YELLOW INTEGER, TOTAL_MISS INTEGER, AVERAGE REAL, TOTAL_SOLVED INTEGER, WIN_RATE REAL, DTE_LAST_GAME INTEGER)`</br></br>
`T_WORDLE_GAMES (USER_ID INTEGER, WORDLE_NUM INTEGER, NUM_MOVES INTEGER, TOTAL_GREEN INTEGER, TOTAL_YELLOW INTEGER, TOTAL_MISS INTEGEER, SOLVED INTEGER, DTE_GAME INTEGER, TIME_GAME INTEGER)`</br></br>
`T_WORDLE_MOVES (USER_ID INTEGER, WORDLE_NUM INTEGER, MOVE_NUM INTEGER, RAW_MOVE INTEGER, NUM_GREEN INTEGER, NUM_YELLOW INTEGER, NUM_MISS INTEGER, SOLVED INTEGER)`</br></br>
`T_FLIP (USER_ID INTEGER PRIMARY KEY, HEADS INTEGER, TAILS INTEGER, DTE_LAST_FLIP INTEGER)`
