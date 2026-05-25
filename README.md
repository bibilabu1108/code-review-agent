# Code Review Agent

A small Python / Streamlit code review assistant powered by DeepSeek.

## Features

- Upload Python / C / C++ source files for review.
- Paste code directly into the editor area.
- Choose review type and output detail level.
- Ask follow-up questions in chat.
- Download the latest review as a Markdown report.

## Setup

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Create a local `.env` file:

```powershell
copy .env.example .env
```

3. Put your DeepSeek API key into `.env`:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## Run

Command line:

```powershell
python agent.py
```

Web app:

```powershell
streamlit run agent.py
```

## Deploy to Streamlit Community Cloud

Deploy settings:

- Repository: `bibilabu1108/code-review-agent`
- Branch: `main`
- Main file path: `agent.py`

In Streamlit Cloud secrets, add:

```toml
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
```

## Security

Do not commit `.env`. It contains your private API key and is ignored by `.gitignore`.
