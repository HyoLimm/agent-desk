PALETTE = {
    "k": "#101418",  # 외곽선·눈동자·모니터 테두리
    "d": "#2a323c",  # 모니터 화면 바탕·책상 앞판
    "p": "#d9a55b",  # 감자 몸
    "b": "#a8743a",  # 감자 그림자·반점·눈썹
    "t": "#30e060",  # 강조색(넥타이·새싹·책상 선·모니터 선·코드 줄)
    "w": "#ffffff",  # 흰자·컵·종이·땀·Z
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


def arm(c, sx, sy, hx, hy, trail=()):
    """막대 팔: 어깨(sx,sy)에서 손(hx,hy)까지 k 선, 끝에 p 2x2 손. trail=잔상 b 선의 손 위치들."""
    for tx, ty in trail:
        line(c, sx, sy, tx, ty, "b")
    line(c, sx, sy, hx, hy, "k")
    rect(c, hx - 1, hy - 1, 4, 4, "k")          # 몸 위에서도 보이게 손 테두리
    rect(c, hx, hy, 2, 2, "p")


# ---------------------------------------------------------------- 감자 몸
def potato(c, ox=0, oy=0, lean=0, burnt=False):
    """감자 몸통. 반환 pos(x,y): 기본형 좌표 -> 실제 좌표(눈·입 등 얼굴 조각용)."""
    def fx(y):
        return ox + round(lean * (24 - y) / 17)

    def pos(x, y):
        return x + fx(y), y + oy

    mask = set()
    for y in range(7, 25):
        dy = (y - 18) / 11.5
        hw = 7 * max(0.0, 1 - dy * dy) ** 0.5
        lo, hi = round(8.5 - hw - 0.25 + 0.01), int(8.5 + hw + 0.25)
        if 10 <= y <= 13:
            hi += 1                      # 오른쪽 혹
        if 19 <= y <= 21:
            lo += 1                      # 왼쪽 움푹
        for x in range(lo, hi + 1):
            mask.add((x, y))
    out = {(x, y) for (x, y) in mask
           if any(n not in mask for n in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))}
    for (x, y) in mask:
        if (x, y) in out:
            ch = "k"
        elif x > 8 and y > 13 and ((x + 1, y) in out or (x, y + 1) in out):
            ch = "b"                      # 오른쪽 아래 그림자
        else:
            ch = "p"
        if burnt and ch != "k":
            v = (x * 3 + y * 5) % 7
            ch = "k" if v < 2 else ("b" if v < 6 else "p")
        px, py = pos(x, y)
        put(c, px, py, ch)
    if not burnt:
        for x, y in ((11, 9), (4, 18), (5, 18), (13, 19)):   # 반점
            put(c, *pos(x, y), "b")
    return pos


def spr(c, pos, x, y, rows):
    """얼굴 조각: 행마다 감자 기울기를 따라 찍는다."""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch != ".":
                put(c, *pos(x + dx, y + dy), ch)


def sprout(c, pos, mode):
    if mode == "droop":
        spr(c, pos, 8, 5, ["tt", ".t", ".t"])
        spr(c, pos, 7, 5, ["t"])
    elif mode == "burnt":
        spr(c, pos, 8, 4, [".kk", "k..", "k.."])


def sprout_up(c, pos):
    spr(c, pos, 6, 3, ["tt.tt"])
    spr(c, pos, 7, 4, ["ttt"])
    spr(c, pos, 8, 5, ["t", "t"])


def eyes_normal(c, pos, px=(6, 11), py=14):
    for wx in (5, 10):
        spr(c, pos, wx, 13, ["www"] * 3)
    for x in px:
        spr(c, pos, x, py, ["kk", "kk"])


def tie(c, pos):
    spr(c, pos, 8, 20, ["tt"])
    spr(c, pos, 8, 21, ["tt"])
    spr(c, pos, 7, 22, ["tttt"])
    spr(c, pos, 7, 23, ["tttt"])


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


# ---------------------------------------------------------------- 상태
def idle(f):
    c = blank()
    pos = potato(c, ox=1, oy=2, lean=-4)
    tie(c, pos)
    scene(c)
    spr(c, pos, 5, 14, ["k.k", ".k."])         # 감은 눈
    spr(c, pos, 10, 14, ["k.k", ".k."])
    spr(c, pos, 5, 12, ["bbb"])                # 풀린 눈썹
    spr(c, pos, 10, 12, ["bbb"])
    spr(c, pos, 8, 17, ["kk"])
    sprout(c, pos, "droop")
    bx, by = pos(10, 16)
    if f == 0:
        rect(c, bx, by - 1, 2, 2, "w")
        stamp(c, 12, 8, ["ww.", ".w.", ".ww"])
        c[12][22] = "t"
    else:
        stamp(c, bx, by - 2, [".ww.", "wwww", "wwww", ".ww."])
        stamp(c, 11, 2, ["wwwww", "...w.", "..w..", ".w...", "wwwww"])
        c[15][26] = "t"
    sx, sy = pos(3, 19)
    arm(c, sx, sy, 0, 22)
    sx, sy = pos(15, 18)
    arm(c, sx, sy, 11, 21)
    return c


