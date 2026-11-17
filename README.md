# agent-desk

A pixel potato office worker at a desk that shows what each Claude Code session and subagent is doing.

## Requirements

- Windows
- Python 3.10+ with tkinter, runnable as `python` from PATH

## Install

```
/plugin marketplace add HyoLimm/agent-desk
/plugin install agent-desk@agent-desk
```

## Behavior

- The window opens automatically when a session starts.
- Each agent type gets one desk, with its own neon color. The main sessions share one big desk (the conductor).
- Several agents of the same type share a desk and show a count (Korean, e.g. `3명`; the conductor desk shows the number of live chats, e.g. `채팅 3개`).
- When a desk changes state it shows a short quip for a few seconds (Korean for now).
- A desk that goes unused for 10 minutes is hidden.
- Drag to move the window. Right-click to close it.
- Idle, work and done each pick one of several poses at random.

## States

| State | What you see |
|-------|--------------|
| idle  | The potato rests at the desk, or has left an "away" card on it |
| work  | Working |
| wait  | Waiting for your permission |
| done  | Just finished a turn (returns to idle after a few seconds) |
| fail  | A tool call failed |

## Data

State files are written only to `~/.claude/agent-desk/state`. Nothing is sent over the network. Prompts and tool inputs are not stored; only the state, tool name, agent type, and timestamp are.

## Uninstall

```
/plugin uninstall agent-desk@agent-desk
```

Right-click the window to close it, then delete `~/.claude/agent-desk` if you want to remove the state files.
