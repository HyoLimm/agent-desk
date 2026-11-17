"""agent-desk: hook(훅 이벤트 -> ~/.claude/agent-desk/state) / 인자 없음(감자 직장인 창) / test(자체 검사)."""
import json
import os
import random
import re
import socket
import subprocess
import sys
import time

STATE_DIR = os.path.join(os.path.expanduser("~"), ".claude", "agent-desk", "state")
KEY = "#ff00ff"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 세션별 네온 강조색: 초록, 청록, 자홍, 보라, 라임, 주황
TUNICS = ["#30e060", "#30d0f0", "#f050d0", "#a070ff", "#c0f030", "#ff8030"]

QUIPS = {  # 상태가 바뀔 때 책상 밑 글자 자리에 잠깐 뜨는 한마디(작은 책상 폭에 맞춰 5글자 이내)
    "work": ["야근 확정", "타닥타닥", "집중…", "바쁨"],
    "wait": ["결재 좀…", "허락 좀", "눌러줘요"],
    "done": ["퇴근각", "끝!", "칼퇴"],
    "fail": ["아니 왜", "망했다", "어…"],
}
CAPTIONS = {"idle_b": "부재중"}  # 포즈별 밑 글자(대사가 없을 때 표시)


def variants(state, keys):
    # 상태의 포즈 후보: "idle" -> ["idle", "idle_b", "idle_c"]처럼 같은 상태의 변형 키 전부
    return [k for k in keys if k == state or k.startswith(state + "_")]


def merge_state(states):
    # 같은 종류 인스턴스들의 상태를 책상 하나의 상태로 합친다
    for s in ("wait", "fail", "work", "done"):
        if s in states:
            return s
    return "idle"


def map_event(payload):
    ev = payload.get("hook_event_name")
    if ev == "SessionStart":
        return "idle"
    if ev in ("UserPromptSubmit", "PreToolUse", "PostToolUse"):
        return "work"
    if ev == "PostToolUseFailure":
        return "fail"
    if ev == "PermissionRequest":
        return "wait"
    if ev == "Notification":
        return "wait" if payload.get("notification_type") == "permission_prompt" else None
    if ev == "Stop":
        return "done"
    if ev == "SessionEnd":
        return "gone"
    if ev == "SubagentStart":
        return "work"
    if ev == "SubagentStop":
        return "gone"
    return None


def agent_key(payload):
    # 파일명으로 쓰므로 영숫자·-·_ 외 글자는 제거(경로 조작 방지)
    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(payload.get("session_id") or "")) or "main"
    aid = re.sub(r"[^A-Za-z0-9_-]", "", str(payload.get("agent_id") or ""))
    return sid + "." + aid if aid else sid


def split_name(name):
    # 파일명(확장자 제외) -> (세션, 하위 에이전트 또는 None)
    sid, dot, aid = name.partition(".")
    return sid, (aid if dot else None)


def launch():
    if sys.platform != "win32":
        return
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    exe = pyw if os.path.exists(pyw) else sys.executable
    subprocess.Popen([exe, os.path.abspath(__file__)],
                     creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                     close_fds=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)


def hook():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        state = map_event(payload)
        if state is None:
            return
        if payload.get("hook_event_name") == "SessionStart" and not payload.get("agent_id"):
            launch()
        os.makedirs(STATE_DIR, exist_ok=True)
        key = agent_key(payload)
        path = os.path.join(STATE_DIR, key + ".json")
        if state == "gone":
            if "." in key:
                if os.path.exists(path):
                    os.remove(path)
            else:  # 세션 종료: 메인 파일(<sid>.json)과 하위 파일(<sid>.<aid>.json) 모두
                for fn in os.listdir(STATE_DIR):
                    if fn.startswith(key + "."):
                        os.remove(os.path.join(STATE_DIR, fn))
            return
        tmp = path + ".tmp"  # 에이전트당 파일이 하나라 같은 파일을 동시에 쓰는 훅은 없다
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"state": state, "tool": payload.get("tool_name", ""),
                       "type": payload.get("agent_type", ""), "time": time.time()}, f)
        os.replace(tmp, path)
    except Exception:
        pass


