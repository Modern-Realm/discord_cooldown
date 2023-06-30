from typing import Mapping, Any

__all__ = [
    "SQlite",
    "MySQL",
    "PostgreSQL"
]


class SQlite:
    def __init__(self, filename: str = None):
        """
        Use this to store the cooldown commands data in database files with `.db` extension

        :param filename: takes the filename or path of the file
        """

        self.filename = "CustomCooldowns.db" if filename is None else filename
        self.fmtr: str = "?"
        self.table_prefix: str = "cooldowns"  # the table name starts with this prefix

    @property
    def kwargs(self) -> Mapping[str, str]:
        return {"database": self.filename}


class MySQL:
    def __init__(self, host: str, db_name: str, user: str, passwd: str, port: int = 3306):
        """
        Use this to store the cooldown commands data in MySQL database

        :param host: Where the MySQL server is being hosted
        :param db_name: Name of the database/ schema
        :param user: Name of the user/ root who has access to the database/ schema
        :param passwd: Password of the given user
        """

        self.db_host = host
        self.db_port = port
        self.db_name = db_name
        self.db_user = user
        self.db_passwd = passwd

        self.fmtr: str = "%s"
        self.table_prefix: str = "cooldowns"  # the table name starts with this prefix

    @property
    def kwargs(self) -> Mapping[str, Any]:
        return {
            "host": self.db_host, "port": self.db_port, "database": self.db_name,
            "user": self.db_user, "passwd": self.db_passwd,
        }


class PostgreSQL:
    def __init__(self, host: str, db_name: str, user: str, passwd: str, port: int = 5432):
        """
        Use this to store the cooldown commands data in PostgreSQL database

        :param host: Where the PostgreSQL server is being hosted
        :param db_name: Name of the database/ schema
        :param user: Name of the user/ root who has access to the database/ schema
        :param passwd: Password of the given user
        :param port: Port of the PostgreSQL server
        """

        self.db_host = host
        self.db_port = port
        self.db_name = db_name
        self.db_user = user
        self.db_passwd = passwd

        self.fmtr: str = "%s"
        self.table_prefix: str = "cooldowns"  # the table name starts with this prefix

    @property
    def kwargs(self) -> Mapping[str, Any]:
        return {
            "host": self.db_host, "port": self.db_port, "database": self.db_name,
            "user": self.db_user, "passwd": self.db_passwd,
        }
