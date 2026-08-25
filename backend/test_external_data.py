import httpx
import pytest

import services.external_data as external_data_module
from services.external_data import (
    ExternalDataError,
    get_coordinates,
    get_weather,
)

_RealAsyncClient = httpx.AsyncClient


def _mock_client_factory(handler):
    def _factory(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return _RealAsyncClient(*args, **kwargs)

    return _factory


@pytest.mark.anyio
async def test_get_coordinates_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"results": [{"latitude": 26.85, "longitude": 80.95, "name": "Lucknow"}]},
        )

    monkeypatch.setattr(httpx, "AsyncClient", _mock_client_factory(handler))

    result = await get_coordinates("Lucknow")
    assert result["latitude"] == 26.85
    assert result["name"] == "Lucknow"


@pytest.mark.anyio
async def test_get_coordinates_no_results_raises(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    monkeypatch.setattr(httpx, "AsyncClient", _mock_client_factory(handler))

    with pytest.raises(ExternalDataError):
        await get_coordinates("Nowhereville")


@pytest.mark.anyio
async def test_get_weather_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"current": {"temperature_2m": 30.1, "precipitation": 0.0, "wind_speed_10m": 12.4}},
        )

    monkeypatch.setattr(httpx, "AsyncClient", _mock_client_factory(handler))

    result = await get_weather(26.85, 80.95)
    assert result["temperature_2m"] == 30.1


@pytest.mark.anyio
async def test_get_weather_http_error_raises(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    monkeypatch.setattr(httpx, "AsyncClient", _mock_client_factory(handler))

    with pytest.raises(ExternalDataError):
        await get_weather(0, 0)


@pytest.fixture
def anyio_backend():
    return "asyncio"
