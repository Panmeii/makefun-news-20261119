#!/usr/bin/env python3
"""Draw the 19 November 2026 world-news front page as one 1024x1024 PNG.

Refresh edition: a dense single-page infographic holding forty stories
that happened, or were first reported, on Thursday 19 November 2026 --
three illustrated lead stories, nine medium panels, a pinned world map,
an around-the-clock dateline strip, four stat boxes, a date-check box
and twenty-eight one-line briefs. Drawn entirely with PIL primitives
(flat shapes only, no photographs, no likenesses of real people) and
set in Liberation Sans / Serif.

Every story was checked against at least one dated news source from
19-20 Nov 2026 before it was allowed on the page; the source list is
printed in the footer of the image itself.
"""

from PIL import Image, ImageDraw, ImageFont

W = 1024
M = 16                       # page margin
CW = W - 2 * M               # content width = 992
PAPER = (246, 242, 233)
CARD = (255, 255, 255)
INK = (23, 25, 31)
MUTE = (94, 98, 108)
FAINT = (202, 197, 185)
RED = (176, 30, 36)
DARK = (30, 33, 43)

SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

# region colours
REG = {
    "ASIA": (14, 120, 114),
    "MIDDLE EAST": (214, 108, 28),
    "EUROPE": (34, 82, 166),
    "AMERICAS": (44, 138, 68),
    "AFRICA": (120, 70, 158),
    "OCEANIA": (196, 54, 90),
    "GLOBAL": (110, 110, 116),
}


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, fill, max_w, max_lines, lh):
    lines = wrap(d, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and d.textlength(last + "…", font=fnt) > max_w:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=fnt, fill=fill)
    return y + len(lines) * lh


def badge(d, cx, cy, num, colour, r=10, fsize=11):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    t = str(num)
    f = F(SANS_B, fsize)
    bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
           t, font=f, fill=(255, 255, 255))


def panel_head(d, x, y, num, region, field, src, colour, width):
    badge(d, x + 10, y + 8, num, colour)
    d.text((x + 26, y + 1), f"{region} · {field}", font=F(SANS_B, 10), fill=colour)
    sf = F(SANS_B, 8)
    sw = d.textlength(src, font=sf)
    d.text((x + width - sw - 2, y + 2), src, font=sf, fill=MUTE)


# ------------------------------------------------------------ scene painters
# Each painter fills the art box (x0, y0, x1, y1) with a small flat scene.

def paint_court(d, x0, y0, x1, y1):
    """A courthouse portico with a balance scale: the ICJ judgment."""
    d.rectangle([x0, y0, x1, y1], fill=(208, 220, 234))
    cx = (x0 + x1) // 2
    base = y1 - 6
    # pediment + roof line
    d.polygon([(cx - 88, y0 + 26), (cx + 88, y0 + 26), (cx, y0 + 6)], fill=(240, 238, 230),
              outline=(120, 124, 134))
    d.rectangle([cx - 92, y0 + 28, cx + 92, y0 + 34], fill=(240, 238, 230), outline=(120, 124, 134))
    # columns
    for i in range(5):
        px = cx - 76 + i * 38
        d.rectangle([px, y0 + 36, px + 12, base - 12], fill=(244, 242, 236), outline=(150, 152, 160))
    d.rectangle([cx - 92, base - 12, cx + 92, base - 6], fill=(240, 238, 230), outline=(120, 124, 134))
    d.rectangle([cx - 98, base - 6, cx + 98, base], fill=(226, 224, 216), outline=(120, 124, 134))
    # scales of justice in front
    sx, sy = cx, y0 + 44
    d.line([sx, sy, sx, sy + 26], fill=(120, 84, 20), width=3)
    d.line([sx - 26, sy + 6, sx + 26, sy + 6], fill=(120, 84, 20), width=3)
    for sgn in (-1, 1):
        px = sx + sgn * 26
        d.line([px, sy + 6, px - 8, sy + 20], fill=(120, 84, 20), width=1)
        d.line([px, sy + 6, px + 8, sy + 20], fill=(120, 84, 20), width=1)
        d.pieslice([px - 11, sy + 14, px + 11, sy + 28], 0, 180, fill=(196, 148, 44))


