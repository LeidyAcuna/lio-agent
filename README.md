# Lio-Agent: AI-Powered Expense Manager

An asynchronous Telegram bot designed to streamline personal finance tracking. Lio-Agent uses Natural Language Processing (NLP) to transform plain text messages into structured financial data.

## 🚀 Key Features

- **Natural Language Input**: Record expenses by simply chatting (e.g., "Spent 50k on groceries yesterday via Nequi").
- **AI Extraction**: Powered by **Ollama (Llama 3.1)** and **LangChain** for precise data structuring.
- **Async Architecture**: High-performance processing using Python's `asyncio` and `Producer-Consumer` patterns.
- **Smart Resource Management**: Integrated **Semaphore** control to prevent hardware overload during AI inference.
- **SQL Telemetry**: Custom logging cursor for real-time SQL debugging and traceability.

## 🛠 Tech Stack

- **Languaje**: Python 3.14+
- **Frameworks**: `python-telegram-bot`, `LangChain`
- **AI Inference**: `Ollama`
- **Database**: `PostgreSQL` with `psycopg3` (Connection Pool)
- **Validation**: `Pydantic`
- **Infrastructure**: `Docker` & `Docker Compose`

## 🏗 Architecture Overview

The system operates as a non-blocking pipeline:
1. **Producer**: Telegram bot receives updates and enqueues messages.
2. **Queue**: An asynchronous `asyncio.Queue` acts as a buffer.
3. **Consumers (Workers)**: Multiple background workers pull messages, process them with LLMs via `ainvoke`, and persist data to the DB.

## 🚦 Quick Start

1. **Clone the repo** and set up your .env file with your Telegram Bot Token.
2. **Run with Docker Compose**:
   ```bash
   docker compose up --build
