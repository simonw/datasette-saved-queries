from datasette import hookimpl
import sqlite_utils


def create_tables(conn):
    db = sqlite_utils.Database(conn)
    if not db["saved_queries"].exists():
        db["saved_queries"].create(
            {"name": str, "sql": str, "author_id": str,}, pk="name"
        )


@hookimpl
def startup(datasette):
    async def inner():
        db = datasette.get_database()
        await db.execute_write_fn(create_tables, block=True)

    return inner
