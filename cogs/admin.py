import discord, logging
from discord.ext import commands

import config
import utils.db as db

logger = logging.getLogger(__name__)
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO, format=config.log_formatter)

# A cog for owner-only commands, mainly to check bot performance and do manual updates.
class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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
        description="Gives technical information about the bot. Owner-only."
    )
    @commands.is_owner()
    async def checkup(self, ctx): 
        resp = db.test_connection()
        await ctx.respond(f'''```Hello, {ctx.user.name}! Thanks for checking on me.
    Current latency: {round(self.bot.latency*1000,3)}ms
    Database status: {"Not connected" if resp == -1 else "Connected"}```''')
        
    @force_update.error
    @checkup.error
    async def owner_error(self, ctx, error):
        if isinstance(error, commands.errors.NotOwner):
            await ctx.respond("You do not have permission to use this command.",ephemeral=True)
            logger.info(f"User {ctx.user.name} blocked from using an owner-only command")

def setup(bot):
    bot.add_cog(AdminCog(bot))