def paint_summit(d, x0, y0, x1, y1):
    """Shenzhen towers behind three flags: China, Russia, United States."""
    d.rectangle([x0, y0, x1, y1], fill=(196, 222, 240))
    # skyline
    towers = [(6, 34, 26), (38, 52, 20), (66, 26, 30), (102, 62, 24), (134, 38, 28),
              (170, 56, 20), (198, 30, 26), (232, 48, 22), (262, 34, 24)]
    for dx, h, wdt in towers:
        d.rectangle([x0 + dx, y1 - h, x0 + dx + wdt, y1], fill=(90, 116, 148))
        for wy in range(y1 - h + 5, y1 - 5, 9):
            d.point((x0 + dx + 5, wy), fill=(230, 238, 200))
            d.point((x0 + dx + wdt - 6, wy), fill=(230, 238, 200))
    d.rectangle([x0, y1 - 4, x1, y1], fill=(70, 96, 128))
    # three flags on poles
    fy = y0 + 12
    for fx in (x0 + 52, x0 + 128, x0 + 204):
        d.line([fx, fy, fx, fy + 44], fill=(60, 60, 66), width=2)
    # China: red field, yellow dots
    d.rectangle([x0 + 52, fy, x0 + 88, fy + 24], fill=(222, 41, 46))
    for dx, dy in ((5, 5), (13, 3), (15, 8), (15, 13), (13, 18)):
        d.ellipse([x0 + 52 + dx, fy + dy, x0 + 55 + dx, fy + dy + 3], fill=(255, 222, 60))
    # Russia: white / blue / red bands
    d.rectangle([x0 + 128, fy, x0 + 164, fy + 8], fill=(245, 245, 245), outline=(170, 170, 170))
    d.rectangle([x0 + 128, fy + 8, x0 + 164, fy + 16], fill=(36, 74, 168))
    d.rectangle([x0 + 128, fy + 16, x0 + 164, fy + 24], fill=(206, 44, 52))
    # USA: stripes + blue canton
    for i in range(6):
        col = (206, 44, 52) if i % 2 == 0 else (245, 245, 245)
        d.rectangle([x0 + 204, fy + i * 4, x0 + 240, fy + i * 4 + 4], fill=col)
    d.rectangle([x0 + 204, fy, x0 + 220, fy + 12], fill=(44, 56, 128))
    for r_ in range(3):
        for c_ in range(3):
            d.point((x0 + 207 + c_ * 5, fy + 3 + r_ * 4), fill=(255, 255, 255))


def paint_ipo(d, x0, y0, x1, y1):
    """A market chart breaking upward: Anthropic's first trading day."""
    d.rectangle([x0, y0, x1, y1], fill=(24, 30, 48))
    for gx in range(x0 + 18, x1, 36):
        d.line([gx, y0 + 4, gx, y1 - 4], fill=(44, 54, 78), width=1)
    for gy in range(y0 + 14, y1, 22):
        d.line([x0 + 4, gy, x1 - 4, gy], fill=(44, 54, 78), width=1)
    base = y1 - 12
    bars = [(14, 26, (90, 160, 120)), (52, 34, (90, 160, 120)), (90, 30, (196, 84, 84)),
            (128, 48, (90, 160, 120)), (166, 58, (90, 160, 120)), (204, 74, (110, 190, 130)),
            (242, 92, (120, 210, 140))]
    for dx, h, col in bars:
        d.rectangle([x0 + dx, base - h, x0 + dx + 24, base], fill=col)
    pts = [(x0 + 26, base - 30), (x0 + 64, base - 38), (x0 + 102, base - 34),
           (x0 + 140, base - 52), (x0 + 178, base - 62), (x0 + 216, base - 78),
           (x0 + 254, base - 96)]
    d.line(pts, fill=(255, 196, 64), width=3)
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 12, ay + 1), (ax - 3, ay + 11)], fill=(255, 196, 64))
    d.text((x0 + 10, y0 + 6), "DEBUT +34%", font=F(SANS_B, 13), fill=(255, 226, 120))


