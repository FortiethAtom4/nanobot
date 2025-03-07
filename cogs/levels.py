import discord, logging, locale
from discord.ext import commands, pages

import config

locale.setlocale(locale.LC_ALL, '')

logger = logging.getLogger(__name__)
logging.basicConfig(filename='nanobot.log', encoding='utf-8', level=logging.INFO, format=config.log_formatter)

class LevelPaginatorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.num_per_page = 10
        self.num_pages = 0
        self.pages = []

    def get_pages(self):
        self.num_pages = ((len(config.users) - 1) // self.num_per_page) + 1
        counter = 0
        self.pages = []
        for i in range(self.num_pages):
            page_string = ""
            new_range = len(config.users) - counter if len(config.users) - counter < self.num_per_page else self.num_per_page
            for j in range(new_range):
                user = config.users[counter]
                page_string += f'''{counter + 1}. **{user.name}**  XP: {user.xp_total:,}  Level: {user.level}\n'''
                counter += 1
            self.pages.append(discord.Embed(title="Leaderboard",description=page_string))
        return self.pages

    @discord.slash_command(
        name="levels",
        guild_ids=config.GUILD_IDS,
        description="Displays the server XP leaderboard."
    )
    async def levels(self, ctx: discord.ApplicationContext):
        paginator = pages.Paginator(pages=self.get_pages(), disable_on_timeout=True, timeout=24*60*60, author_check=False)
        await paginator.respond(ctx.interaction, ephemeral=False)

def setup(bot):
    bot.add_cog(LevelPaginatorCog(bot))