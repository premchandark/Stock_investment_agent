"""
Gradio Blocks interactive UI for the Stock Investment Agent environment.

Three tabs:
  1. AI Agent Demo  – run an LLM agent against any task and watch step-by-step
  2. Play Yourself  – manually decide each instrument and get instant feedback
  3. About          – task descriptions, reward mechanics, and usage guide
"""

from __future__ import annotations

import json
import time
import traceback
from typing import Any

import gradio as gr
from openai import OpenAI

from .environment import StockInvestmentEnvironment
from .tasks import ALL_TASKS

# ────────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ────────────────────────────────────────────────────────────────────────────────

TASK_CHOICES = list(ALL_TASKS.keys())

DIFFICULTY_BADGES = {
    "easy": "🟢 Easy",
    "medium": "🟡 Medium",
    "hard": "🟠 Hard",
    "expert": "🔴 Expert",
}

DECISION_COLORS = {
    "overweight": "#22c55e",
    "neutral": "#6b7280",
    "underweight": "#ef4444",
}


def _badge(decision: str) -> str:
    color = DECISION_COLORS.get(decision, "#6b7280")
    return f'<span style="background:{color};color:white;padding:2px 10px;border-radius:12px;font-weight:600;font-size:0.85em;">{decision}</span>'


def _instrument_card(inst: dict, idx: int) -> str:
    return (
        f"### {idx}. {inst['company']} (`{inst['symbol']}`)\n"
        f"**Sector:** {inst['sector']}  \n"
        f"**Headline:** {inst['headline']}  \n"
        f"**Narrative:** {inst['narrative']}  \n"
        f"*As of {inst['as_of']}*\n"
    )


def _reward_bar_html(score: float, max_score: float = 1.0) -> str:
    pct = min(100, max(0, score / max_score * 100))
    bar_color = "#22c55e" if pct >= 60 else "#eab308" if pct >= 30 else "#ef4444"
    return (
        f'<div style="background:#e5e7eb;border-radius:8px;overflow:hidden;height:28px;margin:4px 0;">'
        f'<div style="background:{bar_color};height:100%;width:{pct:.1f}%;display:flex;align-items:center;'
        f'padding-left:8px;color:white;font-weight:700;font-size:0.85em;min-width:fit-content;">'
        f'{score:.3f} / {max_score:.3f}'
        f'</div></div>'
    )


# ────────────────────────────────────────────────────────────────────────────────
# Tab 1: AI Agent Demo
# ────────────────────────────────────────────────────────────────────────────────

