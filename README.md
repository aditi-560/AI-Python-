# Hunter – Web Chat Frontend

This project now includes a minimal web UI backed by a FastAPI server that wraps the existing LangGraph agent using Gemini.

## Requirements

- Python 3.13+
- A Google API key in `.env`:

```
GOOGLE_API_KEY=your_key_here
```

## Install

Using uv:

```
uv sync
```

Or pip:

```
python -m venv .venv
. .venv/Scripts/activate
pip install -U pip
pip install langchain langchain-openai langgraph python-dotenv langchain-google-genai fastapi uvicorn[standard]
```

## Run the server

```
uv run uvicorn project.main:app --reload
```

Then open `http://127.0.0.1:8000/`.

## Desktop GUI (Tkinter)

You can also run a native desktop chat window:

```
uv run python project/gui.py
```

If you prefer pip/venv, activate your env and run:

```
python project/gui.py
```