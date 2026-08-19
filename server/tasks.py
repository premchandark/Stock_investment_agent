"""
Instrument universes and task configurations for all four difficulty levels.

Indian stock market focus — real NSE/BSE-listed companies with realistic
scenarios drawn from actual market dynamics. Designed for practical
portfolio research training.
"""

from typing import Any

# ─── Task 1: Nifty Screen (Easy) ─────────────────────────────────────────────
# 5 Nifty 50 large-caps, agent assigns overweight / neutral / underweight.

TASK_NIFTY_SCREEN: dict[str, Any] = {
    "name": "nifty_screen",
    "difficulty": "easy",
    "description": (
        "You are covering five Nifty 50 large-caps ahead of quarterly rebalance. "
        "For each name, issue a relative benchmark stance: "
        "'overweight', 'neutral', or 'underweight'."
    ),
    "instructions": (
        "Stance definitions:\n"
        "  overweight   – Increase portfolio weight vs Nifty 50 benchmark (conviction / upside skew)\n"
        "  neutral      – Keep near benchmark weight\n"
        "  underweight  – Reduce vs benchmark (risk, valuation, or deteriorating fundamentals)\n\n"
        "For each step respond with valid JSON ONLY:\n"
        '  {"instrument_id": "<id>", "decision": "<overweight|neutral|underweight>"}\n'
        "Process one instrument per step that is still pending."
    ),
    "max_steps": 5,
    "instruments": [
        {
            "id": "n1",
            "symbol": "RELIANCE",
            "company": "Reliance Industries Ltd.",
            "sector": "Conglomerate / Energy",
            "headline": "Jio + Retail demerger filing accepted by NCLT; O2C margins at 3-year high",
            "narrative": (
                "Board approved demerger of Jio Platforms and Reliance Retail into separately listed entities. "
                "NCLT admitted the scheme; analyst consensus sees 15-20% re-rating on sum-of-parts basis. "
                "O2C segment benefiting from tight global refining spreads — Singapore GRM at $8/bbl. "
                "Consolidated net debt near zero after rights issue proceeds and stake sales."
            ),
            "as_of": "2025-03-15T09:15:00+05:30",
        },
        {
            "id": "n2",
            "symbol": "TCS",
            "company": "Tata Consultancy Services Ltd.",
            "sector": "IT Services",
            "headline": "Revenue growth guidance cut to 1-3% CC; BFSI discretionary spend soft",
            "narrative": (
                "Management cited elongated decision cycles in North American banking clients. "
                "Attrition normalised to 12% but fresher utilisation remains low. Deal TCV healthy "
                "at $8.1bn but skewed towards cost-takeout rather than transformation. "
                "Margins under pressure from wage hikes; operating margin guided flat YoY."
            ),
            "as_of": "2025-03-15T09:30:00+05:30",
        },
        {
            "id": "n3",
            "symbol": "HDFCBANK",
            "company": "HDFC Bank Ltd.",
            "sector": "Banking",
            "headline": "Post-merger integration on track; deposit growth accelerating to 18% YoY",
            "narrative": (
                "LDR improved from 110% to 104% as deposits caught up with merged loan book. "
                "NIM guided stable at 3.5-3.6% despite RBI rate cut cycle commencing. "
                "Retail asset quality pristine — GNPA 1.24%. Branch expansion adding 1,500/year. "
                "Valuation trades at 2.5x book — in line with 5-year average; no re-rating catalyst."
            ),
            "as_of": "2025-03-15T09:00:00+05:30",
        },
        {
            "id": "n4",
            "symbol": "ITC",
            "company": "ITC Ltd.",
            "sector": "FMCG / Hotels",
            "headline": "Hotels demerger approved; FMCG margins cross 10% for first time",
            "narrative": (
                "ITC Hotels demerger into separately listed entity creates value unlock — "
                "hotel business valued at 30x EV/EBITDA as standalone. FMCG segment crossed "
                "Rs 20,000 cr revenue with EBITDA margin expanding 180 bps to 10.2%. "
                "Cigarette volumes resilient at +3% despite tax hike. "
                "Agri business benefiting from strong Rabi procurement season."
            ),
            "as_of": "2025-03-15T10:00:00+05:30",
        },
        {
            "id": "n5",
            "symbol": "SUNPHARMA",
            "company": "Sun Pharmaceutical Industries Ltd.",
            "sector": "Pharmaceuticals",
            "headline": "Specialty portfolio ramp-up offsets base business erosion; USFDA record clean",
            "narrative": (
                "US specialty revenues (Ilumya, Winlevi) grew 24% YoY and now represent 18% of "
                "US sales. Taro consolidation complete — synergies ahead of plan. "
                "No pending USFDA warning letters or import alerts. India formulations "
                "grew 9% in line with IPM. Valuation at 35x forward PE — at upper end of range "
                "but justified if specialty ramp sustains."
            ),
            "as_of": "2025-03-15T08:45:00+05:30",
        },
    ],
    "ground_truth": {
        "n1": {"decision": "overweight"},
        "n2": {"decision": "underweight"},
        "n3": {"decision": "neutral"},
        "n4": {"decision": "overweight"},
        "n5": {"decision": "neutral"},
    },
    "decision_reward": 0.20,
    "risk_tier_reward": 0.0,
    "thesis_reward": 0.0,
    "hedge_reward": 0.0,
    "thesis_required_for": [],
    "ordering_bonus": 0.0,
    "priority_ids": [],
}