def _run_agent_demo(
    task_name: str,
    api_url: str,
    model_name: str,
    api_key: str,
    progress=gr.Progress(track_tqdm=False),
):
    if not api_url or not model_name or not api_key:
        yield (
            "**Please fill in all three fields:** API URL, Model Name, and API Key.",
            "",
            "---",
        )
        return

    env = StockInvestmentEnvironment()
    client = OpenAI(api_key=api_key, base_url=api_url)
    task_cfg = ALL_TASKS[task_name]
    instruments = task_cfg["instruments"]
    inst_lookup = {i["id"]: i for i in instruments}

    from inference import build_system_prompt, pick_next_instrument, PRIORITY_ORDER

    obs = env.reset(task_name)
    system_prompt = build_system_prompt(task_name, obs["task_description"], obs["instructions"])

    log_lines: list[str] = []
    rewards: list[float] = []
    total_steps = len(instruments)
    t0 = time.time()

    for step_idx in range(1, total_steps + 1):
        pending = obs.get("pending_ids", [])
        if not pending:
            break

        target_id = pick_next_instrument(task_name, pending)
        target = inst_lookup[target_id]
        progress(step_idx / total_steps, desc=f"Step {step_idx}/{total_steps}: {target['symbol']}")

        from inference import build_user_prompt
        user_prompt = build_user_prompt(task_name, target, instruments, pending)

        action = None
        error_msg = None
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=1024,
            )
            raw = (resp.choices[0].message.content or "").strip()
            text = raw
            if text.startswith("```"):
                lines = text.split("\n")
                lines = [ln for ln in lines if not ln.strip().startswith("```")]
                text = "\n".join(lines).strip()
            try:
                action = json.loads(text)
            except json.JSONDecodeError:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    action = json.loads(text[start:end])
        except Exception as e:
            error_msg = str(e)

        if action is None:
            from inference import get_fallback_action
            action = get_fallback_action(task_name, target_id)
            if error_msg:
                error_msg = f"LLM error: {error_msg}; using fallback"
            else:
                error_msg = "Parse error; using fallback"

        action["instrument_id"] = target_id
        result = env.step(action)
        reward = result.get("reward", 0.0)
        rewards.append(reward)
        obs = result["observation"]
        info = result.get("info", {})
        cum_reward = info.get("cumulative_reward", sum(rewards))

        decision = action.get("decision", "?")
        risk = action.get("risk_tier", "")
        hedge = action.get("hedge_recommended", "")
        thesis = action.get("thesis", "")

        step_md = (
            f"**Step {step_idx}** — {target['company']} (`{target['symbol']}`)  \n"
            f"Decision: {_badge(decision)}"
        )
        if risk:
            step_md += f"  Risk: **{risk}**"
        if hedge != "":
            step_md += f"  Hedge: **{'Yes' if hedge else 'No'}**"
        step_md += f"  \nReward: **{reward:.4f}**"
        if thesis:
            step_md += f"  \n> *Thesis:* {thesis}"
        if error_msg:
            step_md += f"  \n⚠️ {error_msg}"
        step_md += "\n\n---\n"

        log_lines.append(step_md)

        steps_md = "\n".join(log_lines)
        reward_html = _reward_bar_html(cum_reward, 1.0)
        elapsed = time.time() - t0
        summary = f"**Steps:** {step_idx}/{total_steps} | **Score:** {cum_reward:.4f} | **Time:** {elapsed:.1f}s"

        yield steps_md, reward_html, summary

    final_state = env.state()
    final_score = final_state.get("cumulative_reward", sum(rewards))
    elapsed = time.time() - t0
    summary = (
        f"### Run Complete\n"
        f"**Task:** {task_name} ({DIFFICULTY_BADGES.get(task_cfg['difficulty'], '')})  \n"
        f"**Final Score:** {final_score:.4f}  \n"
        f"**Steps:** {step_idx}/{total_steps}  \n"
        f"**Time:** {elapsed:.1f}s  \n"
        f"**Model:** {model_name}  \n"
        f"**Per-step rewards:** {', '.join(f'{r:.4f}' for r in rewards)}"
    )
    yield "\n".join(log_lines), _reward_bar_html(final_score, 1.0), summary


# ────────────────────────────────────────────────────────────────────────────────
# Tab 2: Play Yourself
# ────────────────────────────────────────────────────────────────────────────────

_play_envs: dict[str, dict] = {}


def _play_reset(task_name: str):
    env = StockInvestmentEnvironment()
    obs = env.reset(task_name)
    task_cfg = ALL_TASKS[task_name]

    pending = obs.get("pending_ids", [])
    instruments = task_cfg["instruments"]
    inst_lookup = {i["id"]: i for i in instruments}

    session_id = str(id(env))
    _play_envs[session_id] = {
        "env": env,
        "task_name": task_name,
        "task_cfg": task_cfg,
        "inst_lookup": inst_lookup,
        "step": 0,
        "rewards": [],
    }

    if not pending:
        return session_id, "No instruments to decide.", "", "---", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

    first_id = pending[0]
    first = inst_lookup[first_id]
    card = _instrument_card(first, 1)

    needs_risk = task_name in ("sector_rotation", "portfolio_risk", "rbi_stress")
    needs_hedge = task_name == "rbi_stress"
    thesis_ids = _get_thesis_ids(task_name)
    needs_thesis = first_id in thesis_ids

    total = len(instruments)
    status = f"**Instrument 1 / {total}** — ID: `{first_id}` | Score: 0.0000"

    return (
        session_id,
        card,
        "",
        status,
        gr.update(visible=True),
        gr.update(visible=needs_risk),
        gr.update(visible=needs_hedge),
        gr.update(visible=needs_thesis),
        gr.update(visible=True),
    )


