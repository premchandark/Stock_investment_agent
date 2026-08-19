# 📈 Stock Investment Agent

An LLM-powered agent for analyzing Indian stock-market scenarios and generating structured portfolio decisions.

## Features

* Investment stance: **Overweight / Neutral / Underweight**
* Risk classification: **Defensive / Balanced / Aggressive**
* AI-generated investment theses
* Portfolio risk analysis
* Market-stress and hedge recommendations
* Automated LLM evaluation and reward scoring
* Interactive Gradio UI

## Tech Stack

**Python · LLMs · LangChain · Llama-3 · FastAPI · Gradio · Pydantic · Docker**

## Architecture

```text
Market Scenario
      ↓
   LLM Agent
      ↓
 Decision + Thesis
      ↓
 Evaluation & Reward
      ↓
    Feedback
```

## Run Locally

```bash
pip install -e .
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
```

## Project Structure

```text
├── inference.py
├── models.py
├── client.py
└── server/
    ├── app.py
    ├── environment.py
    ├── graders.py
    ├── tasks.py
    └── ui.py
```

## Disclaimer

For educational and research purposes only. Not financial advice.
