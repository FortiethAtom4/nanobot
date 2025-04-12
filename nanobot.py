# bot.py
# Defines available commands and runs the bot.
import discord, logging, datetime
from discord.ext import commands, tasks
from asyncio import sleep

#local imports
import utils.db as db, config

logger = logging.getLogger(__name__)
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO, format=config.log_formatter)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)
for cog in config.cogs:
    bot.load_extension(f"cogs.{cog}")

# updates the leaderboard regularly
@tasks.loop(seconds=10)
async def sort_helper():
    config.sort_users_by_rank()

# updates the database automatically at regular intervals
@tasks.loop(minutes=config.update_interval)
async def auto_update():
    db.persist_updates()
    logger.info("DB auto-update completed")

# Print statement when the bot successfully comes online.
@bot.event
async def on_ready():
    config.start_time = datetime.datetime.now()
    print(f'''Successfully logged in as {bot.user}.
Current latency: {round(bot.latency*1000,3)}ms''')
    db.get_users()
    print(f"-> {'User data loaded.' if len(config.users) > 0 else 'Warning: no user data found.'}")
    sort_helper.start()
    auto_update.start()
    print("-> Background tasks started.")


# Bot's main event loop. Gives xp to users who send messages.
@bot.event
async def on_message(message: discord.Message):

    if not message.author.bot:
        if message.author.name not in config.user_names:
            db.add_new_user(message.author.name)
        
        user = next((user for user in config.users if user.name == message.author.name))
        levelup = user.gain_xp()

        # Nano gets a bit nervous if you mention the word "key."
        for string in message.content.lower().split(" "):
            if string == "key":
                await message.channel.send("\U0001F5FF")

        if levelup:
            await message.channel.send(f"Congratulations, <@{message.author.id}>! You are now **{user.level} Inches!**")

# run the bot
bot.run(config.TOKEN)
