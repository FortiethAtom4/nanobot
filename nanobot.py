# bot.py
# Defines available commands and runs the bot.
import discord, logging, datetime
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor

update_tasks = ThreadPoolExecutor(1)

#local imports
import utils.db as db, config

num_updates: int = 0

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)
for cog in config.cogs:
    bot.load_extension(f"cogs.{cog}")

# updates the leaderboard regularly
# @tasks.loop(seconds=10)
# async def sort_helper():
#     config.sort_users_by_rank()

# Print statement when the bot successfully comes online.
@bot.event
async def on_ready():
    config.start_time = datetime.datetime.now()
    print(f'''Successfully logged in as {bot.user}.
Current latency: {round(bot.latency*1000,3)}ms''')
    print(f"-> {'User data loaded.' if len(db.get_all_users()) > 0 else 'Warning: no user data found.'}")
    # sort_helper.start()
    # auto_update.start()
    # print("-> Background tasks started.")


# Bot's main event loop. Gives xp to users who send messages.
@bot.event
async def on_message(message: discord.Message):

    if not message.author.bot:
        levelup = db.gain_xp(message.guild.id,message.author.id,message.author.name)

        # Nano gets a bit nervous if you mention the word "key."
        if any(x in message.content.lower() for x in config.key_words):    
            key_msg = "\U0001F5FF"
            await message.channel.send(key_msg)
        has_sent_msg = False
        for swear in config.swears:    
            if swear in message.content.lower():
                if has_sent_msg == False:
                    await message.channel.send(f"**WARNING**: {message.author.mention} just said a no-no word.")
                    has_sent_msg = True
                
                logger.warning(f"{message.author.name} said the no-no word \'{swear}\'")

        if levelup:
            user = db.get_user_by_ids(message.guild.id, message.author.id)
            await message.channel.send(f"Congratulations, <@{message.author.id}>! You are now **{user.level} Inches!**")

# run the bot
bot.run(config.TOKEN)
