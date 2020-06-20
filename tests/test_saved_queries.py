from datasette.app import Datasette
import pytest
import httpx


@pytest.mark.asyncio
async def test_plugin_is_installed():
    app = Datasette([], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/-/plugins.json")
        assert 200 == response.status_code
        installed_plugins = {p["name"] for p in response.json()}
        assert "datasette-saved-queries" in installed_plugins


@pytest.mark.asyncio
async def test_table_created(tmpdir):
    data = tmpdir / "data.db"
    ds = Datasette([data])
    await ds.invoke_startup()
    app = ds.app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/data/saved_queries.json")
        assert 200 == response.status_code
        assert ["name", "sql", "author_id"] == response.json()["columns"]
