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
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".claude", "agent-desk", "config.json")
SKINS = {"감자": "sprites_potato32", "햄스터": "sprites_hamster32"}  # 메뉴 이름 -> 그림 모듈(scripts 폴더에 있는 것만 메뉴에 뜬다)
KEY = "#ff00ff"
TEXT_BG = "#1a1020"  # 밑 글자 바탕(스프라이트 외곽선과 같은 거의 검정)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 세션별 네온 강조색: 초록, 청록, 자홍, 보라, 라임, 주황
TUNICS = ["#30e060", "#30d0f0", "#f050d0", "#a070ff", "#c0f030", "#ff8030"]

QUIPS = {  # 상태가 바뀔 때 책상 밑 글자 자리에 잠깐 뜨는 한마디(작은 책상 폭에 맞춰 5글자 이내)
    "work": ["야근 확정", "타닥타닥", "집중…", "바쁨"],
    "wait": ["결재 좀…", "허락 좀", "눌러줘요"],
    "done": ["퇴근각", "끝!", "칼퇴"],
    "fail": ["아니 왜", "망했다", "어…"],
}
CAPTIONS = {"idle_b": ["부재중", "쉬러감", "화장실감", "도망감"]}  # 포즈별 밑 글자 후보(포즈가 정해질 때 하나를 골라 대사가 없을 때 표시)
STAGE_AFTER = {"idle": (60, 180), "wait": (30,)}  # 같은 상태가 이어진 초: 넘을 때마다 포즈가 한 단계 세진다(<포즈>~2, ~3 그림이 있을 때만)


def variants(state, keys):
    # 상태의 포즈 후보: "idle" -> ["idle", "idle_b", "idle_c"]처럼 같은 상태의 변형 키 전부. 단계 그림(~2, ~3)은 뽑지 않는다
    return [k for k in keys if "~" not in k and (k == state or k.startswith(state + "_"))]


def agent_label(agent_type, limit):
    # 머리 위 이름: 사람마다 에이전트 이름이 달라 원래 이름을 그대로 쓴다. "plugin:name"이면 name만.
    # 한 줄에 안 들어가면 -나 _ 뒤에서 끊어 두 줄로, 구분자가 없으면 limit에서 끊고, 둘째 줄도 넘치면 … 로 자른다
    name = agent_type.rsplit(":", 1)[-1]
    if len(name) <= limit:
        return name
    cut = max(name.rfind("-", 0, limit), name.rfind("_", 0, limit)) + 1 or limit
    head, tail = name[:cut], name[cut:]
    return head + "\n" + (tail if len(tail) <= limit else tail[:limit - 1] + "…")


def staged(pose, state, elapsed, keys):
    # 상태가 오래 이어질수록 같은 포즈의 더 센 단계 그림을 고른다. 그 단계 그림이 없으면 있는 것 중 가장 높은 단계
    level = 1 + sum(elapsed >= s for s in STAGE_AFTER.get(state, ()))
    while level > 1 and "%s~%d" % (pose, level) not in keys:
        level -= 1
    return pose if level == 1 else "%s~%d" % (pose, level)


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


def saved_skin():
    # 마지막으로 고른 캐릭터 이름. 없거나 깨졌거나 모르는 이름이면 첫 캐릭터
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            name = json.load(f).get("skin")
    except Exception:
        name = None
    return name if name in SKINS else next(iter(SKINS))


