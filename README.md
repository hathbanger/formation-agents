# Multi-Agent API Platform

## Overview

This project provides a modular, extensible platform for running advanced AI-powered agents and workflows for a variety of domains (finance, investment, movie recommendations, recipe creation, etc). Each agent can be run as a standalone CLI tool or exposed as a robust HTTP API using FastAPI.

Agents leverage OpenAI models, web search, and other tools to deliver high-quality, context-aware responses. The architecture is designed for easy extension, session management, and production deployment.

---

## Features

- **Multi-agent workflows**: Compose agents and teams for complex tasks (e.g., research, writing, analysis).
- **API and CLI support**: Run any agent as a REST API or interactively from the command line.
- **Session and caching**: Uses SQLite for persistent session storage and caching.
- **Modular design**: Add new agents or workflows with minimal boilerplate.
- **Rich output**: Markdown responses, tables, and emoji indicators for clarity.
- **Extensible tools**: Integrate with web search, news, financial data, and more.

---

## How It Works

Each agent script (e.g., `finance-agent.py`, `blog-post-generator.py`) follows a common pattern:

- **Workflow Class**: The core logic is wrapped in a class (e.g., `FinanceAgentWorkflow`) with a `.run(query)` method.
- **API Entrypoint**: If `RUN_AS_API=1` is set, the script launches a FastAPI server using `create_agent_api` from `agent_api_server.py`.
- **CLI Mode**: If run normally, the script prompts for input and prints the result to the console.
- **Session Management**: Optionally uses `SqliteStorage` for persistent session and cache.

---

## Requirements & Setup

- Python 3.9+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- (Optional) Set up your OpenAI API key and any other required environment variables.

---

## Running an Agent as an API

1. **Start the API server:**
   ```bash
   RUN_AS_API=1 python finance-agent.py
   # or any other agent script
   ```
2. **Send a request:**
   ```bash
   curl -X POST http://localhost:8000/run-task \
     -H 'Content-Type: application/json' \
     -d '{
       "agent_id": "finance-agent",
       "task_id": "analyze",
       "inputs": {"variables": {"query": {"value": "What is the latest news on Apple (AAPL)?"}}}
     }'
   ```
3. **Response:**
   - The response will include a markdown-formatted answer in `outputs.variables.response.value`.

---

## Using CLI Mode

Just run any agent script directly:

```bash
python recipe-creator.py
```

You will be prompted for a query and see the markdown output in your terminal.

---

## Adding a New Agent

1. Copy an existing agent script (e.g., `movie-recommender.py`).
2. Wrap your agent logic in a workflow class with a `.run(query)` method.
3. Add API entrypoint logic using `create_agent_api` (see other scripts for reference).
4. Register any tools or models needed.
5. (Optional) Add session/caching with `SqliteStorage`.

---

## Main Files

- `agent_api_server.py`: FastAPI server factory for agent APIs.
- `blog-post-generator.py`, `finance-agent.py`, etc.: Example agent scripts.
- `requirements.txt`: Python dependencies.
- `Makefile`, `Dockerfile`: For advanced deployment/automation.

---

## Security & Logging

- Do **not** hardcode secrets; use environment variables.
- Logging is enabled for debugging and error tracking.
- Validate and sanitize all user input if exposing to the public.

---

## Customization

- Add new tools, models, or workflows by extending the agent classes.
- Adjust instructions, prompts, and output formatting as needed.
- Integrate with external APIs or databases as required.

---

## Contributing

Pull requests and issues are welcome! Please open an issue to discuss major changes first.

---

## License

MIT (or specify your license here)
