# Package Name: [discord_cooldown](https://pypi.org/project/discord-cooldown/)

#### A responsive package for Bot command cooldowns

#### • With this package you can create the command cooldowns which will not get reset whenever the bot re-run

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

[![CodeQL](https://github.com/Modern-Realm/discord_cooldown/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Modern-Realm/discord_cooldown/actions/workflows/codeql-analysis.yml)
[![Python](https://img.shields.io/badge/Python-3.8-blue.svg)](https://www.python.org/)
![Github License](https://img.shields.io/badge/license-MIT-blue)
![Windows](https://img.shields.io/badge/os-windows-yellow)
![Linux](https://img.shields.io/badge/os-linux-yellow)

[![GitHub stars](https://img.shields.io/github/stars/Modern-Realm/discord_cooldown?color=gold)](https://github.com/Modern-Realm/discord_cooldown/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Modern-Realm/discord_cooldown?color=%2332cd32)](https://github.com/Modern-Realm/discord_cooldown/network)
[![GitHub issues](https://img.shields.io/github/issues/Modern-Realm/discord_cooldown?color=orange)](https://github.com/Modern-Realm/discord_cooldown/issues)

#### Join [Official Discord Server](https://discord.gg/GVMWx5EaAN  "click to Join") for more guidance !

<hr/>

# Features

- Cooldowns of Bot commands are stored in a **DATABASE**
- Available Databases **MySQL, PostgreSQL and Sqlite`(Sqlite3)`**

<hr/>

# Installation

Python 3.8 or higher is required !

```shell
# Linux/macOS
  python3 -m pip install discord-cooldown

# Windows
  # Method-1:
    py -3 -m pip install discord-cooldown
    # or
    python -m pip install discord-cooldown
  # Method-2:
    pip install discord-cooldown

# Using GIT for ALPHA or BETA Versions
  # Method-1:
    pip install git+https://github.com/Modern-Realm/discord_cooldown
  # Method-2:
    pip install -U git+https://github.com/Modern-Realm/discord_cooldown
```

**Note:** For better stability install package from [GitHub](https://github.com/Modern-Realm/discord_cooldown)
using **`GIT`**

<hr/>

# REQUIRED DEPENDENCIES

> #### You can use ANY ONE of the below discord API Package

- ## [py-cord](https://github.com/Pycord-Development/pycord)
- ## [nextcord](https://github.com/nextcord/nextcord)
- ## [discord.pyV2.0](https://github.com/Rapptz/discord.py)
- ## [disnake](https://github.com/DisnakeDev/disnake)
  `For disnake you should Refactor/ Shim all discord terms to disnake terms to make Package work`

> <b>Note:</b> Don't install more than one **DEPENDENCY !**

#### Other Dependencies

- [mysql-connector-python](https://pypi.org/project/mysql-connector-python/)
- [psycopg2](https://pypi.org/project/psycopg2/)

<hr/>

# QuickStart

```python
from discord_cooldown.modules import MySQL
from discord_cooldown import Cooldown

import discord

from discord.ext import commands
from datetime import timedelta

TOKEN = ""
intents = discord.Intents.all()
client = commands.Bot(command_prefix="&", intents=intents)

# MySQL Database Setup
db = MySQL(
    host="", db_name="",
    user="", passwd=""
)

# For Indian timezone (UTC +5:30)
timezone = +timedelta(hours=5, minutes=30)


def CD():
    return Cooldown(database=db, timezone=timezone)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("&help"))
    print("Bot is online")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(
            f"on cooldown retry after `{timedelta(seconds=error.retry_after)}`"
        )
    else:
        # For resetting a command on any error other than CommandOnCooldown
        return await CD().reset_cooldown(ctx.author, ctx.command.name)


@CD().cooldown(1, 2 * 60)
@client.command()
async def test(ctx):
    await ctx.send("testing")


@CD().cooldown(2, 0, reset_per_day=True)
@client.command()
async def vote(ctx):
    await ctx.send("done")


@CD().cooldown(3, 60)
@client.command()
async def test1(ctx, *, msg: str):
    await ctx.send("message is " + msg)


if __name__ == "__main__":
    client.run(TOKEN)
```

<hr/>

# Project Links

You can get support/help/guidance from below social-media links

- [Home Page](https://github.com/Modern-Realm)
- [Official Discord Server](https://discord.gg/GVMWx5EaAN)
- [PyPi Package](https://pypi.org/project/discord-cooldown/)
