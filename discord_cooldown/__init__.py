"""
Package Name: [discord_cooldown]
HomePage: https://pypi.org/project/discord-cooldown/
Github: https://github.com/Modern-Realm/discord_cooldown

Short Description:
• A responsive package for command cooldowns.
• With this package you can create the command cooldowns which will not get reset whenever the bot re-run.

"""

__title__ = "discord-cooldown"
__author__ = "P. Sai Keerthan reddy"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2023 skrphenix"
__version__ = "0.1.5"

from .modules import SQlite, MySQL, PostgreSQL
from .cooldown import Cooldown