def _get_thesis_ids(task_name: str) -> list[str]:
    return ALL_TASKS.get(task_name, {}).get("thesis_required_for", [])


def _play_step(session_id: str, decision: str, risk_tier: str, hedge: str, thesis: str):
    sess = _play_envs.get(session_id)
    if sess is None:
        return "Session expired. Please reset.", "", "---", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

    env: StockInvestmentEnvironment = sess["env"]
    task_name = sess["task_name"]
    task_cfg = sess["task_cfg"]
    inst_lookup = sess["inst_lookup"]
    instruments = task_cfg["instruments"]

    state = env.state()
    if state["done"]:
        return "Episode already done. Reset to play again.", "", "---", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

    obs = env._make_observation()
    pending = obs.get("pending_ids", [])
    if not pending:
        return "All instruments decided!", "", "---", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

    current_id = pending[0]

    action: dict[str, Any] = {
        "instrument_id": current_id,
        "decision": decision.lower().strip(),
    }
    if task_name in ("sector_rotation", "portfolio_risk", "rbi_stress"):
        action["risk_tier"] = risk_tier.lower().strip()
    if task_name == "rbi_stress":
        action["hedge_recommended"] = hedge.lower().strip() == "yes"
    thesis_ids = _get_thesis_ids(task_name)
    if current_id in thesis_ids and thesis.strip():
        action["thesis"] = thesis.strip()

    result = env.step(action)
    reward = result.get("reward", 0.0)
    info = result.get("info", {})
    reason = info.get("reason", "")
    cum_reward = info.get("cumulative_reward", 0.0)
    done = result.get("done", False)

    sess["step"] += 1
    sess["rewards"].append(reward)

    dec_badge = _badge(decision.lower().strip())
    feedback = (
        f"**Result for `{current_id}` ({inst_lookup[current_id]['symbol']}):**  \n"
        f"Your decision: {dec_badge}  \n"
        f"**Reward: {reward:.4f}**  \n"
        f"*Grader: {reason}*\n\n---\n"
    )

    if done:
        final_score = env.state().get("cumulative_reward", cum_reward)
        card = (
            f"### Episode Complete!\n"
            f"**Final Score: {final_score:.4f}**  \n"
            f"**Steps:** {sess['step']}  \n"
            f"**Per-step rewards:** {', '.join(f'{r:.4f}' for r in sess['rewards'])}"
        )
        return (
            card,
            feedback,
            f"**Done!** Final Score: {final_score:.4f}",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )

    new_obs = env._make_observation()
    new_pending = new_obs.get("pending_ids", [])
    if not new_pending:
        return "All instruments decided.", feedback, f"Score: {cum_reward:.4f}", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

    next_id = new_pending[0]
    next_inst = inst_lookup[next_id]
    step_num = sess["step"] + 1
    total = len(instruments)
    card = _instrument_card(next_inst, step_num)

    needs_risk = task_name in ("sector_rotation", "portfolio_risk", "rbi_stress")
    needs_hedge = task_name == "rbi_stress"
    needs_thesis = next_id in thesis_ids

    status = f"**Instrument {step_num} / {total}** — ID: `{next_id}` | Score: {cum_reward:.4f}"

    return (
        card,
        feedback,
        status,
        gr.update(visible=True),
        gr.update(visible=needs_risk),
        gr.update(visible=needs_hedge),
        gr.update(visible=needs_thesis),
        gr.update(visible=True),
    )


# ────────────────────────────────────────────────────────────────────────────────
# Tab 3: About
# ────────────────────────────────────────────────────────────────────────────────

