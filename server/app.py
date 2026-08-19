"""
FastAPI server for the Stock Investment Agent environment.

Endpoints
---------
POST /reset          – Start a new episode. Body: {"task_name": "<name>", "seed": null}
POST /step           – Execute one instrument decision.
GET  /state          – Return current episode metadata.
GET  /health         – Health check (returns 200 OK).
GET  /info           – Environment metadata (tasks, difficulty levels).
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import gradio as gr

from .environment import StockInvestmentEnvironment
from .tasks import ALL_TASKS
from .ui import demo as gradio_demo

_env: StockInvestmentEnvironment = StockInvestmentEnvironment()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _env.reset("nifty_screen")
    yield


app = FastAPI(
    title="Stock Investment Agent Environment",
    description=(
        "Indian stock market portfolio research RL environment for the "
        "Scaler × Meta PyTorch OpenEnv Hackathon. Four tasks: nifty_screen (easy), "
        "sector_rotation (medium), portfolio_risk (hard), rbi_stress (expert)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ─── Request / Response models ────────────────────────────────────────────────

class ResetRequest(BaseModel):
    task_name: str = Field(default="nifty_screen", description="Task to initialise")
    seed: int | None = Field(default=None, description="Optional random seed (unused)")


class InvestmentActionRequest(BaseModel):
    instrument_id: str = Field(..., description="ID of the instrument row to decide")
    decision: str = Field(
        ...,
        description="'overweight' | 'neutral' | 'underweight' — vs policy benchmark",
    )
    risk_tier: str | None = Field(
        default=None,
        description="'defensive' | 'balanced' | 'aggressive' (medium+ tasks)",
    )
    hedge_recommended: bool | None = Field(
        default=None,
        description="True if hedging/overlay warranted (rbi_stress)",
    )
    thesis: str | None = Field(default=None, description="Rationale when required by task")


# ─── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/info")
async def info() -> dict[str, Any]:
    return {
        "name": "stock-investment-agent",
        "version": "1.0.0",
        "tasks": [
            {
                "name": cfg["name"],
                "difficulty": cfg["difficulty"],
                "description": cfg["description"],
                "max_steps": cfg["max_steps"],
                "num_instruments": len(cfg["instruments"]),
            }
            for cfg in ALL_TASKS.values()
        ],
    }


@app.post("/reset")
async def reset(body: ResetRequest = ResetRequest()) -> dict[str, Any]:
    try:
        observation = _env.reset(task_name=body.task_name, seed=body.seed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "observation": observation,
        "done": False,
        "info": {
            "task_name": body.task_name,
            "episode_id": observation["episode_id"],
        },
    }


@app.post("/step")
async def step(action: InvestmentActionRequest) -> dict[str, Any]:
    result = _env.step(action.model_dump())
    return result


@app.get("/state")
async def state() -> dict[str, Any]:
    return _env.state()


# ─── Mount Gradio UI at root (after all API routes) ─────────────────────────

app = gr.mount_gradio_app(app, gradio_demo, path="/")

# ─── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port, workers=1)


if __name__ == "__main__":
    main()
