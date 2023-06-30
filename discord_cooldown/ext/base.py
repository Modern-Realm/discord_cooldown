from discord_cooldown.ext.database import Database

import json
import discord

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from discord.ext.commands import BucketType

__all__ = [
    "Options",
    "get_datetime",
    "Cooldowns"
]


class Options:
    def __init__(
        self,
        rate: int, count: int, type: BucketType,
        expires_at: datetime,
        default_format: str = "%Y-%m-%d %H:%M:%S"
    ):
        """
        cooldown options

        :param rate: The number of times a command can be used before triggering a cooldown.
        :param count: The number of times a command has been used.
        :param type: The type of cooldown to have.
        :param expires_at: The time when a command expires
        :param default_format: The default format of the datetime.datetime
        """

        self.rate = rate
        self.count = count
        self.expires_at = expires_at
        self.type = type
        self.default_format = default_format

    @classmethod
    def from_dict(cls, options: Dict[str, Any], default_format: str = "%Y-%m-%d %H:%M:%S") -> "Options":
        if options["type"] == BucketType.guild:
            type_ = BucketType.guild
        elif options["type"] == BucketType.channel:
            type_ = BucketType.channel
        elif options["type"] == BucketType.category:
            type_ = BucketType.category
        elif options["type"] == BucketType.role:
            type_ = BucketType.role
        else:
            type_ = BucketType.user

        return cls(
            rate=options["rate"], count=options["count"],
            expires_at=datetime.strptime(options["expires_at"], default_format),
            type=type_,
        )

    def toJSON(self) -> Dict[str, Any]:
        data = {
            "rate": self.rate, "count": self.count,
            "expires_at": str(self.expires_at),
            "type": self.type
        }

        return data


class _Users:
    def __init__(self, db: Database):
        self._db = db
        self._table_prefix = self._db.table_prefix
        self._fmtr = self._db.fmtr

        self.view = f"`{self._table_prefix}_user`"

    async def add_column(self, command_name: str) -> None:
        try:
            self._db.run("ALTER TABLE {} ADD `{}` LONGTEXT DEFAULT NULL".format(self.view, command_name))
        except:
            pass

    async def add_user(self, user: discord.Member):
        data = self._db.execute(
            "SELECT * FROM {} WHERE user_id = {}".format(self.view, self._fmtr),
            (user.id,)
        )
        if data is None:
            self._db.run(
                "INSERT INTO {}(user_id) VALUES({})".format(
                    self.view, self._fmtr),
                (user.id,)
            )

    async def get_cooldown(self, user: discord.Member, command_name: str) -> Optional[Options]:
        data = self._db.execute(
            "SELECT {} FROM {} WHERE user_id = {}".format(command_name, self.view, self._fmtr),
            (user.id,)
        )
        if data is None:
            await self.add_user(user)
            return None
        if data[0] is None:
            return None

        options = json.loads(data[0])
        return Options.from_dict(options)

    async def update_cooldown(self, user: discord.Member, command_name: str, options: Options) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = {v} WHERE user_id = {v}".format(self.view, command_name, v=self._fmtr),
            (json.dumps(options.toJSON()), user.id)
        )

    async def remove_cooldown(self, user: discord.Member, command_name: str) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = NULL WHERE user_id = {}".format(self.view, command_name, self._fmtr),
            (user.id,)
        )

    async def reset_cooldown(self, user: discord.Member, command_name: str) -> None:
        options = await self.get_cooldown(user, command_name)
        if options is None:
            return

        if options.count > 1:
            options.count -= 1
            await self.update_cooldown(user, command_name, options)
        else:
            await self.remove_cooldown(user, command_name)


class _Guilds:
    def __init__(self, db: Database):
        self._db = db
        self._table_prefix = self._db.table_prefix
        self._fmtr = self._db.fmtr

        self.view = f"`{self._table_prefix}_guild`"

    async def add_column(self, command_name: str) -> None:
        try:
            self._db.run("ALTER TABLE {} ADD `{}` LONGTEXT DEFAULT NULL".format(self.view, command_name))
        except:
            pass

    async def add_user(self, user: discord.Member, guild: discord.Guild):
        data = self._db.execute(
            "SELECT * FROM {} WHERE user_id = {v} AND guild_id = {v}".format(self.view, v=self._fmtr),
            (user.id, guild.id)
        )
        if data is None:
            self._db.run(
                "INSERT INTO {}(user_id, guild_id) VALUES({v}, {v})".format(
                    self.view, v=self._fmtr),
                (user.id, guild.id)
            )

    async def get_cooldown(self, user: discord.Member, guild: discord.Guild, command_name: str) -> Optional[Options]:
        data = self._db.execute(
            "SELECT {} FROM {} WHERE user_id = {v} AND guild_id = {v}".format(command_name, self.view, v=self._fmtr),
            (user.id, guild.id)
        )
        if data is None:
            await self.add_user(user, guild)
            return None
        if data[0] is None:
            return None

        options = json.loads(data[0])
        return Options.from_dict(options)

    async def update_cooldown(
        self, user: discord.Member, guild: discord.Guild, command_name: str, options: Options
    ) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = {v} WHERE user_id = {v} AND guild_id = {v}".format(
                self.view, command_name, v=self._fmtr),
            (json.dumps(options.toJSON()), user.id, guild.id)
        )

    async def remove_cooldown(self, user: discord.Member, guild: discord.Guild, command_name: str) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = NULL WHERE user_id = {v} AND guild_id = {v}".format(
                self.view, command_name, v=self._fmtr),
            (user.id, guild.id)
        )

    async def reset_cooldown(self, user: discord.Member, guild: discord.Guild, command_name: str) -> None:
        options = await self.get_cooldown(user, guild, command_name)
        if options is None:
            return

        if options.count > 1:
            options.count -= 1
            await self.update_cooldown(user, guild, command_name, options)
        else:
            await self.remove_cooldown(user, guild, command_name)


