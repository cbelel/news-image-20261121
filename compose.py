"""Typeset the Saturday edition and draw its artwork with Pillow."""
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
# Lead records end with a map point: longitude first, then latitude.
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

page = Image.new("RGB", (1024, 1024), PAPER)
page_pen = ImageDraw.Draw(page)


@lru_cache
def typeface(size, face):
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVu{face}.ttf", size)


def set_line(x, y, value, size, face="Sans", color=INK, width=None, align="left"):
    face = typeface(size, face)
    length = page_pen.textlength(value, font=face)
    if width is not None:
        assert length <= width, (value, length, width)
        if align == "center":
            x += (width - length) / 2
        elif align == "right":
            x += width - length
    assert 0 <= x and x + length <= 1024, value
    page_pen.text((round(x), y), value, font=face, fill=color, anchor="lt")


def split_at_width(words, size, face, measure):
    """Take the longest whole-word prefix that fits the available space."""
    letterforms = typeface(size, face)
    for stop in range(1, len(words) + 1):
        candidate = " ".join(words[:stop])
        if page_pen.textlength(candidate, font=letterforms) > measure:
            return " ".join(words[:stop - 1]), words[stop - 1:]
    return " ".join(words), []


def set_paragraph(x, y, text, size, width, limit, face="Sans", color=INK, step=None):
    leading = step or size + 2
    pending = text.split()
    lines = []
    while pending:
        fitted, rest = split_at_width(pending, size, face, width)
        assert fitted, (pending[0], width)
        lines.append(fitted)
        pending = rest
    assert len(lines) <= limit, (text, lines)
    for row_number, fitted in enumerate(lines):
        set_line(x, y + row_number * leading, fitted, size, face, color, width)
    return y + len(lines) * leading


def horizontal_rule(y, color=RULE, weight=1):
    page_pen.rectangle((24, y, 999, y + weight - 1), fill=color)


SCENE_INKS = [
    ("#272f3b", "#556475", "#e6c58c"), ("#292f2e", "#526b62", "#d8d0a9"),
    ("#326052", "#739481", "#e6d3a4"), ("#313b51", "#617991", "#c9d7ce"),
    ("#55563b", "#8b9364", "#e4d2a0"), ("#63473e", "#9b7159", "#e9c59a"),
    ("#5e3937", "#a26a58", "#eed3ab"), ("#384d58", "#74858b", "#e8c99d"),
    ("#704535", "#ac7754", "#f1d5a5"), ("#344c68", "#6b8797", "#e8cd86"),
    ("#4c3e48", "#8f6461", "#f0c48d"), ("#244e57", "#52908e", "#e3d2a4"),
]


