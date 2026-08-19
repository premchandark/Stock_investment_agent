"""
Core environment logic for the Stock Investment Agent environment.

One StockInvestmentEnvironment instance is created per HTTP session by the FastAPI app.
"""

from __future__ import annotations

import uuid
from typing import Any

from .graders import grade_action
from .tasks import ALL_TASKS


class StockInvestmentEnvironment:
    """
    Stateful equity / multi-asset research environment implementing the OpenEnv interface.

    Supports four tasks with increasing complexity:
        nifty_screen     (easy)    – 5 Nifty 50 large-caps, benchmark-relative stance only
        sector_rotation  (medium)  – 10 cross-sector names + risk tier + metals thesis
        portfolio_risk   (hard)    – 15 multi-cap names + risk tier + three event-driven theses
        rbi_stress       (expert)  – 12 names + hedge flag + green-energy NBFC thesis
    """

    def __init__(self) -> None:
        self._task_cfg: dict[str, Any] = {}
        self._episode_id: str = ""
        self._step_count: int = 0
        self._decided: dict[str, Any] = {}
        self._cumulative_reward: float = 0.0
        self._done: bool = False

    # ─── Public API ─────────────────────────────────────────────────────────

    def reset(self, task_name: str = "nifty_screen", seed: int | None = None) -> dict[str, Any]:
        """
        Reset the environment for a new episode.

        Args:
            task_name: One of 'nifty_screen', 'sector_rotation', 'portfolio_risk', 'rbi_stress'.
            seed:      Optional seed (unused; provided for API compatibility).

        Returns:
            Observation dict.
        """
        if task_name not in ALL_TASKS:
            raise ValueError(f"Unknown task '{task_name}'. Choose from: {list(ALL_TASKS)}")

        self._task_cfg = ALL_TASKS[task_name]
        self._episode_id = str(uuid.uuid4())
        self._step_count = 0
        self._decided = {}
        self._cumulative_reward = 0.0
        self._done = False

        return self._make_observation()

    def step(self, action: dict[str, Any]) -> dict[str, Any]:
        """
        Execute one portfolio research action (one instrument decision).

        Args:
            action: Dict with keys instrument_id, decision, [risk_tier], [hedge_recommended], [thesis].

        Returns:
            Dict with keys: observation, reward, done, info.
        """
        if self._done:
            return {
                "observation": self._make_observation(),
                "reward": 0.0,
                "done": True,
                "info": {"error": "Episode already finished. Call reset() to start a new episode."},
            }

        self._step_count += 1
        instrument_id: str = action.get("instrument_id", "")

        valid_ids = {e["id"] for e in self._task_cfg.get("instruments", [])}
        if instrument_id not in valid_ids:
            return {
                "observation": self._make_observation(),
                "reward": 0.0,
                "done": False,
                "info": {
                    "error": f"Invalid instrument_id '{instrument_id}'. Valid ids: {sorted(valid_ids)}",
                    "step": self._step_count,
                },
            }

        if instrument_id in self._decided:
            return {
                "observation": self._make_observation(),
                "reward": -0.05,
                "done": False,
                "info": {
                    "warning": f"Instrument '{instrument_id}' was already decided. No credit, -0.05 penalty.",
                    "step": self._step_count,
                },
            }

        reward, reason = grade_action(self._task_cfg, action, self._decided)
        self._decided[instrument_id] = {**action, "_reward": reward, "_reason": reason}
        self._cumulative_reward += reward

        total_n = len(self._task_cfg.get("instruments", []))
        max_steps = self._task_cfg.get("max_steps", total_n)
        all_done = len(self._decided) >= total_n
        out_of_steps = self._step_count >= max_steps

        if all_done or out_of_steps:
            self._done = True

        if self._done:
            if self._cumulative_reward <= 0.0:
                delta = 0.001 - self._cumulative_reward
                self._cumulative_reward = 0.001
                reward += delta
            elif self._cumulative_reward >= 1.0:
                delta = self._cumulative_reward - 0.999
                self._cumulative_reward = 0.999
                reward -= delta

        return {
            "observation": self._make_observation(),
            "reward": round(reward, 6),
            "done": self._done,
            "info": {
                "step": self._step_count,
                "reason": reason,
                "cumulative_reward": round(self._cumulative_reward, 4),
                "instruments_remaining": total_n - len(self._decided),
            },
        }

    def state(self) -> dict[str, Any]:
        """Return current episode metadata (does not duplicate full narratives)."""
        total_n = len(self._task_cfg.get("instruments", []))
        clamped_reward = self._cumulative_reward
        if self._done:
            if clamped_reward <= 0.0:
                clamped_reward = 0.001
            elif clamped_reward >= 1.0:
                clamped_reward = 0.999
        return {
            "episode_id": self._episode_id,
            "task_name": self._task_cfg.get("name", ""),
            "difficulty": self._task_cfg.get("difficulty", ""),
            "step_count": self._step_count,
            "max_steps": self._task_cfg.get("max_steps", 0),
            "instruments_total": total_n,
            "instruments_decided": len(self._decided),
            "instruments_remaining": total_n - len(self._decided),
            "cumulative_reward": round(clamped_reward, 4),
            "done": self._done,
        }

    # ─── Private helpers ─────────────────────────────────────────────────────

    def _make_observation(self) -> dict[str, Any]:
        task = self._task_cfg
        total_n = len(task.get("instruments", []))
        pending = [e for e in task.get("instruments", []) if e["id"] not in self._decided]
        return {
            "task_name": task.get("name", ""),
            "task_description": task.get("description", ""),
            "instructions": task.get("instructions", ""),
            "difficulty": task.get("difficulty", ""),
            "instruments": task.get("instruments", []),
            "decided": self._decided,
            "pending_ids": [e["id"] for e in pending],
            "step": self._step_count,
            "max_steps": task.get("max_steps", total_n),
            "done": self._done,
            "episode_id": self._episode_id,
        }
