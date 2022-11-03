# A Telegram Bot API Token, which you can get from @BotFather
TG_TOKEN = '5460406581:AAGrsAxUDwRE0aqxayWeoYSz--12GsEjFsA'

# A link pointing to the table with required data
DATA_URL = 'https://data.gov.lv/dati/dataset/6d564a05-1d8c-49b8-835f-c969c61da182/resource/92af15f3-9674-426e-925c-86c6254baa0d/download/objektusaraksts.csv'

# For now, bot uses MongoDB for finite-state machine storage
# Migration to Redis will be done soon
# But now you need to provide a password for MongoDB user
MONGO_PASSWORD = 'OE6xbZToJC9i2r9w'
# And a connection URL
MONGO_URL = f'mongodb+srv://aiogram:{MONGO_PASSWORD}@cluster0.twuumbu.mongodb.net/?retryWrites=true&w=majority'

# Bot uses SQLite to store and use retrieved data. Choose a file name for that.
# If you are not stingy in terms of RAM, you can enter :memory: below, to store it there.
# The bot will definitely be faster.
SQLITE_FILE = ':memory:'

# How many objects should the bot message to user at once?
OBJ_AT_ONCE = 3


# DO NOT EDIT BELOW UNLESS YOU ARE REALLY SURE WHAT YOU ARE DOING!
class Fields:
    ID = 0
    OBJ = 1
    NAME = 2
    ISIL = 3
    ADDRESS = 4
    LAT = 5
    LON = 6
    LKS_92_X = 7
    LKS_92_Y = 8
    CATEGORY = 9
    PHONE = 10
    EMAIL = 11
    ATVK = 12
    URL = 13
    IMG_URL = 14
