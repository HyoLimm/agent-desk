PALETTE = {
    "k": "#101418",  # 외곽선·눈·입·모니터 테두리
    "d": "#2a323c",  # 모니터 화면 바탕·책상 앞판
    "o": "#e0a050",  # 햄스터 털
    "c": "#f8e8c8",  # 크림색 배·볼·주둥이·앞발
    "t": "#30e060",  # 강조색(넥타이·책상 선·모니터 선·코드 줄)
    "w": "#ffffff",  # 흰자·컵·땀·Z
    "y": "#ffd040",  # 금색
    "r": "#ff3040",  # 빨강
    "g": "#6a7480",  # 회색
}


def blank():
    return [["."] * 32 for _ in range(32)]


def rect(c, x, y, w, h, ch):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 <= xx < 32 and 0 <= yy < 32:
                c[yy][xx] = ch


def stamp(c, x, y, rows):
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch != "." and 0 <= x + dx < 32 and 0 <= y + dy < 32:
                c[y + dy][x + dx] = ch


def text(c):
    return ["".join(r) for r in c]


def put(c, x, y, ch):
    if 0 <= x < 32 and 0 <= y < 32:
        c[y][x] = ch


def line(c, x0, y0, x1, y1, ch):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        put(c, round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), ch)


def arm(c, sx, sy, hx, hy):
    """짧은 팔: 어깨(sx,sy)에서 손(hx,hy)까지 k 선, 끝에 c 2x2 앞발."""
    line(c, sx, sy, hx, hy, "k")
    rect(c, hx - 1, hy - 1, 4, 4, "k")
    rect(c, hx, hy, 2, 2, "c")


# ---------------------------------------------------------------- 햄스터 몸
def outline_fill(c, mask, fill="o"):
    out = {(x, y) for (x, y) in mask
           if any(n not in mask for n in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))}
    for (x, y) in mask:
        put(c, x, y, "k" if (x, y) in out else fill)
    return out


def hamster(c, puff=False, spiky=False):
    """둥글고 통통한 몸(열 2~15, 행 8~24) + 귀 + 크림 볼/주둥이/배."""
    mask = set()
    for y in range(8, 25):
        dy = (y - 17) / 10
        hw = 7 * (1 - abs(dy) ** 2.5) ** 0.4
        lo, hi = round(8.5 - hw), int(8.5 + hw)
        if puff and 13 <= y <= 19:
            lo, hi = lo - 1, hi + 1                  # 볼주머니가 양옆으로 빵빵
        for x in range(lo, hi + 1):
            mask.add((x, y))
    out = outline_fill(c, mask)
    reach = 6 if puff else 5
    for (x, y) in mask - out:
        w = abs(x - 8.5)
        if 14 <= y <= 19 and w <= reach and (y not in (14, 19) or w <= reach - 1.5):
            put(c, x, y, "c")                        # 볼·주둥이
        elif y >= 19 and ((x - 8.5) / 3.5) ** 2 + ((y - 22) / 3.5) ** 2 <= 1:
            put(c, x, y, "c")                        # 배
    if spiky:
        for (x, y) in out:
            if y < 24 and (x * 3 + y * 5) % 4 == 0:
                for n in ((x - 1, y), (x + 1, y), (x, y - 1)):
                    if n not in mask:
                        put(c, n[0], n[1], "k")
    for ex in (3, 12):
        stamp(c, ex, 7, ["kkk", "kck", "kkk"])       # 둥근 귀


def tie(c):
    stamp(c, 8, 19, ["tt", "tt"])
    stamp(c, 7, 21, ["tttt", "tttt"])


def eyes(c, kind="normal"):
    for ex in (4, 11):
        if kind == "normal":
            stamp(c, ex + 1, 12, ["kk", "kk"])
            put(c, ex + 1, 12, "w")
        elif kind == "big":                          # 하이라이트 2칸
            stamp(c, ex, 11, ["kwk", "kkk", "kkw"])
        elif kind == "happy":
            stamp(c, ex, 12, [".kk.", "k..k"])
        elif kind == "shock":
            stamp(c, ex, 11, ["www", "wkw", "www"])


def nose_mouth(c):
    put(c, 8, 15, "r")
    stamp(c, 6, 16, ["k.kk.k", ".k..k."])            # ω 입


def sweat(c, f):
    put(c, 8 + f, 9, "w")
    put(c, 8 + f, 10, "w")


# ---------------------------------------------------------------- 장면
def scene(c):
    rect(c, 0, 25, 32, 1, "t")                 # 책상
    rect(c, 0, 26, 32, 2, "g")
    rect(c, 0, 28, 32, 4, "d")
    rect(c, 0, 28, 1, 4, "k")
    rect(c, 31, 28, 1, 4, "k")
    rect(c, 0, 31, 32, 1, "k")
    rect(c, 17, 7, 14, 15, "t")                # 모니터
    rect(c, 18, 8, 12, 13, "k")
    rect(c, 19, 9, 10, 9, "d")
    rect(c, 23, 22, 2, 2, "k")
    rect(c, 21, 24, 6, 1, "g")
    rect(c, 4, 23, 10, 2, "d")                 # 키보드
    for x in (5, 7, 9, 11):
        c[23][x] = "g"
    for x in (6, 8, 10, 12):
        c[24][x] = "g"
    rect(c, 14, 21, 3, 4, "w")                 # 머그컵
    rect(c, 17, 22, 1, 2, "w")


def screen(c, ch):
    rect(c, 19, 9, 10, 9, ch)


