"""
Grading logic for all four stock-investment tasks.

Each grader receives the task config and the action the agent submitted,
then returns an immediate step reward in [0.0, 1.0] (before normalisation).

Features:
- Per-step grading with partial credit
- Near-miss partial credit for directionally close decisions
- Conviction-ordering bonus (rewards deciding priority/tail-risk names early)
- Anti-exploit thesis validation (keyword stuffing detection)
- Coherence bonus for thesis quality (length, structure, relevance)
- Hedge flag grading on the expert task
"""

from __future__ import annotations

from collections import Counter
from typing import Any


# ─── Decision adjacency for near-miss partial credit ─────────────────────────

_DECISION_ADJACENCY: dict[tuple[str, str], float] = {
    ("overweight", "neutral"): 0.3,
    ("neutral", "overweight"): 0.3,
    ("underweight", "neutral"): 0.3,
    ("neutral", "underweight"): 0.3,
    ("overweight", "underweight"): 0.0,
    ("underweight", "overweight"): 0.0,
}

_RISK_ADJACENCY: dict[tuple[str, str], float] = {
    ("defensive", "balanced"): 0.4,
    ("balanced", "defensive"): 0.4,
    ("balanced", "aggressive"): 0.4,
    ("aggressive", "balanced"): 0.4,
    ("defensive", "aggressive"): 0.0,
    ("aggressive", "defensive"): 0.0,
}


def _decision_score(agent: str, correct: str, full_reward: float) -> tuple[float, str]:
    """Score a decision with partial credit for near-misses."""
    if agent == correct:
        return full_reward, f"decision=✓({agent})"
    adj = _DECISION_ADJACENCY.get((agent, correct), 0.0)
    if adj > 0:
        partial = round(full_reward * adj, 6)
        return partial, f"decision=~({agent}≈{correct},+{partial:.4f})"
    return 0.0, f"decision=✗({agent}≠{correct})"


def _risk_tier_score(agent: str, correct: str, full_reward: float) -> tuple[float, str]:
    """Score a risk tier with partial credit for adjacent tiers."""
    if agent == correct:
        return full_reward, f"risk_tier=✓({agent})"
    adj = _RISK_ADJACENCY.get((agent, correct), 0.0)
    if adj > 0:
        partial = round(full_reward * adj, 6)
        return partial, f"risk_tier=~({agent}≈{correct},+{partial:.4f})"
    return 0.0, f"risk_tier=✗({agent}≠{correct})"


# ─── Anti-exploit helpers ────────────────────────────────────────────────────

def _detect_keyword_stuffing(text: str, keywords: list[str]) -> bool:
    """
    Detect if a thesis is likely keyword-stuffed (gaming the grader).

    Heuristics:
    - Fewer than 3 words → trivially stuffed
    - Short text (< 10 words) with 5+ keyword hits → suspicious
    - Keyword-to-word ratio > 0.75 → suspicious
    - Any single non-stop word repeated N+ times (N scales with length) → suspicious
    """
    if not text:
        return False

    words = text.lower().split()
    if len(words) < 3:
        return True

    matched = sum(1 for kw in keywords if kw.lower() in text.lower())
    keyword_ratio = matched / max(len(words), 1)
    if len(words) < 10 and matched >= 5:
        return True
    if keyword_ratio > 0.75:
        return True

    _STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "and", "but", "or", "nor", "not", "so", "yet", "both",
        "either", "neither", "each", "every", "all", "any", "few", "more",
        "most", "other", "some", "such", "no", "only", "own", "same", "than",
        "too", "very", "just", "because", "if", "when", "while", "that",
        "this", "these", "those", "it", "its", "we", "they", "their",
        "rs", "cr", "crore", "lakh", "per", "also", "which", "about",
        "india", "india's", "indian", "market", "sector", "company",
        "stock", "price", "growth", "risk", "high", "low", "new",
        "rate", "cost", "energy", "however", "given", "due", "likely",
        "overall", "based", "current", "potential", "significant",
    }
    word_counts = Counter(w for w in words if w not in _STOP_WORDS)
    repeat_threshold = 4 if len(words) < 40 else 5 if len(words) < 60 else 6
    if any(c >= repeat_threshold for c in word_counts.values()):
        return True

    return False


