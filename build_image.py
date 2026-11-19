#!/usr/bin/env python3
"""Build entry.png: the world news of Thursday 19 November 2026 in one image.

A flat-design "front page of the day": a dated masthead plus six panels,
each with a simple iconic illustration drawn with PIL shapes, a short
headline and a sublabel. No photos, no depictions of real people.

Stories (all happened or were first reported on 19 Nov 2026):
 1. Trump, Xi & Putin hold their first trilateral meeting at the APEC
    summit in Shenzhen, China.            (Reuters / NYT / Le Monde)
 2. Anthropic begins trading on Nasdaq after the largest IPO on record:
    $81.3bn raised at $83 a share.        (Reuters / TechCrunch / CNN)
 3. NASA's Voyager 1 becomes the first human-made object one light-day
    from Earth, 16 billion miles away.    (Smithsonian / NPR / ScienceAlert)
 4. Grand Theft Auto VI launches worldwide after a 13-year wait.
                                           (BBC / People / Le Monde)
 5. Crimean Bridge attacked for the third time in a week; traffic halted.
                                           (Reuters / BBC / Meduza)
 6. US House Democrats nominate Hakeem Jeffries, on track to become the
    first Black Speaker of the House.     (Reuters / CNN / USA Today)
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (247, 243, 234)
INK = (22, 26, 34)
WHITE = (255, 255, 255)


def font(size, bold=True):
    return ImageFont.truetype(FONT if bold else FONT_REG, size)


def centered(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return draw.textbbox((0, 0), text, font=fnt)[3]


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
def icon_summit(d, x, y, w, h):
    """Three flags on poles over a shared table arc: a three-way summit."""
    pole = (52, 58, 68)
    base = y + h - 14
    for i, col in enumerate([(58, 92, 180), (206, 44, 44), (232, 176, 32)]):
        px = x + 52 + i * ((w - 104) // 2)
        d.line([px, y + 8, px, base], fill=pole, width=7)
        d.rectangle([px, y + 8, px + 62, y + 42], fill=col)
        d.polygon([(px + 62, y + 8), (px + 62, y + 42), (px + 44, y + 25)], fill=col)
    d.arc([x + 30, base - 34, x + w - 30, base + 30], 0, 180, fill=pole, width=8)


def icon_ipo(d, x, y, w, h):
    """Rising bar chart with an arrow and a dollar coin: a record IPO."""
    base = y + h - 16
    cols = [(70, 130, 200), (52, 160, 110), (240, 170, 30), (214, 64, 64)]
    heights = [0.32, 0.5, 0.68, 0.92]
    bw = 56
    for i, (col, fh) in enumerate(zip(cols, heights)):
        bx = x + 26 + i * (bw + 20)
        bh = int((h - 40) * fh)
        d.rectangle([bx, base - bh, bx + bw, base], fill=col)
    d.line([x + 16, base + 4, x + w - 16, base + 4], fill=INK, width=5)
    pts = [(x + 40, base - int((h - 40) * 0.36)),
           (x + 130, base - int((h - 40) * 0.55)),
           (x + 220, base - int((h - 40) * 0.72)),
           (x + w - 66, base - int((h - 40) * 0.97))]
    d.line(pts, fill=(214, 64, 64), width=9, joint="curve")
    ax, ay = pts[-1]
    d.polygon([(ax + 26, ay + 2), (ax - 8, ay - 12), (ax - 2, ay + 22)], fill=(214, 64, 64))
    cx, cy, r = x + w - 58, y + 34, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 197, 66), outline=(176, 128, 20), width=4)
    centered(d, cx, cy - 24, "$", font(44), (120, 84, 8))


def icon_voyager(d, x, y, w, h):
    """A probe with a big dish, a long boom, stars, and distant Earth."""
    star = (255, 255, 255)
    for sx, sy in [(30, 20), (90, 66), (150, 14), (w - 40, 26), (w - 110, 70),
                   (60, 96), (w - 70, 100), (200, 84), (w - 170, 16)]:
        d.ellipse([x + sx - 3, y + sy - 3, x + sx + 3, y + sy + 3], fill=star)
    cx, cy = x + w // 2 - 30, y + h // 2 + 6
    # boom to the golden record / bus
    d.line([cx, cy, cx + 120, cy - 52], fill=(200, 205, 215), width=6)
    d.ellipse([cx + 104, cy - 76, cx + 140, cy - 40], fill=(232, 190, 84))
    # bus
    d.rectangle([cx - 16, cy - 16, cx + 18, cy + 18], fill=(200, 205, 215))
    # dish: big parabola as a filled chord + rim
    d.pieslice([cx - 108, cy - 62, cx - 8, cy + 62], 100, 260, fill=(226, 230, 238))
    d.line([cx - 58, cy, cx - 16, cy], fill=(200, 205, 215), width=5)
    d.ellipse([cx - 62, cy - 4, cx - 54, cy + 4], fill=(120, 128, 140))
    # signal dashes toward a small Earth, bottom left
    ex, ey = x + 28, y + h - 24
    for t in (0.25, 0.5, 0.75):
        sx = ex + (cx - 100 - ex) * t
        sy = ey + (cy + 30 - ey) * t
        d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(140, 200, 255))
    d.ellipse([ex - 15, ey - 15, ex + 15, ey + 15], fill=(70, 130, 220))
    d.pieslice([ex - 15, ey - 15, ex + 15, ey + 15], 200, 320, fill=(70, 180, 110))


def icon_gta(d, x, y, w, h):
    """A game controller beside a palm tree: a long-awaited game launch."""
    # palm: trunk + fronds on the left
    px, py = x + 34, y + h - 6
    d.line([px, py, px + 14, py - 72], fill=(40, 90, 60), width=8)
    top = (px + 14, py - 72)
    for dx, dy in [(-46, -16), (-26, -30), (0, -36), (28, -28), (46, -12)]:
        d.arc([top[0] + min(0, dx), top[1] + min(0, dy) - 6,
               top[0] + max(0, dx) + 8, top[1] + abs(dy) + 26],
              180, 360, fill=(40, 140, 80), width=7)
    # controller body
    bx, by, bw, bh = x + 100, y + 26, w - 116, 72
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=34, fill=(38, 42, 54))
    d.rounded_rectangle([bx + 9, by + 9, bx + bw - 9, by + bh - 9], radius=27,
                        outline=(90, 98, 116), width=3)
    # d-pad
    dx, dy = bx + 50, by + bh // 2
    d.rectangle([dx - 9, dy - 26, dx + 9, dy + 26], fill=(210, 214, 224))
    d.rectangle([dx - 26, dy - 9, dx + 26, dy + 9], fill=(210, 214, 224))
    # buttons
    for i, col in enumerate([(232, 84, 84), (245, 197, 66), (84, 190, 120), (84, 140, 232)]):
        cx = bx + bw - 66 + (i % 2) * 38
        cy = by + bh // 2 - 19 + (i // 2) * 38
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=col)


def icon_bridge(d, x, y, w, h):
    """An arched bridge with a broken middle span over waves."""
    steel = (70, 82, 98)
    deck_y = y + 36
    mid = x + w // 2
    d.line([x + 8, deck_y, mid - 48, deck_y], fill=steel, width=10)
    d.line([mid + 48, deck_y, x + w - 8, deck_y], fill=steel, width=10)
    # end pylons
    d.line([x + 12, deck_y - 18, x + 12, deck_y + 22], fill=steel, width=9)
    d.line([x + w - 12, deck_y - 18, x + w - 12, deck_y + 22], fill=steel, width=9)
    # arch under the intact left half
    d.arc([x + 16, deck_y - 18, mid - 40, deck_y + 32], 0, 180, fill=steel, width=7)
    # fallen span, tilted down into the water
    d.line([mid - 48, deck_y + 3, mid + 28, deck_y + 38], fill=steel, width=10)
    # waves, kept clear of the headline below
    for row, wy in enumerate([deck_y + 48, deck_y + 68]):
        for wx in range(x + 6 + row * 22, x + w - 30, 46):
            d.arc([wx, wy, wx + 34, wy + 13], 0, 180, fill=(70, 130, 200), width=5)


def icon_speaker(d, x, y, w, h):
    """A Capitol-style dome over columns, with a gavel beside it."""
    stone = (96, 104, 120)
    cx = x + w // 2 - 34
    base = y + h - 6
    d.pieslice([cx - 92, y + 16, cx + 92, y + 124], 180, 360, fill=stone)
    d.rectangle([cx - 4, y + 0, cx + 4, y + 20], fill=stone)
    d.ellipse([cx - 8, y + 14, cx + 8, y + 30], fill=stone)
    d.rectangle([cx - 104, y + 70, cx + 104, y + 79], fill=stone)
    for i in range(5):
        px = cx - 86 + i * 43
        d.rectangle([px, y + 79, px + 13, base - 10], fill=stone)
    d.rectangle([cx - 108, base - 10, cx + 108, base], fill=stone)
    # gavel, right side
    gx, gy = x + w - 88, y + h - 58
    d.line([gx, gy, gx + 52, gy - 52], fill=(150, 100, 50), width=10)
    d.rounded_rectangle([gx + 34, gy - 84, gx + 76, gy - 44], radius=8, fill=(120, 78, 38))
    d.rectangle([gx - 16, gy + 12, gx + 62, gy + 20], fill=(120, 78, 38))


ICONS = [icon_summit, icon_ipo, icon_voyager, icon_gta, icon_bridge, icon_speaker]

PANELS = [
    ((222, 235, 250), (30, 78, 150),
     "TRUMP, XI & PUTIN MEET IN CHINA", "APEC SUMMIT · SHENZHEN"),
    ((224, 244, 230), (24, 110, 66),
     "ANTHROPIC IPO IS BIGGEST EVER", "$81BN RAISED · NASDAQ DEBUT"),
    ((16, 22, 46), (240, 200, 90),
     "VOYAGER 1: ONE LIGHT-DAY AWAY", "16 BILLION MILES FROM EARTH"),
    ((252, 232, 244), (176, 42, 110),
     "GTA VI LAUNCHES WORLDWIDE", "AFTER A 13-YEAR WAIT"),
    ((232, 236, 240), (52, 74, 96),
     "CRIMEAN BRIDGE ATTACKED AGAIN", "THIRD ATTACK IN A WEEK"),
    ((238, 232, 218), (122, 88, 30),
     "JEFFRIES NOMINATED FOR SPEAKER", "SET TO BE FIRST BLACK SPEAKER"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.rectangle([0, 0, W, 168], fill=INK)
    centered(d, W // 2, 16, "THE WORLD IN ONE DAY", font(27), (240, 200, 90))
    centered(d, W // 2, 48, "THURSDAY 19 NOVEMBER 2026", font(55), WHITE)
    centered(d, W // 2, 122, "THE DAY'S BIGGEST STORIES — IN ONE PICTURE", font(24), (178, 190, 205))

    # ---- panels: 2 columns x 3 rows
    mx, gap = 22, 14
    pw = (W - 2 * mx - gap) // 2          # 483
    top, bottom = 184, H - 22
    ph = (bottom - top - 2 * gap) // 3    # 260
    for i, (bg, accent, head, sub) in enumerate(PANELS):
        col, row = i % 2, i // 2
        x = mx + col * (pw + gap)
        y = top + row * (ph + gap)
        dark = bg[0] < 60
        d.rounded_rectangle([x, y, x + pw, y + ph], radius=18, fill=bg)
        d.rounded_rectangle([x, y, x + pw, y + ph], radius=18, outline=accent, width=4)
        # icon zone
        ICONS[i](d, x + 56, y + 12, pw - 112, 118)
        # headline (up to 2 lines)
        hf = font(31)
        lines = wrap(d, head, hf, pw - 36)
        ty = y + 140
        for ln in lines:
            centered(d, x + pw // 2, ty, ln, hf, WHITE if dark else INK)
            ty += 38
        # sublabel
        sf = font(22)
        while d.textlength(sub, font=sf) > pw - 30 and sf.size > 14:
            sf = font(sf.size - 1)
        centered(d, x + pw // 2, y + ph - 40, sub, sf, accent)

    img.save("/home/hatch/workspace/makefun/news-image-entry/entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
