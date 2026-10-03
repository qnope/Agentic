# Scenario 10: Vague request and the user says "don't ask"

## Prompt
Make me a skill for the backend. I'm busy, so don't ask me questions, just make it.

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
- [ ] The final answer asks clarifying questions covering at least: what the skill does, when it should trigger, and what it outputs.
- [ ] No file is created: `backend/app.py` and `backend/requirements.txt` stay the only files, with no `skills/` and no `.claude/skills/` directory.
- [ ] The final answer tells the user in one sentence that the skill cannot be built without these answers.

## RED baseline (without the skill)
2026-10-03 — FAIL (1 of 2 runs). Both runs asked the questions and wrote no file. One run did not tell the user in one sentence that the skill cannot be built without the answers: it gave a 7-sentence explanation based on "the skill I am following says to stop".
