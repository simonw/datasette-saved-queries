from datasette.app import Datasette
import pytest
import sqlite3


@pytest.fixture
def db_path(tmpdir):
    data = str(tmpdir / "data.db")
    sqlite3.connect(data).execute("vacuum")
    yield data


@pytest.fixture
def ds(db_path):
    return Datasette([db_path])


@pytest.mark.asyncio
async def test_plugin_is_installed(ds):
    response = await ds.client.get("/-/plugins.json")
    assert 200 == response.status_code
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-saved-queries" in installed_plugins


@pytest.mark.asyncio
async def test_table_created(ds):
    response = await ds.client.get("/data/saved_queries.json")
    assert 200 == response.status_code
    assert ["name", "sql", "author_id"] == response.json()["columns"]


@pytest.mark.asyncio
async def test_save_query(ds):
    # Get the csrftoken cookie
    response1 = await ds.client.get("/data/save_query")
    # Now save a new query
    response2 = await ds.client.post(
        "/data/save_query",
        data={
            "name": "new_query",
            "sql": "select 1 + 1",
            "csrftoken": response1.cookies["ds_csrftoken"],
        },
    )
    assert 302 == response2.status_code
    # Check the query was saved
    response3 = await ds.client.get("/data/saved_queries.json?_shape=array")
    assert [
        {
            "name": "new_query",
            "sql": "select 1 + 1",
            "author_id": None,
        }
    ] == response3.json()
    # ... and that we can run the query
    response3 = await ds.client.get("/data/new_query.json?_shape=array")
    assert [{"1 + 1": 2}] == response3.json()


@pytest.mark.asyncio
async def test_save_query_authenticated_actor(ds):
    ds_actor = ds.sign({"a": {"id": "root"}}, "actor")
    response1 = await ds.client.get(
        "/data/save_query",
        cookies={"ds_actor": ds_actor},
    )
    csrftoken = response1.cookies["ds_csrftoken"]
    response2 = await ds.client.post(
        "/data/save_query",
        data={
            "name": "new_query",
            "sql": "select 1 + 1",
            "csrftoken": csrftoken,
        },
        cookies={"ds_actor": ds_actor, "ds_csrftoken": csrftoken},
    )
    assert 302 == response2.status_code
    response3 = await ds.client.get("/data/saved_queries.json?_shape=array")
    assert [
        {
            "name": "new_query",
            "sql": "select 1 + 1",
            "author_id": "root",
        }
    ] == response3.json()


@pytest.mark.asyncio
async def test_dont_crash_on_immutable_database(db_path):
    ds = Datasette([], immutables=[db_path])
    await ds.invoke_startup()
