# GitaGPT Codebase Overview

This document provides a description of every file and directory in the GitaGPT project to help understand the system's architecture and functionality.

## Root Directory Files

- [app.py](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/app.py): The main entry point for the Flask web application. It initializes the app, registers blueprints, and sets up the database if it doesn't exist.
- [config.py](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/config.py): Centralized configuration file containing environment variables, API keys, file paths, rate limits, and content guardrails.
- [run_local.py](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/run_local.py): A script to run the Telegram bot locally using long polling instead of webhooks. Useful for development.
- [Procfile](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/Procfile): Deployment configuration for platforms like Heroku or Railway.
- [requirements.txt](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/requirements.txt): List of Python dependencies required to run the project.
- [railway.json](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/railway.json): Deployment settings specifically for the Railway platform.
- [CODEBASE_OVERVIEW.md](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/CODEBASE_OVERVIEW.md): This file.
- [.env](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/.env): Local environment variables (API keys, etc.). *Hidden by default.*
- [.gitignore](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/.gitignore): Specifies files and directories that Git should ignore (e.g., `__pycache__`, `.env`, `.venv`).

## Directories

### [routes/](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/routes)
Contains Flask Blueprints for different communication channels.
- `api.py`: Implements RESTful API endpoints for external access.
- `telegram.py`: Handles incoming Telegram messages, commands, and voice notes.
- `web.py`: Handles web-based routes for the frontend.

### [services/](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/services)
The core business logic of the application.
- `ai_interpretation.py`: Interface with LLMs (Cohere/Google GenAI) to interpret Bhagavad Gita verses.
- `search.py`: Vector search implementation using ChromaDB to find relevant Shlokas based on user queries.
- `voice.py`: Handles speech-to-text (transcription) and text-to-speech.
- `formatter.py`: Utilities for formatting Shloka text and interpretations for various platforms.
- `session.py`: Manages user sessions and conversation history.
- `daily.py`: Logic for scheduled tasks, such as sending a "Shloka of the Day".
- `telegram_api.py`: Low-level wrapper for Telegram Bot API calls.

### [models/](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/models)
Data structures and models.
- `shloka.py`: Defines the `Shloka` class and data validation for Gita verses.

### [guardrails/](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/guardrails)
Code for ensuring safety and performance.
- `content_filter.py`: Filters sensitive or blocked keywords from user inputs.
- `rate_limiter.py`: Implements rate limiting to prevent API abuse.
- `sanitizer.py`: Cleans and normalizes input text.

### [data/](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/data)
Stored data used by the application.
- `gita_mvp.json`: The curated set of Shlokas used for the MVP.
- `chromadb_mvp/`: The vector database for semantic search.
- `curated_topics.json`: Pre-defined topics for quick access.
- `interpretations.json`: Cached AI interpretations of various verses.
- `raw/`: Subdirectory containing original source data files (`gita_complete`, `gita_tagged`, etc.).

### [scripts/](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/scripts)
Utility scripts for setup and data processing.
- `setup_db.py`: Initializes the SQLite and vector databases.
- `fetch_gita.py`: Script to pull Gita text from external sources.
- `mvp_embeddings.py`: Generates vector embeddings for the Shlokas.
- `auto_tag.py`: Automatically categorizes Shlokas using AI.

### [docs/](file:///Users/ashishgupta/Desktop/Projects/gita-gpt/docs)
Detailed documentation and technical specs.
- `ARCHITECTURE.md`: Technical overview of the system design.
- `DECISIONS.md`: Record of key technical and design decisions.
- `GTM.md`: Go-To-Market strategy and product roadmap.
- `GUIDE.md`: General user or developer guide.
- `IMPLEMENTATION_GUIDE.md`: Deep dive into how specific features are built.
- `features.md`: List of implemented and planned features.
- `problem.md`: Definition of the problem GitaGPT aims to solve.
- `update.md`: Log of recent updates and changes.
- `PRODUCT_LEDGER_METHODOLOGY.md`: Detailed documentation on the project's development methodology.
