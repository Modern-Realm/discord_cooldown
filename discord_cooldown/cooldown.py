from discord_cooldown import ext
from discord_cooldown.modules import *
from discord_cooldown.ext import Database, get_datetime

import discord

from typing import Union, Any, Dict, Mapping, overload, TypeVar
from discord.ext.commands import cooldowns, BucketType
from discord.ext import commands
from datetime import timedelta

__all__ = [
    "Context",
    "Cooldown"
]

Context = TypeVar("Context", commands.Context, discord.ApplicationContext)


class Cooldown:
    def __init__(self, db_config: Union[SQlite, MySQL, PostgreSQL], timezone: timedelta = None):
        db = Database(db_config)
        if not db.is_connected:
            db.connect()

        self.cd = ext.Cooldowns(db)
        self.cd.create_tables()
        self.timezone = timezone

        self._cooldowns: Dict[str, Dict[str, Any]] = {}

    async def _user_predicate(
        self, context: Context,
        rate: int, per: Union[int, float], type: BucketType, reset_per_day: bool
    ) -> bool:
        command_name = context.command.name
        await self.cd.users.add_column(command_name)

        user = context.author
        if isinstance(context, discord.ApplicationContext):
            user = context.user

        cd = await self.cd.users.get_cooldown(user, command_name)
        if reset_per_day:
            expires_at = get_datetime(per, self.timezone) + timedelta(days=1)
            expires_at = expires_at.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            expires_at = get_datetime(per, self.timezone)

        if cd is None:
            options = ext.Options(rate, +1, type, expires_at=expires_at)
            await self.cd.users.update_cooldown(user, command_name, options)
            return True

        options = cd
        if get_datetime(timezone=self.timezone) > options.expires_at:
            await self.cd.users.update_cooldown(
                user, command_name, ext.Options(rate, +1, type, expires_at=expires_at))

            return True
        else:
            if options.count < rate:
                options.count += 1
                await self.cd.users.update_cooldown(user, command_name, options)
                return True

            left_time = options.expires_at - get_datetime(timezone=self.timezone)
            raise commands.CommandOnCooldown(
                cooldown=cooldowns.Cooldown(rate, per),
                retry_after=round(left_time.total_seconds()),
                type=type
            )

    async def _guild_predicate(
        self, context: Context,
        rate: int, per: Union[int, float], type: BucketType, reset_per_day: bool
    ) -> bool:
        command_name = context.command.name
        await self.cd.guilds.add_column(command_name)

        user = context.author
        if isinstance(context, discord.ApplicationContext):
            user = context.user

        guild = context.guild
        if guild is None:
            return True

        cd = await self.cd.guilds.get_cooldown(user, guild, command_name)
        if reset_per_day:
            expires_at = get_datetime(per, self.timezone) + timedelta(days=1)
            expires_at = expires_at.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            expires_at = get_datetime(per, self.timezone)

        if cd is None:
            options = ext.Options(rate, +1, type, expires_at=expires_at)
            await self.cd.guilds.update_cooldown(user, guild, command_name, options)
            return True

        options = cd
        if get_datetime(timezone=self.timezone) > options.expires_at:
            await self.cd.guilds.update_cooldown(
                user, guild, command_name, ext.Options(
                    rate, +1, type, expires_at=expires_at
                ))

            return True
        else:
            if options.count < rate:
                options.count += 1
                await self.cd.guilds.update_cooldown(user, guild, command_name, options)
                return True

            left_time = options.expires_at - get_datetime(timezone=self.timezone)
            raise commands.CommandOnCooldown(
                cooldown=cooldowns.Cooldown(rate, per),
                retry_after=round(left_time.total_seconds()),
                type=type
            )

    async def _channel_predicate(
        self, context: Context,
        rate: int, per: Union[int, float], type: BucketType, reset_per_day: bool
    ) -> bool:
        command_name = context.command.name
        await self.cd.channels.add_column(command_name)

        user = context.author
        if isinstance(context, discord.ApplicationContext):
            user = context.user

        channel = context.channel
        if not isinstance(channel, discord.TextChannel):
            return True

        cd = await self.cd.channels.get_cooldown(user, channel, command_name)
        if reset_per_day:
            expires_at = get_datetime(per, self.timezone) + timedelta(days=1)
            expires_at = expires_at.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            expires_at = get_datetime(per, self.timezone)

        if cd is None:
            options = ext.Options(rate, +1, type, expires_at=expires_at)
            await self.cd.channels.update_cooldown(user, channel, command_name, options)
            return True

        options = cd
        if get_datetime(timezone=self.timezone) > options.expires_at:
            await self.cd.channels.update_cooldown(
                user, channel, command_name, ext.Options(
                    rate, +1, type, expires_at=expires_at
                ))

            return True
        else:
            if options.count < rate:
                options.count += 1
                await self.cd.channels.update_cooldown(user, channel, command_name, options)
                return True

            left_time = options.expires_at - get_datetime(timezone=self.timezone)
            raise commands.CommandOnCooldown(
                cooldown=cooldowns.Cooldown(rate, per),
                retry_after=round(left_time.total_seconds()),
                type=type
            )

    async def _category_predicate(
        self, context: Context,
        rate: int, per: Union[int, float], type: BucketType, reset_per_day: bool
    ) -> bool:
        command_name = context.command.name
        await self.cd.categories.add_column(command_name)

        user = context.author
        if isinstance(context, discord.ApplicationContext):
            user = context.user

        category = context.channel.category
        if category is None:
            return True

        cd = await self.cd.categories.get_cooldown(user, category, command_name)
        if reset_per_day:
            expires_at = get_datetime(per, self.timezone) + timedelta(days=1)
            expires_at = expires_at.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            expires_at = get_datetime(per, self.timezone)

        if cd is None:
            options = ext.Options(rate, +1, type, expires_at=expires_at)
            await self.cd.categories.update_cooldown(user, category, command_name, options)
            return True

        options = cd
        if get_datetime(timezone=self.timezone) > options.expires_at:
            await self.cd.categories.update_cooldown(
                user, category, command_name, ext.Options(
                    rate, +1, type, expires_at=expires_at
                ))

            return True
        else:
            if options.count < rate:
                options.count += 1
                await self.cd.categories.update_cooldown(user, category, command_name, options)
                return True

            left_time = options.expires_at - get_datetime(timezone=self.timezone)
            raise commands.CommandOnCooldown(
                cooldown=cooldowns.Cooldown(rate, per),
                retry_after=round(left_time.total_seconds()),
                type=type
            )

    async def _role_predicate(
        self, context: Context,
        role_id: int,
        rate: int, per: Union[int, float], type: BucketType, reset_per_day: bool
    ) -> bool:
        command_name = context.command.name
        await self.cd.roles.add_column(command_name)

        user = context.author
        if isinstance(context, discord.ApplicationContext):
            user = context.user

        role = context.guild.get_role(role_id)
        if role is None or role not in user.roles:
            return True

        cd = await self.cd.roles.get_cooldown(user, role, command_name)
        if reset_per_day:
            expires_at = get_datetime(per, self.timezone) + timedelta(days=1)
            expires_at = expires_at.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            expires_at = get_datetime(per, self.timezone)

        if cd is None:
            options = ext.Options(rate, +1, type, expires_at=expires_at)
            await self.cd.roles.update_cooldown(user, role, command_name, options)
            return True

        options = cd
        if get_datetime(timezone=self.timezone) > options.expires_at:
            await self.cd.roles.update_cooldown(
                user, role, command_name, ext.Options(
                    rate, +1, type, expires_at=expires_at
                ))

            return True
        else:
            if options.count < rate:
                options.count += 1
                await self.cd.roles.update_cooldown(user, role, command_name, options)
                return True

            left_time = options.expires_at - get_datetime(timezone=self.timezone)
            raise commands.CommandOnCooldown(
                cooldown=cooldowns.Cooldown(rate, per),
                retry_after=round(left_time.total_seconds()),
                type=type
            )

    @overload
    def cooldown(self, rate: int, per: Union[float, int], *,
                 role_id: int = None, type: BucketType = BucketType.user) -> commands.check:
        ...

    @overload
    def cooldown(self, rate: int, *, reset_per_day: bool, role_id: int,
                 type: BucketType = BucketType.user) -> commands.check:
        ...

    def cooldown(
        self, rate: int = None, per: Union[float, int] = None, *, role_id: int = None,
        type: BucketType = BucketType.user, reset_per_day: bool = False
    ):
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
        :param role_id: Enter the role ID
        :param type: The type of cooldown to have.
        :param reset_per_day: If True is given, then the cooldown will be reset at `0:00` UTC(or provided timezone).

        :return: commands.check
        """

        if not reset_per_day:
            if rate is None and per is None:
                raise ValueError("Excepted values for both rate and per, got None instead")
        else:
            per = 0
            if rate is None:
                raise ValueError("Excepted integer, got None instead for `rate`")

        if type == BucketType.role and role_id is None:
            raise ValueError("Excepted role_id for type:`commands.BucketType.role` got None instead")

        async def predicate(context: Union[commands.Context, discord.ApplicationContext]) -> bool:
            self._cooldowns[context.command.name] = {
                "rate": rate, "per": per, "type": type, "role_id": role_id
            }

            kwargs = {
                "context": context, "rate": rate, "per": per, "type": type, "reset_per_day": reset_per_day
            }

            if type == BucketType.role:
                kwargs["role_id"] = role_id
                return await self._role_predicate(**kwargs)
            elif type == BucketType.guild:
                return await self._guild_predicate(**kwargs)
            elif type == BucketType.channel:
                return await self._channel_predicate(**kwargs)
            elif type == BucketType.category:
                return await self._category_predicate(**kwargs)
            else:
                return await self._user_predicate(**kwargs)

        return commands.check(predicate)

    async def reset_cooldown(self, context: Context, force: bool = False) -> None:
        """
        reset a command cooldown

        if the cooldown rate is > 1 then it will be reduced by 1 on every call, else it will get reset completely when
        force is False

        :param context: command/application context
        :param force: if True, the command cooldown will be removed completely
        """

        command_name = context.command.name
        cmd = self._cooldowns.get(command_name, None)
        if cmd is None:
            return None

        user = context.author
        if isinstance(context, discord.ApplicationContext):
            user = context.user

        cmd_type = cmd["type"]
        if cmd_type == BucketType.guild:
            if context.guild is None:
                return
            if force:
                return await self.cd.guilds.remove_cooldown(user, context.guild, command_name)

            await self.cd.guilds.reset_cooldown(user, context.guild, command_name)
        elif cmd_type == BucketType.channel:
            if force:
                return await self.cd.channels.remove_cooldown(user, context.channel, command_name)

            await self.cd.channels.reset_cooldown(user, context.channel, command_name)
        elif cmd_type == BucketType.category:
            if context.channel.category is None:
                return
            if force:
                return await self.cd.categories.remove_cooldown(user, context.channel.category, command_name)

            await self.cd.categories.reset_cooldown(user, context.channel.category, command_name)
        elif cmd_type == BucketType.role:
            role_id = cmd.get("role_id", None)
            if role_id is None:
                return

            role = context.guild.get_role(role_id)
            if role is None:
                return
            if force:
                return await self.cd.roles.remove_cooldown(user, role, command_name)

            await self.cd.roles.reset_cooldown(user, role, command_name)
        else:
            if force:
                return await self.cd.users.remove_cooldown(user, command_name)

            await self.cd.users.reset_cooldown(user, command_name)

    @property
    def cooldowns(self) -> Mapping[str, Mapping[str, Any]]:
        return self._cooldowns.copy()
