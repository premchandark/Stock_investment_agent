"""
Pydantic models for the Stock Investment Agent environment.

These are the typed models used by both the server and the client.
Inherits from openenv-core base classes when available, falls back to
plain Pydantic models for standalone operation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

try:
    from openenv.core.env_server.types import Action, Observation, State  # type: ignore
    _OPENENV_AVAILABLE = True
except ImportError:
    Action = BaseModel        # type: ignore[misc,assignment]
    Observation = BaseModel   # type: ignore[misc,assignment]
    State = BaseModel         # type: ignore[misc,assignment]
    _OPENENV_AVAILABLE = False


# ─── Domain model ────────────────────────────────────────────────────────────

class Instrument(BaseModel):
    """A single research scenario the agent must act on (one step = one instrument)."""

    id: str
    symbol: str
    company: str
    sector: str
    headline: str
    narrative: str
    as_of: str


# ─── Action ──────────────────────────────────────────────────────────────────

class InvestmentAction(Action):  # type: ignore[valid-type]
    """Action submitted by the agent for a single instrument decision."""

    instrument_id: str = Field(..., description="ID of the instrument row to decide")
    decision: str = Field(
        ...,
        description="'overweight' | 'neutral' | 'underweight' — relative conviction vs benchmark",
    )
    risk_tier: str | None = Field(
        default=None,
        description="'defensive' | 'balanced' | 'aggressive' — required on medium+ tasks",
    )
    hedge_recommended: bool | None = Field(
        default=None,
        description="True if a hedge/overlay is warranted on this name (expert task)",
    )
    thesis: str | None = Field(
        default=None,
        description="Short investment thesis / trade rationale when required by the task",
    )


# ─── Observation ─────────────────────────────────────────────────────────────

class InvestmentObservation(Observation):  # type: ignore[valid-type]
    """Observation returned after reset() or step()."""

    task_name: str
    task_description: str
    instructions: str
    difficulty: str
    instruments: list[Instrument]
    decided: dict[str, Any]          # instrument_id → action record
    pending_ids: list[str]
    step: int
    max_steps: int
    done: bool
    episode_id: str


# ─── State ───────────────────────────────────────────────────────────────────

class InvestmentState(State):  # type: ignore[valid-type]
    """Lightweight episode metadata returned by state()."""

    episode_id: str
    task_name: str
    difficulty: str
    step_count: int
    max_steps: int
    instruments_total: int
    instruments_decided: int
    instruments_remaining: int
    cumulative_reward: float
    done: bool


# ─── Step result ─────────────────────────────────────────────────────────────

class StepResult(BaseModel):
    """Wrapper returned by the async client's step() / reset() methods."""

    observation: InvestmentObservation
    reward: float = 0.0
    done: bool = False
    info: dict[str, Any] = Field(default_factory=dict)


class ResetResult(BaseModel):
    observation: InvestmentObservation
    done: bool = False
    info: dict[str, Any] = Field(default_factory=dict)