class _Channels:
    def __init__(self, db: Database):
        self._db = db
        self._table_prefix = self._db.table_prefix
        self._fmtr = self._db.fmtr

        self.view = f"`{self._table_prefix}_channel`"

    async def add_column(self, command_name: str) -> None:
        try:
            self._db.run("ALTER TABLE {} ADD `{}` LONGTEXT DEFAULT NULL".format(self.view, command_name))
        except:
            pass

    async def add_user(self, user: discord.Member, channel: discord.TextChannel):
        data = self._db.execute(
            "SELECT * FROM {} WHERE user_id = {v} AND channel_id = {v}".format(self.view, v=self._fmtr),
            (user.id, channel.id)
        )
        if data is None:
            self._db.run(
                "INSERT INTO {}(user_id, channel_id) VALUES({v}, {v})".format(
                    self.view, v=self._fmtr),
                (user.id, channel.id)
            )

    async def get_cooldown(
        self, user: discord.Member, channel: discord.TextChannel, command_name: str
    ) -> Optional[Options]:
        data = self._db.execute(
            "SELECT {} FROM {} WHERE user_id = {v} AND channel_id = {v}".format(command_name, self.view, v=self._fmtr),
            (user.id, channel.id)
        )
        if data is None:
            await self.add_user(user, channel)
            return None
        if data[0] is None:
            return None

        options = json.loads(data[0])
        return Options.from_dict(options)

    async def update_cooldown(
        self, user: discord.Member, channel: discord.TextChannel, command_name: str, options: Options
    ) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = {v} WHERE user_id = {v} AND channel_id = {v}".format(
                self.view, command_name, v=self._fmtr),
            (json.dumps(options.toJSON()), user.id, channel.id)
        )

    async def remove_cooldown(self, user: discord.Member, channel: discord.TextChannel, command_name: str) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = NULL WHERE user_id = {v} AND channel_id = {v}".format(
                self.view, command_name, v=self._fmtr),
            (user.id, channel.id)
        )

    async def reset_cooldown(self, user: discord.Member, channel: discord.TextChannel, command_name: str) -> None:
        options = await self.get_cooldown(user, channel, command_name)
        if options is None:
            return

        if options.count > 1:
            options.count -= 1
            await self.update_cooldown(user, channel, command_name, options)
        else:
            await self.remove_cooldown(user, channel, command_name)


class _Categories:
    def __init__(self, db: Database):
        self._db = db
        self._table_prefix = self._db.table_prefix
        self._fmtr = self._db.fmtr

        self.view = f"`{self._table_prefix}_category`"

    async def add_column(self, command_name: str) -> None:
        try:
            self._db.run("ALTER TABLE {} ADD `{}` LONGTEXT DEFAULT NULL".format(self.view, command_name))
        except:
            pass

    async def add_user(self, user: discord.Member, category: discord.CategoryChannel):
        data = self._db.execute(
            "SELECT * FROM {} WHERE user_id = {v} AND category_id = {v}".format(self.view, v=self._fmtr),
            (user.id, category.id)
        )
        if data is None:
            self._db.run(
                "INSERT INTO {}(user_id, category_id) VALUES({v}, {v})".format(
                    self.view, v=self._fmtr),
                (user.id, category.id)
            )

    async def get_cooldown(
        self, user: discord.Member, category: discord.CategoryChannel, command_name: str
    ) -> Optional[Options]:
        data = self._db.execute(
            "SELECT {} FROM {} WHERE user_id = {v} AND category_id = {v}".format(command_name, self.view, v=self._fmtr),
            (user.id, category.id)
        )
        if data is None:
            await self.add_user(user, category)
            return None
        if data[0] is None:
            return None

        options = json.loads(data[0])
        return Options.from_dict(options)

    async def update_cooldown(
        self, user: discord.Member, category: discord.CategoryChannel, command_name: str, options: Options
    ) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = {v} WHERE user_id = {v} AND category_id = {v}".format(
                self.view, command_name, v=self._fmtr),
            (json.dumps(options.toJSON()), user.id, category.id)
        )

    async def remove_cooldown(
        self, user: discord.Member, category: discord.CategoryChannel, command_name: str
    ) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = NULL WHERE user_id = {v} AND category_id = {v}".format(
                self.view, command_name, v=self._fmtr),
            (user.id, category.id)
        )

    async def reset_cooldown(self, user: discord.Member, category: discord.CategoryChannel, command_name: str) -> None:
        options = await self.get_cooldown(user, category, command_name)
        if options is None:
            return

        if options.count > 1:
            options.count -= 1
            await self.update_cooldown(user, category, command_name, options)
        else:
            await self.remove_cooldown(user, category, command_name)


