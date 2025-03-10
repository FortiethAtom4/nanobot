# bot.py
# Defines available commands and runs the bot.
import discord, logging, datetime
from discord.ext import commands
from dotenv import load_dotenv
from asyncio import sleep

#local imports
import utils.db as db, config

logger = logging.getLogger(__name__)
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO, format=config.log_formatter)

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)
for cog in config.cogs:
    bot.load_extension(f"cogs.{cog}")

# Bot's main event loop. Gives xp to users who send messages.
@bot.event
async def on_message(message: discord.Message):

    if not message.author.bot:
        if message.author.name not in config.user_names:
            db.add_new_user(message.author.name)
        
        user = next((user for user in config.users if user.name == message.author.name))
        levelup = user.gain_xp()
        config.sort_users_by_rank()

        # Nano gets a bit nervous if you mention the word "key."
        if "key" in message.content.lower():
            await message.channel.send("\U0001F5FF")

        if levelup:
            await message.channel.send(f"Congratulations, <@{message.author.id}>! You are now **{user.level} Inches!**")

# Print statement when the bot successfully comes online.
@bot.event
async def on_ready():
    print(f'''Successfully logged in as {bot.user}.
Current latency: {round(bot.latency*1000,3)}ms''')
    db.get_users()
    print(f"-> {"User data loaded." if len(config.users) > 0 else "Warning: no user data found."}")

# updates the database automatically at regular intervals
async def auto_update():
    config.update_timer.start(datetime.timedelta(minutes=config.update_interval))
    while True:
        if config.update_timer.increment():
            db.persist_updates()
            logger.info("DB auto-update completed")
            config.update_timer.start(datetime.timedelta(minutes=config.update_interval))
        await sleep(1)

bot.loop.create_task(auto_update())
# run the bot
bot.run(config.TOKEN)
