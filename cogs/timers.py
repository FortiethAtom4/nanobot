import discord, logging, locale, datetime
from discord.ext import commands, tasks

import traceback

import config
from utils.models import User, Timer

from utils import db

locale.setlocale(locale.LC_ALL, '')

log = logging.getLogger(__name__)

class TimerCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

        # key is server ID + user ID
        self.timers: list[Timer] = []
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
                new_timer: Timer = Timer(ctx.guild_id,ctx.author.id,ctx.channel_id)
                new_timer.start(datetime.timedelta(days=(days if days >= 0 else 0),hours=(hours if hours >= 0 else 0),minutes=(minutes if minutes >= 0 else 0)))
                self.timers.append(new_timer)

                await ctx.respond(f"Timer started. You'll get pinged in {new_timer}.")


                msg = await ctx.interaction.original_response()
                if msg:
                    new_timer.set_message_id(msg.id)

                db.set_timer(new_timer) #persist to DB

        except:
            log.error(traceback.format_exc())
            await ctx.respond("Something went wrong starting your timer. Please try again later.",ephemeral=True)

    @tasks.loop(seconds=1)
    async def check_timers(self):
        remaining_timers: list[Timer] = []
        for t in self.timers:
            stopped: bool = t.increment()
            if stopped:
                # TODO move this block to separate async function (probably to run via a separate thread)
                try:
                    channel = await self.bot.fetch_channel(t.channel_id)
                    try:
                        msg = await channel.fetch_message(t.message_id)
                        await msg.reply(f"<@{t.user_id}>! Your timer is up!")
                    except Exception as e:
                        log.warning(f"Failed to reply to original message with timer: {e}")
                        # just chuck the msg in the channel if the original message is gone
                        await channel.send(f"<@{t.user_id}>! Your timer is up!")

                except Exception as e:
                    log.error(f"Failed to get channel to send timer message: {e}")

                finally:
                    db.remove_timer(t) # remove from DB once timer is up

            else:
                remaining_timers.append(t)

        self.timers = remaining_timers

    @check_timers.before_loop
    async def get_timers_in_db(self):
        self.timers = db.get_all_timers() 
        log.info(f"got {str(len(self.timers))} timers from the database.")

    def cog_unload(self):
        self.check_timers.cancel()

def setup(bot: discord.Bot):
    bot.add_cog(TimerCog(bot))