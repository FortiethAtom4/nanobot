import os, dotenv

#local imports
from utils.timer import Timer
from utils.user import User
from utils.server import Server
import logging, logging.handlers

########## ADD YOUR COG FILE NAME TO THIS LIST ##########
cogs: list[str] = [
    "levels",
    "admin"
]
#########################################################

# set when bot is started up
start_time = 0

#for keeping track of update timings
update_timer = Timer()
update_interval: int = 10 #time in minutes between updates

#list of users, pulled from DB at bot start, sorted by total XP descending
servers: list[Server] = []
users: list[User] = []
user_names: list[str] = []

def sort_users_by_rank():
    users.sort(key = lambda x: x.xp_total, reverse=True)


#log formatting
log_formatter = '%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s'
formatter = logging.Formatter(log_formatter)
log_handler = logging.handlers.RotatingFileHandler("bot.log",maxBytes=1000000)
log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# private variables from the .env
dotenv.load_dotenv(dotenv.find_dotenv(".env"))
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_IDS: list[int] = [int(x) for x in (os.getenv('GUILD_IDS')).split(",")] #allows multiple guild IDs separated by comma
USER = os.getenv("MONGODB_USER")
PASS = os.getenv("MONGODB_PASS")
DB_NAME = os.getenv("DB_NAME")
COLLECTION = os.getenv("DB_COLLECTION")
db_URL = f"mongodb+srv://{USER}:{PASS}@nanobot.lab1zmc.mongodb.net/"

swears = []
with open('swears.txt') as swearfile:
    swears = swearfile.read().splitlines()

HF_TOKEN = os.getenv("HF_TOKEN")

# chance of bot replying to a message
maxbot_chance = 5