def work(f):
    c = blank()
    pos = potato(c)
    tie(c, pos)
    scene(c)
    eyes_normal(c, pos, px=(6, 11), py=14)
    spr(c, pos, 4, 11, ["bb"])                 # 화난 눈썹
    spr(c, pos, 6, 12, ["bb"])
    spr(c, pos, 12, 11, ["bb"])
    spr(c, pos, 10, 12, ["bb"])
    spr(c, pos, 7, 17, ["kkkk"])
    sprout_up(c, pos)
    for i in range(5):
        ind, ln = LINES[i + f]
        rect(c, 19 + ind, 9 + 2 * i, ln, 1, "t")
    for x, y in ([(1, 8), (16, 9), (12, 2)], [(0, 6), (16, 12), (13, 1)])[f]:
        put(c, x, y, "w")
        put(c, x, y + 1, "w")
    if f == 0:
        arm(c, 3, 19, 4, 21, trail=[(2, 17), (3, 14)])
        arm(c, 15, 19, 12, 14, trail=[(14, 16), (13, 12)])
        stamp(c, 3, 18, [".r.r", "y.y.", ".y"])
        stamp(c, 8, 19, [".y", "ry", ".r"])
    else:
        arm(c, 3, 19, 4, 14, trail=[(4, 17), (4, 20)])
        arm(c, 15, 19, 11, 21, trail=[(13, 17), (12, 19)])
        stamp(c, 11, 18, ["r.y", ".yr", "y.."])
        stamp(c, 6, 19, ["y.r", ".r."])
    return c


def wait(f, lv=1):
    """lv2: 울면서 매달림(눈물, 큰 울음, 높이 흔드는 종이, 모니터 쪽으로 뻗은 손)."""
    c = blank()
    pos = potato(c)
    tie(c, pos)
    scene(c)
    for ex in (4, 10):                          # 촉촉한 큰 눈 4x4
        if lv == 1:
            spr(c, pos, ex, 13, ["kkkk", "kwkk", "kkkk", "kkwk"])
        else:                                   # 큰 흰자에 동공
            spr(c, pos, ex, 13, ["wwww", "wkkw", "wkkw", "wwww"])
    spr(c, pos, 4, 12, ["bb"])                 # 팔자 눈썹
    spr(c, pos, 6, 11, ["bb"])
    spr(c, pos, 12, 12, ["bb"])
    spr(c, pos, 10, 11, ["bb"])
    if lv == 1:
        spr(c, pos, 8, 18, ["kk"])
        spr(c, pos, 7, 19, ["k..k"])
    else:                                       # 크게 벌린 울음
        spr(c, pos, 7, 17, [".kkk.", "kdddk", "kdddk", ".kkk."])
    sprout_up(c, pos)
    # 서류: 외곽선 포함 7x8, 가슴 높이(눈 아래)에서 프레임 1에 1칸 위로 들썩
    py = 19 - f * lv
    rect(c, 0, py, 7, 8, "k")
    rect(c, 1, py + 1, 5, 6, "w")
    rect(c, 2, py + 2, 3, 1, "k")
    rect(c, 2, py + 4, 3, 1, "k")
    rect(c, 4, py + 5, 2, 2, "r")
    arm(c, 3, 22, 6, py + 5)
    if lv == 1:
        arm(c, 15, 19, 12, 21)
    else:
        arm(c, 15, 19, 18, 19)                  # 모니터 쪽으로 뻗어 매달림
    stamp(c, 21, 10, [".yyyy.", "yy..yy", "....yy", "...yy.", "..yy..", "......", "..yy.."])
    if f == 0:
        rect(c, 27, 16, 1, 2, "w")
    if lv == 2:
        for x in (4, 13):                       # 눈물 줄기
            for y in range(17, 25):
                if (y + f + (x == 13)) % 4:
                    put(c, x, y, "t")
        for x, y in ((1, 1 + f), (13, 2 - f)):   # 머리 위 느낌표 2개
            stamp(c, x, y, ["yy", "yy", "yy", "..", "yy"])
    return c


def done(f):
    c = blank()
    oy = -f
    pos = potato(c, oy=oy)
    tie(c, pos)
    scene(c)
    spr(c, pos, 3, 13, ["kkkkkkkkkkkk"])        # 선글라스 띠
    spr(c, pos, 4, 13, ["kkkk", "kwkk", ".kk."])
    spr(c, pos, 10, 13, ["kkkk", "kwkk", ".kk."])
    spr(c, pos, 6, 17, ["kkkkkk"])              # 크게 웃는 입
    spr(c, pos, 6, 18, ["kwwwwk"])
    spr(c, pos, 7, 19, ["kkkk"])
    sprout_up(c, pos)
    arm(c, 3, 17 + oy, 0, 6 + oy)
    arm(c, 15, 17 + oy, 16, 5 + oy)
    stamp(c, 20, 11, ["......yy", ".....yy.", "y...yy..", "yy.yy...", ".yyy....", "..y....."])
    spark = [[(2, 4), (30, 3), (15, 1), (30, 22)], [(15, 6), (31, 5), (4, 1), (29, 21)]][f]
    for x, y in spark:
        stamp(c, x - 1, y, [".y.", "yyy", ".y."])
    return c