# ─── Task 2: Sector Rotation (Medium) ────────────────────────────────────────
# 10 instruments across Indian sectors; stance + risk tier; thesis for cyclical.

TASK_SECTOR_ROTATION: dict[str, Any] = {
    "name": "sector_rotation",
    "difficulty": "medium",
    "description": (
        "Rotate a 10-name sleeve across Indian sectors. Label each with "
        "overweight/neutral/underweight and a risk tier (defensive/balanced/aggressive). "
        "Produce a thesis for Tata Steel (id='sr3') where the metals cycle is inflecting."
    ),
    "instructions": (
        "For every instrument provide decision and risk_tier.\n"
        "For id='sr3' (Tata Steel — metals cyclical tied to India infra demand vs China overcapacity) "
        "you MUST include a non-empty 'thesis' explaining the cycle call.\n\n"
        "STRATEGY TIP: Decide high-impact cyclical and rate-sensitive names early for an ordering bonus.\n\n"
        "JSON ONLY per step:\n"
        '  {"instrument_id":"<id>","decision":"<overweight|neutral|underweight>",'
        ' "risk_tier":"<defensive|balanced|aggressive>",'
        ' "thesis":"<text or null>"}\n'
    ),
    "max_steps": 10,
    "instruments": [
        {
            "id": "sr1",
            "symbol": "SBIN",
            "company": "State Bank of India",
            "sector": "PSU Banking",
            "headline": "NIM resilient at 3.3%; GNPA at decadal low of 2.2%",
            "narrative": (
                "Credit growth at 15% led by retail and MSME. Treasury gains from bond rally "
                "as RBI cuts rates. CASA ratio stable at 41%. ROA approaching 1% — "
                "best in SBI's history. Dividend yield 2.8%."
            ),
            "as_of": "2025-03-15T09:00:00+05:30",
        },
        {
            "id": "sr2",
            "symbol": "ICICIBANK",
            "company": "ICICI Bank Ltd.",
            "sector": "Private Banking",
            "headline": "Retail credit growth strong at 20% YoY; digital transactions up 40%",
            "narrative": (
                "Best-in-class ROE at 17.5%. Business banking emerging as growth engine. "
                "Asset quality stable — net NPA 0.4%. One ICICI cross-sell strategy gaining "
                "traction across insurance, AMC, and broking subsidiaries."
            ),
            "as_of": "2025-03-15T09:15:00+05:30",
        },
        {
            "id": "sr3",
            "symbol": "TATASTEEL",
            "company": "Tata Steel Ltd.",
            "sector": "Metals & Mining",
            "headline": "India volumes +8%; Europe restructuring nearing completion",
            "narrative": (
                "Kalinganagar expansion Phase 2 (5 MTPA) commissioned ahead of schedule. "
                "India EBITDA/tonne at Rs 15,500 — best among domestic producers. "
                "UK operations: Port Talbot hydrogen-ready EAF decision taken, restructuring charges "
                "largely behind. China steel exports remain elevated at 100MT+ run rate, pressuring "
                "global HRC prices. India's infrastructure capex (Rs 11.1L cr budget) underpins "
                "domestic demand visibility for 3-4 years."
            ),
            "as_of": "2025-03-15T07:45:00+05:30",
        },
        {
            "id": "sr4",
            "symbol": "BHARTIARTL",
            "company": "Bharti Airtel Ltd.",
            "sector": "Telecom",
            "headline": "ARPU up 7% to Rs 233 post tariff hike; 5G rollout 85% complete",
            "narrative": (
                "Subscriber adds healthy. Fixed broadband (Xstream) crossed 8M subs. "
                "Africa business growing 20% in constant currency. Net debt/EBITDA below 2x. "
                "Next tariff hike expected in H2 FY26."
            ),
            "as_of": "2025-03-15T09:30:00+05:30",
        },
        {
            "id": "sr5",
            "symbol": "ONGC",
            "company": "Oil & Natural Gas Corp. Ltd.",
            "sector": "Oil & Gas (Upstream)",
            "headline": "Crude realisation capped by govt windfall tax; KG basin output disappointing",
            "narrative": (
                "Windfall tax triggers at $75/bbl — capping upside. KG-DWN-98/2 ramp delayed "
                "6 months. Subsidy sharing uncertainty if crude spikes above $90. "
                "OVL assets face geopolitical risk. Dividend yield 4.5% provides floor."
            ),
            "as_of": "2025-03-15T08:00:00+05:30",
        },
        {
            "id": "sr6",
            "symbol": "HINDUNILVR",
            "company": "Hindustan Unilever Ltd.",
            "sector": "FMCG",
            "headline": "Volume growth muted at 2%; rural recovery slower than expected",
            "narrative": (
                "Urban demand slowing on high base. Rural FMCG showing green shoots but "
                "below consensus. Input costs (palm oil, crude derivatives) benign. "
                "Price hikes deferred to protect volume. Valuation at 55x PE — premium to sector."
            ),
            "as_of": "2025-03-15T10:00:00+05:30",
        },
        {
            "id": "sr7",
            "symbol": "TATAMOTORS",
            "company": "Tata Motors Ltd.",
            "sector": "Automobiles",
            "headline": "JLR margins at 8.5%; domestic EV market share 65%",
            "narrative": (
                "JLR order book covers 3 months of production. Range Rover and Defender "
                "driving mix improvement. Domestic PV share at 14.5% — EV Nexon/Punch leading. "
                "CV cycle plateauing after 2-year upcycle. Net automotive debt near zero target by FY26."
            ),
            "as_of": "2025-03-15T09:15:00+05:30",
        },
        {
            "id": "sr8",
            "symbol": "LT",
            "company": "Larsen & Toubro Ltd.",
            "sector": "Infrastructure / Capital Goods",
            "headline": "Order inflow +25% YoY; order book at all-time high of Rs 5.3L cr",
            "narrative": (
                "Government infra push (roads, metros, defence, green hydrogen) filling pipeline. "
                "International orders now 40% of book. Margins guided 10.5%+. "
                "IT services subsidiary dragging consolidated ROE."
            ),
            "as_of": "2025-03-15T10:30:00+05:30",
        },
        {
            "id": "sr9",
            "symbol": "DRREDDY",
            "company": "Dr. Reddy's Laboratories Ltd.",
            "sector": "Pharmaceuticals",
            "headline": "US generics pipeline robust; biosimilar launches on track",
            "narrative": (
                "gRevlimid contributing Rs 800cr/quarter. Biosimilar rituximab launched in EU. "
                "India branded generics growing 12%. USFDA compliance strong — "
                "zero observations in last 3 inspections. Valuation reasonable at 25x."
            ),
            "as_of": "2025-03-15T08:15:00+05:30",
        },
        {
            "id": "sr10",
            "symbol": "INFY",
            "company": "Infosys Ltd.",
            "sector": "IT Services",
            "headline": "Large deal wins strong but revenue growth guidance cautious at 1-4%",
            "narrative": (
                "Mega deal wins ($4B+ TCV) skewed to cost-takeout. Generative AI projects "
                "in pilot — not yet revenue-bearing. Margin band maintained at 20-22%. "
                "Buyback program ongoing. Attrition stable at 13%."
            ),
            "as_of": "2025-03-15T11:00:00+05:30",
        },
    ],
    "ground_truth": {
        "sr1": {"decision": "overweight", "risk_tier": "balanced"},
        "sr2": {"decision": "overweight", "risk_tier": "balanced"},
        "sr3": {"decision": "overweight", "risk_tier": "aggressive"},
        "sr4": {"decision": "overweight", "risk_tier": "balanced"},
        "sr5": {"decision": "underweight", "risk_tier": "defensive"},
        "sr6": {"decision": "neutral", "risk_tier": "defensive"},
        "sr7": {"decision": "overweight", "risk_tier": "balanced"},
        "sr8": {"decision": "overweight", "risk_tier": "balanced"},
        "sr9": {"decision": "neutral", "risk_tier": "balanced"},
        "sr10": {"decision": "underweight", "risk_tier": "balanced"},
    },
    "decision_reward": 0.015,
    "risk_tier_reward": 0.015,
    "thesis_reward": 0.60,
    "hedge_reward": 0.0,
    "thesis_required_for": ["sr3"],
    "thesis_keywords": {
        "sr3": {
            "keywords": [
                "steel", "metals", "cycle", "capacity", "infrastructure", "demand",
                "china", "ebitda", "margin", "kalinganagar", "volume", "capex",
                "hrc", "expansion", "infra",
            ],
            "required_matches": 3,
        },
    },
    "ordering_bonus": 0.10,
    "priority_ids": ["sr3", "sr5", "sr7", "sr10"],
}