LINES = [(0, 6), (2, 4), (2, 7), (0, 3), (3, 5), (1, 8)]
BIGQ = [".yyyy.", "yy..yy", "....yy", "...yy.", "..yy..", "......", "..yy.."]
SPARK = [".y.", "yyy", ".y."]
SEED = [".kkk.", "kwdwk", "kwdwk", "kwdwk", ".kwk.", "..k.."]
SEED_S = ["kwk", "kdk", ".k."]


def base(c, **kw):
    hamster(c, **kw)
    tie(c)
    scene(c)


# ---------------------------------------------------------------- 상태
def idle(f):
    c = blank()
    scene(c)
    tmp = blank()
    hamster(tmp)
    for y in range(32):                          # 몸을 3칸 내려 책상에 턱을 괸다
        for x in range(32):
            if tmp[y][x] != "." and 0 <= y + 3 <= 24:
                c[y + 3][x] = tmp[y][x]
    rect(c, 2, 10, 4, 2, ".")                    # 원래 귀 자리 지우고 축 처진 귀
    rect(c, 11, 10, 4, 2, ".")
    stamp(c, 2, 11, ["kkk", "kck", ".kk"])
    stamp(c, 13, 11, ["kkk", "kck", "kk."])
    for ex in (4, 11):
        rect(c, ex, 15, 3, 2, "o")
        stamp(c, ex, 15, ["k.k", "kkk"])         # 감은 눈
    stamp(c, 7, 20, ["kk"])                      # 벌어진 입
    put(c, 6, 21, "w")                           # 침
    put(c, 6, 22, "w")
    stamp(c, 2, 23, ["kkkk", "kcck"])            # 책상 위 앞발
    stamp(c, 12, 23, ["kkkk", "kcck"])
    if f == 0:
        stamp(c, 9, 18, ["kkkk", "kwwk", "kwwk", "kkkk"])
        stamp(c, 11, 6, ["www", ".w.", "www"])
        put(c, 22, 12, "t")
    else:
        stamp(c, 9, 17, ["kkkkkk", "kwwwwk", "kwwwwk", "kwwwwk", "kwwwwk", "kkkkkk"])
        stamp(c, 10, 0, ["wwwww", "...w.", "..w..", ".w...", "wwwww"])
        stamp(c, 6, 5, ["www", ".w.", "www"])
        put(c, 26, 15, "t")
    return c


def work(f):
    c = blank()
    base(c, puff=True)
    eyes(c)
    nose_mouth(c)
    sweat(c, f)
    for i in range(5):
        ind, ln = LINES[i + f]
        rect(c, 19 + ind, 9 + 2 * i, ln, 1, "t")
    lh, rh = ((5, 21), (11, 22)) if f == 0 else ((5, 22), (11, 21))
    arm(c, 3, 19, *lh)
    arm(c, 15, 19, *rh)
    return c


def wait(f):
    c = blank()
    base(c)
    eyes(c, "big")
    nose_mouth(c)
    stamp(c, 6, 19 - f, SEED)
    arm(c, 3, 19, 4, 22 - f)
    arm(c, 15, 19, 11, 22 - f)
    stamp(c, 21, 10, BIGQ)
    if f == 1:
        rect(c, 27, 16, 1, 2, "w")
    return c


def done(f):
    c = blank()
    base(c, puff=True)
    eyes(c, "happy")
    nose_mouth(c)
    arm(c, 3, 17, 0, 6)
    arm(c, 15, 17, 16, 5)
    for dx in (0, 1):
        line(c, 20 + dx, 13, 22 + dx, 16, "y")
        line(c, 22 + dx, 16, 27 + dx, 10, "y")
    spark = [[(8, 2), (30, 3), (20, 1), (30, 22)], [(9, 5), (29, 2), (22, 3), (30, 23)]][f]
    for x, y in spark:
        stamp(c, x - 1, y, SPARK)
    return c


def fail(f):
    c = blank()
    base(c, puff=True, spiky=True)
    eyes(c, "shock")
    put(c, 8, 15, "r")
    stamp(c, 7, 16, ["kkk", "kdk", "kkk"])       # 벌어진 입
    screen(c, "r")
    stamp(c, 20, 10, ["w.....w", ".w...w.", "..w.w..", "...w...", "..w.w..", ".w...w.", "w.....w"])
    arm(c, 3, 19, 1, 22)
    arm(c, 15, 19, 16, 22)
    if f == 0:
        stamp(c, 9, 0, [".g.g", "g.g.", ".gg."])
        stamp(c, 5, 1, ["g.", ".g"])
        seeds = [(0, 10), (14, 3), (0, 3)]
    else:
        stamp(c, 8, 0, ["g.g.", ".g.g", "gg.."])
        stamp(c, 4, 2, [".g", "g."])
        seeds = [(0, 7), (15, 1), (0, 1)]
    for x, y in seeds:
        stamp(c, x, y, SEED_S)
    return c


def _build():
    return {name: [text(fn(f)) for f in (0, 1)]
            for name, fn in (("idle", idle), ("work", work), ("wait", wait),
                             ("done", done), ("fail", fail))}


FRAMES = _build()

if __name__ == "__main__":
    assert list(FRAMES) == ["idle", "work", "wait", "done", "fail"]
    ok_chars = set(PALETTE) | {"."}
    for name, fr in FRAMES.items():
        assert len(fr) == 2, name
        for rows in fr:
            assert len(rows) == 32, name
            for r in rows:
                assert len(r) == 32 and set(r) <= ok_chars, (name, r)
    print("ok")
