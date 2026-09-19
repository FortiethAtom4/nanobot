import discord, logging, locale
from discord.ext import commands, pages

import config
from utils.models import User

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
    def get_pages(self, user_list: list[User]):

        self.num_pages = ((len(user_list) - 1) // self.num_per_page) + 1
        counter = 0
        self.pages = []
        for i in range(self.num_pages):
            page_string = ""
            new_range = len(user_list) - counter if len(user_list) - counter < self.num_per_page else self.num_per_page
            for j in range(new_range):
                user = user_list[counter]
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
        this_server_users = db.get_users(ctx.guild_id)

        if len(this_server_users) > 0:
            config.sort_users_by_rank(this_server_users)

            paginator = pages.Paginator(pages=self.get_pages(this_server_users), disable_on_timeout=True, timeout=60*60, author_check=False)
            await paginator.respond(ctx.interaction, ephemeral=False)
        else:
            await ctx.respond("No user data found for this server. This should change once users send messages.")


    # /rank
    @discord.slash_command(
    name="rank",
    guild_ids=config.GUILD_IDS,
    description="Gets your rank."
    )
    async def rank(self, ctx: discord.ApplicationContext, user: discord.Member = None): # user = discord.User

        this_server_users = db.get_users(ctx.guild_id)

        if user == None:
            ctx.author.id
            this_user = db.get_user_by_ids(ctx.guild_id,ctx.author.id)
            if this_user == None:
                # never sent a message but used /rank, can just temp add them to this list
                this_user = User(ctx.guild_id,ctx.author.id,ctx.author.name)
                this_server_users.append(this_user)

            rank = next((i for i, user in enumerate(this_server_users) if user.name == ctx.author.name), -1)
            await ctx.respond(f'''```You are rank {rank + 1} out of {len(this_server_users)} users.
    Your current level: {this_user.level}
    Total XP: {this_user.xp_total:n}
    Total messages: {this_user.total_messages:n}
    Progress to next level: {this_user.xp_current:n}/{this_user.get_level_req():n} ({round((this_user.xp_current)/this_user.get_level_req()*100,2)}%)```''')
        else:

            rank = next((i for i, u in enumerate(this_server_users) if u.name == user.name), -1)
            if rank == -1:
                await ctx.respond(f"`User {user.name} no longer exists or has not sent any messages since bot startup.`")
                return
            user_info = this_server_users[rank]
            await ctx.respond(f'''```{user.name} is rank {rank + 1} out of {len(this_server_users)} users.
    Current level: {user_info.level}
    Total XP: {user_info.xp_total:n}
    Total messages: {user_info.total_messages:n}
    Progress to next level: {user_info.xp_current:n}/{user_info.get_level_req():n} ({round((user_info.xp_current)/user_info.get_level_req()*100,2)}%)```''')



    @discord.slash_command(
    name="port",
    guild_ids=config.GUILD_IDS,
    description="Attempt to port an old user to the new table."
    )
    async def port_user(self, ctx: discord.ApplicationContext, id, username: str):
        success = db.port_user(ctx.guild_id,id,username)

        match success:
            case 0:
                await ctx.respond(f"Successfully ported user {username}")
            
            case 1:
                await ctx.respond(f"Failed to port user {username}: A user by that name already exists in the new table.")

            case 2:
                await ctx.respond(f"Failed to port user {username}: No user by that name exists in the old table.")

            case 3:
                await ctx.respond(f"Failed to port user {username}: There was a SQL error on insert. Is your ID unique?")

        # msgs = await ctx.channel.history(200).flatten()

        # await ctx.respond(msgs)

def setup(bot: discord.Bot):
    bot.add_cog(LevelPaginatorCog(bot))