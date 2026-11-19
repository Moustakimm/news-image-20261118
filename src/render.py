#!/usr/bin/env python3
"""Renders entry.png (1024x1024) for the news-image-20261118 bounty.

Dense broadsheet format: 45 real stories from Wednesday 18 November 2026 —
giant date masthead, a UTC timeline strip, 3 illustrated lead stories,
10 illustrated medium stories, a 32-item numbered list, a pinned world map,
a date-check box and a sources line. Same format as the winning entries of
the sister 17 November competition (top 10 all used it).

Every story was checked against reporting from 18 November 2026 (see
CAPTION.md). Nothing is invented: no event, quote, number or location.

Run:  python3 src/render.py   (writes ./entry.png at the repo root)
Requires Pillow and the DejaVu fonts (standard on this machine).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (25, 23, 19)
BODY = (43, 40, 34)
RED = (158, 42, 32)
RED_DK = (120, 30, 24)
NAVY = (29, 58, 95)
GOLD = (201, 123, 45)
CREAM2 = (238, 231, 214)
SKY = (178, 205, 224)
SEA = (140, 175, 200)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Region colours (used for tags, number dots and map pins).
EUROPE = (31, 73, 125)
MIDDLE_EAST = (176, 106, 28)
ASIA = (120, 58, 138)
AMERICAS = (172, 32, 32)
AFRICA = (32, 118, 58)
OCEANIA = (0, 128, 138)
GLOBAL = (74, 74, 74)

REGION_NAME = {
    EUROPE: "EUROPE", MIDDLE_EAST: "MIDDLE EAST", ASIA: "ASIA",
    AMERICAS: "AMERICAS", AFRICA: "AFRICA", OCEANIA: "OCEANIA",
    GLOBAL: "GLOBAL",
}


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, lines, f, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def centered(draw, cx, y, s, f, fill, tracking=0):
    """Draw text centred on cx, with optional extra tracking between chars."""
    if tracking:
        w = sum(draw.textlength(ch, font=f) + tracking for ch in s) - tracking
        x = cx - w / 2
        for ch in s:
            draw.text((x, y), ch, font=f, fill=fill)
            x += draw.textlength(ch, font=f) + tracking
    else:
        w = draw.textlength(s, font=f)
        draw.text((cx - w / 2, y), s, font=f, fill=fill)


def fit_font(draw, s, path, start, max_w):
    """Largest size <= start whose text fits max_w."""
    size = start
    while size > 10 and draw.textlength(s, font=font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def num_dot(draw, x, y, n, color, r=7):
    """Numbered circle used for story numbers."""
    draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
    s = str(n)
    f = font(SANS_B, 9 if len(s) < 2 else 8)
    w = draw.textlength(s, font=f)
    draw.text((x - w / 2, y - 5 if len(s) < 2 else y - 4), s, font=f,
              fill=(255, 255, 255))


# ---------------------------------------------------------------- data
# Featured stories: (num, region, tag, headline, summary, label, scene, lon, lat)
LEADS = [
    (1, ASIA, "ASIA · DIPLOMACY",
     "Xi and Putin meet in Shenzhen; Trump lands for first trilateral",
     "The Chinese and Russian leaders hold talks at APEC a day before the "
     "first three-way summit with the US president.",
     "CONFIRMED — AFP / AP", "summit", (114.1, 22.5)),
    (2, MIDDLE_EAST, "MIDDLE EAST · CONFLICT",
     "Iran says its drones struck a US base in Kuwait",
     "Tehran claims hits on Patriot systems at Ali Al Salem; an ADNOC ship "
     "is struck in Hormuz, 11 hurt and one crew member missing.",
     "CLAIM — IRAN / AP", "ship", (48.5, 29.3)),
    (3, ASIA, "SOUTH ASIA · WEATHER",
     "Cyclone Akvan bears down on Odisha; 47,000 evacuated",
     "The severe storm is due to cross the coast near Gopalpur by Friday, "
     "winds 100–110 km/h gusting to 120; shelters are ready.",
     "CONFIRMED — IMD", "cyclone", (85.0, 19.0)),
]

MEDIUM = [
    (4, AMERICAS, "US · POLITICS",
     "Democrats take the US Senate as Peltola wins Alaska",
     "Peltola beats Sullivan; Democrats are projected to hold 56–44.",
     "AP", "vote"),
    (5, ASIA, "ASIA · DIPLOMACY",
     "Quad leaders meet in Manila, first time in two years",
     "Trump announces a US–Philippines trade deal and deeper defence ties.",
     "AP", "handshake"),
    (6, MIDDLE_EAST, "MIDDLE EAST · GAZA",
     "Israel begins 'concentrated operation' in central Gaza",
     "Troops move in three areas; the Board of Peace faults both sides.",
     "AP", "tank"),
    (7, EUROPE, "EUROPE · UKRAINE WAR",
     "Ukraine hits Crimea bridge for a second day",
     "Zelensky confirms the strike; Russia hits two bridges in Kyiv.",
     "AP / REUTERS", "bridge"),
    (8, GLOBAL, "GLOBAL · TECHNOLOGY",
     "Nvidia doubles revenue to $115.8bn — shares still fall",
     "Revenue up 103% and guidance near $130bn, but the stock ends down.",
     "REUTERS", "chip"),
    (9, GLOBAL, "GLOBAL · MARKETS",
     "Wall Street ends split; Dow down 1.1%",
     "Dow falls 561 points; S&P drops a fifth day; Nasdaq up 0.4%.",
     "CNBC", "markets"),
    (10, GLOBAL, "GLOBAL · MARKETS",
     "Anthropic prices record IPO at $83, above its range",
     "The AI firm prices above the $70–78 range; trading starts Thursday.",
     "REUTERS", "ipo"),
    (11, GLOBAL, "GLOBAL · CULTURE",
     "GTA VI launches at midnight after a 13-year wait",
     "Rockstar's return to Leonida and Vice City arrives on PS5 and Xbox.",
     "ROCKSTAR / NDTV", "game"),
    (12, AMERICAS, "US · COURTS",
     "Trump asks court to overturn hush-money conviction",
     "A federal court weighs intervening in the New York case.",
     "AP", "court"),
    (13, MIDDLE_EAST, "MIDDLE EAST · CONFLICT",
     "Saudi-led coalition hits Houthis; at least 17 killed",
     "Major airstrikes follow a week of attacks on Gulf shipping.",
     "AP", "jet"),
]

# Numbered list (14-45): (num, region, text)
LIST_ITEMS = [
    (14, MIDDLE_EAST, "Oil tanker catches fire after hitting naval mine in Hormuz"),
    (15, GLOBAL, "NATO unveils strategy for next-generation networks"),
    (16, ASIA, "India-US trade deal nearly finalised; signing delayed"),
    (17, ASIA, "Bangladesh deploys paramilitary as ousted PM vows to return"),
    (18, ASIA, "Top LeT terrorist killed in encounter in south Kashmir"),
    (19, ASIA, "NEET-UG leak: court orders charges against 14 accused"),
    (20, ASIA, "IPL franchises retain 184 players in final list"),
    (21, ASIA, "PV Sindhu returns to badminton world top five"),
    (22, ASIA, "Sensex up 500 pts; Nifty tops 25,400"),
    (23, ASIA, "FPI flows into India hit record $10bn in November"),
    (24, ASIA, "Amazon plans $7bn renewable investment in India by 2030"),
    (25, ASIA, "Delhi lifts GRAP Stage 3 as air quality improves"),
    (26, EUROPE, "Britain sanctions firms linked to West Bank settlements"),
    (27, EUROPE, "Man charged with axing $60m US military plane in Ireland"),
    (28, EUROPE, "Dozens injured as trains collide near Prague"),
    (29, EUROPE, "Hoax bomb threats rattled Europe's schools and airports"),
    (30, EUROPE, "Serbia's students enter parliament after historic election"),
    (31, EUROPE, "Ex-Kosovo leader Thaci guilty of witness tampering"),
    (32, EUROPE, "Turkish government takes over opposition-linked TV station"),
    (33, EUROPE, "UK hands US soldier accused of spying to America"),
    (34, OCEANIA, "Magnitude 6 earthquake strikes Papua New Guinea"),
    (35, OCEANIA, "Australia's gender pay gap drops below 20% for first time"),
    (36, OCEANIA, "COP31: Australia challenged over coal and gas expansion"),
    (37, AMERICAS, "Thousands march in Haiti to praise Bukele's anti-gang force"),
    (38, AMERICAS, "US judge blocks stay limits for students and journalists"),
    (39, AMERICAS, "Canada names eight Nigerians in $4.5m car-theft ring"),
    (40, AMERICAS, "TJX jumps 10.4%, Target up 5.6% on retail results"),
    (41, AMERICAS, "UnitedHealth plunges 7% as healthcare sell-off deepens"),
    (42, AMERICAS, "Pending home sales fall to record low"),
    (43, MIDDLE_EAST, "Pakistan condemns Israeli attacks in Syria"),
    (44, MIDDLE_EAST, "Child among six killed by Israeli forces across Gaza"),
    (45, AFRICA, "UN warns of rights risks of Rwanda deportation hub"),
]

TIMELINE = [
    ("Overnight", "Iran says drones hit US base in Kuwait"),
    ("Morning", "Xi and Putin meet in Shenzhen"),
    ("12:29 UTC", "Israel begins Gaza operation"),
    ("19:00 UTC", "Fed minutes point to more hikes"),
    ("21:00 UTC", "Wall Street closes split"),
    ("Midnight", "GTA VI launches at midnight"),
]

DATE_CHECK = ("Left out on purpose: the US strike on Qeshm Island and the "
              "Crimea bridge's first strike (both Tue 17 Nov). Not yet: the "
              "Trump–Xi–Putin trilateral, due Thursday; Cyclone Akvan's "
              "landfall, due Friday.")
FOOTER = ("Every story here happened or was first reported on Wednesday 18 November "
          "2026. Contested claims are marked as claims.")
SOURCES = ("Sources: AP, Reuters, AFP, DPA, Outlook India, The Hindu BusinessLine, "
           "Korea Herald, Japan Times, Dawn, Motley Fool, NDTV, ABP Live. "
           "Original drawings.")

# ------------------------------------------------------------- illustrations
def _flag_us(d, x, y, w, h):
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=(30, 50, 110))


def _flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    for sx, sy, r in [(0.2, 0.25, 3), (0.45, 0.2, 2), (0.5, 0.4, 2),
                      (0.35, 0.5, 2)]:
        d.ellipse([x + sx * w - r, y + sy * h - r, x + sx * w + r,
                   y + sy * h + r], fill=(255, 222, 0))


def _flag_ru(d, x, y, w, h):
    for i, c in enumerate([(255, 255, 255), (0, 60, 160), (220, 30, 30)]):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)


def _label_bar(d, x, y, w, text, bg=(25, 23, 19)):
    f = font(SANS_B, 9)
    d.rectangle([x, y, x + w, y + 14], fill=bg)
    d.text((x + 5, y + 3), text, font=f, fill=(255, 255, 255))


def _draw_scene(d, x, y, w, h, kind, label=""):
    """Draw a small iconic illustration inside (x, y, w, h)."""
    if kind == "summit":
        d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
        d.rectangle([x, y, x + w, y + 26], fill=(120, 60, 60))
        d.text((x + 8, y + 6), "SHENZHEN · KYLIN VILLA", font=font(SANS_B, 10),
               fill=(255, 255, 255))
        # three flags on poles
        for i, fl in enumerate((_flag_us, _flag_cn, _flag_ru)):
            fx = x + 30 + i * (w - 60) // 2
            d.line([fx + 14, y + 30, fx + 14, y + h - 34], fill=(60, 50, 40),
                   width=2)
            fl(d, fx, y + 32, 28, 18)
        # table + three seated figures
        d.rectangle([x + 16, y + h - 34, x + w - 16, y + h - 12],
                    fill=(120, 80, 50))
        for i in range(3):
            cx = x + 45 + i * (w - 90) // 2
            d.ellipse([cx - 9, y + h - 56, cx + 9, y + h - 38],
                      fill=(40, 40, 40))
            d.rectangle([cx - 12, y + h - 40, cx + 12, y + h - 34],
                        fill=(40, 40, 40))
    elif kind == "court":
        d.rectangle([x, y, x + w, y + h], fill=(214, 206, 188))
        d.polygon([(x + w / 2, y + 6), (x + 18, y + h * 0.36),
                   (x + w - 18, y + h * 0.36)],
                  fill=(150, 130, 110))
        for i in range(4):
            cx = x + 30 + i * (w - 60) // 3
            d.rectangle([cx - 6, y + h * 0.38, cx + 6, y + h * 0.82],
                        fill=(240, 234, 220))
        d.rectangle([x + 12, y + h * 0.82, x + w - 12, y + h * 0.92],
                    fill=(150, 130, 110))
        # scales of justice
        sx, sy = x + w - 52, y + h * 0.42
        d.line([sx, sy, sx, sy + 22], fill=(90, 70, 40), width=2)
        d.line([sx - 14, sy + 4, sx + 14, sy + 4], fill=(90, 70, 40), width=2)
        d.ellipse([sx - 18, sy + 18, sx - 8, sy + 26], fill=(180, 140, 60))
        d.ellipse([sx + 8, sy + 18, sx + 18, sy + 26], fill=(180, 140, 60))
    elif kind == "cyclone":
        d.rectangle([x, y, x + w, y + h], fill=(150, 180, 205))
        d.rectangle([x, y + h - 26, x + w, y + h], fill=(90, 130, 90))
        cx, cy = x + w * 0.42, y + h * 0.42
        for r in (34, 26, 18, 10):
            d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300,
                  fill=(255, 255, 255), width=3)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255))
        for i in range(6):
            rx = x + 12 + i * 14
            d.line([rx, y + 8, rx - 4, y + 22], fill=(220, 230, 240), width=2)
        _label_bar(d, x, y + h - 14, w, "LANDFALL DUE FRIDAY")
    elif kind == "tower":
        d.rectangle([x, y, x + w, y + h], fill=(226, 196, 150))
        d.rectangle([x, y + h - 30, x + w, y + h], fill=(90, 90, 100))
        tx = x + w // 2 - 16
        d.rectangle([tx, y + 14, tx + 32, y + h - 30], fill=(40, 48, 70))
        for r in range(6):
            for c in range(2):
                if (r + c) % 2 == 0:
                    d.rectangle([tx + 4 + c * 14, y + 20 + r * 9,
                                 tx + 12 + c * 14, y + 26 + r * 9],
                                fill=(255, 210, 90))
        d.ellipse([tx + 26, y + 2, tx + 46, y + 20], fill=(120, 120, 120))
        d.ellipse([tx + 34, y - 6, tx + 52, y + 10], fill=(150, 150, 150))
        d.rectangle([x + 12, y + h - 52, x + 34, y + h - 30], fill=(70, 70, 80))
        d.rectangle([x + w - 34, y + h - 46, x + w - 12, y + h - 30],
                    fill=(70, 70, 80))
        _label_bar(d, x, y + h - 14, w, "PIF TOWER · RIYADH")
    elif kind == "bridge":
        d.rectangle([x, y, x + w, y + h], fill=(168, 198, 220))
        d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(52, 96, 140))
        d.rectangle([x, y + h * 0.42, x + w, y + h * 0.5], fill=(70, 70, 70))
        for px in (x + w * 0.2, x + w * 0.55, x + w * 0.85):
            d.rectangle([px - 4, y + h * 0.5, px + 4, y + h * 0.8],
                        fill=(50, 50, 50))
        # broken span + blast
        bx, by = x + w * 0.68, y + h * 0.42
        d.polygon([(bx, by), (bx + 26, by - 4), (bx + 14, by + 12)],
                  fill=(90, 90, 90))
        for ang in range(0, 360, 45):
            ex = bx + 12 + 16 * math.cos(math.radians(ang))
            ey = by - 14 + 12 * math.sin(math.radians(ang))
            d.line([bx + 12, by - 14, ex, ey], fill=(255, 140, 0), width=3)
        d.ellipse([bx + 2, by - 24, bx + 22, by - 4], fill=(255, 200, 60))
        _label_bar(d, x, y + h - 14, w, "KERCH STRAIT · THIRD STRIKE")
    elif kind == "ipo":
        d.rectangle([x, y, x + w, y + h], fill=(18, 40, 32))
        pts = [(x + 8, y + h - 22), (x + w * 0.3, y + h - 40),
               (x + w * 0.55, y + h - 30), (x + w * 0.8, y + h - 52),
               (x + w - 10, y + 18)]
        d.line(pts, fill=(80, 220, 120), width=3, joint="curve")
        d.polygon([(x + w - 22, y + 12), (x + w - 6, y + 12), (x + w - 14, y + 26)],
                  fill=(80, 220, 120))
        d.text((x + 10, y + 8), "$83", font=font(SANS_B, 26),
               fill=(255, 255, 255))
        d.text((x + 10, y + h - 18), "ANT · NASDAQ", font=font(SANS_B, 9),
               fill=(160, 220, 170))
    elif kind == "markets":
        d.rectangle([x, y, x + w, y + h], fill=(240, 234, 220))
        pts = [(x + 8, y + 14), (x + w * 0.3, y + 26), (x + w * 0.55, y + 20),
               (x + w * 0.8, y + 44), (x + w - 10, y + h - 16)]
        d.line(pts, fill=(172, 32, 32), width=3, joint="curve")
        d.polygon([(x + w - 22, y + h - 22), (x + w - 6, y + h - 22),
                   (x + w - 14, y + h - 8)], fill=(172, 32, 32))
        d.text((x + 8, y + 6), "DOW −1.1%", font=font(SANS_B, 13),
               fill=(172, 32, 32))
    elif kind == "tank":
        d.rectangle([x, y, x + w, y + h], fill=(214, 196, 160))
        d.rectangle([x, y + h - 24, x + w, y + h], fill=(180, 160, 120))
        for bx in (x + 8, x + w * 0.55):
            d.rectangle([bx, y + 12, bx + w * 0.34, y + h - 24],
                        fill=(150, 140, 120))
            d.rectangle([bx + 6, y + 18, bx + w * 0.34 - 6, y + 26],
                        fill=(90, 100, 110))
        tx = x + w * 0.42
        d.rectangle([tx, y + h - 44, tx + 52, y + h - 24], fill=(70, 78, 60))
        d.rectangle([tx + 12, y + h - 56, tx + 40, y + h - 44],
                    fill=(70, 78, 60))
        d.line([tx + 40, y + h - 52, tx + 66, y + h - 58], fill=(70, 78, 60),
               width=4)
        d.ellipse([tx + 4, y + h - 24, tx + 16, y + h - 14], fill=(40, 40, 40))
        d.ellipse([tx + 36, y + h - 24, tx + 48, y + h - 14], fill=(40, 40, 40))
        _label_bar(d, x, y + h - 14, w, "NUSEIRAT · GAZA")
    elif kind == "climate":
        d.rectangle([x, y, x + w, y + h], fill=(190, 214, 228))
        cx, cy, r = x + w * 0.32, y + h * 0.5, 26
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 140, 190))
        d.ellipse([cx - 14, cy - 16, cx + 2, cy - 2], fill=(90, 170, 90))
        d.ellipse([cx + 2, cy + 4, cx + 16, cy + 16], fill=(90, 170, 90))
        # thermometer
        tx = x + w * 0.72
        d.rectangle([tx, y + 8, tx + 10, y + h - 18], fill=(255, 255, 255),
                    outline=(160, 40, 30), width=1)
        d.rectangle([tx + 2, y + h - 26, tx + 8, y + h - 20],
                    fill=(200, 50, 40))
        d.ellipse([tx - 3, y + h - 20, tx + 13, y + h - 6], fill=(200, 50, 40))
        d.text((x + w - 34, y + 6), "1.5°C", font=font(SANS_B, 10),
               fill=(160, 40, 30))
    elif kind == "protest":
        d.rectangle([x, y, x + w, y + h], fill=(228, 216, 196))
        for i in range(7):
            cx = x + 16 + i * (w - 32) // 6
            d.ellipse([cx - 8, y + h - 34, cx + 8, y + h - 18],
                      fill=(90, 70, 60))
            d.rectangle([cx - 10, y + h - 20, cx + 10, y + h - 10],
                        fill=(60 + i * 8, 60, 70))
        d.rectangle([x + w * 0.2, y + 8, x + w * 0.46, y + 26],
                    fill=(255, 255, 255), outline=(150, 40, 30), width=2)
        d.rectangle([x + w * 0.58, y + 12, x + w * 0.84, y + 28],
                    fill=(255, 255, 255), outline=(30, 60, 120), width=2)
    elif kind == "handshake":
        d.rectangle([x, y, x + w, y + h], fill=(222, 214, 196))
        for i, fl in enumerate((_flag_us,)):
            fl(d, x + 14, y + 10, 30, 19)
        # Venezuela tricolour
        vx = x + w - 44
        for i, c in enumerate([(255, 204, 0), (0, 60, 160), (220, 30, 30)]):
            d.rectangle([vx, y + 10 + i * 19 // 3, vx + 30, y + 10 + (i + 1) * 19 // 3],
                        fill=c)
        # clasped hands: two forearms + clasp
        d.polygon([(x + 18, y + h - 12), (x + w * 0.42, y + h - 34),
                   (x + w * 0.42, y + h - 22), (x + 18, y + h - 2)],
                  fill=(200, 170, 140))
        d.polygon([(x + w - 18, y + h - 12), (x + w * 0.58, y + h - 34),
                   (x + w * 0.58, y + h - 22), (x + w - 18, y + h - 2)],
                  fill=(180, 140, 110))
        d.ellipse([x + w * 0.42, y + h - 40, x + w * 0.58, y + h - 20],
                  fill=(210, 180, 150))
    elif kind == "game":
        d.rectangle([x, y, x + w, y + h], fill=(120, 60, 140))
        d.ellipse([x + w * 0.62, y + 2, x + w * 0.62 + 40, y + 42],
                  fill=(255, 180, 80))
        d.rectangle([x, y + h - 12, x + w, y + h], fill=(40, 30, 60))
        for i, hf in enumerate((0.30, 0.45, 0.22, 0.38)):
            bx = x + 10 + i * (w - 20) // 4
            bh = int(h * hf)
            d.rectangle([bx, y + h - 12 - bh, bx + (w - 20) // 5,
                         y + h - 12], fill=(60, 40, 80))
        for px in (x + 16, x + w - 26):
            d.line([px, y + h - 12, px, y + h - 28], fill=(40, 90, 50),
                   width=3)
            for ang in range(-60, 61, 30):
                ex = px + 12 * math.cos(math.radians(ang - 90))
                ey = y + h - 28 + 10 * math.sin(math.radians(ang - 90))
                d.line([px, y + h - 28, ex, ey], fill=(40, 120, 60), width=2)
        _label_bar(d, x, y + h - 14, w, "LEONIDA · VICE CITY")
    elif kind == "chip":
        d.rectangle([x, y, x + w, y + h], fill=(24, 30, 44))
        cx, cy = x + w // 2, y + h // 2
        for i in range(4):
            d.line([x + 8, y + 10 + i * 12, cx - 20, y + 10 + i * 12],
                   fill=(70, 130, 90), width=1)
            d.line([cx + 20, y + 10 + i * 12, x + w - 8, y + 10 + i * 12],
                   fill=(70, 130, 90), width=1)
        d.rectangle([cx - 20, cy - 18, cx + 20, cy + 18], fill=(30, 90, 60),
                    outline=(120, 200, 140), width=2)
        d.rectangle([cx - 10, cy - 8, cx + 10, cy + 8], fill=(20, 60, 40))
        d.text((cx - 9, cy - 6), "AI", font=font(SANS_B, 11),
               fill=(140, 230, 160))
    elif kind == "ship":
        d.rectangle([x, y, x + w, y + h], fill=(168, 198, 220))
        d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(52, 96, 140))
        # tanker hull + containers + bridge tower
        d.rectangle([x + 10, y + h * 0.52, x + w - 10, y + h * 0.72],
                    fill=(40, 40, 48))
        for i, c in enumerate([(200, 60, 40), (30, 90, 140), (220, 160, 40)]):
            d.rectangle([x + 18 + i * 34, y + h * 0.40,
                         x + 46 + i * 34, y + h * 0.52], fill=c)
        d.rectangle([x + w - 34, y + h * 0.30, x + w - 14, y + h * 0.52],
                    fill=(240, 234, 220))
        # fire + smoke from the struck tanker
        d.ellipse([x + w * 0.30, y + 8, x + w * 0.30 + 26, y + 30],
                  fill=(255, 140, 0))
        d.ellipse([x + w * 0.30 + 8, y + 2, x + w * 0.30 + 30, y + 20],
                  fill=(255, 200, 60))
        for sx, sy, r in [(0.42, 0.10, 7), (0.52, 0.05, 9), (0.62, 0.12, 6)]:
            d.ellipse([x + sx * w - r, y + sy * h - r, x + sx * w + r,
                       y + sy * h + r], fill=(120, 120, 120))
        _label_bar(d, x, y + h - 14, w, "STRAIT OF HORMUZ")
    elif kind == "vote":
        d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
        # capitol dome, sized to the box height
        cx, cy = x + w * 0.38, y + h * 0.72
        r = max(12, int(h * 0.32))
        d.pieslice([cx - r, cy - r, cx + r, cy], 180, 360,
                   fill=(240, 234, 220), outline=(90, 80, 60))
        d.rectangle([cx - r - 6, cy, cx + r + 6, cy + 5],
                    fill=(240, 234, 220), outline=(90, 80, 60))
        for i in range(4):
            px = cx - r + 4 + i * (2 * r - 8) // 3
            d.rectangle([px, cy + 5, px + 5, cy + int(h * 0.16)],
                        fill=(240, 234, 220), outline=(90, 80, 60))
        d.rectangle([cx - r - 6, cy + int(h * 0.16), cx + r + 6,
                     cy + int(h * 0.16) + 4], fill=(90, 80, 60))
        # ballot box with a check
        bx, by = x + w * 0.70, y + h * 0.52
        d.rectangle([bx, by, bx + 34, by + 24], fill=(31, 73, 125))
        d.rectangle([bx - 3, by - 5, bx + 37, by + 2], fill=(31, 73, 125))
        d.line([bx + 7, by + 11, bx + 14, by + 18, bx + 28, by + 4],
               fill=(255, 255, 255), width=3)
        d.text((x + 8, y + 4), "56–44", font=font(SANS_B, 16),
               fill=(31, 73, 125))
    elif kind == "jet":
        d.rectangle([x, y, x + w, y + h], fill=(168, 198, 220))
        for i in range(4):
            d.ellipse([x + 14 + i * 40, y + 8 + (i % 2) * 8,
                       x + 34 + i * 40, y + 22 + (i % 2) * 8],
                      fill=(255, 255, 255))
        # fighter jet silhouette + contrail
        jx, jy = x + w * 0.30, y + h * 0.45
        d.polygon([(jx, jy), (jx + 70, jy - 6), (jx + 84, jy),
                   (jx + 70, jy + 6), (jx + 30, jy + 8), (jx + 18, jy + 18),
                   (jx + 6, jy + 8)], fill=(60, 60, 70))
        d.line([x + 6, jy + 2, jx - 4, jy + 2], fill=(255, 255, 255), width=2)
        d.line([x + 6, jy + 8, jx - 4, jy + 8], fill=(255, 255, 255), width=2)
        # blast below
        bx, by = x + w * 0.72, y + h * 0.62
        for ang in range(0, 360, 45):
            ex = bx + 14 * math.cos(math.radians(ang))
            ey = by + 10 * math.sin(math.radians(ang))
            d.line([bx, by, ex, ey], fill=(255, 140, 0),
                   width=2)
        d.ellipse([bx - 8, by - 8, bx + 8,
                   by + 8], fill=(255, 200, 60))
        _label_bar(d, x, y + h - 14, w, "YEMEN · AIRSTRIKES")


_IMG = None


def scene(d, x, y, w, h, kind, label=""):
    """Draw a scene clipped to its own box (no drawing may spill over)."""
    layer = Image.new("RGB", (w, h), PAPER)
    ld = ImageDraw.Draw(layer)
    _draw_scene(ld, 0, 0, w, h, kind, label)
    _IMG.paste(layer, (x, y))


# ------------------------------------------------------------- world map
MAP_X0, MAP_Y0, MAP_W, MAP_H = 14, 622, 330, 252
MAP_LON0, MAP_LON1, MAP_LAT0, MAP_LAT1 = -170, 190, -58, 84


def _ll(lon, lat):
    mx = MAP_X0 + (lon - MAP_LON0) / (MAP_LON1 - MAP_LON0) * MAP_W
    my = MAP_Y0 + (MAP_LAT1 - lat) / (MAP_LAT1 - MAP_LAT0) * MAP_H
    return (mx, my)


CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-75, 72), (-60, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 25),
     (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-140, 60), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-30, 68), (-40, 76), (-58, 74)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -54), (-73, -40),
     (-72, -20), (-80, -5), (-81, 5)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (51, 10), (48, 0), (40, -10), (35, -20), (28, -33),
     (18, -35), (12, -18), (9, 4), (-8, 5)],
    # Asia (drawn before Europe so Europe sits on top)
    [(30, 70), (45, 68), (60, 69), (75, 73), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (160, 55),
     (155, 50), (142, 45), (135, 43), (127, 40), (120, 38), (115, 32),
     (108, 25), (105, 15), (100, 8), (95, 15), (90, 22), (85, 20),
     (80, 15), (75, 8), (72, 20), (65, 25), (58, 26), (52, 28),
     (48, 30), (44, 30), (40, 35), (35, 36), (30, 40), (30, 50),
     (35, 55), (30, 60)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (12, 55),
     (18, 56), (21, 59), (28, 60), (30, 70), (40, 68), (50, 68), (45, 60),
     (40, 55), (30, 50), (28, 45), (23, 40), (19, 42), (12, 44), (8, 44),
     (3, 42), (-2, 37)],
    # Australia
    [(113, -22), (114, -30), (120, -34), (130, -32), (137, -35), (140, -38),
     (145, -38), (150, -37), (153, -27), (150, -22), (146, -19), (142, -11),
     (136, -12), (132, -11), (126, -14), (122, -17), (118, -20)],
    # UK
    [(-5, 50), (-2, 53), (0, 53), (-3, 58), (-5, 58)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 41), (143, 43),
     (145, 44), (142, 42), (140, 36), (136, 34), (132, 33)],
    # Indonesia (simplified chain)
    [(95, 5), (100, 0), (105, -6), (110, -7), (115, -8), (120, -9),
     (125, -9), (130, -4), (135, -3), (140, -4), (138, -8), (130, -8),
     (120, -10), (110, -8), (100, -2), (95, 2)],
    # New Zealand
    [(167, -45), (172, -41), (175, -38), (178, -37), (174, -40),
     (169, -43)],
]

# Featured-story pin locations (num -> lon, lat).
PINS = {1: (114.1, 22.5), 2: (48.5, 29.3), 3: (85.0, 19.0),
        4: (-77.0, 38.9), 5: (121.0, 14.6), 6: (34.5, 31.5),
        7: (34.0, 45.0), 8: (-121.0, 37.4), 9: (-74.0, 40.7),
        10: (-122.4, 37.8), 11: (-80.2, 25.8), 12: (-74.0, 40.7),
        13: (44.2, 15.4)}
PIN_COLOR = {1: ASIA, 2: MIDDLE_EAST, 3: ASIA, 4: AMERICAS, 5: ASIA,
             6: MIDDLE_EAST, 7: EUROPE, 8: GLOBAL, 9: GLOBAL,
             10: GLOBAL, 11: GLOBAL, 12: AMERICAS, 13: MIDDLE_EAST}
# Pins that would overlap a neighbour are nudged with a leader line.
PIN_OFFSET = {4: (-13, 9), 5: (12, 8), 10: (13, 9), 12: (12, -10)}

# ------------------------------------------------------------- layout
def render():
    global _IMG
    img = Image.new("RGB", (W, H), PAPER)
    _IMG = img
    d = ImageDraw.Draw(img)
    x0, x1 = 14, 1010

    # Kicker row
    d.text((x0, 8), "THE WORLD'S NEWS IN ONE PICTURE",
           font=font(SANS_B, 11), fill=RED)
    right = "45 STORIES · 6 CONTINENTS · ALL FROM THIS WEDNESDAY"
    d.text((x1 - d.textlength(right, font=font(SANS_B, 11)), 8), right,
           font=font(SANS_B, 11), fill=INK)

    # Masthead
    mast = fit_font(d, "Wednesday 18 November 2026", SERIF, 66, x1 - x0)
    centered(d, W // 2, 24, "Wednesday 18 November 2026", mast, INK)
    d.rectangle([x0, 92, x1, 94], fill=INK)
    d.rectangle([x0, 96, x1, 97], fill=INK)

    # Timeline strip
    d.rectangle([x0, 102, 78, 130], fill=RED)
    d.text((x0 + 5, 104), "THE DAY", font=font(SANS_B, 9),
           fill=(255, 255, 255))
    d.text((x0 + 5, 115), "IN UTC", font=font(SANS_B, 9),
           fill=(255, 255, 255))
    col_w = (x1 - 84) / 6
    for i, (t, cap) in enumerate(TIMELINE):
        cx = 84 + i * col_w
        d.text((cx + 4, 103), t, font=font(SANS_B, 10), fill=RED)
        draw_wrapped(d, cx + 4, 116,
                     wrap(d, cap, font(SANS, 9), col_w - 8),
                     font(SANS, 9), BODY, 11)
    d.rectangle([x0, 140, x1, 141], fill=INK)

    # ---- 3 lead stories
    lead_w, lead_gap = 326, 9
    for i, (num, region, tag, head, summ, label, kind, lonlat) in enumerate(LEADS):
        lon, lat = lonlat
        lx = x0 + i * (lead_w + lead_gap)
        scene(d, lx, 146, lead_w, 102, kind)
        num_dot(d, lx + 8, 256, num, region, r=8)
        d.text((lx + 20, 250), tag, font=font(SANS_B, 9), fill=region)
        lw = d.textlength(label, font=font(SANS_B, 8))
        d.text((lx + lead_w - lw, 251), label, font=font(SANS_B, 8),
               fill=(110, 105, 95))
        draw_wrapped(d, lx, 266,
                     wrap(d, head, font(SERIF, 16), lead_w)[:3],
                     font(SERIF, 16), INK, 19)
        draw_wrapped(d, lx, 325,
                     wrap(d, summ, font(SANS, 10), lead_w)[:2],
                     font(SANS, 10), BODY, 12)
    d.rectangle([x0, 352, x1, 353], fill=INK)

    # ---- 10 medium stories (5 cols x 2 rows)
    med_w, med_gap, row_h = 193, 8, 118
    for i, (num, region, tag, head, summ, src, kind) in enumerate(MEDIUM):
        col, row = i % 5, i // 5
        mx = x0 + col * (med_w + med_gap)
        my = 358 + row * row_h
        scene(d, mx, my, med_w, 48, kind)
        num_dot(d, mx + 8, my + 58, num, region, r=7)
        d.text((mx + 18, my + 53), tag, font=font(SANS_B, 8), fill=region)
        draw_wrapped(d, mx, my + 65,
                     wrap(d, head, font(SERIF, 12), med_w)[:2],
                     font(SERIF, 12), INK, 13)
        draw_wrapped(d, mx, my + 91,
                     wrap(d, summ, font(SANS, 9), med_w)[:2],
                     font(SANS, 9), BODY, 11)
    d.rectangle([x0, 598, x1, 599], fill=INK)

    # ---- bottom: map (left) + numbered list (right)
    d.text((x0, 604), "WHERE IT HAPPENED", font=font(SANS_B, 11), fill=RED)
    d.text((356, 604), "ALSO ON WEDNESDAY 18 NOVEMBER",
           font=font(SANS_B, 11), fill=RED)
    # ocean + continents
    d.rectangle([MAP_X0, MAP_Y0, MAP_X0 + MAP_W, MAP_Y0 + MAP_H],
                fill=(196, 216, 228))
    for poly in CONTINENTS:
        d.polygon([_ll(lon, lat) for lon, lat in poly],
                  fill=(238, 228, 202), outline=(190, 178, 150))
    for n, (lon, lat) in PINS.items():
        px, py = _ll(lon, lat)
        dx, dy = PIN_OFFSET.get(n, (0, 0))
        if dx or dy:
            d.line([px, py, px + dx, py + dy], fill=(90, 85, 75), width=1)
            px, py = px + dx, py + dy
        num_dot(d, px, py, n, PIN_COLOR[n], r=7)
    # legend
    lx = MAP_X0
    ly = MAP_Y0 + MAP_H + 8
    for color, name in [(AMERICAS, "Americas"), (EUROPE, "Europe"),
                        (MIDDLE_EAST, "Middle East"), (ASIA, "Asia"),
                        (AFRICA, "Africa"), (OCEANIA, "Oceania"),
                        (GLOBAL, "Global & space")]:
        d.ellipse([lx, ly, lx + 8, ly + 8], fill=color)
        d.text((lx + 11, ly - 1), name, font=font(SANS, 8), fill=BODY)
        lx += 12 + d.textlength(name, font=font(SANS, 8)) + 8
    # numbered list, two columns
    list_font = font(SANS, 9)
    for ci in range(2):
        cx = 356 + ci * 332
        cy = 624
        for num, region, text in LIST_ITEMS[ci * 16:(ci + 1) * 16]:
            lines = wrap(d, text, list_font, 322 - 18)
            num_dot(d, cx + 7, cy + 6, num, region, r=6)
            draw_wrapped(d, cx + 18, cy, lines, list_font, BODY, 12)
            cy += max(14, len(lines) * 12 + 3)

    # ---- date check
    d.rectangle([x0, 926, x1, 964], outline=RED, width=2)
    d.rectangle([x0, 926, x0 + 92, 964], fill=RED)
    d.text((x0 + 8, 934), "DATE CHECK", font=font(SANS_B, 11),
           fill=(255, 255, 255))
    d.text((x0 + 8, 948), "LEFT OUT", font=font(SANS_B, 8),
           fill=(255, 255, 255))
    draw_wrapped(d, x0 + 100, 930,
                 wrap(d, DATE_CHECK, font(SANS, 9), x1 - x0 - 110),
                 font(SANS, 9), BODY, 12)

    # ---- footer
    centered(d, W // 2, 972, FOOTER, font(SANS, 9), BODY)
    centered(d, W // 2, 986, SOURCES, font(SANS, 8), (120, 115, 105))
    return img


if __name__ == "__main__":
    # This script lives in src/; the image belongs at the repo root.
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "entry.png")
    render().save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
