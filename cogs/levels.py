import discord, datetime, config, logging
from discord.ext import commands
from utils.paginator import Pagination

logger = logging.getLogger(__name__)
logging.basicConfig(filename='nanobot.log', encoding='utf-8', level=logging.INFO, format=config.log_formatter)


# Use this file to add your own suite of custom commands to the bot. 
# Feel free to edit this file as you see fit.
# Try copy/pasting command functions from other cog files into the class below if you aren't sure where to start.
class LevelCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="rank",
        guild_ids=config.GUILD_IDS,
        description="Gets your rank."
    )
    async def rank(self, ctx: discord.ApplicationContext):
        rank = next((i for i, user in enumerate(config.users) if user.name == ctx.user.name), -1)
        user = config.users[rank]
        await ctx.respond(f'''```You are rank {rank + 1} out of {len(config.users)} users.
Your current level: {user.level}
Total XP: {user.xp_total}
Progress to next level: {user.xp_current}/{user.get_level_req()} ({round((user.xp_current)/user.get_level_req()*100,2)}%)```''')
        

    @discord.slash_command(
        name="levels",
        guild_ids=config.GUILD_IDS,
        description="Displays the server XP leaderboard."
    )
    async def levels(self, ctx: discord.ApplicationContext):
        page_length = 15
        async def get_page(page: int):
            emb = discord.Embed(title="Leaderboard", description="")
            offset = (page-1) * page_length
            for i, user in enumerate(config.users[offset:offset+page_length]):
                emb.description += f"{i + 1}. **{user.name}**  XP: {user.xp_total}  Level: {user.level} \n"
            n = Pagination.compute_total_pages(len(config.users), page_length)
            emb.set_footer(text=f"Page {page} of {n}")
            return emb, n

        await Pagination(ctx, get_page).navigate()

        # end_string = "```Server XP Leaderboard\n"
        # for i, user in enumerate(config.users):
        #     end_string += f"\n{i + 1}. {user.name} (Level {user.level}) Total XP: {user.xp_total}"

        # end_string += "```"
        # await ctx.respond(end_string)


def setup(bot: discord.Bot):
    bot.add_cog(LevelCommands(bot)) 