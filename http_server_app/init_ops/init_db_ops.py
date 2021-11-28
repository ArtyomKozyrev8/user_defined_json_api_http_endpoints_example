import aiosqlite
import os


def _create_db_file_if_not_exist() -> bool:
    """
    Creates SQLITE3 database.db file and returns True if file was created, otherwise returns False.
    True indicates that tables should be created in the next step, False indicates that no
    further steps are required.
    :return: True/False
    """
    # creates directory to store database
    if not os.path.exists(os.path.join(os.getcwd(), "database")):
        os.mkdir(os.path.join(os.getcwd(), "database"))

    # creates database file if it does not exist
    if not os.path.exists(os.path.join(os.getcwd(), "database", "database.db")):
        with open(os.path.join(os.getcwd(), "database", "database.db"), mode="wb"):
            return True  # should create table in the next step

    return False  # no need to create tables in the next step


async def _create_json_schemas_table(conn: aiosqlite.Connection) -> None:
    """
    user_defined_json_http_api_schemas_table - is the table which stores json schemas which are defined
    by api users.
    Schemas are Rules, which are used to process json messages to api endpoints according to these Rules.
    :param conn:  aiosqlite.Connection
    :return: None
    """
    q = """
    CREATE TABLE IF NOT EXISTS user_defined_json_http_api_schemas_table (
        id integer PRIMARY KEY,
        json_schema_name VARCHAR(50) NOT NULL UNIQUE,
        json_shema_value text NOT NULL
    );
    """
    await conn.execute(q)


async def init_db() -> aiosqlite.Connection:
    """Is used to initialize SQLITE3 database for the app"""
    do_create_tables = _create_db_file_if_not_exist()
    conn = await aiosqlite.connect(os.path.join(os.getcwd(), "database", "database.db"))
    if do_create_tables:
        await _create_json_schemas_table(conn)
    return conn
