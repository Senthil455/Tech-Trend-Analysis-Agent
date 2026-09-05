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
1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Set up the database using the provided migration scripts.
4. Run the FastAPI server using `uvicorn api.main:app --reload`.

## Requirements
- Python 3.9+
- PostgreSQL with pgvector extension
- FastAPI
- OpenAI GPT or similar LLM
- Pydantic

## Development Phases
1. Project Foundation
2. Tools Development
3. ReAct Agent Implementation
4. Trend Engine Development
5. Memory Integration
6. Configuration Setup
7. Report Generation
8. Dashboard and Content Agent Integration