def fail(f):
    c = blank()
    pos = potato(c, burnt=True)
    tie(c, pos)
    scene(c)
    for ex in (4, 10):                          # 흰자만 남은 놀란 눈
        spr(c, pos, ex, 12, ["wwww"] * 4)
    spr(c, pos, 6, 14, ["k"])
    spr(c, pos, 11, 14, ["k"])
    spr(c, pos, 8, 17, ["kk"])
    spr(c, pos, 7, 18, ["kkkk"])
    spr(c, pos, 7, 19, ["kkkk"])
    sprout(c, pos, "burnt")
    screen(c, "r")
    stamp(c, 20, 10, ["w.....w", ".w...w.", "..w.w..", "...w...", "..w.w..", ".w...w.", "w.....w"])
    arm(c, 3, 19, 1, 22)
    arm(c, 15, 19, 16, 22)
    if f == 0:
        stamp(c, 9, 0, [".g.g", "g.g.", ".gg."])
        stamp(c, 3, 0, ["g.", ".g"])
        stamp(c, 20, 3, ["r..r..", "ryrrry", "yyyyyr"])
        em = [(1, 16), (16, 12), (15, 22), (2, 10)]
    else:
        stamp(c, 8, 0, ["g.g.", ".g.g", "gg.."])
        stamp(c, 4, 1, [".g", "g."])
        stamp(c, 21, 3, [".r.r.", "ryyry", "yyyyr"])
        em = [(1, 12), (16, 16), (15, 20), (2, 15)]
    for x, y in em:
        put(c, x, y, "r")
    return c


def zzz_screen(c, lines):
    z = ["ww.", ".w.", ".ww"]
    ys = (10, 14) if lines == 2 else (9, 12, 15)
    for i, y in enumerate(ys):
        for x in (19 + i % 2, 23 + i % 2, 27 + i % 2):
            if x + 3 <= 29:
                stamp(c, x, y, z)


def idle_c(f):
    c = blank()
    scene(c)
    t = blank()
    pos = potato(t, ox=-1, oy=6, lean=5)
    sprout(t, pos, "droop")
    for y in range(25):                          # 몸은 책상 앞판 위로 나오지 않게
        for x in range(32):
            if t[y][x] != ".":
                c[y][x] = t[y][x]
    stamp(c, 11, 11, ["ttt", "..t"])             # 앞으로 꺾인 새싹
    zzz_screen(c, 2 if f == 0 else 3)
    arm(c, 4, 22, 0, 24)
    arm(c, 14, 22, 19, 24)
    if f == 0:
        stamp(c, 11, 4, ["ww.", ".w.", ".ww"])
    else:
        stamp(c, 10, 2, ["ww.", ".w.", ".ww"])
        stamp(c, 14, 6, ["ww", ".w"])
    return c


def bigcheck(c):
    for dx in (0, 1):
        line(c, 20 + dx, 13, 22 + dx, 16, "y")
        line(c, 22 + dx, 16, 27 + dx, 10, "y")


def done_b(f):
    c = blank()
    pos = potato(c, oy=1)
    tie(c, pos)
    scene(c)
    for ex in (4, 10):                          # 감격한 반짝 눈
        spr(c, pos, ex, 13, ["kwwk", "wyyw", "wyyw", "kwwk"])
    spr(c, pos, 6, 17, ["kkkkkk"])
    spr(c, pos, 6, 18, ["kwwwwk"])
    spr(c, pos, 7, 19, ["kkkk"])
    ty = 1 - f
    hy = ty + 4
    arm(c, 3, 19, 4, hy)
    arm(c, 15, 19, 9, hy)
    stamp(c, 4, ty, [".yyyyy.", "yyyyyyy", "y.yyy.y", "..yyy..", "...y...", "..yyy..", ".yyyyy."])
    bigcheck(c)
    spark = [[(1, 2), (14, 3), (29, 3)], [(2, 6), (15, 1), (30, 5)]][f]
    for x, y in spark:
        stamp(c, x - 1, y, [".y.", "yyy", ".y."])
    return c


def done_c(f):
    c = blank()
    pos = potato(c, oy=1)
    tie(c, pos)
    scene(c)
    spr(c, pos, 5, 11, ["bbb"])
    spr(c, pos, 10, 11, ["bbb"])
    eyes_normal(c, pos, px=(6, 11), py=14)
    spr(c, pos, 7, 16, [".kk.", "kkkk", "kkkk", ".kk."])   # "와" 입
    stamp(c, 4, 1, ["...yy...", "...yy...", "...rr...", "..rrrr..", "..wwww..", ".rrrrrr.", "rrrrrrrr"])
    bigcheck(c)
    arm(c, 3, 19, 1, 22)
    arm(c, 15, 18, 13, 11)
    rect(c, 13, 6, 2, 5, "g")                   # 폭죽
    cells = [
        [(13, 4, "y"), (12, 3, "r"), (15, 3, "t"), (14, 1, "y"), (16, 2, "r"), (18, 3, "y"),
         (13, 0, "t"), (17, 0, "w"), (20, 2, "t"), (19, 5, "r"), (11, 1, "w")],
        [(11, 3, "r"), (15, 4, "y"), (19, 3, "r"), (22, 2, "t"), (25, 4, "y"), (27, 7, "w"),
         (23, 9, "r"), (29, 6, "t"), (17, 1, "w"), (21, 6, "y"), (14, 0, "t")],
    ][f]
    for x, y, ch in cells:
        put(c, x, y, ch)
    return c


