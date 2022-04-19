# Package Name: [discord_cooldown](https://pypi.org/project/discord-cooldown/)

#### A responsive package for Bot command cooldowns

#### • With this package you can create the command cooldowns which will not get reset whenever the bot re-run

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

[![Generic badge](https://img.shields.io/badge/Python-3.8-blue.svg)](https://shields.io/)
[![GitHub license](https://badgen.net/github/license/Naereen/Strapdown.js)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)
[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)

### Join [Official Discord Server](https://discord.gg/GVMWx5EaAN) for more guidance !

<hr/>

# Features

- Cooldowns of Bot commands are stored in a **DATABASE**
- Available Databases **MySQL, PostgreSQL and Sqlite`(Sqlite3)`**
- **asynchronous** functions are used throughout the module

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
    pip install git+https://github.com/Modern-Realm/discord_cooldown.git
  # Method-2:
    pip install -U git+https://github.com/Modern-Realm/discord_cooldown
```

**Note:** For better stability install package from [GitHub](https://github.com/Modern-Realm/discord_cooldown) using **`GIT`**

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
from discord_cooldown.cooldown import Cooldown
import discord
from discord.ext import commands

intents = discord.Intents.all()
client = commands.Bot(command_prefix="&", intents=intents)


@client.event
async def on_ready():
    print("Bot's online !")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(description=f"This command is on cooldown\n"
                                       f"Retry after `{error.retry_after}` seconds")

        return await ctx.reply(embed=em, mention_author=False)


@Cooldown().cooldown(1, 2 * 60)
@client.command()
async def test(ctx):
    """
    Returns an error: commands.CommandOnCooldown if it's on cooldown
    """
    await ctx.send("Hello world !")


@Cooldown().cooldown(1, 0, commands.BucketType.guild, reset_per_day=True)
@client.command(aliases=['sf'])
async def serverinfo(ctx):
    guild = ctx.guild
    em = discord.Embed(
        title="Server Info",
        description=f"Server Name: {guild.name}\n"
                    f"Total Members: {guild.member_count}\n"
                    f"Owner: {guild.owner.mention}"
    )

    await ctx.reply(embed=em, mention_author=False)


client.run(TOKEN)
```

<hr/>

# Project Links

You can get support/help/guidance from below social-media links

- [Home Page](https://github.com/Modern-Realm)
- [Official Discord Server](https://discord.gg/GVMWx5EaAN)
- [PyPi Package](https://pypi.org/project/discord-cooldown/)
