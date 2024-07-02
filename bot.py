# bot.py
# Defines available commands and runs the bot.

import os
import discord
import logging
import db
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()

bot = commands.Bot(intents=intents)

# Logfile setup - will log events in the discord.log file.
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# MISC COMMANDS
# This first section is a collection of miscellaneous commands or events NanoBot watches.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# login successful
@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user}')

# /checkup
# gives some tech info about NanoBot. 
@bot.slash_command(
    name="checkup",
    guild_ids=[825590571606999040],
    description="Gives technical information about the bot."
)
async def checkup(ctx): 
    await ctx.respond(f'''Hello, {ctx.user.name}! Thanks for checking on me.
Current latency: {round(bot.latency*1000,3)}ms
Database status: {"Online" if db.test_connection() != -1 else "Connection failed"}''')

# /add
# adds two numbers together. A test function.
@bot.slash_command(
    name="add",
    guild_ids=[825590571606999040]
)
async def add(ctx,first: int, second: int):
    await ctx.respond(f"the sum of {first} and {second} is {first + second}.")

# Nano gets a bit nervous if you mention the word "key."
@bot.event
async def on_message(message: discord.Message):
    if not message.author.bot and "key" in message.content.lower():
        await message.channel.send("\U0001F5FF")


# RPG COMMANDS
# This section contains the various RPG-related commands and events in NanoBot.
# TODO: needs a privacy policy since player username is collected for DB storage/access.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# /start
# instantiates a new PlayerClass, assigns it to the player, and persists it to the database.
@bot.slash_command(
    name="start",
    guild_ids=[825590571606999040],
    description="Choose a class: Warrior, Mage, Ranger, General, Trickster"
)
async def add_new_user(ctx,player_class: str):
    # check if player has made a class before
    valid_classes=["warrior","mage","ranger","general","trickster"]
    if player_class.lower() not in valid_classes:
        await ctx.respond("Sorry, that is not a valid class.")
        return
    # attempt to insert a new user
    newplayer = db.insert_new_user(ctx.user.name,player_class)
    if newplayer == -1:
        await ctx.respond("You already have a character!")
        return
    await ctx.respond(f'''Successfully created a new character for {ctx.user.name}!
Class: {newplayer.pclass}
HP: {newplayer.maxhp[0]}
ATK: {newplayer.atk[0]}
Defense: {newplayer.defense[0] * 100}%''')

# /stats
# check your character stats.
@bot.slash_command(
    name="stats",
    guild_ids=[825590571606999040]
)  
async def get_stats(ctx: discord.ApplicationContext):
    stats = db.find_user(ctx.user.name)
    if stats == -1:
        await ctx.respond("No character found! Create a character with /start.")
        return
    await ctx.respond(f'''Stats for {ctx.user.name}:
Class: {stats.pclass}
Level: {stats.level}
Current XP: {stats.xp}/{stats.get_level_req()}
HP: {stats.maxhp[0]}
ATK: {stats.atk[0]}
Defense: {round(stats.defense[0] * 100,2)}%''')


# /delete
# Deletes a user's character from the database. TODO
@bot.slash_command(
    name="delete",
    guild_ids=[825590571606999040],
    description="Deletes your character permanently. This command cannot be undone."
)
async def delete_user(ctx: discord.ApplicationContext):
    res = db.delete_user(ctx.user.name)
    if res == -1:
        await ctx.respond("Delete unsuccessful. Please try again later.")
    else:
        await ctx.respond("Your character has successfully been deleted.")

@bot.slash_command(
    name="xp",
    guild_ids=[825590571606999040],
    description="test level-up function"
)
async def gain_xp(ctx: discord.ApplicationContext):
    player_entity = db.find_user(ctx.user.name)
    await ctx.respond(player_entity.test_xp())
    print(db.update_stats(player_entity))
    pass

# run the bot
bot.run(TOKEN)