def _score_thesis(
    thesis: str | None,
    keyword_cfg: dict[str, Any],
) -> float:
    """
    Score a thesis by keyword matching with anti-exploit checks and coherence bonus.

    Returns a float in [0.0, 1.0] representing quality.
    Base: matched / required_matches, capped at 1.0.
    Coherence bonus: up to +0.15 for well-structured, substantive theses.
    """
    if not thesis:
        return 0.0

    stripped = thesis.strip()
    if len(stripped) < 20:
        return 0.05

    keywords: list[str] = keyword_cfg.get("keywords", [])
    required: int = keyword_cfg.get("required_matches", 1)

    if _detect_keyword_stuffing(thesis, keywords):
        return 0.1

    thesis_lower = thesis.lower()
    matched = sum(1 for kw in keywords if kw.lower() in thesis_lower)
    base_score = min(1.0, matched / required) if required > 0 else 0.0

    coherence_bonus = 0.0
    word_count = len(stripped.split())
    sentence_count = max(1, stripped.count(".") + stripped.count("!") + stripped.count("?"))

    if word_count >= 25 and sentence_count >= 2:
        coherence_bonus += 0.05
    if word_count >= 40 and sentence_count >= 2:
        coherence_bonus += 0.05
    if matched > required and word_count >= 30:
        coherence_bonus += 0.05

    return min(1.0, base_score + coherence_bonus)


# ─── Ordering bonus ────────────────────────────────────────────────────────────

def _compute_ordering_bonus(
    task_cfg: dict[str, Any],
    instrument_id: str,
    decided: dict[str, Any],
) -> float:
    """Bonus for addressing priority (high-impact / tail-risk) names earlier in the episode."""
    priority_ids: list[str] = task_cfg.get("priority_ids", [])
    total_bonus: float = task_cfg.get("ordering_bonus", 0.0)

    if instrument_id not in priority_ids or total_bonus <= 0:
        return 0.0

    num_priority = len(priority_ids)
    per_bonus = total_bonus / num_priority if num_priority > 0 else 0.0

    position = len(decided) + 1
    total_n = len(task_cfg.get("instruments", []))
    halfway = total_n / 2

    if position <= halfway:
        return round(per_bonus, 6)
    decay = 1.0 - ((position - halfway) / halfway)
    return round(per_bonus * max(0.0, decay), 6)


# ─── Task 1: nifty_screen ─────────────────────────────────────────────────────