# ─── Task 3: Portfolio Risk (Hard) ───────────────────────────────────────────
# 15 instruments; decision + risk tier + theses for three critical names.

_DECISION_EACH = 0.01
_RISK_EACH = 0.01
_THESIS_EACH = 0.15

TASK_PORTFOLIO_RISK: dict[str, Any] = {
    "name": "portfolio_risk",
    "difficulty": "hard",
    "description": (
        "Manage a 15-name multi-cap Indian portfolio with benchmark-relative stances and "
        "explicit risk budgets. Draft theses for Adani Enterprises (pr4 — governance / promoter risk), "
        "Paytm (pr9 — RBI regulatory action), and Vodafone Idea (pr12 — survival risk)."
    ),
    "instructions": (
        "Each step handles one pending instrument.\n"
        "Provide decision, risk_tier, and thesis (null except for pr4, pr9, pr12 where thesis is mandatory).\n\n"
        "STRATEGY TIP: Address tail-risk and event-driven names early to capture ordering bonus.\n\n"
        "JSON ONLY:\n"
        '  {"instrument_id":"<id>","decision":"<overweight|neutral|underweight>",'
        ' "risk_tier":"<defensive|balanced|aggressive>",'
        ' "thesis":"<text or null>"}\n'
    ),
    "max_steps": 15,
    "instruments": [
        {
            "id": "pr1",
            "symbol": "NIFTY50ETF",
            "company": "Nifty 50 Index ETF Sleeve",
            "sector": "Multi-Cap",
            "headline": "Beta=1.0; tracking error 15 bps; expense ratio 5 bps",
            "narrative": "Core index allocation for benchmark-hugging. Securities lending income adds 3 bps. Rebalance twice yearly.",
            "as_of": "2025-03-15T08:00:00+05:30",
        },
        {
            "id": "pr2",
            "symbol": "BAJFINANCE",
            "company": "Bajaj Finance Ltd.",
            "sector": "NBFC",
            "headline": "AUM growth 28% YoY; new consumer loan verticals scaling",
            "narrative": "Customer franchise at 80M+. Cross-sell ratio improving. NIM at 10%+ but rising CoF a risk. GNPA stable at 0.9%. Valuation at 6.5x book — premium to sector.",
            "as_of": "2025-03-15T09:00:00+05:30",
        },
        {
            "id": "pr3",
            "symbol": "MARUTI",
            "company": "Maruti Suzuki India Ltd.",
            "sector": "Automobiles",
            "headline": "SUV mix improvement drives ASP +15%; EV launch FY27",
            "narrative": (
                "Market share recovered to 42% in passenger vehicles. Jimny and Fronx exports strong. "
                "EV timeline seen as late vs Tata/Hyundai. Gujarat plant ramping."
            ),
            "as_of": "2025-03-15T09:30:00+05:30",
        },
        {
            "id": "pr4",
            "symbol": "ADANIENT",
            "company": "Adani Enterprises Ltd.",
            "sector": "Conglomerate / Infra",
            "headline": "Hindenburg aftermath: promoter pledge at 4.2%; FPO withdrawn; governance reforms underway",
            "narrative": (
                "SEBI and SC investigations concluded with no adverse findings on stock manipulation. "
                "However, concentrated promoter holding (73%) with pledged shares raises governance concerns. "
                "New businesses (green hydrogen, data centres, airports) are pre-profit and capex-heavy. "
                "Debt/equity elevated at 2.1x across group. Counter-party banks comfortable but "
                "FII ownership dropped from 22% to 14% post-crisis."
            ),
            "as_of": "2025-03-15T07:30:00+05:30",
        },
        {
            "id": "pr5",
            "symbol": "WIPRO",
            "company": "Wipro Ltd.",
            "sector": "IT Services",
            "headline": "Turnaround attempt under new CEO; margins recovering to 16%",
            "narrative": "Large deal momentum improving but organic growth lagging peers. Consulting integration ongoing. Buyback at premium to CMP.",
            "as_of": "2025-03-15T10:00:00+05:30",
        },
        {
            "id": "pr6",
            "symbol": "COALINDIA",
            "company": "Coal India Ltd.",
            "sector": "Mining",
            "headline": "E-auction premiums strong; FSA offtake at 95%",
            "narrative": "Production growth on track at 5%. E-auction realisations at 30% premium to notified prices. Dividend yield 6.5%. ESG risk from thermal coal exposure limits institutional demand.",
            "as_of": "2025-03-15T08:45:00+05:30",
        },
        {
            "id": "pr7",
            "symbol": "ZOMATO",
            "company": "Zomato Ltd.",
            "sector": "Consumer Tech",
            "headline": "Blinkit rapid commerce GMV +80% YoY; food delivery margins at breakeven",
            "narrative": "Quick commerce is the growth engine. Hyperpure B2B supply gaining traction. Food delivery adjusted EBITDA breakeven achieved. Valuation at 180x PE — priced for perfection.",
            "as_of": "2025-03-15T10:15:00+05:30",
        },
        {
            "id": "pr8",
            "symbol": "TITAN",
            "company": "Titan Company Ltd.",
            "sector": "Consumer Discretionary",
            "headline": "Jewellery division +18% revenue growth; wedding season strong",
            "narrative": "Tanishq franchise expansion to Tier 2-3 cities driving volume. Watches and eyewear stable. Gold price rally aiding revenue but margin on making charges flat. CaratLane integration complete.",
            "as_of": "2025-03-15T11:00:00+05:30",
        },
        {
            "id": "pr9",
            "symbol": "PAYTM",
            "company": "One 97 Communications Ltd. (Paytm)",
            "sector": "Fintech",
            "headline": "RBI bars Paytm Payments Bank from onboarding; merchant lending pivot underway",
            "narrative": (
                "RBI action on Paytm Payments Bank forced business model restructuring. "
                "Payments GMV declined 20% as wallet users migrated. Merchant lending through "
                "partner banks scaling — disbursals recovering to Rs 5,000 cr/month. "
                "Operating burn narrowing but path to profitability pushed out 18 months. "
                "Cash runway ~6 quarters at current burn rate."
            ),
            "as_of": "2025-03-15T07:00:00+05:30",
        },
        {
            "id": "pr10",
            "symbol": "ASIANPAINT",
            "company": "Asian Paints Ltd.",
            "sector": "Consumer Discretionary",
            "headline": "Volume growth soft at 3%; new home decor vertical in pilot",
            "narrative": "Decorative paints demand subdued on real estate slowdown in metros. Input costs (TiO2, crude) benign. Beautiful Homes service expanding. Valuation at 60x PE — sector premium intact.",
            "as_of": "2025-03-15T09:45:00+05:30",
        },
        {
            "id": "pr11",
            "symbol": "HAL",
            "company": "Hindustan Aeronautics Ltd.",
            "sector": "Defence",
            "headline": "Order book Rs 94,000 cr; Tejas Mk2 development on schedule",
            "narrative": "LCA Tejas production ramping to 16/year. Helicopter orders from armed forces and exports to friendly nations. Margin expansion as indigenous content rises. Valuation reasonable at 22x given visibility.",
            "as_of": "2025-03-15T10:30:00+05:30",
        },
        {
            "id": "pr12",
            "symbol": "IDEA",
            "company": "Vodafone Idea Ltd.",
            "sector": "Telecom",
            "headline": "Subscriber losses continue; FPO raised Rs 18,000 cr but debt at Rs 2.1L cr",
            "narrative": (
                "AGR dues and spectrum payments create Rs 25,000 cr/year outflow. "
                "Subscriber base down to 210M from 270M peak. ARPU at Rs 146 — lowest among peers. "
                "Government equity conversion provides breathing room but dilutes existing shareholders. "
                "4G/5G capex requirement of Rs 50,000 cr+ unfunded. Survival depends on tariff hikes and government support."
            ),
            "as_of": "2025-03-15T08:15:00+05:30",
        },
        {
            "id": "pr13",
            "symbol": "NESTLEIND",
            "company": "Nestle India Ltd.",
            "sector": "FMCG",
            "headline": "Maggi volume growth +6%; premiumisation strategy on track",
            "narrative": "Rural distribution expanding. New product launches (plant-based, health range) growing from low base. Input cost tailwinds. Royalty increase to parent a concern.",
            "as_of": "2025-03-15T11:15:00+05:30",
        },
        {
            "id": "pr14",
            "symbol": "IREDA",
            "company": "Indian Renewable Energy Development Agency Ltd.",
            "sector": "Green Finance / NBFC",
            "headline": "Loan book +35% YoY; sanctions pipeline Rs 1.5L cr on renewable capex wave",
            "narrative": "Government's 500 GW renewable target by 2030 provides structural tailwind. NIM at 3.2%. GNPA improved to 2.8%. Recently listed — re-rating potential as track record builds.",
            "as_of": "2025-03-15T09:20:00+05:30",
        },
        {
            "id": "pr15",
            "symbol": "DMART",
            "company": "Avenue Supermarts Ltd. (DMart)",
            "sector": "Retail",
            "headline": "SSSG at 8%; quick commerce cannibalising grocery footfall in metros",
            "narrative": "DMart Ready (online) growing but unit economics inferior to stores. Store additions at 40-45/year. Working capital advantage intact. Valuation at 85x PE — premium under pressure from quick commerce threat.",
            "as_of": "2025-03-15T12:00:00+05:30",
        },
    ],
    "ground_truth": {
        "pr1": {"decision": "neutral", "risk_tier": "balanced"},
        "pr2": {"decision": "overweight", "risk_tier": "balanced"},
        "pr3": {"decision": "overweight", "risk_tier": "balanced"},
        "pr4": {"decision": "underweight", "risk_tier": "defensive"},
        "pr5": {"decision": "neutral", "risk_tier": "balanced"},
        "pr6": {"decision": "neutral", "risk_tier": "defensive"},
        "pr7": {"decision": "overweight", "risk_tier": "aggressive"},
        "pr8": {"decision": "overweight", "risk_tier": "balanced"},
        "pr9": {"decision": "underweight", "risk_tier": "defensive"},
        "pr10": {"decision": "neutral", "risk_tier": "balanced"},
        "pr11": {"decision": "overweight", "risk_tier": "balanced"},
        "pr12": {"decision": "underweight", "risk_tier": "defensive"},
        "pr13": {"decision": "neutral", "risk_tier": "balanced"},
        "pr14": {"decision": "overweight", "risk_tier": "aggressive"},
        "pr15": {"decision": "neutral", "risk_tier": "defensive"},
    },
    "decision_reward": _DECISION_EACH,
    "risk_tier_reward": _RISK_EACH,
    "thesis_reward": _THESIS_EACH,
    "hedge_reward": 0.0,
    "thesis_required_for": ["pr4", "pr9", "pr12"],
    "thesis_keywords": {
        "pr4": {
            "keywords": [
                "governance", "promoter", "pledge", "debt", "adani", "hindenburg",
                "capex", "concentration", "fii", "transparency", "risk", "group",
            ],
            "required_matches": 2,
        },
        "pr9": {
            "keywords": [
                "rbi", "regulatory", "payments", "bank", "lending", "burn",
                "profitability", "compliance", "merchant", "wallet", "restructuring",
            ],
            "required_matches": 2,
        },
        "pr12": {
            "keywords": [
                "debt", "agr", "subscriber", "survival", "arpu", "capex",
                "spectrum", "tariff", "government", "dilution", "losses",
            ],
            "required_matches": 2,
        },
    },
    "ordering_bonus": 0.25,
    "priority_ids": ["pr4", "pr9", "pr12", "pr7", "pr14"],
}