class BannerPainter:
    """Paint each scene on a double-size surface using percentage coordinates."""

    def __init__(self, width, height, scene_number):
        self.width = width
        self.height = height
        self.shadow, self.midtone, self.highlight = SCENE_INKS[scene_number]
        self.image = Image.new("RGB", (width * 2, height * 2), self.shadow)
        self.pen = ImageDraw.Draw(self.image)
        self.random = random.Random(21 + scene_number)

    def pixel(self, point):
        horizontal, vertical = point
        return (round(horizontal * self.width / 100 * 2),
                round(vertical * self.height / 100 * 2))

    def stroke(self, points, color=None, width=1):
        ink = self.highlight if color is None else color
        self.pen.line([self.pixel(point) for point in points],
                      fill=ink, width=width * 2, joint="curve")

    def polygon(self, points, color):
        self.pen.polygon([self.pixel(point) for point in points], fill=color)

    def rectangle(self, start, end, color):
        self.pen.rectangle((self.pixel(start), self.pixel(end)), fill=color)

    def ellipse(self, start, end, color):
        self.pen.ellipse((self.pixel(start), self.pixel(end)), fill=color)

    def portrait(self, center, top, scale=1, coat=None, direction=1):
        def position(dx, dy):
            return center + dx * scale * direction, top + dy * scale

        jacket = self.midtone if coat is None else coat
        self.polygon([position(-16, 54), position(-12, 33), position(-5, 23),
                      position(5, 23), position(14, 34), position(18, 54)], jacket)
        self.ellipse(position(-5 * direction, 1), position(5 * direction, 28),
                     self.highlight)
        self.polygon([position(-5, 15), position(-5, 5), position(-2, 0),
                      position(3, 1), position(5, 10), position(0, 8)], self.shadow)
        for vertical in (15, 21):
            self.stroke([position(1, vertical), position(3, vertical)], self.shadow)
        self.stroke([position(-5, 29), position(0, 43), position(6, 29)], self.shadow)

    def add_engraving_grain(self):
        # Scene details continue the same random stream after the background.
        for _ in range(540):
            x = self.random.uniform(0, 100)
            y = self.random.uniform(0, 100)
            dash = self.random.uniform(.1, .7)
            self.stroke([(x, y), (x + dash, y)], self.midtone)

    def night_over_kyiv(self):
        self.ellipse((76, 9), (85, 45), self.midtone)
        for u, v in [(7, 9), (22, 5), (34, 16), (47, 8)]:
            self.stroke([(u, v), (u + 17, v + 27)], self.midtone, 2)
            self.stroke([(u + 8, v + 12), (u + 19, v + 30)], self.highlight)
            self.ellipse((u + 18.5, v + 28), (u + 19.5, v + 32), self.highlight)
        for u in range(-2, 102, 4):
            roof = self.random.randint(56, 84)
            self.polygon([(u, 100), (u, roof), (u + 1.5, roof - 5),
                  (u + 3.2, roof), (u + 3.2, 100)], INK)
            for v in range(roof + 5, 96, 8):
                self.stroke([(u + .6, v), (u + 2, v)], self.midtone)
        self.stroke([(0, 92), (26, 92), (33, 82), (58, 82), (65, 92), (100, 92)], self.highlight, 2)
        for u in range(31, 65, 4):
            self.stroke([(u, 90), (u + 2, 83)], self.highlight)

    def falling_market(self):
        for v in range(14, 100, 16):
            self.stroke([(0, v), (100, v)], self.midtone)
        for u in range(4, 100, 7):
            self.stroke([(u, 0), (u, 100)], self.midtone)
        for u in range(5, 100, 4):
            v = self.random.randint(62, 95)
            self.rectangle((u, v), (u + 1.6, 100), self.midtone)
        pts = [(3, 22), (14, 23), (23, 12), (32, 31), (41, 29), (49, 53),
               (58, 44), (66, 62), (75, 57), (86, 75), (96, 85)]
        self.stroke(pts, "#e9a08a", 3)
        self.polygon([(96, 75), (97, 88), (92, 87)], "#e9a08a")
        for u, v in pts[:-1]:
            self.ellipse((u - .55, v - 2), (u + .55, v + 2), self.highlight)

    def climate_delegates(self):
        for u in (18, 37, 59, 80):
            self.portrait(u, 12 + self.random.randrange(10), .86)
            self.stroke([(u + 4, 70), (u + 7, 42), (u + 9, 42)])
        self.polygon([(0, 80), (100, 70), (100, 100), (0, 100)], self.highlight)
        for u in (13, 33, 54, 76):
            self.stroke([(u, 91), (u + 10, 90)], self.shadow)

    def agency_terminals(self):
        for u, v in [(5, 10), (37, 19), (69, 8)]:
            self.rectangle((u, v), (u + 26, v + 58), self.highlight)
            self.rectangle((u + 2, v + 5), (u + 24, v + 50), self.shadow)
            for k in range(3):
                self.stroke([(u + 5, v + 13 + 10*k), (u + 20 - 3*k, v + 13 + 10*k)], self.midtone, 2)
        self.polygon([(35, 100), (43, 70), (58, 70), (66, 100)], INK)
        self.ellipse((42, 50), (59, 85), INK)
        self.stroke([(47, 71), (54, 71)], self.highlight)

    def bottle_and_fields(self):
        for u in range(0, 105, 10):
            self.stroke([(50, 49), (u, 100)], self.midtone, 2)
        self.rectangle((19, 31), (45, 85), self.highlight)
        self.rectangle((26, 13), (38, 32), self.highlight)
        self.rectangle((25, 49), (39, 69), self.midtone)
        self.stroke([(54, 78), (96, 70)], self.highlight, 3)
        for u in (65, 74, 83, 91):
            self.stroke([(u, 76), (u, 91)], self.highlight)
        for u in range(61, 99, 5):
            self.stroke([(u, 94), (u + 2, 87)], self.midtone)

    def andean_fault(self):
        self.polygon([(0, 85), (21, 17), (33, 47), (49, 9), (69, 57), (77, 26),
              (100, 86), (100, 100), (0, 100)], self.midtone)
        for u, v in ((21, 17), (49, 9), (77, 26)):
            self.polygon([(u - 8, v + 21), (u, v), (u + 10, v + 23), (u + 3, v + 17),
                  (u, v + 23), (u - 3, v + 14)], self.highlight)
        self.stroke([(0, 81), (25, 81), (33, 70), (39, 91), (49, 57),
                (58, 87), (67, 77), (100, 77)], "#f0a68a", 2)

    def protest_crowd(self):
        for u in (14, 39, 63, 88):
            v = self.random.randrange(7, 24)
            self.rectangle((u - 1, v), (u, 87), self.highlight)
            self.polygon([(u - 10, v), (u + 9, v - 5), (u + 10, v + 20),
                  (u - 9, v + 24)], self.midtone)
            self.stroke([(u - 5, v + 9), (u + 5, v + 7)])
        for u in (17, 37, 57, 78, 93):
            self.portrait(u, self.random.randrange(42, 61), 1.05, INK)

    def press_podium(self):
        for u in (12, 50, 88):
            self.portrait(u, 8, 1.25, self.midtone, -1 if u > 50 else 1)
        self.polygon([(24, 73), (78, 73), (71, 100), (30, 100)], self.highlight)
        for u in (39, 51, 62):
            self.stroke([(u, 76), (u - 3, 59), (u - 7, 58)], self.shadow, 2)

    def baseball_ground(self):
        self.polygon([(0, 77), (34, 33), (66, 33), (100, 77), (100, 100), (0, 100)], self.midtone)
        self.stroke([(19, 83), (49, 39), (82, 83), (50, 98), (19, 83)], self.highlight, 2)
        for u in (9, 24, 70, 89):
            self.portrait(u, 28 + self.random.randrange(15), .87, INK)
            self.stroke([(u, 74), (u - 6, 96)], INK, 2)
            self.stroke([(u, 74), (u + 8, 90)], INK, 2)

    def brussels_handshake(self):
        for u in (19, 79):
            self.stroke([(u, 11), (u, 86)], self.highlight)
            self.polygon([(u, 14), (u + 17, 19), (u + 17, 47), (u, 42)], self.midtone)
        for j in range(8):
            u = 27 + (j % 4)*2.6
            v = 24 + (j // 4)*10
            self.ellipse((u, v), (u + 1.1, v + 3), self.highlight)
        self.polygon([(0, 85), (39, 45), (55, 54), (70, 46), (100, 74),
              (100, 100), (69, 83), (52, 96), (32, 72), (0, 100)], self.highlight)
        for u in (42, 48, 54, 60):
            self.stroke([(u, 65), (u + 7, 78)], self.midtone, 2)

    def riyadh_skyline(self):
        for u, v in [(13, 7), (32, 6), (51, 15)]:
            self.stroke([(u, v), (u + 24, v + 31)], self.highlight, 2)
            self.stroke([(u + 11, v + 10), (u + 24, v + 31)], "#f4a590", 2)
        for u in range(0, 100, 7):
            top = self.random.randrange(59, 83)
            self.rectangle((u, top), (u + 5, 100), INK)
        self.polygon([(66, 100), (68, 47), (72, 28), (77, 47), (79, 100)], self.highlight)
        self.rectangle((70, 39), (75, 48), self.shadow)

    def strait_patrol(self):
        for v in (65, 76, 89, 98):
            for u in range(-5, 101, 12):
                self.stroke([(u, v), (u + 4, v - 4), (u + 9, v)], self.midtone, 2)
        self.polygon([(13, 30), (43, 30), (47, 18), (51, 17), (55, 30), (87, 30),
              (87, 35), (54, 40), (55, 51), (66, 57), (65, 63), (39, 61),
              (40, 55), (46, 48), (46, 40), (13, 35)], self.highlight)
        self.stroke([(48, 37), (53, 37)], self.shadow, 2)
        self.ellipse((23, 74), (28, 86), self.highlight)
        self.stroke([(13, 87), (20, 78), (25, 84), (36, 83)], self.highlight, 2)

BANNER_SCENES = (
    BannerPainter.night_over_kyiv,
    BannerPainter.falling_market,
    BannerPainter.climate_delegates,
    BannerPainter.agency_terminals,
    BannerPainter.bottle_and_fields,
    BannerPainter.andean_fault,
    BannerPainter.protest_crowd,
    BannerPainter.press_podium,
    BannerPainter.baseball_ground,
    BannerPainter.brussels_handshake,
    BannerPainter.riyadh_skyline,
    BannerPainter.strait_patrol,
)


def place_banner(x, y, width, height, scene_number):
    painter = BannerPainter(width, height, scene_number)
    painter.add_engraving_grain()
    BANNER_SCENES[scene_number](painter)
    banner = painter.image.resize((width, height), Image.Resampling.LANCZOS)
    page.paste(banner, (x, y))


def draw_story_card(index, x, y, card_width, hero=False):
    city, region, headline, deck, source, _ = LEADS[index]
    height, banner_height = (208, 85) if hero else (150, 49)
    page_pen.rectangle((x, y, x + card_width - 1, y + height - 1), fill="#f9f0df", outline=RULE)
    place_banner(x + 1, y + 1, card_width - 2, banner_height, index)
    left, text_width = x + 8, card_width - 16
    kicker = f"{index + 1:02d} / {city.upper()}"
    if hero:
        kicker += "  •  " + ("OVERNIGHT ATTACK" if index == 0 else "MARKETS")
    set_line(left, y + banner_height + 7, kicker, 11 if hero else 9,
         "Sans-Bold", REGIONS[region], text_width)
    end = set_paragraph(left, y + banner_height + (22 if hero else 19), headline, 27 if hero else 16,
                text_width, 2, "Serif-Bold", step=29 if hero else 17)
    end = set_paragraph(left, end + 2, deck, 12 if hero else 10,
                text_width, 3, "Sans", step=14 if hero else 11)
    source_y = y + height - 13
    assert end <= source_y, (headline, end, source_y)
    set_line(left, source_y, source.upper(), 8, "Sans-Bold", MUTED, text_width)


def draw_locator_map():
    # Coarse coastline polygons keep the map readable beneath the pin labels.
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

    page_pen.rectangle((24, 808, 307, 903), fill="#e9e4d5", outline=RULE)
    for lat in (-45, 0, 45):
        yy = project(0, lat)[1]
        page_pen.line((25, yy, 306, yy), fill="#d4cbb7")
    for polygon in shapes:
        page_pen.polygon([project(*point) for point in polygon], fill="#c9bfa5", outline="#a49679")
    labels = [(207, 821), (131, 821), (214, 841), (96, 845), (71, 828),
              (111, 878), (167, 815), (123, 856), (76, 862), (148, 830),
              (196, 863), (230, 854)]
    for lead_data, (lx, ly) in zip(LEADS, labels):
        xx, yy = project(*lead_data[-1])
        color = REGIONS[lead_data[1]]
        page_pen.line((xx, yy, lx, ly), fill=color)
        page_pen.ellipse((xx - 1, yy - 1, xx + 1, yy + 1), fill=color)
    for i, ((lx, ly), lead_data) in enumerate(zip(labels, LEADS), 1):
        color = REGIONS[lead_data[1]]
        page_pen.ellipse((lx - 7, ly - 6, lx + 7, ly + 6), fill=color, outline=PAPER)
        set_line(lx - 7, ly - 3, str(i), 8, "Sans-Bold", "white", 14, "center")
    for i, (name, color) in enumerate(REGIONS.items()):
        x, y = 25 + (i % 4) * 71, 910 + (i // 4) * 14
        page_pen.rectangle((x, y + 1, x + 6, y + 7), fill=color)
        set_line(x + 9, y, name, 8, "Sans-Bold", color, 62)
    set_line(25, 939, "Pin numbers match lead cards; country pins are approximate.",
         8, "Sans", MUTED, 283)


def draw_footer():
    page_pen.rectangle((24, 956, 999, 1001), outline=RED, width=2)
    set_line(33, 963, "DATE CHECK", 11, "Sans-Bold", RED, 117)
    set_line(33, 980, "FIRST REPORTED EARLIER", 8, "Sans-Bold", RED, 123)
    set_line(160, 963, "20 NOV  /  ICJ Rohingya genocide ruling; separate Kyiv attack that killed three.",
         10, "Sans", INK, 831)
    set_line(160, 980, "19 NOV  /  Shenzhen summit and peace declaration; Anthropic market debut; $22.5 million train heist charges.",
         10, "Sans", INK, 831)
    set_line(24, 1008, "SOURCES  /  Verified 21 November news brief, compiled from roundups dated 21 November 2026.",
         9, "Sans", MUTED, 976)


def draw_lower_section():
    horizontal_rule(770, INK, 2)
    set_line(24, 780, "WHERE IT HAPPENED", 16, "Serif-Bold", INK, 285)
    set_line(322, 780, "ALSO ON SATURDAY 21 NOVEMBER", 16, "Serif-Bold", INK, 580)
    set_line(900, 784, f"{len(BRIEFS)} BRIEFS", 10, "Sans-Bold", RED, 99, "right")
    draw_locator_map()
    for i, (place, region, brief) in enumerate(BRIEFS):
        col, row = divmod(i, 6)
        x, y = 322 + col * 227, 803 + row * 25
        if row == 0:
            page_pen.line((x - 8, 802, x - 8, 949), fill=RULE)
        prefix = place.upper() + "  "
        offset = round(page_pen.textlength(prefix, font=typeface(9, "Sans-Bold"))) + 1
        set_line(x, y, prefix, 9, "Sans-Bold", REGIONS[region], 219)
        first_line, overflow = split_at_width(brief.split(), 9, "Sans", 219 - offset)
        set_line(x + offset, y, first_line, 9, "Sans", INK, 219 - offset)
        if overflow:
            set_paragraph(x, y + 11, " ".join(overflow), 9, 219, 1)
        if row < 5:
            page_pen.line((x, y + 22, x + 213, y + 22), fill=RULE)


def draw_lead_grid():
    set_line(24, 448, f"MORE LEADS  /  {len(LEADS) - 2} REPORTS", 13, "Sans-Bold", RED, 400)
    for i in range(2, len(LEADS)):
        row, col = divmod(i - 2, 5)
        draw_story_card(i, 24 + col * 197, 466 + row * 151, 188)


def draw_numbers_strip():
    horizontal_rule(369, RED)
    set_line(25, 374, "BY THE NUMBERS", 11, "Sans-Bold", RED, 210)
    for i, (figure, label) in enumerate(NUMBERS):
        x = 24 + i * 163
        if i:
            page_pen.line((x, 392, x, 436), fill=RULE)
        size = 32
        while page_pen.textlength(figure, font=typeface(size, "Serif-Bold")) > 153:
            size -= 1
        set_line(x, 389 + (32 - size) // 2, figure, size, "Serif-Bold", RED, 161, "center")
        set_line(x, 426, label, 9, "Sans-Bold", INK, 161, "center")
    horizontal_rule(441, RED)


def draw_region_strip(counts):
    for i, (region, color) in enumerate(REGIONS.items()):
        x = 24 + 140 * i
        page_pen.rounded_rectangle((x, 338, x + 135, 360), radius=4, fill=color)
        set_line(x, 343, f"{region}  /  {counts[region]}", 11, "Sans-Bold",
             "#fff8ea", 136, "center")


def draw_hero_pair():
    draw_story_card(0, 24, 123, 483, True)
    draw_story_card(1, 517, 123, 483, True)


def draw_nameplate(story_total):
    horizontal_rule(15, RED, 2)
    set_line(24, 22, "THE WORLD IN ONE DAY", 17, "Sans-Bold", RED, 450)
    set_line(540, 25, f"{story_total} STORIES  /  INTERNATIONAL EDITION",
         11, "Sans-Bold", INK, 460, "right")
    horizontal_rule(43, RED)
    page_pen.rectangle((24, 51, 109, 111), fill=RED)
    set_line(24, 54, "NOV", 10, "Sans-Bold", PAPER, 86, "center")
    set_line(24, 64, "21", 32, "Serif-Bold", PAPER, 86, "center")
    set_line(24, 97, "SAT 2026", 9, "Sans-Bold", PAPER, 86, "center")
    set_line(121, 55, "Saturday 21 November 2026", 53, "Serif-Bold", INK, 879, "center")
    horizontal_rule(116, INK, 2)


def add_paper_grain():
    rng = random.Random(21112026)
    for _ in range(41000):
        x, y = rng.randrange(1024), rng.randrange(1024)
        page_pen.point((x, y), rng.choice(("#f2e8d2", "#f7eedb", "#efe3cd")))


def compose():
    """Assemble bands from top to bottom, then encode the finished page."""
    counts = Counter(record[1] for record in LEADS + BRIEFS)
    assert set(counts) <= set(REGIONS)
    add_paper_grain()
    draw_nameplate(sum(counts.values()))
    draw_hero_pair()
    draw_region_strip(counts)
    draw_numbers_strip()
    draw_lead_grid()
    draw_lower_section()
    draw_footer()
    page.save(Path(__file__).with_name("entry.png"), optimize=True)


if __name__ == "__main__":
    compose()
