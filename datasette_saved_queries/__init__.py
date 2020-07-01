from datasette import hookimpl
import sqlite_utils


def create_tables(conn):
    db = sqlite_utils.Database(conn)
    if not db["saved_queries"].exists():
        db["saved_queries"].create(
            {"name": str, "sql": str, "author_id": str,}, pk="name"
        )


def actorornull(key, request):
    if request.actor is None:
        return None
    return request.actor.get(key)


@hookimpl
def register_magic_parameters():
    return [
        ("actorornull", actorornull),
    ]


@hookimpl
def startup(datasette):
    async def inner():
        db = datasette.get_database()
        await db.execute_write_fn(create_tables, block=True)

    return inner


@hookimpl
def canned_queries(datasette, database):
    async def inner():
        db = datasette.get_database(database)
        if await db.table_exists("saved_queries"):
            queries = {
                row["name"]: {"sql": row["sql"]}
                for row in await db.execute("select name, sql from saved_queries")
            }
            queries.update(
                {
                    "save_query": {
                        "sql": "insert into saved_queries (name, sql, author_id) values (:name, :sql, :_actorornull_id)",
                        "write": True,
                        "on_success_redirect": "/{}#queries".format(database),
                    }
                }
            )
            return queries

    return inner