def work_b(f):
    c = blank()
    pos = potato(c)
    tie(c, pos)
    scene(c)
    for ex in (5, 10):                          # 흰자 3x3 + 동공
        spr(c, pos, ex, 13, ["www"] * 3)
    spr(c, pos, 6, 14, ["kk"])
    spr(c, pos, 10, 14, ["kk"])
    spr(c, pos, 4, 11, ["kk"])                  # V자 굵은 눈썹(안쪽이 아래)
    spr(c, pos, 6, 12, ["kk"])
    spr(c, pos, 12, 11, ["kk"])
    spr(c, pos, 10, 12, ["kk"])
    spr(c, pos, 6, 17, ["kkkkkk"])              # 이를 악문 입
    spr(c, pos, 6, 18, ["kwwwwk"])
    spr(c, pos, 7, 19, ["kkkk"])
    mx = 9 + f                                  # 이마 화남 표시
    spr(c, pos, mx, 8, [".r.", "r.r", ".r."])
    if f == 1:
        spr(c, pos, mx + 1, 7, ["r"])
    spr(c, pos, 6, 3, ["kk.kk"])                # 그을린 새싹
    spr(c, pos, 7, 4, ["kkk"])
    spr(c, pos, 8, 5, ["k", "k"])
    for i in range(5):                          # 코드 줄, 위로 한 줄 밀림
        ind, ln = LINES[(i + f + 1) % 6]
        rect(c, 19 + ind, 9 + 2 * i, ln, 1, "t")
    tall = [".r.", ".r.", "rr.", "rrr", "ryr", "ryr"]
    mid = [".r.", ".rr", "rrr", "ryr", "ryr"]
    low = [".r.", "rrr", "ryr"]
    if f == 0:
        flames = [(2, 2, tall), (4, 5, low), (12, 3, tall), (14, 6, low),
                  (-1, 10, mid), (-1, 16, mid), (16, 10, mid), (16, 16, mid)]
        steam = []
    else:
        flames = [(2, 3, mid), (4, 4, tall), (12, 4, mid), (13, 1, tall),
                  (-1, 11, tall), (-1, 17, mid), (16, 11, tall), (16, 17, mid)]
        steam = [(8, 1), (9, 0)]
    for x, y, rows in flames:
        stamp(c, x, y, rows)
    for x, y in steam:
        put(c, x, y, "g")
    if f == 0:
        arm(c, 3, 19, 5, 20, trail=[(4, 17)])
        arm(c, 15, 19, 11, 22, trail=[(13, 20)])
        stamp(c, 13, 21, ["w", ".w"])
        stamp(c, 8, 20, ["g"])
        stamp(c, 12, 19, ["g"])
        stamp(c, 14, 20, ["g"])
    else:
        arm(c, 3, 19, 5, 22, trail=[(4, 20)])
        arm(c, 15, 19, 11, 20, trail=[(13, 17)])
        stamp(c, 3, 21, ["w"])
        stamp(c, 7, 21, [".w", "w."])
        stamp(c, 7, 19, ["g"])
        stamp(c, 13, 19, ["g"])
        stamp(c, 3, 20, ["g"])
    return c


def work_c(f):
    c = blank()
    pos = potato(c, oy=1)                       # 평소보다 1칸 처져 앉음
    tie(c, pos)
    scene(c)
    for i in range(5):
        ind, ln = LINES[i + f]
        rect(c, 19 + ind, 9 + 2 * i, ln, 1, "t")
    lid = (["ppp", "kkk", "wkw"], ["ppp", "ppp", "kkk"])[f]   # 반쯤 감긴 눈 -> 거의 감김
    for ex in (5, 10):
        spr(c, pos, ex, 12, lid)
        spr(c, pos, ex, 15, ["bbb", "bbb"])     # 다크서클
    spr(c, pos, 4, 11, ["k"])                   # 팔자 눈썹(바깥쪽이 아래)
    spr(c, pos, 5, 10, ["kk"])
    spr(c, pos, 10, 10, ["kk"])
    spr(c, pos, 12, 11, ["k"])
    spr(c, pos, 6, 18, [".kk.", "k..k"])        # 처진 입
    spr(c, pos, 13, 12 + f, ["w"])              # 땀방울
    sprout(c, pos, "droop")
    if f == 1:
        spr(c, pos, 11, 18, ["gg", ".g"])       # 한숨 구름
        spr(c, pos, 13, 17, ["g"])
    arm(c, 3, 20, 5, 22)
    if f == 0:
        arm(c, 15, 20, 11, 21)
    else:
        arm(c, 15, 20, 11, 22)
    return c


def _work_base(c, ox=0, lean=0):
    pos = potato(c, ox=ox, lean=lean)
    tie(c, pos)
    scene(c)
    return pos


def _codelines(c, f):
    for i in range(5):
        ind, ln = LINES[i + f]
        rect(c, 19 + ind, 9 + 2 * i, ln, 1, "t")


def _typing(c, pos, f, trail=False):
    """키보드 위에서 번갈아 치는 두 손."""
    lh, rh = ((5, 21), (11, 22)) if f == 0 else ((5, 22), (11, 21))
    lt = [pos(4, 22 - 2 * (f == 0))] if trail else ()
    rt = [pos(12, 20 + 2 * (f == 0))] if trail else ()
    arm(c, *pos(3, 19), *pos(*lh), trail=lt)
    arm(c, *pos(15, 19), *pos(*rh), trail=rt)


NOTE = ["..yy", "..y.", "..y.", "yyy.", "yy.."]


def _note(c, x, y, ch):
    stamp(c, x, y, [r.replace("y", ch) for r in NOTE])


def work_d(f):
    """콧노래: 감은 ^ 눈 + 활짝 웃는 입 + 떠다니는 음표."""
    c = blank()
    pos = _work_base(c, lean=(1, -1)[f])
    _codelines(c, f)
    spr(c, pos, 5, 14, [".k.", "k.k"])
    spr(c, pos, 10, 14, [".k.", "k.k"])
    spr(c, pos, 6, 17, ["kkkkkk"])
    spr(c, pos, 6, 18, ["kwwwwk"])
    spr(c, pos, 7, 19, ["kkkk"])
    sprout_up(c, pos)
    for x, y, ch in ([(0, 3, "w"), (12, 2, "y"), (21, 1, "w")],
                     [(1, 1, "y"), (13, 0, "w"), (22, 0, "y")])[f]:
        _note(c, x, y, ch)
    _typing(c, pos, f)
    return c


