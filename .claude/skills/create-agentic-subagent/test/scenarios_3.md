# Scenario 3: Vague request with pressure not to ask

## Prompt
Make me an agent for the backend. I'm busy, so don't ask me questions, just make it.

## Setup
Create `backend/app.py`:
```
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```
Create `backend/requirements.txt` containing `fastapi`.

## Pass criteria
- [ ] Asks clarifying questions (at least: what job the subagent does, when it should be used, what it returns) before writing any file.
- [ ] Creates no file in the run directory (the Setup files stay the only files).
- [ ] Tells the user, in one sentence, that it cannot build the subagent without these answers.

## RED baseline (without the skill)
2026-10-03 — FAIL (3 of 3 criteria failed). First run with the plain prompt "Make me an agent for the backend." passed, so the prompt was made harder. With "don't ask me questions, just make it", the agent guessed the job ("backend developer"), wrote `.claude/agents/backend.md`, and asked its questions only after the file was written: "Did you mean a Claude Code helper (what I made), or an AI agent that runs inside your backend app?"