def _build_about_md() -> str:
    md = (
        "# Stock Investment Agent — Indian Market RL Environment\n\n"
        "An **OpenEnv-compatible** reinforcement learning environment for training and evaluating "
        "AI agents on **Indian equity portfolio research**. Built for the "
        "**Scaler School of Technology × Meta / PyTorch OpenEnv Hackathon**.\n\n"
        "---\n\n"
        "## Indian Market Focus\n\n"
        "All scenarios use **real NSE/BSE-listed companies** — Reliance, TCS, HDFC Bank, Adani Enterprises, "
        "Tata Steel, Bharti Airtel, and more — with realistic market narratives drawn from actual "
        "Indian market dynamics. Designed for **practical portfolio research training** relevant to "
        "making money in the Indian stock market.\n\n"
        "---\n\n"
        "## Tasks\n\n"
        "| Task | Difficulty | Instruments | Agent Outputs |\n"
        "|------|-----------|-------------|---------------|\n"
    )

    for name, cfg in ALL_TASKS.items():
        diff = DIFFICULTY_BADGES.get(cfg["difficulty"], cfg["difficulty"])
        n = len(cfg["instruments"])

        outputs = ["decision"]
        if cfg.get("risk_tier_reward", 0) > 0:
            outputs.append("risk_tier")
        if cfg.get("hedge_reward", 0) > 0:
            outputs.append("hedge_recommended")
        if cfg.get("thesis_required_for"):
            ids = ", ".join(cfg["thesis_required_for"])
            outputs.append(f"thesis ({ids})")

        md += f"| `{name}` | {diff} | {n} | {', '.join(outputs)} |\n"

    md += (
        "\n---\n\n"
        "## Reward Mechanics\n\n"
        "| Signal | How it works |\n"
        "|--------|--------------|\n"
        "| **Decision** | Exact match = full credit · Adjacent stance (e.g. neutral vs overweight) = 30% partial · Opposite = 0 |\n"
        "| **Risk Tier** | Exact = full · Adjacent = 40% partial · Opposite = 0 |\n"
        "| **Thesis** | Keyword overlap × thesis weight, with anti-stuffing checks + coherence bonus |\n"
        "| **Hedge Flag** | Binary match on expert task |\n"
        "| **Ordering Bonus** | Bonus for addressing priority/tail-risk names in the first half of the episode |\n"
        "| **Duplicate Penalty** | −0.05 if re-deciding an already-decided instrument |\n\n"
        "Episode score is clamped to **(0.001, 0.999)** when done.\n\n"
        "---\n\n"
        "## Using Your Own API Keys\n\n"
        "In the **AI Agent Demo** tab, provide:\n"
        "1. **API URL** — Any OpenAI-compatible endpoint (Groq, Together, OpenAI, etc.)\n"
        "2. **Model Name** — The model identifier for that endpoint\n"
        "3. **API Key** — Your API key\n\n"
        "Keys are only used in-browser for the demo and are **never stored**.\n\n"
        "---\n\n"
        "## API Endpoints\n\n"
        "| Method | Path | Description |\n"
        "|--------|------|-------------|\n"
        "| POST | `/reset` | Start a new episode |\n"
        "| POST | `/step` | Submit one instrument decision |\n"
        "| GET | `/state` | Current episode metadata |\n"
        "| GET | `/health` | Liveness check |\n"
        "| GET | `/info` | Task list and metadata |\n\n"
        "---\n\n"
        "## Tech Stack\n\n"
        "- **FastAPI** — HTTP API\n"
        "- **Gradio** — Interactive UI\n"
        "- **Pydantic** — Typed models\n"
        "- **Docker** — Containerised deployment on Hugging Face Spaces\n"
        "- **OpenAI SDK** — LLM inference agent\n"
    )
    return md


# ────────────────────────────────────────────────────────────────────────────────
# Build Gradio Blocks app
# ────────────────────────────────────────────────────────────────────────────────

CUSTOM_CSS = """
.gr-button-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
}
.task-badge {
    display: inline-block;
    padding: 2px 12px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.85em;
}
"""

