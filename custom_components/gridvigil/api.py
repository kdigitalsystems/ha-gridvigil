"""Minimal client for the public GridVigil API (no key required)."""

from typing import Any

import aiohttp

from .const import API_BASE


class GridVigilApiError(Exception):
    """The API could not be reached or returned something unusable."""


async def _get_json(session: aiohttp.ClientSession, path: str) -> Any:
    try:
        async with session.get(f"{API_BASE}{path}", timeout=aiohttp.ClientTimeout(total=30)) as resp:
            resp.raise_for_status()
            # The API is served as static files, and some responses carry
            # application/octet-stream rather than application/json; the body
            # is always JSON, so skip aiohttp's content-type check.
            return await resp.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError, ValueError) as err:
        raise GridVigilApiError(f"Could not fetch {path}: {err}") from err


async def fetch_grids(session: aiohttp.ClientSession) -> list[dict[str, Any]]:
    """Every supported grid, for the setup dropdown."""
    data = await _get_json(session, "/grids")
    return data["grids"]


async def fetch_status(session: aiohttp.ClientSession, grid_id: str) -> dict[str, Any]:
    """One grid's current status."""
    return await _get_json(session, f"/grid/{grid_id}/status")
