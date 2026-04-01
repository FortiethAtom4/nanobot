import discord, logging, datetime
from discord.ext import commands

import config
import utils.db as db

logger = logging.getLogger(__name__)
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO, format=config.log_formatter)

# A cog for owner-only commands, mainly to check bot performance and do manual updates.
class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @discord.slash_command(
        name="forceupdate",
        guild_ids=config.GUILD_IDS,
        description="Forces the bot to sync its data with the database. Owner-only."
    )
    @commands.is_owner()
    async def force_update(self, ctx):
        msg = await ctx.respond("Updating database...")
        updates_successful = db.persist_updates()
        if not updates_successful:
            await msg.edit(content="Update failure, please check DB connection")
            logger.warning("/forcepersist update failure")
            return
        await msg.edit(content="Updated successfully.")
        logger.info("DB force-updated by owner")


    # /checkup
    # gives some tech info about NanoBot. 
    @discord.slash_command(
        name="checkup",
        guild_ids=config.GUILD_IDS,
        description="OWNER: Gives technical information about the bot."
    )
    @commands.is_owner()
    async def checkup(self, ctx): 
        checkup = await ctx.respond(f'''```Hello, {ctx.user.name}! Thanks for checking on me.
Loading checkup results...```''')
        duration: datetime.timedelta = (datetime.datetime.now() - config.start_time)
        duration = duration - datetime.timedelta(microseconds=duration.microseconds) #is this really how I have to do this

        problems: bool = False
        resp = db.test_connection()
        db_connected = ""
        if not resp:
            problems = True
            db_connected = "!- The database is disconnected. Be sure to check on that ASAP."
        
        latency = round(self.bot.latency*1000,3)
        high_ping = ""
        if latency > 150:
            problems = True
            high_ping = "!- Ping appears to be high. Users may notice a bit of a delay."

        status_string = "-> No problems detected. Everything seems to be in order." if not problems else f"{high_ping}\n{db_connected}"
        
        await checkup.edit(content=f'''```Hello, {ctx.user.name}! Thanks for checking on me. \n
{status_string}\n
- Runtime: {duration}
- Current latency: {latency}ms
- Database status: {'Not connected' if not resp else 'Connected'}```''')
        
# /stuff
    # a funny command which makes Nano say whatever I want.
    @discord.slash_command(
    name="stuff",
    guild_ids=config.GUILD_IDS,
    description="OWNER: "
    )
    @commands.is_owner()
    async def stuff(self, ctx: discord.ApplicationContext, m: str):
        await ctx.delete()
        await ctx.send(m)


    
    @discord.slash_command(
    name="grok",
    guild_ids=config.GUILD_IDS,
    description="OWNER: determine how much of a scourge Nanobot will be in chat."
    )
    @commands.is_owner()
    async def maxbotinator(self, ctx: discord.ApplicationContext, percent:int):
        config.maxbot_chance = percent
        await ctx.respond(f"Response chance changed to {percent}%",ephemeral=True)
        
    @force_update.error
    @checkup.error
    async def owner_error(self, ctx, error):
        if isinstance(error, commands.errors.NotOwner):
            await ctx.respond("You do not have permission to use this command.",ephemeral=True)
            logger.info(f"User {ctx.user.name} blocked from using an owner-only command")
        else:
            await ctx.respond(f"An error occurred when attempting to perform this command: {error}",ephemeral=True)

def setup(bot):
    bot.add_cog(AdminCog(bot))