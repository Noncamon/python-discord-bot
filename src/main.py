import discord
from discord.ext import bridge

intents = discord.Intents.all()
intents.message_content = True
bot = bridge.Bot(command_prefix="n!", intents=intents)

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    print(f"bot loaded in {bot.user} and ready to fire!\n{bot.guilds}")

cogs = [
    "TaskLoop",
    "MusicPlayer",
]
for cog in cogs:
    bot.load_extension(f"cogs.{cog}")

with open("token.txt", "r") as f:
    token = f.read()
bot.run(token)
