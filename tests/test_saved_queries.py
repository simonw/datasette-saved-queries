from datasette.app import Datasette
import pytest
import sqlite3
import httpx


@pytest.fixture
def db_path(tmpdir):
    data = tmpdir / "data.db"
    sqlite3.connect(data).execute("vacuum")
    yield data


@pytest.fixture
@pytest.mark.asyncio
async def ds(db_path):
    ds = Datasette([db_path])
    await ds.invoke_startup()
    yield ds


@pytest.mark.asyncio
async def test_plugin_is_installed(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/-/plugins.json")
        assert 200 == response.status_code
        installed_plugins = {p["name"] for p in response.json()}
        assert "datasette-saved-queries" in installed_plugins


@pytest.mark.asyncio
async def test_table_created(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/data/saved_queries.json")
        assert 200 == response.status_code
        assert ["name", "sql", "author_id"] == response.json()["columns"]


@pytest.mark.asyncio
async def test_save_query(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        # Get the csrftoken cookie
        response1 = await client.get("http://localhost/data/save_query")
        # Now save a new query
        response2 = await client.post(
            "http://localhost/data/save_query",
            data={
                "name": "new_query",
                "sql": "select 1 + 1",
                "csrftoken": response1.cookies["ds_csrftoken"],
            },
            allow_redirects=False,
        )
        assert 302 == response2.status_code
        # Check the query was saved
        response3 = await client.get(
            "http://localhost/data/saved_queries.json?_shape=array"
        )
        assert [
            {"name": "new_query", "sql": "select 1 + 1", "author_id": None,}
        ] == response3.json()
        # ... and that we can run the query
        response3 = await client.get(
            "http://localhost/data/new_query.json?_shape=array"
        )
        assert [{"1 + 1": 2}] == response3.json()


@pytest.mark.asyncio
async def test_save_query_authenticated_actor(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response1 = await client.get("http://localhost/data/save_query")
        response2 = await client.post(
            "http://localhost/data/save_query",
            data={
                "name": "new_query",
                "sql": "select 1 + 1",
                "csrftoken": response1.cookies["ds_csrftoken"],
            },
            cookies={"ds_actor": ds.sign({"a": {"id": "root"}}, "actor")},
            allow_redirects=False,
        )
        assert 302 == response2.status_code
        response3 = await client.get(
            "http://localhost/data/saved_queries.json?_shape=array"
        )
        assert [
            {"name": "new_query", "sql": "select 1 + 1", "author_id": "root",}
        ] == response3.json()


@pytest.mark.asyncio
async def test_dont_crash_on_immutable_database(db_path):
    ds = Datasette([], immutables=[str(db_path)])
    await ds.invoke_startup()