class _Roles:
    def __init__(self, db: Database):
        self._db = db
        self._table_prefix = self._db.table_prefix
        self._fmtr = self._db.fmtr

        self.view = f"`{self._table_prefix}_role`"

    async def add_column(self, command_name: str) -> None:
        try:
            self._db.run("ALTER TABLE {} ADD `{}` LONGTEXT DEFAULT NULL".format(self.view, command_name))
        except:
            pass

    async def add_user(self, user: discord.Member, role: discord.Role):
        data = self._db.execute(
            "SELECT * FROM {} WHERE user_id = {v} AND role_id = {v}".format(self.view, v=self._fmtr),
            (user.id, role.id)
        )
        if data is None:
            self._db.run(
                "INSERT INTO {}(user_id, role_id) VALUES({v}, {v})".format(
                    self.view, v=self._fmtr),
                (user.id, role.id)
            )

    async def get_cooldown(
        self, user: discord.Member, role: discord.Role, command_name: str
    ) -> Optional[Options]:
        data = self._db.execute(
            "SELECT {} FROM {} WHERE user_id = {v} AND role_id = {v}".format(command_name, self.view, v=self._fmtr),
            (user.id, role.id)
        )
        if data is None:
            await self.add_user(user, role)
            return None
        if data[0] is None:
            return None

        options = json.loads(data[0])
        return Options.from_dict(options)

    async def update_cooldown(
        self, user: discord.Member, role: discord.Role, command_name: str, options: Options
    ) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = {v} WHERE user_id = {v} AND role_id = {v}".format(
                self.view, command_name, v=self._fmtr),
            (json.dumps(options.toJSON()), user.id, role.id)
        )

    async def remove_cooldown(self, user: discord.Member, role: discord.Role, command_name: str) -> None:
        self._db.run(
            "UPDATE {} SET `{}` = NULL WHERE user_id = {v} AND role_id = {v}".format(
                self.view, command_name, v=self._fmtr),
            (user.id, role.id)
        )

    async def reset_cooldown(self, user: discord.Member, role: discord.Role, command_name: str) -> None:
        options = await self.get_cooldown(user, role, command_name)
        if options is None:
            return

        if options.count > 1:
            options.count -= 1
            await self.update_cooldown(user, role, command_name, options)
        else:
            await self.remove_cooldown(user, role, command_name)


def get_datetime(seconds: int | float = None, timezone: timedelta = None) -> datetime:
    cur_time = datetime.utcnow()
    if timezone is not None:
        cur_time = cur_time + timezone

    if seconds is None:
        return cur_time.replace(microsecond=0)

    return (cur_time + timedelta(seconds=seconds)).replace(microsecond=0)


class Cooldowns:
    def __init__(self, db: Database):
        self._db = db
        self._table_prefix = self._db.table_prefix
        self._fmtr = self._db.fmtr

    def create_tables(self) -> None:
        """
        Creates required tables for cooldown of all types: BucketType

        :return:
        """

        # User type cooldown
        self._db.run(
            "CREATE TABLE IF NOT EXISTS {}(user_id BIGINT NOT NULL)".format(
                f"`{self._table_prefix}_user`")
        )

        # Guild type cooldown
        self._db.run(
            "CREATE TABLE IF NOT EXISTS {}(user_id BIGINT NOT NULL, guild_id BIGINT NOT NULL)".format(
                f"`{self._table_prefix}_guild`")
        )

        # Channel type cooldown
        self._db.run(
            "CREATE TABLE IF NOT EXISTS {}(user_id BIGINT NOT NULL, channel_id BIGINT NOT NULL)".format(
                f"`{self._table_prefix}_channel`")
        )

        # Category type cooldown
        self._db.run(
            "CREATE TABLE IF NOT EXISTS {}(user_id BIGINT NOT NULL, category_id BIGINT NOT NULL)".format(
                f"`{self._table_prefix}_category`")
        )

        # Role type cooldown
        self._db.run(
            "CREATE TABLE IF NOT EXISTS {}(user_id BIGINT NOT NULL, role_id BIGINT NOT NULL)".format(
                f"`{self._table_prefix}_role`")
        )

    @property
    def users(self) -> _Users:
        return _Users(self._db)

    @property
    def guilds(self) -> _Guilds:
        return _Guilds(self._db)

    @property
    def channels(self) -> _Channels:
        return _Channels(self._db)

    @property
    def categories(self) -> _Categories:
        return _Categories(self._db)

    @property
    def roles(self) -> _Roles:
        return _Roles(self._db)
