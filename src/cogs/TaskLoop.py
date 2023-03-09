import discord
from discord.ext import commands, tasks
from itertools import cycle

class TaskLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=10)
    async def change_status(self):
        status = cycle(["n!help", "In development :warning:", "UwU"])
        await self.bot.change_presence(activity=discord.Game(name=next(status)))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.change_status()

def setup(bot):
    bot.add_cog(TaskLoop(bot))