# ------------------------------------------------------------------- content

FEATURES = [
    (1, "ASIA", "JUSTICE", "ICJ · AP · LE MONDE", paint_court,
     "World Court: Myanmar committed genocide against the Rohingya",
     "Judges vote 9–6 that Myanmar's 2017 Rohingya clearance was genocide; "
     "the state must make restitution."),
    (2, "ASIA", "DIPLOMACY", "BBC · REUTERS", paint_summit,
     "Trump, Xi & Putin issue a 'peace declaration' in Shenzhen",
     "Three leaders pledge nuclear-risk dialogue and common positions on "
     "energy and the UN — but no peace deal."),
    (3, "AMERICAS", "MARKETS", "REUTERS · BLOOMBERG", paint_ipo,
     "Anthropic's record $81.3bn IPO lights up Wall Street",
     "980m shares sold at $83 in the largest IPO ever; the AI firm's stock "
     "leaps 34% on its first day."),
]

MEDIUMS = [
    (4, "EUROPE", "DEFENCE", "RUSSELL RECORD · WIRES",
     "Denmark approves Greenland–US Arctic security pact",
     "The Folketing votes 109–0 for the expanded defence arrangement; a final "
     "notification to Washington remains before it takes effect."),
    (5, "MIDDLE EAST", "WAR", "AL JAZEERA · FX",
     "Israel wraps up ground push past Gaza's Yellow Line",
     "The Nuseirat operation ends a day after it began; at least four people are "
     "killed across Gaza on Thursday as the ceasefire frays again."),
    (6, "EUROPE", "WAR", "LE MONDE · BBC",
     "Russian missiles hit three Kyiv bridges; six dead",
     "The EU says it will summon Russia's envoy over embassy damage from the "
     "19 November strikes on the Ukrainian capital."),
    (7, "AMERICAS", "ECONOMY", "WALMART · REUTERS",
     "Walmart posts $188.8bn revenue as value shoppers pile in",
     "Revenue climbs 5.2% and US e-commerce jumps 23%; the retail giant raises "
     "its full-year outlook heading into the holidays."),
    (8, "AMERICAS", "POLITICS", "AP · US SENATE",
     "Senate rejects Iran war-powers resolution, 51–48",
     "The House had passed the measure; three Republicans back it and one "
     "Democrat votes against, but it falls short in the Senate."),
    (9, "EUROPE", "WAR", "MOD · WIRES",
     "UK & Norway fund two Ukrainian naval craft in £100m deal",
     "The joint programme, run through the Maritime Capability Coalition, will "
     "build both vessels in the UK, funded equally by London and Oslo."),
    (10, "ASIA", "STORM", "IMD · RSMC NEW DELHI",
     "Severe Cyclone Akvan bears down on the Odisha coast",
     "Red alert: winds of 90–100 km/h gusting to 110. Landfall is due Friday "
     "noon near Gopalpur; evacuations move along the Andhra–Odisha coast."),
    (11, "EUROPE", "CLIMATE", "LE MONDE · UN NEWS",
     "COP31 outcry as fossil fuels fall out of the draft deal",
     "Negotiators in Antalya face a backlash in the summit's final days after "
     "fossil-fuel language is stripped from the draft text."),
    (12, "AMERICAS", "CULTURE", "ROCKSTAR · REUTERS",
     "GTA VI launches worldwide at midnight, after two delays",
     "Out now on PS5 and Xbox Series X|S at $79.99; day-one sales estimated "
     "at 24.6m copies, $2.36bn (Sensor Tower)."),
]

