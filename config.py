import os, dotenv, sys

#local imports
from utils.models import User
from utils.server import Server #one day
import logging, logging.handlers

########## ADD YOUR COG FILE NAME TO THIS LIST ##########
cogs: list[str] = [
    "levels",
    "admin",
    "timers"
]
#########################################################

# set when bot is started up
start_time = 0

def sort_users_by_rank(users: list[User]):
    users.sort(key = lambda x: x.xp_total, reverse=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#log formatting
log_formatter = '%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s'
formatter = logging.Formatter(log_formatter)

# log to file
log_handler = logging.handlers.RotatingFileHandler("bot.log",maxBytes=1000000)
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

# log to console
console_log_handler = logging.StreamHandler(sys.stdout)
console_log_handler.setFormatter(formatter)
logger.addHandler(console_log_handler)

# private variables from the .env
dotenv.load_dotenv(dotenv.find_dotenv(".env"))
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_IDS: list[int] = [int(x) for x in (os.getenv('GUILD_IDS')).split(",")] #allows multiple guild IDs separated by comma

swears = []
with open('swears.txt') as swearfile:
    swears = swearfile.read().splitlines()

key_words = ["key", "きー", "キー","ねじ","ネジ","螺子"]