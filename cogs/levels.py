import discord, logging, locale
from discord.ext import commands, pages

import config

locale.setlocale(locale.LC_ALL, '')

logger = logging.getLogger(__name__)
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO, format=config.log_formatter)

class LevelPaginatorCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.num_per_page = 10
        self.num_pages = 0
        self.pages = []

    # Helper function for /levels.
    def get_pages(self):
        self.num_pages = ((len(config.users) - 1) // self.num_per_page) + 1
        counter = 0
        self.pages = []
        for i in range(self.num_pages):
            page_string = ""
            new_range = len(config.users) - counter if len(config.users) - counter < self.num_per_page else self.num_per_page
            for j in range(new_range):
                user = config.users[counter]
                page_string += f'''{counter + 1}. **{user.name}**  XP: {user.xp_total:n}  Level: {user.level}\n'''
                counter += 1
            self.pages.append(discord.Embed(title="Leaderboard",description=page_string))
        return self.pages


    # /levels
    @discord.slash_command(
        name="levels",
        guild_ids=config.GUILD_IDS,
        description="Displays the server XP leaderboard."
    )
    async def levels(self, ctx: discord.ApplicationContext):
        paginator = pages.Paginator(pages=self.get_pages(), disable_on_timeout=True, timeout=24*60*60, author_check=False)
        await paginator.respond(ctx.interaction, ephemeral=False)


    # /rank
    @discord.slash_command(
    name="rank",
    guild_ids=config.GUILD_IDS,
    description="Gets your rank."
    )
    async def rank(self, ctx: discord.ApplicationContext, user: discord.User = None):

        if user == None:
            rank = next((i for i, user in enumerate(config.users) if user.name == ctx.user.name), -1)
            user = config.users[rank]
            await ctx.respond(f'''```You are rank {rank + 1} out of {len(config.users)} users.
    Your current level: {user.level}
    Total XP: {user.xp_total:n}
    Total messages: {user.total_messages:n}
    Progress to next level: {user.xp_current:n}/{user.get_level_req():n} ({round((user.xp_current)/user.get_level_req()*100,2)}%)```''')
        else:
            rank = next((i for i, u in enumerate(config.users) if u.name == user.name), -1)
            if rank == -1:
                await ctx.respond(f"`User {user.name} no longer exists or has not sent any messages since bot startup.`")
                return
            user_info = config.users[rank]
            await ctx.respond(f'''```{user.name} is rank {rank + 1} out of {len(config.users)} users.
    Current level: {user_info.level}
    Total XP: {user_info.xp_total:n}
    Total messages: {user_info.total_messages:n}
    Progress to next level: {user_info.xp_current:n}/{user_info.get_level_req():n} ({round((user_info.xp_current)/user_info.get_level_req()*100,2)}%)```''')

def setup(bot: discord.Bot):
    bot.add_cog(LevelPaginatorCog(bot))