# Scenario 3: Vague request

## Prompt
Make me an agent for the backend.

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
- [ ] Creates no file in the run directory.

## RED baseline (without the skill)