BRIEFS = [
    (13, "EUROPE", "Serbia elects Aleksandar Cupic speaker of parliament, 140 votes to 97"),
    (14, "ASIA", "Russian bombers return to Vietnam amid regional tensions"),
    (15, "MIDDLE EAST", "Iran widens Gulf attacks on Kuwait & Bahrain as the US blockade holds"),
    (16, "EUROPE", "Ukrainian strikes hammer Russia's fuel supply, Kyiv reports"),
    (17, "AMERICAS", "Trump vents frustration at Vance over his Iran-war criticism"),
    (18, "AMERICAS", "Musk calls his $446m of midterm election spending 'pretty foolish'"),
    (19, "AFRICA", "Ethiopia and Eritrea mass troops along their shared border"),
    (20, "ASIA", "Mongolia's parliament accepts President Khurelsukh's resignation"),
    (21, "ASIA", "Pakistan says two days of raids kill 22 militants in Khyber Pakhtunkhwa"),
    (22, "MIDDLE EAST", "Taiz water crisis: output nearly halves; 800,000 cut off from aid — UNICEF"),
    (23, "MIDDLE EAST", "Baghdad and Kata'ib Hezbollah agree to end the Jurf al-Sakhar standoff"),
    (24, "AMERICAS", "Venezuela signs a military deal with the US, a year after Maduro's removal"),
    (25, "AFRICA", "US consortium wins a huge Kenya mining deal, beating Chinese rivals"),
    (26, "AFRICA", "Dozens missing after a migrant boat sinks off Senegal's coast"),
    (27, "AFRICA", "Survivors of Uganda's deadly landslide take their case to the UN"),
    (28, "EUROPE", "Van Gogh sells for a record $190.4m after a row over its Nazi-era history"),
    (29, "AMERICAS", "Florida pastor found guilty over his role in Haiti president's assassination"),
    (30, "AMERICAS", "Susan Smith denied parole again, 32 years after drowning her two sons"),
    (31, "ASIA", "Indian driver wins a life-changing $1.3m lottery prize"),
    (32, "EUROPE", "France orders internet giants to share revenue with the media"),
    (33, "EUROPE", "French nationals stand trial in Iraq over joining Islamic State"),
    (34, "EUROPE", "Merz hosts Zelensky and the Coalition of the Willing in Berlin"),
    (35, "EUROPE", "Putin vows a 'far more painful' reply to the Crimean Bridge strikes"),
    (36, "GLOBAL", "Nearly a quarter of the world's children live in conflict zones — Save the Children"),
    (37, "OCEANIA", "England beat Australia by 97 runs in Hobart to take the ODI series 2–1; Duckett 133"),
    (38, "EUROPE", "Alcaraz beats Medvedev 6–2 6–4 in Turin to reach the ATP Finals semi-finals"),
    (39, "AFRICA", "Harmer's 6/51 spins South Africa past Bangladesh; Proteas top the Test table"),
    (40, "EUROPE", "Women's Champions League: Chelsea edge PSG 1–0, Barcelona hit six, Lyon win at Arsenal"),
]

REGION_STRIP = [("EUROPE", 13), ("ASIA", 7), ("AMERICAS", 9), ("MIDDLE EAST", 4),
                ("AFRICA", 5), ("OCEANIA", 1), ("GLOBAL", 1)]

CLOCK = [
    ("SHENZHEN", "Three leaders, one declaration"),
    ("THE HAGUE", "Genocide judgment on Myanmar"),
    ("KYIV", "Bridges hit in a missile barrage"),
    ("NEW YORK", "Anthropic's $81bn debut"),
    ("ANTALYA", "COP31 draft drops fossil fuels"),
    ("HOBART", "England seal the ODI series"),
]

STATS = [
    ("9–6", "the ICJ vote finding Myanmar responsible for genocide"),
    ("$81.3bn", "raised in Anthropic's record IPO — 980m shares at $83"),
    ("24.6m", "estimated GTA VI copies sold on day one (Sensor Tower)"),
    ("110", "km/h gusts as Cyclone Akvan closes on Odisha (IMD)"),
]

PINS = [
    (1, 98.5, 24.5), (2, 114.1, 22.5), (3, -66.0, 45.0), (4, 12.6, 55.7),
    (5, 34.3, 31.4), (6, 30.5, 50.4), (7, -94.2, 36.4), (8, -77.0, 38.9),
    (9, -0.1, 51.5), (10, 87.5, 15.5), (11, 30.7, 36.9), (12, -80.2, 25.8),
]

