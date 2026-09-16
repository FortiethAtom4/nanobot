import discord, logging, locale
from discord.ext import commands, pages

import config
from utils.user import User

from utils import db

locale.setlocale(locale.LC_ALL, '')

logger = logging.getLogger(__name__)

class LevelPaginatorCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.num_per_page = 10
        self.num_pages = 0
        self.pages = []

    # Helper function for /levels.
    def get_pages(self):
        all_users: list[User] = db.get_users()

        self.num_pages = ((len(all_users) - 1) // self.num_per_page) + 1
        counter = 0
        self.pages = []
        for i in range(self.num_pages):
            page_string = ""
            new_range = len(all_users) - counter if len(all_users) - counter < self.num_per_page else self.num_per_page
            for j in range(new_range):
                user = all_users[counter]
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
    async def rank(self, ctx: discord.ApplicationContext, user: discord.Member = None): # user = discord.User

        all_users = db.get_users()

        if user == None:
            this_user = db.get_user_by_name(ctx.author.name)
            if this_user == None:
                # never sent a message but used /rank, can just temp add them to this list
                this_user = User(ctx.author.name)
                all_users.append(this_user)

            config.sort_users_by_rank(all_users)

            rank = next((i for i, user in enumerate(all_users) if user.name == ctx.author.name), -1)
            await ctx.respond(f'''```You are rank {rank + 1} out of {len(all_users)} users.
    Your current level: {this_user.level}
    Total XP: {this_user.xp_total:n}
    Total messages: {this_user.total_messages:n}
    Progress to next level: {this_user.xp_current:n}/{this_user.get_level_req():n} ({round((this_user.xp_current)/this_user.get_level_req()*100,2)}%)```''')
        else:

            rank = next((i for i, u in enumerate(all_users) if u.name == user.name), -1)
            if rank == -1:
                await ctx.respond(f"`User {user.name} no longer exists or has not sent any messages since bot startup.`")
                return
            user_info = all_users[rank]
            await ctx.respond(f'''```{user.name} is rank {rank + 1} out of {len(all_users)} users.
    Current level: {user_info.level}
    Total XP: {user_info.xp_total:n}
    Total messages: {user_info.total_messages:n}
    Progress to next level: {user_info.xp_current:n}/{user_info.get_level_req():n} ({round((user_info.xp_current)/user_info.get_level_req()*100,2)}%)```''')

def setup(bot: discord.Bot):
    bot.add_cog(LevelPaginatorCog(bot))