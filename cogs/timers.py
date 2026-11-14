import discord, logging, locale, datetime
from discord.ext import commands, tasks

import traceback

import config
from utils.models import User

from utils import db, timer

locale.setlocale(locale.LC_ALL, '')

logger = logging.getLogger(__name__)

class TimerCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

        # key is server ID + user ID
        self.timers: list[timer.Timer] = []
        self.check_timers.start()

    @discord.slash_command(
        name="reminder",
        guild_ids=config.GUILD_IDS,
        description="Sets a reminder."
    )
    async def set_reminder(self, ctx: discord.ApplicationContext, days: int = 0, hours: int = 0, minutes: int = 0):
        if (days <= 0 and hours <= 0 and minutes <= 0):
            await ctx.respond("Please pick a valid amount of time!",ephemeral=True)
            return
        
        try:
            this_user: User | None = db.get_user_by_ids(ctx.guild_id,ctx.author.id)
            if this_user != None:
                new_timer: timer.Timer = timer.Timer(ctx.guild_id,ctx.author.id,ctx.channel_id)
                new_timer.start(datetime.timedelta(days=days,hours=hours,minutes=minutes))
                self.timers.append(new_timer)

                await ctx.respond(f"Timer started. You'll get pinged in {new_timer}.")
                msg = await ctx.interaction.original_response()
                new_timer.set_message_id(msg.id)

        except:
            logger.error(traceback.format_exc())
            await ctx.respond("Something went wrong starting your timer. Please try again later.",ephemeral=True)

    @tasks.loop(seconds=1)
    async def check_timers(self):
        remaining_timers: list[timer.Timer] = []
        for t in self.timers:
            stopped: bool = t.increment()
            if stopped:
                channel = await self.bot.fetch_channel(t.channel_id)
                msg = await channel.fetch_message(t.message_id)
                if channel != None:
                    await msg.reply(f"<@{t.user_id}>! Your timer is up!")
            else:
                remaining_timers.append(t)

        self.timers = remaining_timers

    def cog_unload(self):
        self.check_timers.cancel()

def setup(bot: discord.Bot):
    bot.add_cog(TimerCog(bot))