# coarse continent outlines, (lon, lat) — stylised, drawn for this page
LAND = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-80, 73),
     (-75, 62), (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 38), (-76, 35),
     (-80, 32), (-80, 26), (-84, 22), (-90, 20), (-95, 18), (-97, 16), (-94, 17),
     (-90, 14), (-83, 9), (-79, 9), (-83, 10), (-90, 13), (-95, 16), (-105, 20),
     (-110, 23), (-114, 28), (-120, 33), (-124, 40), (-124, 47), (-130, 55),
     (-150, 60), (-165, 60)],
    [(-79, 9), (-75, 10), (-70, 12), (-62, 10), (-55, 6), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -26), (-55, -32), (-62, -38), (-65, -45),
     (-68, -52), (-72, -54), (-74, -48), (-73, -40), (-72, -30), (-70, -20),
     (-75, -15), (-79, -8), (-80, -4), (-77, 0), (-80, 3)],
    [(-17, 15), (-10, 29), (-6, 33), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (48, 11), (51, 10), (44, 0), (40, -8), (38, -18),
     (35, -24), (32, -29), (25, -34), (18, -33), (15, -27), (13, -18), (12, -10),
     (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 52), (5, 53), (8, 55), (8, 57),
     (18, 56), (21, 60), (18, 65), (25, 71), (40, 68), (60, 69), (80, 73),
     (100, 77), (120, 73), (140, 72), (160, 70), (178, 66), (178, 62), (162, 60),
     (158, 52), (142, 50), (140, 40), (135, 35), (129, 33), (122, 31), (120, 25),
     (110, 20), (108, 12), (103, 6), (100, 8), (97, 16), (92, 16), (90, 22),
     (86, 20), (80, 15), (77, 8), (72, 20), (66, 25), (57, 26), (50, 24),
     (48, 28), (52, 25), (55, 24), (58, 22), (55, 17), (43, 12), (42, 15),
     (38, 20), (34, 28), (36, 36), (30, 36), (26, 38), (22, 37), (19, 40),
     (15, 38), (12, 44), (10, 44), (3, 43), (0, 39), (-2, 37)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -9), (125, -10),
     (131, -3), (136, -2), (141, -3), (141, -8), (136, -7), (130, -4), (125, -1),
     (120, 1), (115, 3), (109, 1), (102, 3), (97, 5)],
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44), (140, 42),
     (138, 38), (135, 34), (131, 32)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 54), (1, 51)],
    [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -36), (140, -38), (145, -38), (150, -37),
     (153, -31), (153, -27), (151, -24), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -11), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    [(167, -45), (170, -43), (172, -41), (174, -39), (176, -37), (174, -41),
     (171, -44), (168, -46)],
]


# --------------------------------------------------------------------- layout

