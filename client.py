"""
Async HTTP client for the Stock Investment Agent environment.

Usage
-----
    import asyncio
    from client import StockInvestmentEnv, InvestmentAction

    async def main():
        async with StockInvestmentEnv(base_url="http://localhost:8000") as env:
            result = await env.reset("nifty_screen")
            result = await env.step(
                InvestmentAction(instrument_id="n1", decision="overweight")
            )
            print(result.reward, result.done)

    asyncio.run(main())
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from models import (
    InvestmentAction,
    InvestmentObservation,
    InvestmentState,
    ResetResult,
    StepResult,
)

__all__ = ["StockInvestmentEnv", "InvestmentAction"]


class StockInvestmentEnv:
    """
    Async client for the Stock Investment Agent FastAPI environment.

    Connects to a running server via HTTP. Supports context-manager usage
    and class-method constructors for Docker / HuggingFace Spaces.
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 60.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
        self._timeout = timeout

    async def __aenter__(self) -> "StockInvestmentEnv":
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @classmethod
    def from_docker_image(cls, image_name: str | None, port: int = 8000) -> "StockInvestmentEnv":
        """
        Compatibility constructor – connects to a locally running container.
        The container must already be started externally.
        """
        base_url = f"http://localhost:{port}"
        return cls(base_url=base_url)

    @classmethod
    def from_env(cls, space_name: str | None = None) -> "StockInvestmentEnv":
        """Connect to a HuggingFace Space."""
        if space_name:
            base_url = f"https://{space_name.replace('/', '-')}.hf.space"
        else:
            base_url = os.getenv("HF_SPACE_URL", "http://localhost:8000")
        return cls(base_url=base_url)

    async def reset(
        self,
        task_name: str = "nifty_screen",
        seed: int | None = None,
    ) -> ResetResult:
        """Initialise a new episode and return the first observation."""
        resp = await self._ensure_client().post(
            "/reset",
            json={"task_name": task_name, "seed": seed},
        )
        resp.raise_for_status()
        data = resp.json()
        return ResetResult(
            observation=InvestmentObservation(**data["observation"]),
            done=data.get("done", False),
            info=data.get("info", {}),
        )

    async def step(self, action: InvestmentAction) -> StepResult:
        """Execute one instrument decision."""
        resp = await self._ensure_client().post(
            "/step",
            json=action.model_dump(),
        )
        resp.raise_for_status()
        data = resp.json()
        return StepResult(
            observation=InvestmentObservation(**data["observation"]),
            reward=data.get("reward", 0.0),
            done=data.get("done", False),
            info=data.get("info", {}),
        )

    async def state(self) -> InvestmentState:
        """Return current episode metadata."""
        resp = await self._ensure_client().get("/state")
        resp.raise_for_status()
        return InvestmentState(**resp.json())

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self._client
