
from fastapi.routing import APIRoute

from football_intel.api import app


def test_forecast_endpoint_registered_once():
    routes = [
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == "/v1/forecast"
        and "POST" in route.methods
    ]

    assert len(routes) == 1
