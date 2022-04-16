from discord_cooldown.modules import SQlite, MySQL, CooldownsDB, BucketTypes

import discord

from typing import Optional, Union
from datetime import datetime, timedelta
from discord.ext.commands import cooldowns, BucketType
from discord.ext import commands


class Cooldown:
    def __init__(self, database: Union[MySQL, SQlite] = SQlite(), *, timezone: timedelta = timedelta(hours=0)):
        """
        It overwrites commands.cooldown

        For examples: https://github.com/Modern-Realm/discord_cooldown/tree/main/Examples

        :param database: takes MySQL or SQlite
        :param timezone: add no.of hours you need to get your timezone

        :returns: cooldown: commands.check
        """

        self.user: Optional[discord.Member] = None
        self.rate: int = 0
        self.per: float = 0
        self.timezone = timezone
        self.reset: bool = False
        self.type: Optional[BucketTypes] = None
        self.db = database
        self.default_format: str = "%Y-%m-%d %H:%M:%S"
        self.command_name: Optional[str] = None

        self.CD = CooldownsDB(self.db)

    def cooldown(self, rate: int, per: float, type_: Union[BucketTypes, BucketType] = BucketTypes.user,
                 reset_per_day: bool = False) -> commands.check:
        """

        A decorator that adds a cooldown to a command

        A cooldown allows a command to only be used a specific amount
        of times in a specific time frame. These cooldowns can be based
        either on a per-guild, per-channel, per-user, per-role or global basis.
        Denoted by the third argument of ``type`` which must be of enum
        type :class:`BucketTypes` or :class:`commands.BucketType`.

        If a cooldown is triggered, then :exc:`commands.CommandOnCooldown` is triggered in
        :func:`.on_command_error` and the local error handler.

        A command can only have a single cooldown.

        :param rate: The number of times a command can be used before triggering a cooldown.
        :param per: The amount of seconds to wait for a cooldown when it's been triggered.
        :param type_: The type of cooldown to have.
        :param reset_per_day: If True is given, then the cooldown will be reset at `0:00` UTC(or provided timezone).

        :return: commands.check
        """

        self.rate = rate
        self.per = per
        self.type = type_
        self.reset = reset_per_day

        def predicate(context) -> bool:
            self.user = context.author
            self.command_name = context.command.name

            if self.type == BucketTypes.guild or self.type == BucketType.guild:
                self.user = context.guild

            try:
                cmd_rate, cmd_per, cmd_cd = self.CD.get_cd(self.user, self.command_name)
            except:
                cmd_rate = cmd_per = 0
                cmd_cd = None

            if cmd_cd is None:
                self.set_CD()

            try:
                cmd_rate, cmd_per, cmd_cd = self.CD.get_cd(self.user, self.command_name)
            except:
                cmd_rate = cmd_per = 0
                cmd_cd = None

            if cmd_per < cmd_rate:
                self.update_CD()
                return True
            else:
                if cmd_cd is None:
                    return True
                else:
                    cur_time = datetime.utcnow() + self.timezone
                    cur_time = cur_time.replace(microsecond=0)
                    if cur_time > cmd_cd:
                        self.clear_CD()
                        self.set_CD()
                        self.update_CD()
                        return True
                    else:
                        left_time = (cmd_cd - cur_time).total_seconds()
                        raise commands.CommandOnCooldown(
                            cooldown=cooldowns.Cooldown(self.rate, self.per),
                            retry_after=int(round(left_time, 0)),
                            type=self.type
                        )

        return commands.check(predicate)

    def set_CD(self):
        cur_time = datetime.utcnow() + self.timezone
        cur_time = cur_time.replace(microsecond=0)
        if self.reset:
            cd_time = (cur_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            cd_time = cur_time + timedelta(seconds=self.per)
        cd_time = cd_time.strftime(self.default_format)

        self.CD.create_cd(self.user, self.command_name,
                          rate=self.rate, per=0, cooldown=cd_time)

    def update_CD(self):
        cur_time = datetime.utcnow() + self.timezone
        cur_time = cur_time.replace(microsecond=0)
        if self.reset:
            cd_time = (cur_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            cd_time = cur_time + timedelta(seconds=self.per)
        cd_time = cd_time.strftime(self.default_format)

        self.CD.update_cd(self.user, self.command_name, per=+1, cooldown=cd_time)

    def clear_CD(self):
        self.CD.reset_cd(self.user, self.command_name)
