#!/usr/bin/env python3
"""Render the Nov 18, 2026 world-news front page to entry.png (1024x1024, PIL only)."""
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (20, 20, 20)
RED = (138, 31, 31)
GREY = (85, 82, 74)
NAVY = (29, 53, 87)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, leading, fill=INK):
    for ln in wrap(draw, text, fnt, max_w):
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def centered(draw, cx, y, text, fnt, fill=INK):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


def flag_usa(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK, width=2)
    stripe = h / 13
    for i in range(0, 13, 2):
        d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=(178, 34, 52))
    d.rectangle([x, y, x + w * 0.42, y + h * 0.54], fill=(60, 59, 110))


def flag_china(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16), outline=INK, width=2)
    cx, cy, r = x + w * 0.22, y + h * 0.28, h * 0.22
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.4
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=(255, 222, 0))


def flag_russia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK, width=2)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 43, 30))


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
MX = 30  # margin

# ---------- Masthead ----------
f_kick = font(SANS_B, 15)
centered(d, W // 2, 26, "ONE DAY  ·  FIVE STORIES  ·  THE WHOLE WORLD", f_kick, RED)
f_title = font(SERIF_B, 62)
centered(d, W // 2, 50, "THE WORLD TODAY", f_title)
f_date = font(SANS_B, 17)
d.text((MX, 130), "WEDNESDAY", font=f_date, fill=INK)
centered(d, W // 2, 130, "NOVEMBER 18, 2026", f_date, RED)
right = "ONE IMAGE · ONE DAY'S NEWS"
d.text((W - MX - d.textlength(right, font=f_date), 130), right, font=f_date, fill=INK)
d.line([(MX, 160), (W - MX, 160)], fill=INK, width=2)
d.line([(MX, 165), (W - MX, 165)], fill=INK, width=1)

# ---------- Lead story ----------
y = 180
f_tag = font(SANS_B, 14)
tag = "LEAD STORY — CHINA"
tw = d.textlength(tag, font=f_tag)
d.rectangle([MX, y, MX + tw + 18, y + 26], fill=RED)
d.text((MX + 9, y + 4), tag, font=f_tag, fill=(255, 255, 255))
y += 36
f_head = font(SERIF_B, 36)
y = draw_wrapped(d, MX, y, "XI AND PUTIN MEET IN SHENZHEN AS TRUMP LANDS IN CHINA", f_head, 560, 41)
y += 8
f_body = font(SERIF, 18)
y = draw_wrapped(d, MX, y, "The Chinese and Russian leaders hold talks at the APEC summit, a day before the first-ever three-way summit with U.S. President Donald Trump. Xi pledges to stand against trade protectionism; Putin criticises Western sanctions.", f_body, 560, 25)

# Lead art: globe + three flags
ax, ay = 640, 180
d.rectangle([ax, ay, ax + 324, ay + 250], fill=NAVY)
centered(d, ax + 162, ay + 10, "APEC · SHENZHEN", font(SANS_B, 14), (241, 250, 238))
d.ellipse([ax + 62, ay + 42, ax + 262, ay + 196], fill=(69, 123, 157))
d.ellipse([ax + 100, ay + 66, ax + 168, ay + 100], fill=(47, 107, 79))
d.ellipse([ax + 180, ay + 108, ax + 250, ay + 150], fill=(47, 107, 79))
d.ellipse([ax + 140, ay + 158, ax + 200, ay + 186], fill=(47, 107, 79))
flag_china(d, ax + 8, ay + 198, 100, 46)
flag_russia(d, ax + 112, ay + 198, 100, 46)
flag_usa(d, ax + 216, ay + 198, 100, 46)

d.line([(MX, 448), (W - MX, 448)], fill=INK, width=2)

# ---------- Four stories, 2x2 grid ----------
stories = [
    ("1 · IRAN WAR", "IRAN SAYS IT STRUCK U.S. FORCES IN KUWAIT",
     "Iran says its drones hit U.S. positions at Ali Al Salem Air Base; Bahrain says it intercepted attacks. An ADNOC ship was hit in the Strait of Hormuz: 11 injured, one missing.", "gulf"),
    ("2 · THE QUAD", "LEADERS MEET IN MANILA, FIRST TIME IN TWO YEARS",
     "The U.S., Japan, India and Australia hold their first leaders' summit in over two years. Trump announces a major U.S.–Philippines trade deal and wider defence cooperation.", "quad"),
    ("3 · GAZA", "ISRAEL BEGINS NEW OPERATION IN CENTRAL GAZA",
     "Israel's military says it has begun a “concentrated operation” in three areas of central Gaza. Trump's Board of Peace accuses both Israel and Hamas of failing their ceasefire commitments.", "gaza"),
    ("4 · WASHINGTON", "DEMOCRATS TAKE THE SENATE AS PELTOLA WINS ALASKA",
     "Democrat Mary Peltola defeats Republican Sen. Dan Sullivan in Alaska, giving Democrats a projected 56–44 majority in the incoming U.S. Senate — a historic flip.", "senate"),
]


def art_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(35, 48, 56))
    d.ellipse([x + 18, y + 14, x + 74, y + 70], fill=(224, 122, 63))
    d.rectangle([x + 8, y + 58, x + 84, y + 64], fill=INK)
    d.polygon([(x + 150, y + 28), (x + 208, y + 28), (x + 222, y + 40), (x + 208, y + 52), (x + 150, y + 52)], fill=(201, 206, 214))
    d.ellipse([x + 210, y + 34, x + 222, y + 46], fill=RED)
    for xx in [248, 298, 348, 398]:
        d.arc([x + xx, y + 48, x + xx + 36, y + 78], 180, 360, fill=(224, 122, 63), width=4)


def art_quad(d, x, y, w, h):
    # USA
    d.rectangle([x, y + 6, x + 100, y + 70], fill=(255, 255, 255), outline=INK, width=2)
    sh = 64 / 13
    for i in range(0, 13, 2):
        d.rectangle([x, y + 6 + i * sh, x + 100, y + 6 + (i + 1) * sh], fill=(178, 34, 52))
    d.rectangle([x, y + 6, x + 42, y + 40], fill=(60, 59, 110))
    # Japan
    d.rectangle([x + 118, y + 6, x + 218, y + 70], fill=(255, 255, 255), outline=INK, width=2)
    d.ellipse([x + 148, y + 19, x + 188, y + 59], fill=(188, 0, 45))
    # India
    d.rectangle([x + 236, y + 6, x + 336, y + 70], fill=(255, 255, 255), outline=INK, width=2)
    d.rectangle([x + 236, y + 6, x + 336, y + 27], fill=(255, 153, 51))
    d.rectangle([x + 236, y + 49, x + 336, y + 70], fill=(19, 136, 8))
    d.ellipse([x + 275, y + 27, x + 297, y + 49], outline=(0, 0, 128), width=2)
    # Australia
    d.rectangle([x + 354, y + 6, x + 454, y + 70], fill=(0, 36, 125), outline=INK, width=2)
    for sx, sy in [(368, 18), (430, 22), (414, 52)]:
        star(d, x + sx, y + sy, 11, (255, 255, 255))


def art_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 220, 195))
    for bx, by, bw, bh in [(16, 30, 34, 54), (58, 44, 30, 40), (96, 22, 36, 62), (146, 52, 30, 32), (184, 34, 34, 50), (226, 48, 28, 36)]:
        d.rectangle([x + bx, y + by, x + bx + bw, y + by + bh], fill=(122, 106, 82))
    d.polygon([(x + 296, y + 16), (x + 326, y + 44), (x + 326, y + 84), (x + 296, y + 84)], fill=RED)
    d.rectangle([x + 326, y + 44, x + 436, y + 84], fill=(201, 184, 150))
    d.line([(x + 326, y + 44), (x + 436, y + 44)], fill=RED, width=3)
    d.text((x + 381, y + 14), "CENTRAL GAZA", font=font(SANS_B, 12), fill=INK, anchor="ma")


