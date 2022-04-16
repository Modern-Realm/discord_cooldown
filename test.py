from discord_cooldown.cooldown import Cooldown
from discord_cooldown.modules import MySQL

import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv("C:/users/sai keerthan/PyEnvirons/variables.env")

TOKEN = os.getenv("EMOJIS_BOT")
intents = discord.Intents.all()

command_prefix = "$"
activity = discord.Game(f"{command_prefix}help")

client = commands.Bot(command_prefix=command_prefix, intents=intents, status=discord.Status.online,
                      activity=activity)

CD = Cooldown(MySQL(
    os.getenv("DB_HOST"),
    os.getenv("DB_NAME"),
    os.getenv("DB_USER"),
    os.getenv("DB_PASSWD"),
    table_name="CustomCooldowns"
))


@client.event
async def on_ready():
    print("Bot's online !")


@CD.cooldown(1, 1.5 * 60, commands.BucketType.guild)
@client.command()
@commands.is_owner()
async def test(ctx):
    await ctx.send("Testing ...")


if __name__ == '__main__':
    client.run(TOKEN)