def main():
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)

    # kicker
    d.text((M, 8), "THE DAY IN WORLD NEWS", font=F(SANS_B, 11), fill=MUTE)
    kr = "EVERY STORY FIRST REPORTED ON THE DAY · ANY TIME ZONE"
    d.text((W - M - d.textlength(kr, font=F(SANS_B, 11)), 8), kr, font=F(SANS_B, 11), fill=MUTE)

    # masthead
    d.rectangle([M, 26, M + 64, 90], fill=RED)
    d.text((M + 32 - d.textlength("NOV", font=F(SANS_B, 11)) / 2, 31), "NOV",
           font=F(SANS_B, 11), fill=(255, 255, 255))
    d.text((M + 32 - d.textlength("19", font=F(SANS_B, 30)) / 2, 44), "19",
           font=F(SANS_B, 30), fill=(255, 255, 255))
    d.text((M + 32 - d.textlength("THU", font=F(SANS_B, 11)) / 2, 76), "THU",
           font=F(SANS_B, 11), fill=(255, 255, 255))
    d.text((M + 78, 28), "Thursday 19 November 2026", font=F(SERIF_B, 43), fill=INK)
    d.text((M + 80, 76), "40 STORIES · 7 REGIONS · ONE FRONT PAGE",
           font=F(SANS_B, 13), fill=RED)
    strap = "SUMMED UP IN A SINGLE IMAGE"
    d.text((W - M - d.textlength(strap, font=F(SANS_B, 11)), 78), strap,
           font=F(SANS_B, 11), fill=MUTE)
    d.line([M, 96, W - M, 96], fill=INK, width=3)

    # region strip
    seg_w = CW / len(REGION_STRIP)
    for i, (name, count) in enumerate(REGION_STRIP):
        x0 = M + i * seg_w
        d.rectangle([x0 + 1, 102, x0 + seg_w - 1, 124], fill=REG[name])
        label = f"{name} · {count}"
        f = F(SANS_B, 11)
        d.text((x0 + (seg_w - d.textlength(label, font=f)) / 2, 107), label,
               font=f, fill=(255, 255, 255))

    # around-the-clock dateline strip
    d.line([M, 130, W - M, 130], fill=FAINT, width=1)
    d.text((M, 136), "AROUND", font=F(SANS_B, 10), fill=INK)
    d.text((M, 149), "THE CLOCK", font=F(SANS_B, 10), fill=INK)
    tx = M + 76
    tw = (W - M - tx) / len(CLOCK)
    for i, (city, text) in enumerate(CLOCK):
        x0 = tx + i * tw
        d.text((x0, 134), city, font=F(SANS_B, 12), fill=RED)
        draw_wrapped(d, x0, 150, text, F(SANS_R, 9), MUTE, tw - 8, 2, 11)
    d.line([M, 174, W - M, 174], fill=FAINT, width=1)

    pw = (CW - 2 * 12) // 3

    # lead features
    fy, fh = 182, 176
    for i, (num, region, field, src, painter, head, det) in enumerate(FEATURES):
        x = M + i * (pw + 12)
        col = REG[region]
        d.rectangle([x, fy, x + pw, fy + fh], fill=CARD, outline=FAINT, width=1)
        d.rectangle([x, fy, x + pw, fy + 5], fill=col)
        painter(d, x + 8, fy + 10, x + pw - 8, fy + 84)
        panel_head(d, x + 8, fy + 90, num, region, field, src, col, pw - 16)
        draw_wrapped(d, x + 10, fy + 112, head, F(SANS_B, 15), INK, pw - 20, 2, 18)
        draw_wrapped(d, x + 10, fy + 148, det, F(SANS_R, 10), MUTE, pw - 20, 2, 12)

    # medium panels, 3 x 3
    my = fy + fh + 8
    mh, mgap = 80, 6
    for i, (num, region, field, src, head, det) in enumerate(MEDIUMS):
        col_i, row_i = i % 3, i // 3
        x = M + col_i * (pw + 12)
        y = my + row_i * (mh + mgap)
        col = REG[region]
        d.rectangle([x, y, x + pw, y + mh], fill=CARD, outline=FAINT, width=1)
        d.rectangle([x, y, x + 5, y + mh], fill=col)
        panel_head(d, x + 10, y + 6, num, region, field, src, col, pw - 20)
        draw_wrapped(d, x + 12, y + 24, head, F(SANS_B, 13), INK, pw - 24, 2, 15)
        draw_wrapped(d, x + 12, y + 54, det, F(SANS_R, 9), MUTE, pw - 24, 2, 11)

    # map + stats + date check
    by = my + 3 * mh + 2 * mgap + 8
    bh = 180
    map_w = 548
    d.rectangle([M, by, M + map_w, by + bh], fill=CARD, outline=FAINT, width=1)
    d.text((M + 10, by + 7), "WHERE IT HAPPENED", font=F(SANS_B, 10), fill=INK)
    note = "PINS MATCH THE STORY NUMBERS"
    d.text((M + map_w - 10 - d.textlength(note, font=F(SANS_B, 8)), by + 8), note,
           font=F(SANS_B, 8), fill=MUTE)
    mx0, my0 = M + 12, by + 28
    mw, mh2 = map_w - 24, bh - 38
    scale = min(mw / 360.0, mh2 / 136.0)
    ox = mx0 + (mw - 360 * scale) / 2
    oy = my0 + (mh2 - 136 * scale) / 2
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh2], fill=(226, 233, 238))

    def proj(lon, lat):
        return (ox + (lon + 180) * scale, oy + (78 - lat) * scale)

    for poly in LAND:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(216, 208, 182), outline=(168, 158, 132))
    pin_col = {}
    for (num, region, *_rest) in [(f[0], f[1]) for f in FEATURES] + \
            [(m_[0], m_[1]) for m_ in MEDIUMS] + [(b[0], b[1]) for b in BRIEFS]:
        pin_col[num] = REG[region]
    for num, lon, lat in PINS:
        cx, cy = proj(lon, lat)
        badge(d, cx, cy, num, pin_col[num], r=8, fsize=9)

    rx = M + map_w + 12
    rw = W - M - rx
    sw = (rw - 3 * 8) // 4
    for i, (big, label) in enumerate(STATS):
        x = rx + i * (sw + 8)
        d.rectangle([x, by, x + sw, by + 84], fill=DARK)
        bf = F(SANS_B, 21)
        d.text((x + (sw - d.textlength(big, font=bf)) / 2, by + 7), big,
               font=bf, fill=(255, 255, 255))
        lines = wrap(d, label, F(SANS_R, 8), sw - 10)
        for j, ln in enumerate(lines[:4]):
            lf = F(SANS_R, 8)
            d.text((x + (sw - d.textlength(ln, font=lf)) / 2, by + 38 + j * 10),
                   ln, font=lf, fill=(198, 202, 214))
    dy = by + 92
    d.rectangle([rx, dy, rx + rw, by + bh], fill=(252, 244, 224),
                outline=(214, 188, 120), width=1)
    d.text((rx + 10, dy + 6), "DATE CHECK", font=F(SANS_B, 10), fill=(150, 104, 20))
    draw_wrapped(
        d, rx + 10, dy + 22,
        "Held out as Wednesday 18 Nov news: the EU's €45bn Ukraine loan plan and "
        "the Alaska Senate result — both on yesterday's page. Still ahead: Fri "
        "20 Nov — Cyclone Akvan makes landfall near Gopalpur and COP31 closes "
        "in Antalya.",
        F(SANS_R, 9), (90, 74, 40), rw - 20, 6, 11)

    # briefs
    yy = by + bh + 8
    d.text((M, yy), "ALSO ON THURSDAY 19 NOVEMBER", font=F(SANS_B, 12), fill=INK)
    bnote = "BRIEFS 13–40 · ONE LINE EACH"
    d.text((W - M - d.textlength(bnote, font=F(SANS_B, 9)), yy + 2), bnote,
           font=F(SANS_B, 9), fill=MUTE)
    d.line([M, yy + 17, W - M, yy + 17], fill=INK, width=2)
    col_w = (CW - 24) // 2
    bf, bn = F(SANS_R, 10), F(SANS_B, 10)
    for i, (num, region, text) in enumerate(BRIEFS):
        col_i = 0 if i < 14 else 1
        row_i = i if i < 14 else i - 14
        x = M + col_i * (col_w + 24)
        y = yy + 22 + row_i * 12
        col = REG[region]
        ns = f"{num}"
        d.text((x, y), ns, font=bn, fill=col)
        nw = d.textlength(ns, font=bn)
        t = text
        while t and d.textlength(t, font=bf) > col_w - nw - 10:
            t = t[:-1]
        if t != text:
            t = t.rstrip() + "…"
        d.text((x + nw + 6, y), t, font=bf, fill=INK)

    # footer
    fy2 = yy + 22 + 14 * 12 + 6
    d.line([M, fy2, W - M, fy2], fill=FAINT, width=1)
    foot = ("Sources: ICJ · AP · Reuters · BBC · Al Jazeera · Le Monde · IMD · UNICEF · "
            "Rockstar · Sensor Tower — all 40 stories first reported Thu 19 Nov 2026")
    d.text((M, fy2 + 4), foot, font=F(SANS_R, 8), fill=MUTE)

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
