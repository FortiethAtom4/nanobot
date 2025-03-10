# bot.py
# Defines available commands and runs the bot.
import discord, os, logging, datetime
from discord.ext import commands
from dotenv import load_dotenv
from asyncio import sleep

#local imports
import utils.db as db, config
from utils.user import User

logger = logging.getLogger(__name__)
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO, format=config.log_formatter)

load_dotenv()
intents = discord.Intents.all() #TODO: definitely doesn't need everything. Reduce later.
bot = commands.Bot(intents=intents)
for cog in config.cogs:
    bot.load_extension(f"cogs.{cog}")


# MISC COMMANDS
# This section is a collection of miscellaneous commands or events NanoBot watches.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# /add
# adds two numbers together. A test function.
@bot.slash_command(
    name="add",
    guild_ids=config.GUILD_IDS
)
async def add(ctx,first: int, second: int):
    await ctx.respond(f"the sum of {first} and {second} is {first + second}.")

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




# ADMIN COMMANDS
# This section contains technical commands/events restricted to the bot owner and/or bot admins.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Print statement when the bot successfully comes online.
@bot.event
async def on_ready():
    print(f'''Successfully logged in as {bot.user}.
Current latency: {round(bot.latency*1000,3)}ms''')
    db.get_users()
    print(f"-> {"User data loaded." if len(config.users) > 0 else "Warning: no user data found."}")

# /checkup
# gives some tech info about NanoBot. 
@bot.slash_command(
    name="checkup",
    guild_ids=config.GUILD_IDS,
    description="Gives technical information about the bot. Owner-only."
)
@commands.is_owner()
async def checkup(ctx): 
    resp = db.test_connection()
    await ctx.respond(f'''```Hello, {ctx.user.name}! Thanks for checking on me.
Current latency: {round(bot.latency*1000,3)}ms
Database status: {"Not connected" if resp == -1 else "Connected"}```''')


@bot.slash_command(
    name="forceupdate",
    guild_ids=config.GUILD_IDS,
    description="Forces the bot to sync its data with the database. Owner-only."
)
@commands.is_owner()
async def force_update(ctx: discord.ApplicationContext):
    msg = await ctx.respond("Updating database...")
    updates_successful = db.persist_updates()
    if not updates_successful:
        await msg.edit(content="Update failure, please check DB connection")
        logger.warning("/forcepersist update failure")
        return
    await msg.edit(content="Updated successfully.")
    logger.info("DB force-updated by owner")
    
    

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
