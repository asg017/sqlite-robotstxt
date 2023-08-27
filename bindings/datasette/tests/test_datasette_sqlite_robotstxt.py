from datasette.app import Datasette
import pytest


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-sqlite-robotstxt" in installed_plugins

@pytest.mark.asyncio
async def test_sqlite_robotstxt_functions():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/_memory.json?sql=select+robotstxt_version(),robotstxt('alex')")
    assert response.status_code == 200
    robotstxt_version, robotstxt = response.json()["rows"][0]
    assert robotstxt_version[0] == "v"
    assert len(robotstxt) == 26