GHOST = ["..www..", ".wwwww.", "wwkwkww", "wwwwwww", "wwwwwww", "w.www.w"]


def work_e(f):
    """영혼 가출: 멍한 눈·입, 머리 위로 빠져나가는 흰 유령."""
    c = blank()
    pos = _work_base(c)
    _codelines(c, f)
    for ex in (4, 10):
        spr(c, pos, ex, 13, ["kkkk", "kwwk", "kwwk", "kkkk"])
    spr(c, pos, 7, 17, [".k.", "kkk", "kkk", ".k."])
    if f == 0:
        stamp(c, 5, 1, GHOST)
        stamp(c, 8, 7, ["ww"])
    else:
        stamp(c, 6, 0, GHOST)
        stamp(c, 9, 6, ["w"])
        stamp(c, 8, 7, ["ww"])
    _typing(c, pos, f)
    return c


def work_f(f):
    """안경 집중: 동그란 안경, 렌즈 반사, 꾹 다문 입."""
    c = blank()
    pos = _work_base(c, lean=1)
    _codelines(c, f)
    lens = [".kkk.", "kwwwk", "kwwwk", "kwwwk", ".kkk."]
    spr(c, pos, 4, 13, lens)
    spr(c, pos, 10, 13, lens)
    spr(c, pos, 9, 15, ["k"])
    spr(c, pos, 7, 16, ["k"])
    spr(c, pos, 13, 16, ["k"])
    refl = ([(5, 14), (6, 15), (11, 14), (12, 15)], [(7, 14), (6, 15), (13, 14), (12, 15)])[f]
    for x, y in refl:
        spr(c, pos, x, y, ["t"])
    spr(c, pos, 7, 18, ["kkkk"])
    sprout_up(c, pos)
    if f == 0:
        _typing(c, pos, f)
    else:
        arm(c, *pos(3, 19), *pos(5, 22))
        arm(c, 15, 19, 16, 14)
    return c


def work_g(f):
    """땀 범벅: 걱정 눈썹, 물결 입, 사방 땀방울, 책상 물웅덩이."""
    c = blank()
    pos = _work_base(c)
    _codelines(c, f)
    for ex in (5, 10):
        spr(c, pos, ex, 13, ["www"] * 3)
    spr(c, pos, 6, 14, ["k"])
    spr(c, pos, 11, 14, ["k"])
    spr(c, pos, 4, 10, ["..kk", ".k..", "k..."])
    spr(c, pos, 10, 10, ["kk..", "..k.", "...k"])
    spr(c, pos, 6, 17, [".k.k.k.", "k.k.k.k"])
    sprout_up(c, pos)
    drops = ([(1, 3), (5, 0), (12, 1), (15, 4), (0, 10), (0, 15), (14, 17)],
             [(2, 5), (7, 0), (13, 3), (15, 0), (0, 8), (0, 13), (15, 18)])[f]
    for x, y in drops:
        stamp(c, x, y, [".w", "ww"])
    if f == 0:
        rect(c, 19, 25, 6, 1, "w")
        rect(c, 18, 26, 8, 1, "w")
        put(c, 20, 26, "t")
        put(c, 23, 26, "t")
        put(c, 21, 25, "t")
        arm(c, 3, 19, 4, 21, trail=[(4, 22)])
        arm(c, 15, 19, 12, 22, trail=[(12, 20)])
    else:
        rect(c, 18, 25, 8, 1, "w")
        rect(c, 17, 26, 10, 1, "w")
        put(c, 19, 26, "t")
        put(c, 23, 26, "t")
        put(c, 25, 26, "t")
        put(c, 21, 25, "t")
        arm(c, 3, 19, 6, 22, trail=[(5, 20)])
        arm(c, 15, 19, 10, 21, trail=[(11, 22)])
    return c


