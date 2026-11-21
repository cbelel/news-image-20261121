"""Draw the Saturday edition entirely from type and geometric illustrations."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFont


PAPER = "#f5ecd8"
INK = "#241f1b"
MUTED = "#62594a"
RULE = "#ad9e84"
RED = "#942b29"
REGIONS = {
    "Europe": "#355773", "Americas": "#883b34", "Asia-Pacific": "#326052",
    "Middle East": "#865016", "Africa": "#725033", "Oceania": "#5a497a",
    "World": "#555357",
}
# Location, region, headline, deck, attribution, longitude/latitude.
LEADS = [
    ("Kyiv / Poland", "Europe", "Russia strikes Ukraine; missiles land in Poland",
     "Russia fired 400+ drones and 110 missiles overnight. At least eight died in Kyiv; two Russian missiles and a suspected drone came down in Poland.",
     "21 Nov roundup", (30.52, 50.45)),
    ("New York", "Americas", "AI stock rout pushes Wall Street into correction",
     "The chip sell-off sent the S&P 500 down 3.70%. Nasdaq lost 5.28%, erasing its 2026 gains; the Nikkei 225 fell 5.06%.",
     "21 Nov roundup", (-74, 40.71)),
    ("Antalya", "Middle East", "COP31 runs into overtime",
     "Nearly 200 nations failed to agree on fossil fuels.", "UN climate summit", (30.71, 36.90)),
    ("Washington", "Americas", "FBI and USDA hacked",
     "Cyberattacks hit both agencies after outages in strategic sectors.", "21 Nov roundup", (-77.04, 38.91)),
    ("United States", "Americas", "Bayer’s $7.25bn Roundup deal",
     "A US judge approved the agreement to settle Roundup complaints.", "US court", (-99, 39)),
    ("Peruvian Andes", "Americas", "6.9 quake hits Andes",
     "The earthquake struck Peru’s mountain region.", "21 Nov roundup", (-74, -13)),
    ("Berlin", "Europe", "Gen Z protests spread",
     "Demonstrations spread across 25 European countries.", "21 Nov roundup", (13.4, 52.52)),
    ("Washington", "Americas", "Trump defends Putin and Xi ties",
     "After the Shenzhen summit, Trump called Putin his “friend.”", "Trump press conference", (-77.04, 38.91)),
    ("Guasave", "Americas", "‘Chapo Isidro’ captured",
     "Mexico’s army captured the cartel figure; a gunfight sent baseball fans fleeing.", "21 Nov roundup", (-108.47, 25.57)),
    ("Brussels", "Europe", "UK and EU sign three deals",
     "The post-Brexit deals cover food, carbon markets and youth mobility.", "21 Nov roundup", (4.35, 50.85)),
    ("Riyadh", "Middle East", "Three missiles intercepted",
     "The Saudi-led coalition says the Houthi missiles targeted Riyadh.", "Saudi-led coalition", (46.68, 24.71)),
    ("Strait of Hormuz", "Middle East", "Iran says it downed US drone",
     "Iran’s Revolutionary Guards say they brought down a US MQ-9 over the strait.", "Revolutionary Guards", (56.3, 26.6)),
]
BRIEFS = [
    ("India", "Asia-Pacific", "11 die, 180+ hospitalised after drinking adulterated alcohol."),
    ("Nigeria", "Africa", "Funeral boat capsizes; at least four die, including two children."),
    ("Afghanistan", "Asia-Pacific", "Old mortar shell explodes, killing four students."),
    ("Indonesia", "Asia-Pacific", "Forest fires burn 7.1m acres in 2026; losses top $30bn."),
    ("Crypto", "World", "About $2.02bn liquidated in 24h; Bitcoin down 5.58%."),
    ("NASA", "Americas", "Hardware trouble halts science on two Mars missions."),
    ("West Bank", "Middle East", "Israel advances plans for a city of 200,000 residents."),
    ("US court", "Americas", "Nikhil Gupta gets 19 years over plot targeting Pannun."),
    ("Denmark", "Europe", "Russian diplomat expelled over alleged plot to kill a rapper."),
    ("Estonia", "Europe", "Five road crossings with Russia to shut from 1 Dec."),
    ("Spain", "Europe", "Conservatives gain ahead of 29 Nov election."),
    ("Brasilia", "Americas", "Bolsonaro hospitalised with intestinal obstruction."),
    ("Nepal", "Asia-Pacific", "PM Balendra Shah to visit India on 22–23 Nov."),
    ("New York", "Americas", "Mamdani plans to close Rikers Island by 2032."),
    ("South Korea", "Asia-Pacific", "Ruling party moves to impeach the chief justice."),
    ("Vietnam", "Asia-Pacific", "Death penalty ends for drug trafficking and four other offences."),
    ("Iraq", "Middle East", "Federal police enter Jurf al-Sakhar for first time in 12 years."),
    ("Gaming", "World", "GTA 6 sells about $4.9bn on day one."),
]
NUMBERS = [
    ("400+", "drones; 110 missiles"), ("-5.28%", "Nasdaq; S&P 500 -3.70%"),
    ("$7.25 billion", "Bayer Roundup deal"), ("6.9", "magnitude in Peru"),
    ("25", "countries in Gen Z protests"), ("$4.9 billion", "GTA 6 day-one sales"),
]

canvas = Image.new("RGB", (1024, 1024), PAPER)
draw = ImageDraw.Draw(canvas)


@lru_cache
def font(size, face):
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVu{face}.ttf", size)


def line(x, y, value, size, face="Sans", color=INK, width=None, align="left"):
    face = font(size, face)
    length = draw.textlength(value, font=face)
    if width is not None:
        assert length <= width, (value, length, width)
        if align == "center":
            x += (width - length) / 2
        elif align == "right":
            x += width - length
    assert 0 <= x and x + length <= 1024, value
    draw.text((round(x), y), value, font=face, fill=color, anchor="lt")


def block(x, y, value, size, width, limit, face="Sans", color=INK, step=None):
    step = step or size + 2
    rows = []
    row = ""
    for word in value.split():
        trial = f"{row} {word}".strip()
        if row and draw.textlength(trial, font=font(size, face)) > width:
            rows.append(row)
            row = word
        else:
            row = trial
    rows.append(row)
    assert len(rows) <= limit, (value, rows)
    for i, row in enumerate(rows):
        line(x, y + i * step, row, size, face, color, width)
    return y + len(rows) * step


def rule(y, color=RULE, weight=1):
    draw.rectangle((24, y, 999, y + weight - 1), fill=color)


def art(x, y, w, h, scene):
    """Original spot illustrations in a shared two-ink engraving style."""
    palettes = [
        ("#272f3b", "#556475", "#e6c58c"), ("#292f2e", "#526b62", "#d8d0a9"),
        ("#326052", "#739481", "#e6d3a4"), ("#313b51", "#617991", "#c9d7ce"),
        ("#55563b", "#8b9364", "#e4d2a0"), ("#63473e", "#9b7159", "#e9c59a"),
        ("#5e3937", "#a26a58", "#eed3ab"), ("#384d58", "#74858b", "#e8c99d"),
        ("#704535", "#ac7754", "#f1d5a5"), ("#344c68", "#6b8797", "#e8cd86"),
        ("#4c3e48", "#8f6461", "#f0c48d"), ("#244e57", "#52908e", "#e3d2a4"),
    ]
    dark, mid, light = palettes[scene]
    # Work at twice the banner resolution for smooth diagonal strokes.
    img = Image.new("RGB", (w * 2, h * 2), dark)
    pen = ImageDraw.Draw(img)

    def p(pt):
        return (round(pt[0] * w / 100 * 2), round(pt[1] * h / 100 * 2))

    def stroke(points, color=light, width=1):
        pen.line([p(pt) for pt in points], fill=color, width=width * 2, joint="curve")

    def poly(points, color):
        pen.polygon([p(pt) for pt in points], fill=color)

    def box(a, b, color):
        pen.rectangle((p(a), p(b)), fill=color)

    def disk(a, b, color):
        pen.ellipse((p(a), p(b)), fill=color)

    def person(cx, cy, scale=1, coat=mid, flip=1):
        def q(dx, dy):
            return cx + dx * scale * flip, cy + dy * scale
        poly([q(-16, 54), q(-12, 33), q(-5, 23), q(5, 23),
              q(14, 34), q(18, 54)], coat)
        disk(q(-5 if flip > 0 else 5, 1), q(5 if flip > 0 else -5, 28), light)
        poly([q(-5, 15), q(-5, 5), q(-2, 0), q(3, 1), q(5, 10), q(0, 8)], dark)
        stroke([q(1, 15), q(3, 15)], dark)
        stroke([q(1, 21), q(3, 21)], dark)
        stroke([q(-5, 29), q(0, 43), q(6, 29)], dark)

    rng = random.Random(21 + scene)
    for _ in range(540):
        u, v = rng.uniform(0, 100), rng.uniform(0, 100)
        stroke([(u, v), (u + rng.uniform(.1, .7), v)], mid)
    if scene == 0:
        disk((76, 9), (85, 45), mid)
        for u, v in [(7, 9), (22, 5), (34, 16), (47, 8)]:
            stroke([(u, v), (u + 17, v + 27)], mid, 2)
            stroke([(u + 8, v + 12), (u + 19, v + 30)], light)
            disk((u + 18.5, v + 28), (u + 19.5, v + 32), light)
        for u in range(-2, 102, 4):
            roof = rng.randint(56, 84)
            poly([(u, 100), (u, roof), (u + 1.5, roof - 5),
                  (u + 3.2, roof), (u + 3.2, 100)], INK)
            for v in range(roof + 5, 96, 8):
                stroke([(u + .6, v), (u + 2, v)], mid)
        stroke([(0, 92), (26, 92), (33, 82), (58, 82), (65, 92), (100, 92)], light, 2)
        for u in range(31, 65, 4):
            stroke([(u, 90), (u + 2, 83)], light)
    elif scene == 1:
        for v in range(14, 100, 16):
            stroke([(0, v), (100, v)], mid)
        for u in range(4, 100, 7):
            stroke([(u, 0), (u, 100)], mid)
        for u in range(5, 100, 4):
            v = rng.randint(62, 95)
            box((u, v), (u + 1.6, 100), mid)
        pts = [(3, 22), (14, 23), (23, 12), (32, 31), (41, 29), (49, 53),
               (58, 44), (66, 62), (75, 57), (86, 75), (96, 85)]
        stroke(pts, "#e9a08a", 3)
        poly([(96, 75), (97, 88), (92, 87)], "#e9a08a")
        for u, v in pts[:-1]:
            disk((u - .55, v - 2), (u + .55, v + 2), light)
    elif scene == 2:
        for u in (18, 37, 59, 80):
            person(u, 12 + rng.randrange(10), .86)
            stroke([(u + 4, 70), (u + 7, 42), (u + 9, 42)])
        poly([(0, 80), (100, 70), (100, 100), (0, 100)], light)
        for u in (13, 33, 54, 76):
            stroke([(u, 91), (u + 10, 90)], dark)
    elif scene == 3:
        for u, v in [(5, 10), (37, 19), (69, 8)]:
            box((u, v), (u + 26, v + 58), light)
            box((u + 2, v + 5), (u + 24, v + 50), dark)
            for k in range(3):
                stroke([(u + 5, v + 13 + 10*k), (u + 20 - 3*k, v + 13 + 10*k)], mid, 2)
        poly([(35, 100), (43, 70), (58, 70), (66, 100)], INK)
        disk((42, 50), (59, 85), INK)
        stroke([(47, 71), (54, 71)], light)
    elif scene == 4:
        for u in range(0, 105, 10):
            stroke([(50, 49), (u, 100)], mid, 2)
        box((19, 31), (45, 85), light)
        box((26, 13), (38, 32), light)
        box((25, 49), (39, 69), mid)
        stroke([(54, 78), (96, 70)], light, 3)
        for u in (65, 74, 83, 91):
            stroke([(u, 76), (u, 91)], light)
        for u in range(61, 99, 5):
            stroke([(u, 94), (u + 2, 87)], mid)
    elif scene == 5:
        poly([(0, 85), (21, 17), (33, 47), (49, 9), (69, 57), (77, 26),
              (100, 86), (100, 100), (0, 100)], mid)
        for u, v in ((21, 17), (49, 9), (77, 26)):
            poly([(u - 8, v + 21), (u, v), (u + 10, v + 23), (u + 3, v + 17),
                  (u, v + 23), (u - 3, v + 14)], light)
        stroke([(0, 81), (25, 81), (33, 70), (39, 91), (49, 57),
                (58, 87), (67, 77), (100, 77)], "#f0a68a", 2)
    elif scene == 6:
        for u in (14, 39, 63, 88):
            v = rng.randrange(7, 24)
            box((u - 1, v), (u, 87), light)
            poly([(u - 10, v), (u + 9, v - 5), (u + 10, v + 20),
                  (u - 9, v + 24)], mid)
            stroke([(u - 5, v + 9), (u + 5, v + 7)])
        for u in (17, 37, 57, 78, 93):
            person(u, rng.randrange(42, 61), 1.05, INK)
    elif scene == 7:
        for u in (12, 50, 88):
            person(u, 8, 1.25, mid, -1 if u > 50 else 1)
        poly([(24, 73), (78, 73), (71, 100), (30, 100)], light)
        for u in (39, 51, 62):
            stroke([(u, 76), (u - 3, 59), (u - 7, 58)], dark, 2)
    elif scene == 8:
        poly([(0, 77), (34, 33), (66, 33), (100, 77), (100, 100), (0, 100)], mid)
        stroke([(19, 83), (49, 39), (82, 83), (50, 98), (19, 83)], light, 2)
        for u in (9, 24, 70, 89):
            person(u, 28 + rng.randrange(15), .87, INK)
            stroke([(u, 74), (u - 6, 96)], INK, 2)
            stroke([(u, 74), (u + 8, 90)], INK, 2)
    elif scene == 9:
        for u in (19, 79):
            stroke([(u, 11), (u, 86)], light)
            poly([(u, 14), (u + 17, 19), (u + 17, 47), (u, 42)], mid)
        for j in range(8):
            u = 27 + (j % 4)*2.6
            v = 24 + (j // 4)*10
            disk((u, v), (u + 1.1, v + 3), light)
        poly([(0, 85), (39, 45), (55, 54), (70, 46), (100, 74),
              (100, 100), (69, 83), (52, 96), (32, 72), (0, 100)], light)
        for u in (42, 48, 54, 60):
            stroke([(u, 65), (u + 7, 78)], mid, 2)
    elif scene == 10:
        for u, v in [(13, 7), (32, 6), (51, 15)]:
            stroke([(u, v), (u + 24, v + 31)], light, 2)
            stroke([(u + 11, v + 10), (u + 24, v + 31)], "#f4a590", 2)
        for u in range(0, 100, 7):
            top = rng.randrange(59, 83)
            box((u, top), (u + 5, 100), INK)
        poly([(66, 100), (68, 47), (72, 28), (77, 47), (79, 100)], light)
        box((70, 39), (75, 48), dark)
    else:
        for v in (65, 76, 89, 98):
            for u in range(-5, 101, 12):
                stroke([(u, v), (u + 4, v - 4), (u + 9, v)], mid, 2)
        poly([(13, 30), (43, 30), (47, 18), (51, 17), (55, 30), (87, 30),
              (87, 35), (54, 40), (55, 51), (66, 57), (65, 63), (39, 61),
              (40, 55), (46, 48), (46, 40), (13, 35)], light)
        stroke([(48, 37), (53, 37)], dark, 2)
        disk((23, 74), (28, 86), light)
        stroke([(13, 87), (20, 78), (25, 84), (36, 83)], light, 2)
    canvas.paste(img.resize((w, h), Image.Resampling.LANCZOS), (x, y))


def lead(index, x, y, w, hero=False):
    city, region, headline, deck, source, _ = LEADS[index]
    height, banner = (208, 85) if hero else (150, 49)
    draw.rectangle((x, y, x + w - 1, y + height - 1), fill="#f9f0df", outline=RULE)
    art(x + 1, y + 1, w - 2, banner, index)
    left, measure = x + 8, w - 16
    kicker = f"{index + 1:02d} / {city.upper()}"
    if hero:
        kicker += "  •  " + ("OVERNIGHT ATTACK" if index == 0 else "MARKETS")
    line(left, y + banner + 7, kicker, 11 if hero else 9,
         "Sans-Bold", REGIONS[region], measure)
    end = block(left, y + banner + (22 if hero else 19), headline, 27 if hero else 16,
                measure, 2, "Serif-Bold", step=29 if hero else 17)
    end = block(left, end + 2, deck, 12 if hero else 10,
                measure, 3, "Sans", step=14 if hero else 11)
    source_y = y + height - 13
    assert end <= source_y, (headline, end, source_y)
    line(left, source_y, source.upper(), 8, "Sans-Bold", MUTED, measure)


def map_panel():
    # Simplified coastlines in longitude/latitude.
    shapes = [
        [(-166, 65), (-146, 72), (-107, 74), (-81, 68), (-59, 52), (-79, 43),
         (-82, 27), (-97, 23), (-83, 10), (-95, 15), (-115, 28), (-126, 51)],
        [(-73, 82), (-19, 81), (-43, 60), (-61, 62)],
        [(-81, 10), (-60, 12), (-35, -6), (-50, -29), (-65, -55), (-76, -41)],
        [(-11, 36), (-10, 49), (7, 55), (18, 70), (42, 70), (62, 75),
         (100, 77), (157, 70), (179, 63), (154, 49), (128, 42), (119, 22),
         (105, 6), (88, 22), (76, 8), (66, 24), (54, 26), (43, 12),
         (32, 30), (35, 37), (18, 41), (9, 38)],
        [(-17, 32), (10, 38), (32, 30), (50, 10), (39, -13), (20, -35),
         (9, -23), (2, 4), (-14, 11)],
        [(112, -23), (128, -15), (152, -19), (155, -36), (135, -39), (115, -34)],
        [(97, 5), (119, 1), (141, -5), (151, -10), (121, -9), (104, -5)],
    ]

    def project(lon, lat):
        return round(166 + lon * .74), round(863 - lat * .62)

    draw.rectangle((24, 808, 307, 903), fill="#e9e4d5", outline=RULE)
    for lat in (-45, 0, 45):
        yy = project(0, lat)[1]
        draw.line((25, yy, 306, yy), fill="#d4cbb7")
    for polygon in shapes:
        draw.polygon([project(*point) for point in polygon], fill="#c9bfa5", outline="#a49679")
    labels = [(207, 821), (131, 821), (214, 841), (96, 845), (71, 828),
              (111, 878), (167, 815), (123, 856), (76, 862), (148, 830),
              (196, 863), (230, 854)]
    for lead_data, (lx, ly) in zip(LEADS, labels):
        xx, yy = project(*lead_data[-1])
        color = REGIONS[lead_data[1]]
        draw.line((xx, yy, lx, ly), fill=color)
        draw.ellipse((xx - 1, yy - 1, xx + 1, yy + 1), fill=color)
    for i, ((lx, ly), lead_data) in enumerate(zip(labels, LEADS), 1):
        color = REGIONS[lead_data[1]]
        draw.ellipse((lx - 7, ly - 6, lx + 7, ly + 6), fill=color, outline=PAPER)
        line(lx - 7, ly - 3, str(i), 8, "Sans-Bold", "white", 14, "center")
    for i, (name, color) in enumerate(REGIONS.items()):
        x, y = 25 + (i % 4) * 71, 910 + (i // 4) * 14
        draw.rectangle((x, y + 1, x + 6, y + 7), fill=color)
        line(x + 9, y, name, 8, "Sans-Bold", color, 62)
    line(25, 939, "Pin numbers match lead cards; country pins are approximate.",
         8, "Sans", MUTED, 283)


def compose():
    counts = Counter(item[1] for item in LEADS + BRIEFS)
    assert set(counts) <= set(REGIONS)
    rng = random.Random(21112026)
    for _ in range(41000):
        x, y = rng.randrange(1024), rng.randrange(1024)
        draw.point((x, y), rng.choice(("#f2e8d2", "#f7eedb", "#efe3cd")))
    rule(15, RED, 2)
    line(24, 22, "THE WORLD IN ONE DAY", 17, "Sans-Bold", RED, 450)
    line(540, 25, f"{sum(counts.values())} STORIES  /  INTERNATIONAL EDITION",
         11, "Sans-Bold", INK, 460, "right")
    rule(43, RED)
    draw.rectangle((24, 51, 109, 111), fill=RED)
    line(24, 54, "NOV", 10, "Sans-Bold", PAPER, 86, "center")
    line(24, 64, "21", 32, "Serif-Bold", PAPER, 86, "center")
    line(24, 97, "SAT 2026", 9, "Sans-Bold", PAPER, 86, "center")
    line(121, 55, "Saturday 21 November 2026", 53, "Serif-Bold", INK, 879, "center")
    rule(116, INK, 2)

    lead(0, 24, 123, 483, True)
    lead(1, 517, 123, 483, True)
    for i, (region, color) in enumerate(REGIONS.items()):
        x = 24 + 140 * i
        draw.rounded_rectangle((x, 338, x + 135, 360), radius=4, fill=color)
        line(x, 343, f"{region}  /  {counts[region]}", 11, "Sans-Bold",
             "#fff8ea", 136, "center")

    rule(369, RED)
    line(25, 374, "BY THE NUMBERS", 11, "Sans-Bold", RED, 210)
    for i, (figure, label) in enumerate(NUMBERS):
        x = 24 + i * 163
        if i:
            draw.line((x, 392, x, 436), fill=RULE)
        size = 32
        while draw.textlength(figure, font=font(size, "Serif-Bold")) > 153:
            size -= 1
        line(x, 389 + (32 - size) // 2, figure, size, "Serif-Bold", RED, 161, "center")
        line(x, 426, label, 9, "Sans-Bold", INK, 161, "center")
    rule(441, RED)
    line(24, 448, f"MORE LEADS  /  {len(LEADS) - 2} REPORTS", 13, "Sans-Bold", RED, 400)
    for i in range(2, len(LEADS)):
        row, col = divmod(i - 2, 5)
        lead(i, 24 + col * 197, 466 + row * 151, 188)

    rule(770, INK, 2)
    line(24, 780, "WHERE IT HAPPENED", 16, "Serif-Bold", INK, 285)
    line(322, 780, "ALSO ON SATURDAY 21 NOVEMBER", 16, "Serif-Bold", INK, 580)
    line(900, 784, f"{len(BRIEFS)} BRIEFS", 10, "Sans-Bold", RED, 99, "right")
    map_panel()
    for i, (place, region, brief) in enumerate(BRIEFS):
        col, row = divmod(i, 6)
        x, y = 322 + col * 227, 803 + row * 25
        if row == 0:
            draw.line((x - 8, 802, x - 8, 949), fill=RULE)
        prefix = place.upper() + "  "
        offset = round(draw.textlength(prefix, font=font(9, "Sans-Bold"))) + 1
        line(x, y, prefix, 9, "Sans-Bold", REGIONS[region], 219)
        words = brief.split()
        first = ""
        while words:
            trial = (first + " " + words[0]).strip()
            if draw.textlength(trial, font=font(9, "Sans")) > 219 - offset:
                break
            first = trial
            words.pop(0)
        line(x + offset, y, first, 9, "Sans", INK, 219 - offset)
        if words:
            block(x, y + 11, " ".join(words), 9, 219, 1)
        if row < 5:
            draw.line((x, y + 22, x + 213, y + 22), fill=RULE)

    draw.rectangle((24, 956, 999, 1001), outline=RED, width=2)
    line(33, 963, "DATE CHECK", 11, "Sans-Bold", RED, 117)
    line(33, 980, "FIRST REPORTED EARLIER", 8, "Sans-Bold", RED, 123)
    line(160, 963, "20 NOV  /  ICJ Rohingya genocide ruling; separate Kyiv attack that killed three.",
         10, "Sans", INK, 831)
    line(160, 980, "19 NOV  /  Shenzhen summit and peace declaration; Anthropic market debut; $22.5 million train heist charges.",
         10, "Sans", INK, 831)
    line(24, 1008, "SOURCES  /  Verified 21 November news brief, compiled from roundups dated 21 November 2026.",
         9, "Sans", MUTED, 976)
    canvas.save(Path(__file__).with_name("entry.png"), optimize=True)


if __name__ == "__main__":
    compose()