def art_senate(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.polygon([(x + 56, y + 72), (x + 56, y + 48), (x + 60, y + 36), (x + 80, y + 26), (x + 88, y + 18), (x + 96, y + 26), (x + 116, y + 36), (x + 120, y + 48), (x + 120, y + 72)], fill=(241, 250, 238))
    d.rectangle([x + 52, y + 72, x + 124, y + 78], fill=(241, 250, 238))
    d.ellipse([x + 82, y + 48, x + 94, y + 60], fill=NAVY)
    d.rectangle([x + 156, y + 22, x + 286, y + 66], fill=(241, 250, 238))
    d.text((x + 221, y + 44), "56 – 44", font=font(SANS_B, 26), fill=NAVY, anchor="mm")
    star(d, x + 322, y + 44, 16, (255, 209, 102))
    d.text((x + 386, y + 36), "SENATE", font=font(SANS_B, 15), fill=(241, 250, 238))


ART = {"gulf": art_gulf, "quad": art_quad, "gaza": art_gaza, "senate": art_senate}

f_tag2 = font(SANS_B, 13)
f_sh = font(SERIF_B, 21)
f_sp = font(SERIF, 15)
col_w = 460
positions = [(MX, 464), (MX + col_w + 26, 464), (MX, 700), (MX + col_w + 26, 700)]
for (tag, head, body, kind), (sx, sy) in zip(stories, positions):
    ART[kind](d, sx, sy, col_w, 84)
    ty = sy + 94
    d.text((sx, ty), tag, font=f_tag2, fill=RED)
    hy = ty + 20
    hy = draw_wrapped(d, sx, hy, head, f_sh, col_w, 25)
    by = hy + 5
    draw_wrapped(d, sx, by, body, f_sp, col_w, 18)

# ---------- Footer ----------
fy = 946
d.line([(MX, fy), (W - MX, fy)], fill=INK, width=2)
d.line([(MX, fy + 5), (W - MX, fy + 5)], fill=INK, width=1)
f_also = font(SANS, 14)
draw_wrapped(d, MX, fy + 12, "ALSO TODAY:  Cyclone Akvan strengthens in the Bay of Bengal, bearing down on India's east coast  ·  Grand Theft Auto VI launches at midnight, 13 years after the last one  ·  Britain sanctions firms linked to West Bank settlements  ·  Magnitude 6 earthquake strikes Papua New Guinea", f_also, W - 2 * MX, 18)

img.save("entry.png", optimize=True)
print("saved entry.png", img.size)