def window():
    if sys.platform != "win32":
        sys.stderr.write("agent-desk: Windows 전용\n")
        return
    guard = socket.socket()
    try:
        guard.bind(("127.0.0.1", 47613))  # ponytail: 고정 포트로 단일 실행 보장, 다른 프로그램과 겹치면 포트 변경
    except OSError:
        return
    from sprites_potato32 import FRAMES, PALETTE
    import tkinter as tk
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", KEY)
    root.configure(bg=KEY)
    # 창 크기 고정: 세션 한 줄 = 하위 슬롯 4개(64px) + 메인(96px) 가로, 높이 그림 96 + 글자 24. 3줄.
    root.geometry("352x360+%d+%d" % (root.winfo_screenwidth() - 160 - 256, root.winfo_screenheight() - 220 - 240))

    # images[zoom][옷 색 인덱스][상태]: PhotoImage, 참조를 들고 있어야 GC되지 않는다
    images = {3: [{} for _ in TUNICS], 2: [{} for _ in TUNICS]}
    n = len(FRAMES["idle"][0])
    for ti, tunic in enumerate(TUNICS):
        for name, pair in FRAMES.items():
            for zoom in images:
                images[zoom][ti][name] = []
            for rows in pair:
                img = tk.PhotoImage(width=n, height=n)
                for y, row in enumerate(rows):
                    for x, c in enumerate(row):
                        img.put(tunic if c == "t" else PALETTE.get(c, KEY), (x, y))
                for zoom in images:
                    images[zoom][ti][name].append(img.zoom(zoom))

    # slots[줄][칸]: 칸 0~3 = 하위(왼쪽부터), 칸 4 = 메인. 위젯은 여기서 한 번만 만든다.
    slots = []
    for r in range(3):
        line = []
        for i in range(5):
            pic = tk.Label(root, bg=KEY, bd=0)
            pic.grid(row=2 * r, column=i, sticky="s")
            txt = tk.Label(root, bg=KEY, fg="#ffffff", font=("Consolas", 8), bd=0)
            txt.grid(row=2 * r + 1, column=i)
            line.append((pic, txt))
        slots.append(line)
        root.grid_rowconfigure(2 * r, minsize=96)
        root.grid_rowconfigure(2 * r + 1, minsize=24)
    for i in range(5):
        root.grid_columnconfigure(i, minsize=96 if i == 4 else 64)

    drag = [0, 0]

    def press(e):
        drag[:] = [e.x_root - root.winfo_x(), e.y_root - root.winfo_y()]

    root.bind_all("<ButtonPress-1>", press)
    root.bind_all("<B1-Motion>", lambda e: root.geometry("+%d+%d" % (e.x_root - drag[0], e.y_root - drag[1])))
    root.bind_all("<Button-3>", lambda e: root.destroy())

    cur = {"n": 0}

    def read_sessions():
        now = time.time()
        found = {}  # 에이전트 종류 -> 살아 있는 인스턴스 목록(메인은 "")
        try:
            names = sorted(os.listdir(STATE_DIR))
        except OSError:
            return found
        for fn in names:
            if not fn.endswith(".json"):
                continue
            path = os.path.join(STATE_DIR, fn)
            sid, aid = split_name(fn[:-5])
            try:
                with open(path, encoding="utf-8") as f:
                    d = json.load(f)
                d = {"state": d["state"], "tool": d.get("tool", ""), "type": d.get("type", ""),
                     "time": float(d.get("time", 0))}
            except Exception:
                continue
            if now - d["time"] > 86400:  # 하루 넘은 파일은 쌓이지 않게 삭제
                try:
                    os.remove(path)
                except OSError:
                    pass
                continue
            # ponytail: 600초 넘게 조용한 인스턴스는 죽은 것으로 본다(비정상 종료 대비). 오래 생각하는 에이전트가 사라져 보이면 값 조정
            if now - d["time"] <= 600:
                found.setdefault("" if aid is None else d["type"], []).append(d)
        return found

    def show(slot, zoom, ti, state, text):
        state = state if state in images[zoom][ti] else "idle"
        slot[0].configure(image=images[zoom][ti][state][(cur["n"] // 2) % 2])  # 200ms x 2 = 400ms
        slot[1].configure(text=text)

    order = {"": 0}  # 종류 -> 처음 본 순번(색 인덱스), 지휘자는 항상 0
    last_alive = {}  # 종류 -> 살아 있는 인스턴스를 마지막으로 본 시각
    last_state = {}  # 종류 -> 직전에 그린 상태
    quip = {}  # 종류 -> (대사, 표시 끝 시각)
    pose = {}  # 종류 -> 지금 그리는 포즈 키(상태가 바뀔 때 변형 중 하나를 랜덤으로 고름)
    # 하위 종류 책상 자리: 아래 줄 칸 3->0, 가운데 줄 3->0, 위 줄 3->0
    cells = [(r, i) for r in (2, 1, 0) for i in (3, 2, 1, 0)]

    def tick():
        now = time.time()
        alive = read_sessions()
        for t in alive:
            order.setdefault(t, len(order))
            last_alive[t] = now
        shown = {}  # (줄, 칸) -> (배율, 색 인덱스, 상태, 글자)
        k = 0
        for t in order:
            if now - last_alive.get(t, -1e9) > 600:
                last_state.pop(t, None)
                quip.pop(t, None)
                pose.pop(t, None)
                continue
            insts = alive.get(t, [])
            # done은 6초 지나면 idle로 본다
            state = merge_state(["idle" if d["state"] == "done" and now - d["time"] > 6 else d["state"]
                                 for d in insts])
            ti = order[t] % len(TUNICS)
            if last_state.get(t) != state:
                last_state[t] = state
                pose[t] = random.choice(variants(state, FRAMES) or [state])
                if state in QUIPS:
                    quip[t] = (random.choice(QUIPS[state]), now + 4)
                else:
                    quip.pop(t, None)
            said = quip[t][0] if t in quip and now < quip[t][1] else ""
            # 밑 글자는 한글 대사만 보여 준다. 같은 종류가 여러 개면 개수 표시: 지휘자는 "3인분 하는 중", 하위 종류는 "알바 3명"
            text = ("%d인분 하는 중" if t == "" else "알바 %d명") % len(insts) if len(insts) >= 2 else ""
            text = CAPTIONS.get(pose.get(t, state)) or text
            if t == "":
                shown[(2, 4)] = (3, ti, pose.get(t, state), said or text)
            else:
                if k >= len(cells):  # ponytail: 하위 종류 12개까지만 표시
                    continue
                shown[cells[k]] = (2, ti, pose.get(t, state), said or text)
                k += 1
        for r in range(3):
            for i in range(5):
                slot = slots[r][i]
                if (r, i) in shown:
                    show(slot, *shown[(r, i)])
                else:
                    slot[0].configure(image="")
                    slot[1].configure(text="")
        cur["n"] += 1
        root.after(200, tick)

    tick()
    root.mainloop()


def test():
    from sprites_potato32 import FRAMES, PALETTE
    assert len(FRAMES["idle"][0]) == 32
    for name, pair in FRAMES.items():
        assert len(pair) == 2, name
        for rows in pair:
            assert len(rows) == 32, (name, len(rows))
            for row in rows:
                assert len(row) == 32, (name, row)
                assert all(c == "." or c in PALETTE for c in row), (name, row)
    assert len(PALETTE) <= 9
    assert len(TUNICS) == 6
    assert all(re.fullmatch(r"#[0-9a-f]{6}", c) for c in TUNICS), TUNICS
    for states, want in [([], "idle"), (["idle", "work"], "work"), (["done", "work"], "work"),
                         (["work", "wait"], "wait"), (["fail", "work"], "fail"),
                         (["done", "idle"], "done")]:
        assert merge_state(states) == want, states
    cases = [({"hook_event_name": "SessionStart"}, "idle"),
             ({"hook_event_name": "UserPromptSubmit"}, "work"),
             ({"hook_event_name": "PreToolUse"}, "work"),
             ({"hook_event_name": "PostToolUse"}, "work"),
             ({"hook_event_name": "PostToolUseFailure"}, "fail"),
             ({"hook_event_name": "PermissionRequest"}, "wait"),
             ({"hook_event_name": "Notification", "notification_type": "permission_prompt"}, "wait"),
             ({"hook_event_name": "Notification", "notification_type": "idle_prompt"}, None),
             ({"hook_event_name": "Stop"}, "done"),
             ({"hook_event_name": "SessionEnd"}, "gone"),
             ({"hook_event_name": "SubagentStart"}, "work"),
             ({"hook_event_name": "SubagentStop"}, "gone"),
             ({"hook_event_name": "Whatever"}, None)]
    for payload, want in cases:
        assert map_event(payload) == want, payload
    for payload, want in [({}, "main"), ({"session_id": "abc-1"}, "abc-1"),
                          ({"session_id": "abc-1", "agent_id": "a17e"}, "abc-1.a17e"),
                          ({"session_id": "../s", "agent_id": "../x"}, "s.x"),
                          ({"agent_id": "a17e"}, "main.a17e")]:
        assert agent_key(payload) == want, payload
    for name, want in [("abc-1", ("abc-1", None)), ("abc-1.a17e", ("abc-1", "a17e")),
                       ("main.a17e", ("main", "a17e"))]:
        assert split_name(name) == want, name
    assert all(s in ("idle", "work", "wait", "done", "fail") for s in QUIPS), QUIPS
    assert all(q and len(q) <= 5 for qs in QUIPS.values() for q in qs), QUIPS
    assert variants("idle", ["idle", "idle_b", "work", "done", "done_c"]) == ["idle", "idle_b"]
    assert variants("work", ["idle", "idle_b", "work"]) == ["work"]
    assert all(k.split("_")[0] in ("idle", "work", "wait", "done", "fail") for k in FRAMES), list(FRAMES)
    assert all(s in FRAMES for s in ("idle", "work", "wait", "done", "fail"))
    assert all(k in FRAMES and 0 < len(v) <= 5 for k, v in CAPTIONS.items()), CAPTIONS
    print("ok")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "hook":
        hook()
        sys.exit(0)
    elif mode == "test":
        test()
    else:
        window()
