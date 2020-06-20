from datasette.app import Datasette
import pytest
import httpx


@pytest.fixture
@pytest.mark.asyncio
async def app(tmpdir):
    data = tmpdir / "data.db"
    ds = Datasette([data])
    await ds.invoke_startup()
    yield ds.app()


@pytest.mark.asyncio
async def test_plugin_is_installed(app):
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/-/plugins.json")
        assert 200 == response.status_code
        installed_plugins = {p["name"] for p in response.json()}
        assert "datasette-saved-queries" in installed_plugins


@pytest.mark.asyncio
async def test_table_created(app):
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/data/saved_queries.json")
        assert 200 == response.status_code
        assert ["name", "sql", "author_id"] == response.json()["columns"]


@pytest.mark.asyncio
async def test_save_query(app):
    async with httpx.AsyncClient(app=app) as client:
        # Get the csrftoken cookie
        response1 = await client.get("http://localhost/data/save_query")
        # Now save a new query
        response2 = await client.post(
            "http://localhost/data/save_query",
            data={
                "name": "new_query",
                "sql": "select * from sqlite_master",
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
            {
                "name": "new_query",
                "sql": "select * from sqlite_master",
                "author_id": None,
            }
        ] == response3.json()