def grade_nifty_screen(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    instrument_id: str = action.get("instrument_id", "")
    decision: str = (action.get("decision") or "").lower().strip()

    gt: dict[str, Any] = task_cfg["ground_truth"].get(instrument_id, {})
    correct: str = gt.get("decision", "")

    reward, reason = _decision_score(decision, correct, task_cfg["decision_reward"])
    return reward, f"{reason} for {instrument_id}"


# ─── Task 2: sector_rotation ──────────────────────────────────────────────────

def grade_sector_rotation(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    instrument_id: str = action.get("instrument_id", "")
    decision: str = (action.get("decision") or "").lower().strip()
    risk_tier: str = (action.get("risk_tier") or "").lower().strip()
    thesis: str | None = action.get("thesis") or None

    gt: dict[str, Any] = task_cfg["ground_truth"].get(instrument_id, {})
    correct_decision: str = gt.get("decision", "")
    correct_risk: str = gt.get("risk_tier", "")

    reward = 0.0
    parts: list[str] = []

    d_score, d_reason = _decision_score(decision, correct_decision, task_cfg["decision_reward"])
    reward += d_score
    parts.append(d_reason)

    r_score, r_reason = _risk_tier_score(risk_tier, correct_risk, task_cfg["risk_tier_reward"])
    reward += r_score
    parts.append(r_reason)

    if instrument_id in task_cfg["thesis_required_for"]:
        kw_cfg = task_cfg["thesis_keywords"].get(instrument_id, {})
        quality = _score_thesis(thesis, kw_cfg)
        tr = round(task_cfg["thesis_reward"] * quality, 6)
        reward += tr
        parts.append(f"thesis_quality={quality:.2f}(+{tr:.3f})")

    order_bonus = _compute_ordering_bonus(task_cfg, instrument_id, decided)
    if order_bonus > 0:
        reward += order_bonus
        parts.append(f"ordering_bonus=+{order_bonus:.4f}")

    return round(reward, 6), " | ".join(parts)


# ─── Task 3: portfolio_risk ───────────────────────────────────────────────────

def grade_portfolio_risk(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    instrument_id: str = action.get("instrument_id", "")
    decision: str = (action.get("decision") or "").lower().strip()
    risk_tier: str = (action.get("risk_tier") or "").lower().strip()
    thesis: str | None = action.get("thesis") or None

    gt: dict[str, Any] = task_cfg["ground_truth"].get(instrument_id, {})
    correct_decision: str = gt.get("decision", "")
    correct_risk: str = gt.get("risk_tier", "")

    reward = 0.0
    parts: list[str] = []

    d_score, d_reason = _decision_score(decision, correct_decision, task_cfg["decision_reward"])
    reward += d_score
    parts.append(d_reason)

    r_score, r_reason = _risk_tier_score(risk_tier, correct_risk, task_cfg["risk_tier_reward"])
    reward += r_score
    parts.append(r_reason)

    if instrument_id in task_cfg["thesis_required_for"]:
        kw_cfg = task_cfg["thesis_keywords"].get(instrument_id, {})
        quality = _score_thesis(thesis, kw_cfg)
        tr = round(task_cfg["thesis_reward"] * quality, 6)
        reward += tr
        parts.append(f"thesis_quality={quality:.2f}(+{tr:.4f})")

    order_bonus = _compute_ordering_bonus(task_cfg, instrument_id, decided)
    if order_bonus > 0:
        reward += order_bonus
        parts.append(f"ordering_bonus=+{order_bonus:.4f}")

    return round(reward, 6), " | ".join(parts)


# ─── Task 4: rbi_stress ──────────────────────────────────────────────────────

def grade_rbi_stress(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    instrument_id: str = action.get("instrument_id", "")
    decision: str = (action.get("decision") or "").lower().strip()
    risk_tier: str = (action.get("risk_tier") or "").lower().strip()
    thesis: str | None = action.get("thesis") or None

    raw_hedge = action.get("hedge_recommended")
    if isinstance(raw_hedge, bool):
        hedge = raw_hedge
    elif isinstance(raw_hedge, str):
        hedge = raw_hedge.lower().strip() == "true"
    else:
        hedge = False

    gt: dict[str, Any] = task_cfg["ground_truth"].get(instrument_id, {})
    correct_decision: str = gt.get("decision", "")
    correct_risk: str = gt.get("risk_tier", "")
    correct_hedge: bool = gt.get("hedge_recommended", False)

    reward = 0.0
    parts: list[str] = []

    d_score, d_reason = _decision_score(decision, correct_decision, task_cfg["decision_reward"])
    reward += d_score
    parts.append(d_reason)

    r_score, r_reason = _risk_tier_score(risk_tier, correct_risk, task_cfg["risk_tier_reward"])
    reward += r_score
    parts.append(r_reason)

    if hedge == correct_hedge:
        reward += task_cfg.get("hedge_reward", 0.0)
        parts.append(f"hedge=✓({hedge})")
    else:
        parts.append(f"hedge=✗({hedge}≠{correct_hedge})")

    if instrument_id in task_cfg["thesis_required_for"]:
        kw_cfg = task_cfg["thesis_keywords"].get(instrument_id, {})
        quality = _score_thesis(thesis, kw_cfg)
        tr = round(task_cfg["thesis_reward"] * quality, 6)
        reward += tr
        parts.append(f"thesis_quality={quality:.2f}(+{tr:.4f})")

    order_bonus = _compute_ordering_bonus(task_cfg, instrument_id, decided)
    if order_bonus > 0:
        reward += order_bonus
        parts.append(f"ordering_bonus=+{order_bonus:.4f}")

    return round(reward, 6), " | ".join(parts)


# ─── Dispatcher ───────────────────────────────────────────────────────────────

GRADERS = {
    "nifty_screen": grade_nifty_screen,
    "sector_rotation": grade_sector_rotation,
    "portfolio_risk": grade_portfolio_risk,
    "rbi_stress": grade_rbi_stress,
}


def grade_action(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    """Dispatch to the right grader and return (reward, reason)."""
    task_name: str = task_cfg["name"]
    grader = GRADERS.get(task_name)
    if grader is None:
        return 0.0, f"No grader found for task '{task_name}'"
    return grader(task_cfg, action, decided)