def save_skin(name):
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"skin": name}, f, ensure_ascii=False)
    except OSError:
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
    import importlib
    import tkinter as tk
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", KEY)
    root.configure(bg=KEY)
    # 창 크기 고정: 한 줄 = 하위 슬롯 4개(64px) + 메인(96px) 가로, 높이 이름 두 줄 28 + 그림 96 + 글자 24. 3줄.
    root.geometry("352x444+%d+%d" % (root.winfo_screenwidth() - 160 - 256, root.winfo_screenheight() - 220 - 324))

    # 고를 수 있는 캐릭터: 그림 모듈이 실제로 있는 것만
    skins = [s for s in SKINS if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), SKINS[s] + ".py"))]
    skin = {"name": None, "FRAMES": {}, "images": {}}

    def load_skin(name):
        # images[zoom][옷 색 인덱스][상태]: PhotoImage, 참조를 들고 있어야 GC되지 않는다
        mod = importlib.import_module(SKINS[name])
        frames, palette = mod.FRAMES, mod.PALETTE
        images = {3: [{} for _ in TUNICS], 2: [{} for _ in TUNICS]}
        n = len(frames["idle"][0])
        for ti, tunic in enumerate(TUNICS):
            for key, pair in frames.items():
                for zoom in images:
                    images[zoom][ti][key] = []
                for rows in pair:
                    img = tk.PhotoImage(width=n, height=n)
                    img.put(tuple(tuple(tunic if c == "t" else palette.get(c, KEY) for c in row) for row in rows))
                    for zoom in images:
                        images[zoom][ti][key].append(img.zoom(zoom))
        skin.update(name=name, FRAMES=frames, images=images)

    load_skin(saved_skin() if saved_skin() in skins else skins[0])

    # slots[줄][칸]: 칸 0~3 = 하위(왼쪽부터), 칸 4 = 메인. 위젯은 여기서 한 번만 만든다.
    slots = []
    for r in range(3):
        line = []
        for i in range(5):
            tag = tk.Label(root, bg=KEY, fg="#ffffff", font=("Consolas", 8), bd=0, padx=3)  # 머리 위 에이전트 이름
            tag.grid(row=3 * r, column=i, sticky="s")
            pic = tk.Label(root, bg=KEY, bd=0)
            pic.grid(row=3 * r + 1, column=i, sticky="s")
            txt = tk.Label(root, bg=KEY, fg="#ffffff", font=("Consolas", 8), bd=0, padx=3)
            txt.grid(row=3 * r + 2, column=i)
            line.append((pic, txt, tag))
        slots.append(line)
        root.grid_rowconfigure(3 * r, minsize=28)
        root.grid_rowconfigure(3 * r + 1, minsize=96)
        root.grid_rowconfigure(3 * r + 2, minsize=24)
    for i in range(5):
        root.grid_columnconfigure(i, minsize=96 if i == 4 else 64)

    drag = [0, 0]

    def press(e):
        drag[:] = [e.x_root - root.winfo_x(), e.y_root - root.winfo_y()]

    root.bind_all("<ButtonPress-1>", press)
    root.bind_all("<B1-Motion>", lambda e: root.geometry("+%d+%d" % (e.x_root - drag[0], e.y_root - drag[1])))
    menu = tk.Menu(root, tearoff=0)
    choice = tk.StringVar(value=skin["name"])

    def pick_skin():
        # 고른 캐릭터를 저장하고 그림을 다시 만든다. 포즈 기억은 새 캐릭터 기준으로 다시 뽑게 비운다
        save_skin(choice.get())
        load_skin(choice.get())
        for memo in (last_state, pose, caption, since):
            memo.clear()

    for s in skins:
        menu.add_radiobutton(label=s, variable=choice, value=s, command=pick_skin)
    menu.add_separator()
    menu.add_command(label="닫기", command=root.destroy)
    root.bind_all("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

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

    def show(slot, zoom, ti, state, text, name):
        images = skin["images"]
        state = state if state in images[zoom][ti] else "idle"
        slot[0].configure(image=images[zoom][ti][state][(cur["n"] // 2) % 2])  # 200ms x 2 = 400ms
        # 글자 테두리가 투명 키 색(자홍)과 섞이면 분홍 번짐이 남으므로, 글자가 있을 때만 어두운 바탕을 깐다
        slot[1].configure(text=text, bg=TEXT_BG if text else KEY)
        slot[2].configure(text=name, bg=TEXT_BG if name else KEY)

    order = {"": 0}  # 종류 -> 처음 본 순번(색 인덱스), 지휘자는 항상 0
    last_alive = {}  # 종류 -> 살아 있는 인스턴스를 마지막으로 본 시각
    last_state = {}  # 종류 -> 직전에 그린 상태
    quip = {}  # 종류 -> (대사, 표시 끝 시각)
    pose = {}  # 종류 -> 지금 그리는 포즈 키(상태가 바뀔 때 변형 중 하나를 랜덤으로 고름)
    caption = {}  # 종류 -> 지금 포즈의 밑 글자(포즈를 고를 때 함께 골라 tick마다 바뀌지 않게 함)
    since = {}  # 종류 -> 지금 상태가 시작된 시각(단계 계산용)
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
                caption.pop(t, None)
                since.pop(t, None)
                continue
            insts = alive.get(t, [])
            # done은 6초 지나면 idle로 본다
            state = merge_state(["idle" if d["state"] == "done" and now - d["time"] > 6 else d["state"]
                                 for d in insts])
            ti = order[t] % len(TUNICS)
            if last_state.get(t) != state:
                last_state[t] = state
                since[t] = now
                pose[t] = random.choice(variants(state, skin["FRAMES"]) or [state])
                caption[t] = random.choice(CAPTIONS.get(pose[t], [""]))
                if state in QUIPS:
                    quip[t] = (random.choice(QUIPS[state]), now + 4)
                else:
                    quip.pop(t, None)
            said = quip[t][0] if t in quip and now < quip[t][1] else ""
            # 밑 글자는 한글 대사만 보여 준다. 같은 종류가 여러 개면 개수 표시: 지휘자는 "3인분 하는 중", 하위 종류는 "알바 3명"
            text = ("%d인분 하는 중" if t == "" else "알바 %d명") % len(insts) if len(insts) >= 2 else ""
            text = caption.get(t) or text
            drawn = staged(pose.get(t, state), state, now - since.get(t, now), skin["FRAMES"])
            if t == "":
                shown[(2, 4)] = (3, ti, drawn, said or text, "")
            else:
                if k >= len(cells):  # ponytail: 하위 종류 12개까지만 표시
                    continue
                shown[cells[k]] = (2, ti, drawn, said or text, agent_label(t, 9))
                k += 1
        for r in range(3):
            for i in range(5):
                slot = slots[r][i]
                if (r, i) in shown:
                    show(slot, *shown[(r, i)])
                else:
                    slot[0].configure(image="")
                    slot[1].configure(text="", bg=KEY)
                    slot[2].configure(text="", bg=KEY)
        cur["n"] += 1
        root.after(200, tick)

    tick()
    root.mainloop()


def test():
    import importlib
    here = os.path.dirname(os.path.abspath(__file__))
    for skin_name, mod_name in SKINS.items():  # 있는 캐릭터마다 기본 5상태와 32x32 프레임을 갖췄는지
        if not os.path.exists(os.path.join(here, mod_name + ".py")):
            continue
        mod = importlib.import_module(mod_name)
        assert all(s in mod.FRAMES for s in ("idle", "work", "wait", "done", "fail")), skin_name
        assert len(mod.PALETTE) <= 9, skin_name
        for key, pair in mod.FRAMES.items():
            assert len(pair) == 2 and all(len(rows) == 32 and all(len(r) == 32 and set(r) <= set(mod.PALETTE) | {"."}
                                                                   for r in rows) for rows in pair), (skin_name, key)
    assert saved_skin() in SKINS
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
    keys = ["idle", "idle_d", "idle_d~2", "idle_d~3", "wait", "wait~2"]
    assert variants("idle", keys) == ["idle", "idle_d"]  # 단계 그림은 처음부터 뽑히지 않는다
    for pose, state, sec, want in [("idle_d", "idle", 0, "idle_d"), ("idle_d", "idle", 60, "idle_d~2"),
                                   ("idle_d", "idle", 200, "idle_d~3"), ("idle", "idle", 999, "idle"),
                                   ("wait", "wait", 29, "wait"), ("wait", "wait", 31, "wait~2"),
                                   ("wait", "wait", 999, "wait~2"), ("work", "work", 999, "work")]:
        assert staged(pose, state, sec, keys) == want, (pose, sec)
    assert all(k.split("~")[0] in FRAMES for k in FRAMES), list(FRAMES)  # 단계 그림마다 1단계 포즈가 있다
    for name, want in [("Explore", "Explore"), ("task-worker", "task-\nworker"), ("default-worker", "default-\nworker"),
                       ("caveman:cavecrew-builder", "cavecrew-\nbuilder"), ("general-purpose", "general-\npurpose"),
                       ("verylongagentname", "verylonga\ngentname"), ("a-verylongagentname", "a-\nverylong…"), ("", "")]:
        assert agent_label(name, 9) == want, name
    assert all(k.split("_")[0].split("~")[0] in ("idle", "work", "wait", "done", "fail") for k in FRAMES), list(FRAMES)
    assert all(s in FRAMES for s in ("idle", "work", "wait", "done", "fail"))
    assert all(k in FRAMES and v and all(0 < len(s) <= 5 for s in v) for k, v in CAPTIONS.items()), CAPTIONS
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
