import discord
import sqlite3
import mysql.connector as mysql
import psycopg2

import threading
import asyncio
from typing import Optional, Union, List, Tuple, Callable, Any
from datetime import datetime
from discord.ext.commands import BucketType


def run_async(target: Callable, *args, **kwargs) -> Optional[Any]:
    class RunThread(threading.Thread):
        def __init__(self, func: Callable):
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.result = None
            super().__init__()

        def run(self):
            self.result = self.func(*self.args, **self.kwargs)

    thread = RunThread(target)
    thread.start()
    thread.join()
    return thread.result


class SQlite:
    def __init__(self, filename: str = None, table_name: str = "cooldowns"):
        """
        Use this to store the cooldown commands data in database files with `.db` extension

        :param filename: takes the filename or path of the file
        :param table_name: By default it's cooldowns, if provided the table will be created with the given name
        """

        self.filename = "CustomCooldowns.db" if filename is None else filename
        self.table_name = table_name

        self.connector = lambda: sqlite3.connect(self.filename)


class MySQL:
    def __init__(self, host: str, db_name: str, user: str, passwd: str, *, table_name: str = "cooldowns"):
        """
        Use this to store the cooldown commands data in MySQL database

        :param host: Where the MySQL server is being hosted
        :param db_name: Name of the database/ schema
        :param user: Name of the user/ root who has access to the database/ schema
        :param passwd: Password of the given user
        :param table_name: By default it's cooldowns, if provided the table will be created with the given name
        """

        self.DB_HOST: str = host
        self.DB_NAME: str = db_name
        self.DB_USER: str = user
        self.DB_PASSWD: str = passwd
        self.table_name = table_name

        self.connector = lambda: mysql.connect(host=self.DB_HOST, user=self.DB_USER,
                                               passwd=self.DB_PASSWD, database=self.DB_NAME)


class PostgreSQL:
    def __init__(self, host: str, db_name: str, user: str, passwd: str, port: str, *, table_name: str = "cooldowns"):
        """
        Use this to store the cooldown commands data in PostgreSQL database

        :param host: Where the PostgreSQL server is being hosted
        :param db_name: Name of the database/ schema
        :param user: Name of the user/ root who has access to the database/ schema
        :param passwd: Password of the given user
        :param port: Port of the PostgreSQL server
        :param table_name: By default it's cooldowns, if provided the table will be created with the given name
        """

        self.DB_HOST: str = host
        self.DB_PORT: str = port
        self.DB_NAME: str = db_name
        self.DB_USER: str = user
        self.DB_PASSWD: str = passwd
        self.table_name = table_name

        self.connector = lambda: psycopg2.connect(host=self.DB_HOST, port=self.DB_PORT, user=self.DB_USER,
                                                  passwd=self.DB_PASSWD, database=self.DB_NAME)


class CooldownsDB:
    def __init__(self, database: Union[MySQL, SQlite, PostgreSQL], /):
        if database.connector is None:
            raise RuntimeError("Something went wrong !")
        else:
            self.database = database
            self.table_name = database.table_name

    def update_cooldowns(self):
        db = self.database.connector()
        cursor = db.cursor()

        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} (userID BIGINT)")
        db.commit()

        cursor.close()
        db.close()

    def open_cd(self, user: Union[discord.Member, discord.Guild]):
        run_async(self.update_cooldowns)

        db = self.database.connector()
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM {self.table_name} WHERE userID = {user.id}")
        data = cursor.fetchone()
        if data is None:
            cursor.execute(f"INSERT INTO {self.table_name}(userID) VALUES({user.id})")
            db.commit()

        cursor.close()
        db.close()

    def add_column(self, column_name: str):
        db = self.database.connector()
        cursor = db.cursor()

        try:
            cursor.execute(f"ALTER TABLE {self.table_name} ADD COLUMN `{column_name}` LONGTEXT")
            db.commit()
        except:
            pass

        cursor.close()
        db.close()

    def get_cd(self, user: Union[discord.Member, discord.Guild],
               mode: str) -> Optional[Tuple[int, int, Optional[datetime]]]:
        db = self.database.connector()
        cursor = db.cursor()

        cursor.execute(f"SELECT `{mode}` FROM {self.table_name} WHERE userID = {user.id}")
        data: Optional[str] = cursor.fetchone()

        cursor.close()
        db.close()

        if data is None or data[0] is None:
            return None

        CD: List = [mode_.strip() for mode_ in data[0].split(',', 3)]
        rate = int(CD[0])
        per = int(CD[1])
        try:
            cooldown = datetime.strptime(CD[2], "%Y-%m-%d %H:%M:%S")
        except:
            cooldown = None

        return rate, per, cooldown

    def create_cd(self, user: Union[discord.Member, discord.Guild], mode: str, *, rate: int, per: int,
                  cooldown: str):
        db = self.database.connector()
        cursor = db.cursor()

        cursor.execute(
            f"UPDATE {self.table_name} SET `{mode}` = '{', '.join([str(rate), str(per), str(cooldown)])}' WHERE userID = {user.id}")
        db.commit()

        cursor.close()
        db.close()

    def update_cd(self, user: Union[discord.Member, discord.Guild], mode: str, *, rate: int = None,
                  per: int = None, cooldown: str = None):
        db = self.database.connector()
        cursor = db.cursor()

        try:
            cmd_rate, cmd_per, cmd_cd = run_async(self.get_cd, user, mode)
        except:
            cmd_rate = cmd_per = 0
            cmd_cd = None

        if rate is None and per is None and cooldown is None:
            raise AttributeError("Provide value for atleat one parameter which you want to update !")

        if rate is not None:
            cmd_rate = cmd_rate + rate
        if per is not None:
            cmd_per = cmd_per + per
        if cooldown is not None:
            cmd_cd = cooldown

        cursor.execute(
            f"UPDATE {self.table_name} SET `{mode}` = '{', '.join([str(cmd_rate), str(cmd_per), str(cmd_cd)])}' "
            f"WHERE userID = {user.id} ")
        db.commit()

        cursor.close()
        db.close()

    def reset_cd(self, user: Union[discord.Member, discord.Guild], mode: str):
        db = self.database.connector()
        cursor = db.cursor()

        cursor.execute(
            F"UPDATE {self.table_name} SET `{mode}` = NULL WHERE userID = {user.id}")
        db.commit()

        cursor.close()
        db.close()


class BucketTypes(BucketType):
    """
    Used to overwrite BucketType

    Available BucketType's: user

    more BucketType's will be implemented soon in further updates
    """

    # Available BucketType's
    user = BucketType.user
    guild = user

    # Will be implemented soon, it then their value will be overwritten to `BucketType.user`
    category = user
    channel = user
    role = user
    member = user