def work_h(f):
    """헤드폰: 큰 이어컵, 머리띠, 리듬 타며 좌우로 기울기."""
    c = blank()
    pos = _work_base(c, ox=(0, 2)[f])
    _codelines(c, f)
    pts = [(2, 10), (3, 8), (5, 6), (7, 5), (10, 5), (12, 6), (14, 8), (15, 10)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for dy in (0, 1):
            line(c, *pos(x0, y0 + dy), *pos(x1, y1 + dy), "k")
    sprout_up(c, pos)
    spr(c, pos, 5, 14, [".k.", "k.k"])
    spr(c, pos, 9, 14, [".k.", "k.k"])
    spr(c, pos, 7, 17, [".kk.", "k..k", ".kk."])
    cup = ["kkkk", "kttk", "kttk", "kttk", "kkkk"]
    spr(c, pos, 1, 10, cup)
    spr(c, pos, 12, 10, cup)
    for x, y in ([(22, 2), (0, 0)], [(24, 0), (0, 2)])[f]:
        _note(c, x, y, "y")
    _typing(c, pos, f)
    return c


def idle_b(f):
    """부재중: 감자 없는 빈 책상. 돌아간 빈 의자 + 세워 둔 안내 카드 + 걸린 넥타이."""
    c = blank()
    scene(c)
    rect(c, 3, 5, 10, 9, "k")                   # 의자 등받이
    rect(c, 4, 6, 8, 7, "g")
    rect(c, 5, 6, 6, 1, "w")                    # 쿠션 하이라이트
    for x, y in ((3, 5), (12, 5), (3, 13), (12, 13)):
        put(c, x, y, ".")                       # 모서리 깎기
    rect(c, 7, 14, 2, 9, "k")                   # 기둥
    rect(c, 5, 22, 6, 1, "k")                   # 받침
    rect(c, 0, 11, 3, 1, "k")                   # 팔걸이
    rect(c, 13, 11, 3, 1, "k")
    tx = 10 + f                                  # 걸린 넥타이: 끝이 흔들림
    rect(c, 9, 4, 3, 1, "t")
    rect(c, 10, 5, 1, 3, "t")
    rect(c, tx, 8, 1, 2, "t")
    put(c, tx + (1 if f == 0 else -1), 9, "t")
    for y, x0, x1 in ((19, 19, 27), (20, 19, 27), (21, 18, 28), (22, 18, 28), (23, 18, 28)):
        rect(c, x0, y, x1 - x0 + 1, 1, "k")     # 텐트 카드 앞면 (사다리꼴)
        if y not in (19, 23):
            rect(c, x0 + 1, y, x1 - x0 - 1, 1, "w")
    rect(c, 21, 21, 5, 1, "k")                  # 글씨 줄
    rect(c, 22, 22, 3, 1, "g")
    put(c, 28, 20, "g")                         # 옆면
    for x, y in ((29, 21), (29, 22), (30, 22), (29, 23)):
        put(c, x, y, "g")
    rect(c, 19, 24, 11, 1, "d")                 # 그림자
    put(c, *((22, 12), (26, 15))[f], "t")        # 화면 보호기 점
    rect(c, (27, 30)[f], 24, 2, 1, "w")          # 지나가는 먼지 뭉치
    return c


def _saver(c, f, spots):
    """어두운 화면 보호기: t 점 하나가 프레임마다 옮겨 다님."""
    put(c, *spots[f], "t")


FLY = ["w..w", ".kk."]
IDLE_D_FLIES = {
    2: ([(1, 2), (14, 5), (0, 8)], [(13, 2), (1, 5), (-1, 11)]),
    3: ([(0, 1), (1, 5), (-1, 9)], [(2, 1), (0, 6), (-1, 11)]),
}
IDLE_D_GHOST = (
    [".wwww.", "wwwwww", "wkwwkw", "wwwwww", "wwkkww", "wwwww.", "www...", "ww...."],
    [".wwww.", "wwwwww", "wkwwkw", "wwwwww", "wwkkww", ".wwwww", ".ww...", "ww...."],
)


def idle_d(f, lv=1):
    """멍때리기: 점 눈, 벌어진 입, 축 처진 팔, 머리 위를 빙빙 도는 파리.
    lv2: 큰 입+침+파리 3마리, lv3: 영혼이 빠져나가고 거미줄."""
    c = blank()
    pos = potato(c)
    tie(c, pos)
    scene(c)
    spr(c, pos, 6, 14, ["kk", "kk"])
    spr(c, pos, 11, 14, ["kk", "kk"])
    if lv == 1:
        spr(c, pos, 8, 17, [".k.", "k.k", ".k."])
    else:
        spr(c, pos, 6, 17, [".kkkk.", "kddddk", ".kkkk."])
    sprout_up(c, pos)
    _saver(c, f, [(21, 12), (26, 14)])
    arm(c, 3, 19, 1, 23)
    arm(c, 15, 19, 10, 23)
    if lv >= 2:
        for y in range(19, 23 if f else 25):         # 입가에서 책상 쪽으로 늘어진 침
            put(c, 6, y, "w")
        if f:
            put(c, 6, 24, "w")
    if lv == 1:
        flies = [(1, 2)] if f == 0 else [(13, 2)]
    else:
        flies = IDLE_D_FLIES[lv][f]
    for x, y in flies:
        stamp(c, x, y, FLY)
    for x, y in ((6, 1), (8, 0), (10, 1)):
        put(c, x, y, "g")
    if lv == 3:
        stamp(c, 11, 0, IDLE_D_GHOST[f])
        for x, y in ((4, 3), (5, 4), (6, 5), (7, 6), (5, 6), (6, 6), (4, 6), (5, 5)):   # 거미줄 한 조각
            put(c, x, y, "g")
    return c


COMBO_DIGIT = (["yyy", "..y", "yyy", "..y", "yyy"], ["y.y", "y.y", "yyy", "..y", "..y"])
FLAME_TALL = [".r.", ".r.", "rr.", "rrr", "ryr", "ryr"]
FLAME_MID = [".r.", ".rr", "rrr", "ryr", "ryr"]
FLAME_LOW = [".r.", "rrr", "ryr"]


def idle_e(f, lv=1):
    """게임하기: 모니터에 떨어지는 블록, 화면을 곁눈질하는 감자, 혀, 바쁜 손.
    lv2: 땀+콤보+더 높은 블록, lv3: 게임 오버 화면+불꽃."""
    c = blank()
    pos = potato(c)
    tie(c, pos)
    scene(c)
    for ex in (5, 10):
        spr(c, pos, ex, 13, ["www"] * 3)
        spr(c, pos, ex + 1, 14, ["kk"])
    if lv == 1:
        spr(c, pos, 5, 11, ["kkk"])
        spr(c, pos, 10, 11, ["kkk"])
    elif lv == 2:                                                  # 안쪽으로 기운 눈썹
        spr(c, pos, 5, 10, ["kk.", ".kk"])
        spr(c, pos, 10, 10, [".kk", "kk."])
    else:                                                          # 화난 V자 눈썹
        for bx, by in ((4, 11), (6, 12), (12, 11), (10, 12)):
            spr(c, pos, bx, by, ["kk"])
    if lv == 3:
        spr(c, pos, 6, 17, ["kkkkkk"])                             # 이를 악문 입
        spr(c, pos, 6, 18, ["kwwwwk"])
        spr(c, pos, 7, 19, ["kkkk"])
    else:
        spr(c, pos, 6, 17, ["kkkkkk"])
        spr(c, pos, 10, 18, ["rr"])
        spr(c, pos, 10, 19, ["rr"])
    if lv == 2:                                                    # 이마 땀방울
        for x, y in (((6, 8), (6, 9), (10, 8), (10, 9), (8, 9)),
                     ((7, 8), (7, 9), (9, 8), (9, 9)))[f]:
            put(c, x, y, "w")
    sprout_up(c, pos)
    if lv == 3:
        screen(c, "r")
        rect(c, 20, 10, 8, 2, "w")                                 # GAME OVER 느낌의 가로줄 2개
        rect(c, 21, 14, 6, 2, "w")
        for x, y, rows in ([(2, 2, FLAME_TALL), (12, 2, FLAME_TALL), (15, 4, FLAME_LOW),
                            (-1, 9, FLAME_MID), (-1, 15, FLAME_MID)],
                           [(2, 3, FLAME_MID), (12, 3, FLAME_MID), (14, 0, FLAME_TALL),
                            (-1, 10, FLAME_TALL), (-1, 16, FLAME_MID)])[f]:
            stamp(c, x, y, rows)
        _typing(c, pos, f)
        return c
    for x, ch in ((19, "t"), (21, "y"), (25, "r"), (27, "t")):     # 쌓인 블록 아랫줄
        rect(c, x, 16, 2, 2, ch)
    for x, ch in ((19, "r"), (21, "t"), (25, "r"), (27, "y")):     # 윗줄
        rect(c, x, 14, 2, 2, ch)
    if lv == 1:
        ty = 9 + 2 * f                                             # 떨어지는 T 블록
        rect(c, 21, ty, 6, 2, "y")
        rect(c, 23, ty + 2, 2, 2, "y")
    else:
        rect(c, 25, 12, 2, 2, "r")                                 # 오른쪽 기둥이 더 높이 쌓임
        rect(c, 27, 12, 2, 2, "y")
        rect(c, 25, 10, 2, 2, "t")
        rect(c, 27, 10, 2, 2, "r")
        rect(c, 23, 9 + 2 * f, 2, 2, "y")                          # 틈으로 떨어지는 블록
        stamp(c, 19, 9, COMBO_DIGIT[f])                            # 깜빡이는 콤보 숫자
    _typing(c, pos, f)
    return c


def idle_f(f, lv=1):
    """영상 보기: 화면 가운데 재생 버튼, 진행 막대, 턱을 괴고 넋 놓은 감자.
    lv2: 깔깔 웃으며 책상 두드림, lv3: 감동해서 눈물 콸콸."""
    c = blank()
    pos = potato(c)
    tie(c, pos)
    scene(c)
    if lv == 1:
        for ex in (5, 10):
            spr(c, pos, ex, 13, ["kkk", "wkk", "www"])
        spr(c, pos, 7, 17, ["k..k", ".kk."])
    elif lv == 2:
        spr(c, pos, 5, 14, [".k.", "k.k"])                         # 감은 ^ 눈
        spr(c, pos, 10, 14, [".k.", "k.k"])
        spr(c, pos, 6, 17, ["kkkkkk", "kdrrdk", ".kkkk."])         # 크게 벌린 웃음 + 혀
    else:
        spr(c, pos, 5, 14, ["k.k", ".k."])                         # 감은 눈
        spr(c, pos, 10, 14, ["k.k", ".k."])
        spr(c, pos, 7, 17, (["k.k.k", ".k.k."], [".k.k.", "k.k.k"])[f])   # 떨리는 입
        gaps = ((19, 22), (18, 21))[f]                             # 눈물 줄기가 흘러내림
        for x in (5, 12):
            for y in range(16, 25):
                if y not in gaps:
                    put(c, x, y, "w")
    sprout_up(c, pos)
    stamp(c, 21, 9, [".rrrrr.", "rrrrrrr", "rrrrrrr", "rrrrrrr", ".rrrrr."])
    stamp(c, 23, 10, ["w..", "ww.", "w.."])
    rect(c, 20, 16, 8, 1, "g")
    mx = (21 + 2 * f, 24 + f, 26 + f)[lv - 1]
    if lv > 1:
        rect(c, 20, 16, mx - 20, 1, "w")                           # 진행된 만큼 채움
    rect(c, mx, 15, 2, 2, "w")
    if lv == 1:
        arm(c, 3, 19, 1, 22)
        line(c, 15, 19, 13, 24, "k")                  # 팔꿈치는 책상 위, 손은 턱 밑
        line(c, 13, 24, 11, 21, "k")
        rect(c, 9, 19, 4, 4, "k")
        rect(c, 10, 20, 2, 2, "p")
    elif lv == 2:
        arm(c, 3, 19, 1, 22)
        hx, hy = ((13, 21), (12, 24))[f]                           # 번갈아 책상을 두드리는 손
        ox, oy = ((12, 24), (13, 21))[f]
        arm(c, 15, 19, hx, hy, trail=[(ox, oy)])
        for pts in (((14, 2), (13, 3)), ((16, 5), (15, 6)), ((1, 4), (2, 5))):
            for x, y in pts:
                put(c, x, y + f, "y")
    else:
        arm(c, 3, 19, 1, 22)
        arm(c, 15, 19, 14, 22)
        stamp(c, 0, 16, ["kkkkk", "kwwwk", "kwwwk", "kwwwk", "kkkkk"])   # 휴지 덩어리
    return c


IDLE_G_BUSH = ["....tt...", ".tt.tt.tt", "..ttttt..", "..tt..tt.", "....t....", "....t...."]
IDLE_G_FLOWER = ["..y..", ".yyy.", "yyryy", ".yyy.", "..y.."]
IDLE_G_SPARKLES = ([(15, 1), (4, 1), (15, 6)], [(16, 3), (6, 1), (14, 7)])
IDLE_G_DROPS_BUSH = (
    [(9, 3), (9, 6), (12, 3), (7, 4), (14, 4), (11, 6), (15, 2)],
    [(9, 2), (7, 2), (12, 2), (13, 4), (11, 5), (10, 5), (14, 6)],
)


def idle_g(f, lv=1):
    """셀프 물주기: 머리 옆 바깥에서 분무기로 새싹에 물, 행복한 눈, 쑥 자라는 새싹.
    lv2: 잎 무성+물방울 증가, lv3: 꽃이 활짝+감격."""
    c = blank()
    pos = potato(c, ox=1, oy=1)
    tie(c, pos)
    scene(c)
    spr(c, pos, 5, 14, [".k.", "k.k"])
    spr(c, pos, 10, 14, [".k.", "k.k"])
    if lv == 3:
        spr(c, pos, 6, 17, ["kkkkkk"])                             # 큰 웃음
        spr(c, pos, 6, 18, ["kwwwwk"])
        spr(c, pos, 7, 19, ["kkkk"])
        spr(c, pos, 4, 16, ["w", "w"])                             # 감격의 눈물 한 방울
    else:
        spr(c, pos, 6, 17, ["k....k"])
        spr(c, pos, 7, 18, ["kkkk"])
    if lv > 1:
        stamp(c, 6, 2, IDLE_G_BUSH)
        if f:
            stamp(c, 10, 1, ["tt"])
    elif f == 0:
        sprout_up(c, pos)
    else:
        spr(c, pos, 7, -1, ["ttt"])
        spr(c, pos, 6, 0, ["tt.tt"])
        spr(c, pos, 7, 1, ["ttt"])
        spr(c, pos, 8, 2, ["t", "t", "t", "t"])
    if lv == 3:
        stamp(c, 8, 0, IDLE_G_FLOWER)
    _saver(c, f, [(21, 11), (25, 15)])
    # 병 모양 분무기: 머리(노즐 tt + 끝 k, 방아쇠 k) -> 좁은 목 -> 아래로 넓은 몸통
    stamp(c, 0, 3, [".kkkk...", "kgggk...", "kgggkttk", "kgggkk..",
                    ".kgk.k..", "kgggk...", "kggggk..", "kkkkk..."])
    arm(c, 3, 19, 1, 11)
    arm(c, 15, 19, 11, 22)
    if lv == 1:
        drops = ([(8, 3), (9, 2), (10, 3), (7, 2)], [(7, 4), (8, 3), (8, 5), (6, 3)])[f]
    else:
        drops = IDLE_G_DROPS_BUSH[f]
    for x, y in drops:
        put(c, x, y, "w")
    if lv == 3:
        for x, y in IDLE_G_SPARKLES[f]:
            stamp(c, x - 1, y - 1, [".y.", "yyy", ".y."])
    return c


def _build():
    out = {}
    for name, fn in (("idle", idle), ("idle_b", idle_b), ("idle_c", idle_c),
                     ("idle_d", idle_d), ("idle_d~2", lambda f: idle_d(f, 2)),
                     ("idle_d~3", lambda f: idle_d(f, 3)),
                     ("idle_e", idle_e), ("idle_e~2", lambda f: idle_e(f, 2)),
                     ("idle_e~3", lambda f: idle_e(f, 3)),
                     ("idle_f", idle_f), ("idle_f~2", lambda f: idle_f(f, 2)),
                     ("idle_f~3", lambda f: idle_f(f, 3)),
                     ("idle_g", idle_g), ("idle_g~2", lambda f: idle_g(f, 2)),
                     ("idle_g~3", lambda f: idle_g(f, 3)), ("work", work),
                     ("work_b", work_b), ("work_c", work_c),
                     ("work_d", work_d), ("work_e", work_e), ("work_f", work_f),
                     ("work_g", work_g), ("work_h", work_h),
                     ("wait", wait), ("wait~2", lambda f: wait(f, 2)), ("done", done), ("done_b", done_b), ("done_c", done_c),
                     ("fail", fail)):
        out[name] = [text(fn(f)) for f in (0, 1)]
    return out


FRAMES = _build()

if __name__ == "__main__":
    assert list(FRAMES) == ["idle", "idle_b", "idle_c",
                            "idle_d", "idle_d~2", "idle_d~3", "idle_e", "idle_e~2", "idle_e~3",
                            "idle_f", "idle_f~2", "idle_f~3", "idle_g", "idle_g~2", "idle_g~3",
                            "work", "work_b", "work_c",
                            "work_d", "work_e", "work_f", "work_g", "work_h",
                            "wait", "wait~2", "done", "done_b", "done_c", "fail"]
    ok_chars = set(PALETTE) | {"."}
    for name, fr in FRAMES.items():
        assert len(fr) == 2, name
        for rows in fr:
            assert len(rows) == 32, name
            for r in rows:
                assert len(r) == 32 and set(r) <= ok_chars, (name, r)
    print("ok")