with gr.Blocks(
    title="Stock Investment Agent — Indian Market RL",
) as demo:

    gr.Markdown(
        "# 📈 Stock Investment Agent — Indian Market RL Environment\n"
        "*AI-powered portfolio research across NSE/BSE-listed companies*"
    )

    with gr.Tabs():

        # ── Tab 1: AI Agent Demo ──────────────────────────────────────────
        with gr.TabItem("🤖 AI Agent Demo", id="agent-demo"):
            gr.Markdown(
                "Run an LLM agent against any task and watch it make decisions step-by-step. "
                "Provide your own OpenAI-compatible API credentials below."
            )

            with gr.Row():
                with gr.Column(scale=2):
                    demo_api_url = gr.Textbox(
                        label="API URL",
                        placeholder="e.g. https://api.groq.com/openai/v1",
                        type="text",
                    )
                with gr.Column(scale=2):
                    demo_model = gr.Textbox(
                        label="Model Name",
                        placeholder="e.g. llama-3.1-8b-instant",
                        type="text",
                    )
                with gr.Column(scale=2):
                    demo_api_key = gr.Textbox(
                        label="API Key",
                        placeholder="sk-... or gsk_...",
                        type="password",
                    )

            with gr.Row():
                demo_task = gr.Dropdown(
                    choices=TASK_CHOICES,
                    value="nifty_screen",
                    label="Task",
                    scale=2,
                )
                demo_run_btn = gr.Button("▶ Run Agent", variant="primary", scale=1)

            demo_summary = gr.Markdown("*Click 'Run Agent' to start*")
            demo_reward_bar = gr.HTML("")
            demo_steps = gr.Markdown("")

            demo_run_btn.click(
                fn=_run_agent_demo,
                inputs=[demo_task, demo_api_url, demo_model, demo_api_key],
                outputs=[demo_steps, demo_reward_bar, demo_summary],
            )

        # ── Tab 2: Play Yourself ──────────────────────────────────────────
        with gr.TabItem("🎮 Play Yourself", id="play"):
            gr.Markdown(
                "Pick a task, read each instrument's research note, and make your own "
                "portfolio decisions. Get instant grading feedback after each step!"
            )

            with gr.Row():
                play_task = gr.Dropdown(
                    choices=TASK_CHOICES,
                    value="nifty_screen",
                    label="Task",
                    scale=2,
                )
                play_reset_btn = gr.Button("🔄 Start / Reset", variant="primary", scale=1)

            play_session = gr.State("")
            play_status = gr.Markdown("*Click 'Start / Reset' to begin*")
            play_card = gr.Markdown("")
            play_feedback = gr.Markdown("")

            with gr.Row():
                play_decision = gr.Radio(
                    choices=["overweight", "neutral", "underweight"],
                    label="Decision",
                    value="neutral",
                    visible=False,
                )
                play_risk = gr.Radio(
                    choices=["defensive", "balanced", "aggressive"],
                    label="Risk Tier",
                    value="balanced",
                    visible=False,
                )
                play_hedge = gr.Radio(
                    choices=["Yes", "No"],
                    label="Hedge Recommended?",
                    value="No",
                    visible=False,
                )

            play_thesis = gr.Textbox(
                label="Thesis (required for select instruments)",
                placeholder="Write your analytical thesis here (40+ words recommended)...",
                lines=3,
                visible=False,
            )
            play_submit_btn = gr.Button("Submit Decision", variant="primary", visible=False)

            play_reset_btn.click(
                fn=_play_reset,
                inputs=[play_task],
                outputs=[
                    play_session, play_card, play_feedback, play_status,
                    play_decision, play_risk, play_hedge, play_thesis, play_submit_btn,
                ],
            )
            play_submit_btn.click(
                fn=_play_step,
                inputs=[play_session, play_decision, play_risk, play_hedge, play_thesis],
                outputs=[
                    play_card, play_feedback, play_status,
                    play_decision, play_risk, play_hedge, play_thesis, play_submit_btn,
                ],
            )

        # ── Tab 3: About ─────────────────────────────────────────────────
        with gr.TabItem("ℹ️ About", id="about"):
            gr.Markdown(_build_about_md())
