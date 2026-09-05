# Tech Trend Analysis Agent

## Overview
This project is an autonomous ReAct-based AI agent designed to analyze technology and AI trends across multiple platforms. It collects data, reasons over evidence, maintains memory of previous trends, detects emerging trends, and generates structured trend intelligence reports.

## Features
- **ReAct Loop**: Reason and act iteratively to gather and analyze data.
- **Tools**: Modular tools for data collection and analysis.
- **Memory**: Short-term and long-term memory for historical context.
- **Configuration**: YAML and environment-based settings for flexible behavior.
- **Trend Engine**: Deterministic analysis of trends.
- **Report Generation**: Structured JSON reports for downstream consumption.

## Directory Structure
```
Tech-Trend-Analysis-Agent/
│
├── tools/               # Modular tools for data collection and analysis
├── memory/              # Memory management modules
├── config/              # Configuration files
├── trend_engine/        # Deterministic trend analysis engine
├── reports/             # Report generation modules
├── api/                 # FastAPI application
├── database/            # Database models and migrations
├── tests/               # Unit and integration tests
└── README.md            # Project documentation
```

## Getting Started
1. Install dependencies using `pip install -r requirements.txt`.
2. Run the API with `uvicorn api.main:app --reload`.
3. Open `http://127.0.0.1:8000/` to use the visual dashboard.
4. The raw API is also available at `http://127.0.0.1:8000/docs`.

The dashboard lets you enter a topic, run an analysis, and inspect the score,
emerging trends, evidence, content opportunities, and ReAct trace.

The default mode is deterministic and offline. Reports are persisted to
`trend_memory.db` as JSON so historical scores survive between runs without
requiring PostgreSQL. Set `TREND_LIVE_DATA=1` to query Reddit and GitHub, and
set `NEWS_API_KEY` to enable NewsAPI. Set `OPENAI_API_KEY` to let the LLM
choose the source tools; without it, the deterministic planner is used.

Each request runs a ReAct trace across enabled source tools, calculates a
deterministic score, compares long-term memory, persists the result, and
returns structured evidence, predictions, and content opportunities.

Run the tests with `python -m unittest discover -s tests`.

## Requirements
- Python 3.9+
- FastAPI
- Pydantic and pydantic-settings

## Development Phases
1. Project Foundation
2. Tools Development
3. ReAct Agent Implementation
4. Trend Engine Development
5. Memory Integration
6. Configuration Setup
7. Report Generation
8. Dashboard and Content Agent Integration