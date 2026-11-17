# agent-desk

[한국어](#한국어) | [English](#english)

## 한국어

Claude Code 세션과 하위 에이전트가 지금 무엇을 하는지, 책상에 앉은 픽셀 감자 직장인이 보여 줍니다.

### 요구 사항

- Windows
- Python 3.10 이상(tkinter 포함), PATH에서 `python`으로 실행 가능해야 합니다

### 설치

```
/plugin marketplace add HyoLimm/agent-desk
/plugin install agent-desk@agent-desk
```

### 동작

- 세션이 시작되면 창이 자동으로 뜹니다.
- 에이전트 종류마다 책상이 하나씩 생기고 네온 색이 서로 다릅니다. 메인 세션들은 큰 책상 하나(지휘자)를 같이 씁니다.
- 같은 종류의 에이전트가 여러 개면 한 책상을 같이 쓰고 개수를 표시합니다(예: `3명`). 지휘자 책상은 살아 있는 채팅 수를 표시합니다(예: `채팅 3개`).
- 책상의 상태가 바뀌면 몇 초 동안 짧은 한마디가 뜹니다.
- 10분 동안 쓰이지 않은 책상은 숨겨집니다.
- 창은 끌어서 옮기고, 오른쪽 클릭으로 닫습니다.
- 쉼, 작업, 완료는 여러 포즈 중 하나가 랜덤으로 나옵니다.

### 상태

| 상태 | 보이는 모습 |
|------|-------------|
| idle | 감자가 책상에서 쉬거나, "부재중" 카드를 두고 자리를 비웁니다 |
| work | 일하는 중 |
| wait | 사용자의 승인을 기다리는 중 |
| done | 방금 턴을 마침(몇 초 뒤 idle로 돌아갑니다) |
| fail | 도구 호출이 실패함 |

### 데이터

상태 파일은 `~/.claude/agent-desk/state`에만 씁니다. 네트워크로 보내는 것은 없습니다. 프롬프트와 도구 입력 내용은 저장하지 않고, 상태, 도구 이름, 에이전트 종류, 시각만 저장합니다.

### 제거

```
/plugin uninstall agent-desk@agent-desk
```

창은 오른쪽 클릭으로 닫고, 상태 파일까지 지우려면 `~/.claude/agent-desk` 폴더를 삭제합니다.

### 라이선스

MIT. [LICENSE](LICENSE)를 참고하세요.

## English

A pixel potato office worker at a desk that shows what each Claude Code session and subagent is doing.

### Requirements

- Windows
- Python 3.10+ with tkinter, runnable as `python` from PATH

### Install

```
/plugin marketplace add HyoLimm/agent-desk
/plugin install agent-desk@agent-desk
```

### Behavior

- The window opens automatically when a session starts.
- Each agent type gets one desk, with its own neon color. The main sessions share one big desk (the conductor).
- Several agents of the same type share a desk and show a count (Korean, e.g. `3명`; the conductor desk shows the number of live chats, e.g. `채팅 3개`).
- When a desk changes state it shows a short quip for a few seconds (Korean for now).
- A desk that goes unused for 10 minutes is hidden.
- Drag to move the window. Right-click to close it.
- Idle, work and done each pick one of several poses at random.

### States

| State | What you see |
|-------|--------------|
| idle  | The potato rests at the desk, or has left an "away" card on it |
| work  | Working |
| wait  | Waiting for your permission |
| done  | Just finished a turn (returns to idle after a few seconds) |
| fail  | A tool call failed |

### Data

State files are written only to `~/.claude/agent-desk/state`. Nothing is sent over the network. Prompts and tool inputs are not stored; only the state, tool name, agent type, and timestamp are.

### Uninstall

```
/plugin uninstall agent-desk@agent-desk
```

Right-click the window to close it, then delete `~/.claude/agent-desk` if you want to remove the state files.

### License

MIT. See [LICENSE](LICENSE).
