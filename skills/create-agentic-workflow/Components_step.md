## Create the parts

Decide the kind of each step, then create it with the matching skill.

| The part is | Kind | Call |
|---|---|---|
| A procedure the agent follows | skill | `create-agentic-skill` |
| Work given to an isolated worker | agent | `create-agentic-agent` |
| An automatic check or gate | hook | `create-agentic-hook` |

- Use the kind the user named. If the user named none, a step is a skill.
- A step name is the name of its skill or agent (kebab-case).
- Give each call everything it needs, so it does not have to ask: the name, a one-sentence purpose, the file the step reads and the file it writes (the next step reads that file). For a hook, give the command it runs, when it runs, and what it returns, in the user's words.
- Run the calls one after the other. Wait until a call has finished, with its own tests green, before the next one.
- A call is finished only when the called skill has done all its own steps in full, with every run it requires. Never shorten one: not fewer runs, not a skipped step.