# ─── Task 4: RBI Stress (Expert) ────────────────────────────────────────────
# 12 instruments under macro stress; stance + risk tier + hedge flag + thesis.

TASK_RBI_STRESS: dict[str, Any] = {
    "name": "rbi_stress",
    "difficulty": "expert",
    "description": (
        "Stress regime: RBI pauses rate cuts citing inflation, FII outflows at $8B/quarter, "
        "crude at $95/bbl, INR at 87/USD. For each name choose stance, risk tier, "
        "whether a hedge is warranted (hedge_recommended), and produce a thesis for "
        "PFC (rs7 — green energy NBFC as liquidity hinge under rate stress)."
    ),
    "instructions": (
        "Fields per step:\n"
        "  decision            – overweight | neutral | underweight\n"
        "  risk_tier           – defensive | balanced | aggressive\n"
        "  hedge_recommended   – true if Nifty puts, currency hedge, or commodity overlay justified\n"
        "  thesis              – required for rs7; null otherwise\n\n"
        "HEDGE HEURISTICS (Indian market context):\n"
        "  – High beta + FII-heavy ownership + rate-sensitive → often true\n"
        "  – Export earners benefiting from weak INR → usually false\n"
        "  – Oil importers with unhedged crude exposure → often true\n"
        "  – PSU with government backing + low leverage → usually false\n"
        "  – NBFC with ALM mismatch under rising rates → often true\n\n"
        "STRATEGY TIP: Address liquidity/rate-sensitive clusters early.\n\n"
        "JSON ONLY:\n"
        '  {"instrument_id":"<id>","decision":"<...>","risk_tier":"<...>",'
        ' "hedge_recommended":<true|false>,"thesis":"<text or null>"}\n'
    ),
    "max_steps": 12,
    "instruments": [
        {
            "id": "rs1",
            "symbol": "LIQUIDBEES",
            "company": "Liquid ETF / TREPS Sleeve",
            "sector": "Cash",
            "headline": "Overnight rate at 6.5%; zero duration risk",
            "narrative": "Government securities-backed overnight lending. No credit spread exposure. NAV stable.",
            "as_of": "2025-03-15T06:00:00+05:30",
        },
        {
            "id": "rs2",
            "symbol": "BANDHANBNK",
            "company": "Bandhan Bank Ltd.",
            "sector": "Small Finance / Microfinance",
            "headline": "Microfinance stress rising; GNPA up 120 bps to 4.8%",
            "narrative": "Assam/Bengal portfolio quality deteriorating. Collection efficiency dropped to 94%. Provisioning coverage adequate but earnings under pressure. Deposit franchise still developing. FII ownership 35% — heavy selling pressure if stress escalates.",
            "as_of": "2025-03-15T07:00:00+05:30",
        },
        {
            "id": "rs3",
            "symbol": "BRITANNIA",
            "company": "Britannia Industries Ltd.",
            "sector": "FMCG (Staples)",
            "headline": "Volume growth +5%; wheat prices benign; distribution deepening",
            "narrative": "Defensive earnings profile. Rural penetration expanding. Adjacent categories (dairy, croissants) scaling. Input cost tailwind from stable commodities. Low beta to rate/FII cycle.",
            "as_of": "2025-03-15T08:00:00+05:30",
        },
        {
            "id": "rs4",
            "symbol": "PNB",
            "company": "Punjab National Bank",
            "sector": "PSU Banking",
            "headline": "Credit growth 12% but NIM compressing as deposit costs rise",
            "narrative": (
                "PSU bank with high government ownership (73%). Book value accretion positive "
                "but ROA still sub-0.7%. Corporate loan book improving but MSME slippages "
                "elevated in current stress. Rising rates widen ALM gap — 30% of book reprices "
                "in <1 year vs 45% of deposits."
            ),
            "as_of": "2025-03-15T07:15:00+05:30",
        },
        {
            "id": "rs5",
            "symbol": "TATAELXSI",
            "company": "Tata Elxsi Ltd.",
            "sector": "IT Services (ER&D)",
            "headline": "Revenue growth moderating to 12%; auto ER&D demand softening",
            "narrative": "Export-oriented earnings benefit from weak INR. Embedded software and EV design services have structural tailwind. But auto OEM capex slowing globally. High valuation at 50x PE.",
            "as_of": "2025-03-15T08:30:00+05:30",
        },
        {
            "id": "rs6",
            "symbol": "IOC",
            "company": "Indian Oil Corporation Ltd.",
            "sector": "Oil & Gas (Downstream)",
            "headline": "GRM at $4/bbl; under-recovery on diesel at Rs 5/litre at crude $95",
            "narrative": "Government may not allow retail price hike ahead of state elections. Under-recovery eats into refining margin. Inventory losses on crude held in transit if prices drop. Dividend yield 5% but uncertain if earnings compress.",
            "as_of": "2025-03-15T09:00:00+05:30",
        },
        {
            "id": "rs7",
            "symbol": "PFC",
            "company": "Power Finance Corporation Ltd.",
            "sector": "Infrastructure NBFC",
            "headline": "Loan book Rs 4.5L cr; incremental CoF rising 40 bps as bonds widen",
            "narrative": (
                "PFC is the largest lender to India's power sector — renewables now 15% of book. "
                "ALM well-matched but incremental bond spreads widening 40 bps as FII sell Indian debt. "
                "Government guarantee on some liabilities provides floor. Green energy transition capex "
                "(Rs 30L cr by 2030) depends on PFC/REC pipeline. If rates stay elevated and FII "
                "outflows persist, PFC's cost of funding rises, slowing disbursals and impacting "
                "India's renewable energy capacity addition targets."
            ),
            "as_of": "2025-03-15T06:30:00+05:30",
        },
        {
            "id": "rs8",
            "symbol": "HCLTECH",
            "company": "HCL Technologies Ltd.",
            "sector": "IT Services",
            "headline": "Products & Platforms segment margin expansion; FX tailwind from weak INR",
            "narrative": "Export earner with 70%+ revenue in USD. Weak INR adds 200 bps to margins. Defensive business model in stress scenario. Dividend yield 3.5%.",
            "as_of": "2025-03-15T09:30:00+05:30",
        },
        {
            "id": "rs9",
            "symbol": "CIPLA",
            "company": "Cipla Ltd.",
            "sector": "Pharmaceuticals",
            "headline": "US business strong; India respiratory franchise #1",
            "narrative": "gAdvair launch ramping. One-India strategy driving branded generics. Export revenue provides natural FX hedge. Defensive sector in macro stress. Low leverage.",
            "as_of": "2025-03-15T10:00:00+05:30",
        },
        {
            "id": "rs10",
            "symbol": "POLYCAB",
            "company": "Polycab India Ltd.",
            "sector": "Electricals / Cables",
            "headline": "Cables & wires demand robust on infra + real estate; FMEG lagging",
            "narrative": "Beneficiary of power T&D capex and real estate cycle. Copper price pass-through protects margins. FMEG (fans, switches) facing consumer slowdown. High institutional ownership — FII 25%.",
            "as_of": "2025-03-15T10:30:00+05:30",
        },
        {
            "id": "rs11",
            "symbol": "EMBASSYOFC",
            "company": "Embassy Office Parks REIT",
            "sector": "Real Estate (REIT)",
            "headline": "Occupancy 88%; rental reversion +15% but cap rate expansion risk",
            "narrative": "IT/ITeS tenants stable but new leasing slow amid work-from-home headwinds. Rising 10-year G-sec yield (7.5%) compresses NAV via higher cap rates. Distribution yield 6.5% but unit price at risk if yields rise further.",
            "as_of": "2025-03-15T07:45:00+05:30",
        },
        {
            "id": "rs12",
            "symbol": "JIOFIN",
            "company": "Jio Financial Services Ltd.",
            "sector": "Fintech / NBFC",
            "headline": "Lending book nascent at Rs 2,000 cr; insurance and broking JVs pre-revenue",
            "narrative": "Capital-rich but pre-profit across all verticals. Optionality on Reliance ecosystem distribution. BlackRock JV for AMC could be transformative. But near-term — zero earnings and elevated valuation on hope.",
            "as_of": "2025-03-15T11:00:00+05:30",
        },
    ],
    "ground_truth": {
        "rs1": {"decision": "neutral", "risk_tier": "defensive", "hedge_recommended": False},
        "rs2": {"decision": "underweight", "risk_tier": "defensive", "hedge_recommended": True},
        "rs3": {"decision": "neutral", "risk_tier": "balanced", "hedge_recommended": False},
        "rs4": {"decision": "underweight", "risk_tier": "defensive", "hedge_recommended": True},
        "rs5": {"decision": "neutral", "risk_tier": "balanced", "hedge_recommended": False},
        "rs6": {"decision": "underweight", "risk_tier": "defensive", "hedge_recommended": True},
        "rs7": {"decision": "underweight", "risk_tier": "defensive", "hedge_recommended": True},
        "rs8": {"decision": "overweight", "risk_tier": "balanced", "hedge_recommended": False},
        "rs9": {"decision": "overweight", "risk_tier": "balanced", "hedge_recommended": False},
        "rs10": {"decision": "neutral", "risk_tier": "balanced", "hedge_recommended": True},
        "rs11": {"decision": "underweight", "risk_tier": "defensive", "hedge_recommended": True},
        "rs12": {"decision": "neutral", "risk_tier": "aggressive", "hedge_recommended": True},
    },
    "decision_reward": 0.01,
    "risk_tier_reward": 0.02,
    "hedge_reward": 0.025,
    "thesis_reward": 0.15,
    "thesis_required_for": ["rs7"],
    "thesis_keywords": {
        "rs7": {
            "keywords": [
                "rate", "funding", "cost", "bond", "spread", "renewable",
                "green", "capex", "nbfc", "disbursals", "fii", "liquidity",
                "alm", "government", "power",
            ],
            "required_matches": 3,
        },
    },
    "ordering_bonus": 0.19,
    "priority_ids": ["rs7", "rs2", "rs11", "rs4", "rs6"],
}


ALL_TASKS = {
    "nifty_screen": TASK_NIFTY_SCREEN,
    "sector_rotation": TASK_SECTOR_ROTATION,
    "portfolio_risk": TASK_PORTFOLIO_RISK,
    "rbi_stress": TASK_RBI_STRESS,
}
