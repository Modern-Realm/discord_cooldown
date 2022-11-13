from discord_cooldown.modules import SQlite, MySQL, PostgreSQL
from discord_cooldown.modules import CooldownsDB, BucketTypes

import discord

from typing import Optional, Union, Tuple
from datetime import datetime, timedelta
from discord.ext.commands import cooldowns, BucketType
from discord.ext import commands


class Cooldown:
    def __init__(self, database: Union[MySQL, SQlite, PostgreSQL] = SQlite(), *,
                 timezone: timedelta = timedelta(hours=0)):
        """
        It returns commands.cooldown

        For examples: https://github.com/Modern-Realm/discord_cooldown/tree/main/Examples

        :param database: takes PostgreSQL, MySQL or SQlite
        :param timezone: add/ remove no.of hours using datetime.timedelta you need to get your timezone

        :returns: cooldown: commands.check
        """

        self.user: Optional[discord.Member] = None
        self.__rate: int = 0
        self.__per: float = 0
        self.timezone = timezone
        self.reset: bool = False
        self.__type: Optional[BucketTypes] = None
        self.db = database
        self.default_format: str = "%Y-%m-%d %H:%M:%S"
        self.command_name: Optional[str] = None

        self.CD = CooldownsDB(self.db)

    def cooldown(self, rate: int, per: float, type_: Union[BucketTypes, BucketType] = BucketTypes.user, *,
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

        self.__rate = rate
        self.__per = per
        self.__type = type_
        self.reset = reset_per_day

        if self.reset:
            self.__per = 24 * 60 * 60

        async def predicate(context) -> bool:
            self.user = context.author
            self.command_name = context.command.name
            await self.CD.open_cd(self.user)
            await self.CD.add_column(self.command_name)

            try:
                cmd_rate, cmd_per, cmd_cd = await self.CD.get_cd(self.user, self.command_name)
            except TypeError:
                cmd_rate = cmd_per = 0
                cmd_cd = None

            if cmd_cd is None:
                cmd_rate, cmd_per, cmd_cd = await self._set_CD()

            cur_time = (datetime.utcnow() + self.timezone).replace(microsecond=0)
            if cur_time > cmd_cd:
                await self.CD.reset_cd(self.user, self.command_name)
                await self._set_CD(per=+1)
                return True
            else:
                if cmd_per + 1 == cmd_rate:
                    if self.reset:
                        cur_time = (datetime.utcnow() + self.timezone).replace(microsecond=0)
                        cd_time_ = (cur_time + timedelta(days=1)).replace(
                            hour=0, minute=0, second=0, microsecond=0
                        )
                        cd_time = cd_time_.strftime(self.default_format)
                    else:
                        cur_time = (datetime.utcnow() + self.timezone).replace(microsecond=0)
                        cd_time_ = cur_time + timedelta(seconds=self.__per)
                        cd_time = cd_time_.strftime(self.default_format)
                    await self.CD.update_cd(self.user, self.command_name, per=+1, cooldown=cd_time)
                    return True
                elif cmd_per < cmd_rate:
                    await self.CD.update_cd(self.user, self.command_name, per=+1)
                    return True

                cmd_rate, cmd_per, cmd_cd = await self.CD.get_cd(self.user, self.command_name)
                left_time = (cmd_cd - cur_time).total_seconds()
                raise commands.CommandOnCooldown(
                    cooldown=cooldowns.Cooldown(self.__rate, self.__per),
                    retry_after=int(round(left_time, 0)),
                    type=self.__type
                )

        return commands.check(predicate)

    async def _set_CD(self, /, per: int = 0) -> Tuple[int, int, datetime]:
        cur_time = (datetime.utcnow() + self.timezone).replace(microsecond=0)
        if self.reset:
            cd_time_ = (cur_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            cd_time_ = cur_time + timedelta(seconds=self.__per)

        await self.CD.create_cd(self.user, self.command_name,
                                rate=self.__rate, per=per, cooldown=cd_time_.strftime(self.default_format))

        return self.__rate, per, cd_time_

    async def reset_cooldown(self, user: discord.Member, command_name: str) -> None:
        await self.CD.reset_cd(user, command_name)
