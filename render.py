"""Draw entry.png: the world news of Wednesday 25 November 2026 on one page.

Everything is drawn with Pillow primitives and macOS system fonts at 2x, then
downsampled with LANCZOS and quantized, so the output is deterministic.
Facts and sources for every story are in FACTS.md.
"""
import math
from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersampling factor
W, H = 1024, 1024
CHARTER = "/System/Library/Fonts/Supplemental/Charter.ttc"
AVENIR = "/System/Library/Fonts/Avenir Next Condensed.ttc"
HELV = "/System/Library/Fonts/HelveticaNeue.ttc"

PAPER = (247, 243, 234)
INK = (24, 24, 28)
GREY = (96, 96, 104)
RULE = (190, 182, 168)
RED = (178, 34, 34)
NAVY = (28, 52, 92)
STATUS = {"CONFIRMED": (35, 120, 60), "OFFICIAL": (30, 90, 170),
          "REPORTED": (180, 110, 0), "CLAIM": (120, 60, 160)}

_fonts = {}


def font(kind, size):
    path, idx = {"black": (CHARTER, 5), "serif": (CHARTER, 3), "roman": (CHARTER, 0),
                 "italic": (CHARTER, 1), "heavy": (AVENIR, 8), "bold": (AVENIR, 0),
                 "demi": (AVENIR, 2), "med": (AVENIR, 5), "sans": (HELV, 0)}[kind]
    key = (kind, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, round(size * S), index=idx)
    return _fonts[key]


img = Image.new("RGB", (W * S, H * S), PAPER)
d = ImageDraw.Draw(img)
WARN = []


def P(*v):
    return [round(x * S) for x in v]


def rect(x, y, w, h, fill=None, outline=None, width=1, r=0):
    box = P(x, y, x + w, y + h)
    if r:
        d.rounded_rectangle(box, radius=r * S, fill=fill, outline=outline, width=round(width * S))
    else:
        d.rectangle(box, fill=fill, outline=outline, width=round(width * S))


def line(pts, fill=INK, width=1):
    d.line([round(c * S) for p in pts for c in p], fill=fill, width=max(1, round(width * S)))


def poly(pts, fill=None, outline=None):
    d.polygon([(round(a * S), round(b * S)) for a, b in pts], fill=fill, outline=outline)


def ellipse(x, y, w, h, fill=None, outline=None, width=1):
    d.ellipse(P(x, y, x + w, y + h), fill=fill, outline=outline, width=round(width * S))


def tw(s, f):
    return d.textlength(s, font=f) / S


def text(x, y, s, f, fill=INK, anchor="la", maxw=None, tag=""):
    if maxw is not None and tw(s, f) > maxw + 0.5:
        WARN.append(f"overflow {tag or s[:30]!r}: {tw(s, f):.0f} > {maxw}")
    d.text((round(x * S), round(y * S)), s, font=f, fill=fill, anchor=anchor)


def wrap(s, f, maxw):
    out, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if tw(t, f) <= maxw:
            cur = t
        else:
            out.append(cur)
            cur = word
    out.append(cur)
    return out


def para(x, y, s, f, maxw, lh, maxlines, fill=INK, tag=""):
    lines = wrap(s, f, maxw)
    if len(lines) > maxlines:
        WARN.append(f"too many lines ({len(lines)}>{maxlines}) {tag or s[:30]!r}")
    for i, ln in enumerate(lines[:maxlines]):
        text(x, y + i * lh, ln, f, fill)
    return len(lines[:maxlines])


def chip(x, y, s, bg, f=None, fg=(255, 255, 255), pad=3, h=12, anchor_right=False):
    f = f or font("bold", 8.5)
    w = tw(s, f) + 2 * pad
    if anchor_right:
        x -= w
    rect(x, y, w, h, fill=bg, r=2)
    text(x + pad, y + h / 2 + 0.3, s, f, fg, anchor="lm")
    return w


# ---------------------------------------------------------------- stories
# region, field, status; pin = (lat, lon) for the numbered map pins
LEADS = [
    dict(n=1, pic="tariff", fig="14", lab="TRADE PARTNERS", place="USA / WORLD", field="Trade",
         region="N. America", time="by 14:55 UTC", status="OFFICIAL", pin=(38.9, -77.0),
         head="US proposes new tariffs on 14 trading partners",
         dek="The trade representative's office names China, the EU, India and Taiwan over "
             "'excess capacity'; China would face an extra 20%. Duties would start early next year.",
         src="Al Jazeera · Guardian · Reuters"),
    dict(n=2, pic="rocket", fig="00:18", lab="UTC LIFT-OFF", place="CHINA / PAKISTAN", field="Space",
         region="South Asia", time="00:18 UTC", status="CONFIRMED", pin=(40.0, 98.5),
         head="Pakistan's first astronaut reaches Tiangong",
         dek="Shenzhou-24 lifts off from Jiuquan; Muhammad Zeeshan Ali becomes the first "
             "foreign astronaut aboard China's space station, for a stay of 5 to 10 days.",
         src="BBC · Al Jazeera · Reuters"),
    dict(n=3, pic="markets", fig="−6.2%", lab="KOSPI", place="ASIA · WALL ST", field="Markets",
         region="East Asia", time="Asia session · 21:00 UTC", status="CONFIRMED", pin=(37.5, 127.0),
         head="AI doubts shake markets: Kospi falls 6.2%",
         dek="Taiwan's Taiex closes 4.8% lower. In New York the S&P 500 is down as much as "
             "3.2% before closing just 0.3% lower; the Dow ends up 0.3%.",
         src="Al Jazeera · AP"),
]

CARDS = [
    dict(n=4, pic="fire", fig="31", lab="KILLED", place="CAIRO, EGYPT", field="Disaster",
         region="Africa", time="evening", status="CONFIRMED", pin=(30.0, 31.2),
         head="Fuel tanker blaze on Cairo ring road",
         dek="Truck overturns and burns in Warraq, Giza; health ministry counts 31 dead.",
         src="Al Jazeera · BBC · AFP"),
    dict(n=5, pic="gavel", fig="1 of 3", lab="CASES", place="ISRAEL", field="Justice",
         region="Middle East", time="by 19:47", status="CONFIRMED", pin=(31.8, 35.2),
         head="Judges urge dropping Netanyahu bribery case",
         dek="Court doubts the media-favours charge; he calls for the trial to end.",
         src="BBC · Al Jazeera"),
    dict(n=6, pic="sats", fig="1M", lab="ORBITAL MODULES", place="USA", field="Tech",
         region="N. America", time="by 19:13", status="OFFICIAL", pin=(38.9, -77.0),
         head="FCC clears SpaceX data centres in orbit",
         dek="'Starmind' licence covers up to 1,000,000 compute modules in space.",
         src="Al Jazeera · Guardian"),
    dict(n=7, pic="energy", fig="+26%", lab="PRICE CAP", place="UK", field="Energy",
         region="Europe", time="by 00:03", status="OFFICIAL", pin=(51.5, -0.1),
         head="UK energy bills to jump from January",
         dek="Ofgem cap: a typical bill rises from £1,723 to £2,166 a year.",
         src="BBC · Guardian"),
    dict(n=8, pic="garment", fig="+36%", lab="TK 17,000", place="BANGLADESH", field="Labour",
         region="South Asia", time="early hours", status="CONFIRMED", pin=(23.8, 90.4),
         head="Garment pay floor lifted; unions say too low",
         dek="Wage board sets Tk 17,000 a month, up from 12,500; factories shut.",
         src="Daily Star · Al Jazeera · AFP"),
    dict(n=9, pic="treaty", fig="No.1", lab="SECURITY PARTNER", place="SOLOMON IS.", field="Security",
         region="Oceania", time="by 01:51", status="CONFIRMED", pin=(-9.4, 160.0),
         head="Solomon Islands signs Australia treaty",
         dek="PM Wale names Australia its 'primary security partner', curbing China ties.",
         src="Guardian · Al Jazeera · NBC"),
    dict(n=10, pic="grid", fig="5", lab="REGIONS HIT", place="UKRAINE", field="War",
         region="Europe", time="overnight", status="CONFIRMED", pin=(47.8, 35.2),
         head="Russian strikes cut power in five regions",
         dek="At least five killed; Zaporizhzhia and Dnipropetrovsk worst hit.",
         src="Al Jazeera · BBC"),
    dict(n=11, pic="court", fig="2022", lab="REPORT UNLAWFUL", place="SOUTH AFRICA", field="Politics",
         region="Africa", time="by 15:35", status="CONFIRMED", pin=(-33.9, 18.4),
         head="Ramaphosa wins 'Farmgate' court fight",
         dek="High Court voids the panel report that opened the way to impeachment.",
         src="Al Jazeera · BBC"),
    dict(n=12, pic="thermo", fig="6", lab="DAYS ABOVE 2°C", place="GLOBAL", field="Climate",
         region="Global", time="by 14:52", status="REPORTED", pin=None,
         head="Six straight days 2°C above pre-industrial",
         dek="First such run on record, the Guardian learns; peak 2.24°C on Monday.",
         src="Guardian"),
    dict(n=13, pic="strike", fig="~15k", lab="MARCH IN ATHENS", place="GREECE", field="Labour",
         region="Europe", time="all day", status="CONFIRMED", pin=(38.0, 23.7),
         head="Greek general strike over wages",
         dek="Ferries, metro and flights disrupted; police count ~15,000 in Athens.",
         src="Reuters · AFP"),
]

BRIEFS = [
    ("Middle East", "War", "CONFIRMED", "Gaza: Israeli strike kills Hamas security chief and family", "AJ/BBC", (31.5, 34.5)),
    ("Middle East", "War", "CLAIM", "Yemen: Houthis hit Saudi port of Jizan; coalition: minor damage", "AJ", (16.9, 42.6)),
    ("Middle East", "Justice", "REPORTED", "Iraq top court backs federal troops at Kurdish borders", "AJ", (36.2, 44.0)),
    ("N. America", "Environment", "CONFIRMED", "Iowa: US Army blows up ~4,500 kg of lead azide", "AJ/BBC", (41.0, -91.0)),
    ("N. America", "Migration", "CONFIRMED", "Kilmar Abrego Garcia lands in Madrid after leaving US", "AJ/Reuters", (40.4, -3.7)),
    ("N. America", "Tech", "OFFICIAL", "New York bans AI-chatbot toys for five years", "Guardian", (42.7, -73.8)),
    ("Europe", "Business", "CONFIRMED", "Poundland collapses; 10,000+ UK jobs at risk", "Guardian/BBC", (52.5, -1.9)),
    ("Europe", "Business", "REPORTED", "EU and UK fine fragrance cartel over €570m", "AFP", (50.8, 4.4)),
    ("Europe", "Trade", "REPORTED", "EU offers UK new deal on 'Made in Europe' scheme", "BBC", (50.8, 4.4)),
    ("Europe", "War", "REPORTED", "Leaked Rosstat files point to ~500,000 Russian war dead", "BBC Russian", (55.8, 37.6)),
    ("East Asia", "Diplomacy", "CONFIRMED", "North Korea shuts Swiss office in Pyongyang", "AJ/BBC", (39.0, 125.8)),
    ("SE Asia", "Security", "REPORTED", "Cambodia, China start Golden Dragon drills, ~3,000 troops", "AFP", (11.6, 104.9)),
    ("Oceania", "Economy", "OFFICIAL", "Australian inflation hits 4.9% in year to October", "Guardian", (-35.3, 149.1)),
    ("Oceania", "Justice", "CONFIRMED", "Sydney ex-officer guilty of double murder", "Guardian/BBC", (-33.9, 151.2)),
    ("Africa", "Politics", "REPORTED", "Nigeria: Tinubu vows peace at Maiduguri rally", "AJ", (11.8, 13.2)),
    ("S. America", "Security", "REPORTED", "Ecuador says US 'action plan' set after paused operations", "AJ", (-0.2, -78.5)),
    ("S. America", "Labour", "REPORTED", "Venezuela: police clash with minimum-wage marchers", "AJ", (10.5, -66.9)),
    ("S. America", "Finance", "REPORTED", "Brazil curbs revolving credit-card debt", "Rio Times", (-15.8, -47.9)),
    ("S. America", "Politics", "REPORTED", "Chile's lower house passes 2027 budget, 113–9", "Rio Times", (-33.4, -70.6)),
    ("Global", "Science", "CONFIRMED", "New close-ups of asteroid Dimorphos, 4 years after DART", "Guardian/BBC", None),
    ("Europe", "Sport", "REPORTED", "Chess title: Gukesh–Sindarov game 2 drawn, 1–1", "Guardian", (46.2, 6.1)),
    ("Europe", "Sport", "CONFIRMED", "Champions League: PSG 2–2 Roma; Sporting 2–2 Man Utd", "AJ/Guardian", (48.9, 2.3)),
]

DATE_CHECK = [
    "Huawei convicted in Brooklyn — 24 Nov", "Serbia school shooting — 24 Nov",
    "Cartagena hostage siege began — 24 Nov", "China probes Politburo's Chen Jining — 24 Nov",
    "RSF drone strikes on Damazin — late 24 Nov", "West Java mine flood — 23 Nov",
    "Sinner knee surgery — 24 Nov",
]

UTC = [
    ("00:18", "Shenzhou-24 lifts off with Pakistani astronaut"),
    ("~05:30", "Taiwan's Taiex closes 4.8% down"),
    ("by 14:55", "USTR tariff plan on 14 partners out"),
    ("15:00", "US Army detonates lead azide in Iowa"),
    ("by 18:55", "Tanker fire on Cairo ring road kills 31"),
    ("by 19:13", "FCC approves SpaceX 'Starmind'"),
    ("21:00", "Wall St closes: S&P 500 −0.3%"),
]

NUMBERS = [
    ("14", "partners in new US tariff plan"),
    ("−6.2%", "South Korea's Kospi"),
    ("31", "killed in Cairo tanker fire"),
    ("1M", "orbital compute modules cleared by FCC"),
    ("+26%", "UK energy price cap, Jan"),
    ("4.9%", "Australian inflation, Oct"),
]

ALL = LEADS + CARDS
REGION_ORDER = ["N. America", "S. America", "Europe", "Middle East", "Africa",
                "South Asia", "East Asia", "SE Asia", "Oceania", "Global"]
region_count = {r: 0 for r in REGION_ORDER}
fields = set()
for s in ALL:
    region_count[s["region"]] += 1
    fields.add(s["field"])
for b in BRIEFS:
    region_count[b[0]] += 1
    fields.add(b[1])
N_STORIES = len(ALL) + len(BRIEFS)
N_REGIONS = sum(1 for r in REGION_ORDER if r != "Global" and region_count[r])
N_FIELDS = len(fields)


# ---------------------------------------------------------------- pictures
def sky(x, y, w, h, top, bottom):
    for i in range(int(h * S)):
        t = i / (h * S)
        c = tuple(round(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line([(x * S, y * S + i), ((x + w) * S - 1, y * S + i)], fill=c)


def pic_tariff(x, y, w, h):
    sky(x, y, w, h, (214, 228, 240), (176, 200, 222))
    rect(x, y + h * 0.78, w, h * 0.22, fill=(60, 90, 130))          # sea
    hull_y = y + h * 0.66
    poly([(x + w * 0.08, hull_y), (x + w * 0.92, hull_y), (x + w * 0.84, y + h * 0.84),
          (x + w * 0.14, y + h * 0.84)], fill=(40, 44, 52))
    cols = [(196, 64, 52), (40, 110, 170), (230, 160, 40), (70, 140, 90), (150, 80, 140)]
    cw, ch = w * 0.095, h * 0.11
    for row in range(3):
        for c in range(7 - row):
            cx = x + w * 0.14 + c * cw + row * cw * 0.5
            cy = hull_y - (row + 1) * ch
            col = cols[(c * 3 + row * 2) % 5]
            rect(cx, cy, cw - 1, ch - 1, fill=col)
            for k in range(1, 4):
                line([(cx + k * cw / 4, cy + 1.5), (cx + k * cw / 4, cy + ch - 2.5)],
                     fill=tuple(max(0, v - 45) for v in col), width=0.7)
    # tariff tag
    tx, ty = x + w * 0.70, y + h * 0.08
    poly([(tx, ty + 10), (tx + 12, ty), (tx + 58, ty), (tx + 58, ty + 20), (tx + 12, ty + 20)],
         fill=(250, 246, 236), outline=INK)
    ellipse(tx + 7, ty + 7.5, 5, 5, fill=INK)
    text(tx + 36, ty + 10.5, "+20%", font("heavy", 12), RED, anchor="mm")
    line([(tx + 9.5, ty + 10), (tx - 4, ty + 26)], fill=INK, width=0.8)


def pic_rocket(x, y, w, h):
    sky(x, y, w, h, (12, 18, 46), (44, 58, 110))
    for i in range(40):
        sx = x + (i * 37 % 97) / 97 * w
        sy = y + (i * 53 % 89) / 89 * h * 0.8
        r = 0.6 + (i % 3) * 0.35
        ellipse(sx, sy, r, r, fill=(235, 235, 255))
    # Earth limb
    ellipse(x - w * 0.3, y + h * 0.82, w * 1.6, h * 0.9, fill=(40, 110, 170))
    ellipse(x - w * 0.3, y + h * 0.82, w * 1.6, h * 0.9, outline=(140, 200, 240), width=1.5)
    # station (top right)
    sx, sy = x + w * 0.70, y + h * 0.22
    rect(sx - 2, sy - 4, 26, 8, fill=(210, 210, 220))
    for dx in (-22, 26):
        rect(sx + dx, sy - 11, 18, 22, fill=(40, 70, 140), outline=(200, 210, 230), width=0.6)
        for k in range(1, 4):
            line([(sx + dx, sy - 11 + k * 5.5), (sx + dx + 18, sy - 11 + k * 5.5)],
                 fill=(120, 150, 210), width=0.4)
    rect(sx + 6, sy - 9, 8, 18, fill=(225, 225, 232))
    # rocket rising, tilted
    rx, ry = x + w * 0.50, y + h * 0.22
    body = [(rx, ry), (rx + 7, ry + 10), (rx + 7, ry + 44), (rx - 7, ry + 44), (rx - 7, ry + 10)]
    flame = [(rx - 6, ry + 44), (rx + 6, ry + 44), (rx, ry + 68)]
    poly(flame, fill=(255, 170, 40))
    poly([(rx - 3, ry + 44), (rx + 3, ry + 44), (rx, ry + 58)], fill=(255, 240, 160))
    poly(body, fill=(240, 240, 245), outline=(150, 150, 160))
    poly([(rx - 7, ry + 34), (rx - 13, ry + 46), (rx - 7, ry + 44)], fill=(200, 40, 40))
    poly([(rx + 7, ry + 34), (rx + 13, ry + 46), (rx + 7, ry + 44)], fill=(200, 40, 40))
    rect(rx - 7, ry + 22, 14, 3, fill=(200, 40, 40))
    # dashed path to station
    for k in range(9):
        t0, t1 = k / 9, (k + 0.5) / 9
        p0 = (rx + 10 + (sx - rx - 26) * t0, ry - 4 - (ry - sy - 10) * t0 ** 0.6)
        p1 = (rx + 10 + (sx - rx - 26) * t1, ry - 4 - (ry - sy - 10) * t1 ** 0.6)
        line([p0, p1], fill=(230, 230, 255), width=0.8)


def pic_markets(x, y, w, h):
    rect(x, y, w, h, fill=(24, 28, 36))
    for k in range(1, 5):
        line([(x, y + k * h / 5), (x + w, y + k * h / 5)], fill=(50, 56, 68), width=0.6)
    pts = []
    vals = [0.25, 0.22, 0.28, 0.20, 0.26, 0.30, 0.36, 0.44, 0.50, 0.62, 0.70, 0.78, 0.74, 0.82]
    for i, v in enumerate(vals):
        pts.append((x + 8 + i * (w - 16) / (len(vals) - 1), y + h * v))
    for i, (px, py) in enumerate(pts):          # volume bars
        bh = 6 + (i * 7 % 11)
        rect(px - 2.5, y + h - bh - 2, 5, bh, fill=(80, 60, 66) if i > 5 else (60, 80, 70))
    line(pts, fill=(235, 70, 60), width=2.2)
    ex, ey = pts[-1]
    ellipse(ex - 3, ey - 3, 6, 6, fill=(235, 70, 60))
    poly([(ex - 6, ey + 6), (ex + 6, ey + 6), (ex, ey + 14)], fill=(235, 70, 60))
    text(x + 8, y + 6, "KOSPI  TAIEX  S&P 500", font("bold", 9), (170, 176, 190))


def pic_fire(x, y, w, h):
    sky(x, y, w, h, (30, 24, 34), (90, 50, 40))
    for i in range(5):                                   # smoke
        ellipse(x + w * (0.30 + i * 0.13), y - 4 + (i % 2) * 5, w * 0.22, h * 0.26, fill=(66, 58, 62))
    rect(x, y + h * 0.74, w, h * 0.26, fill=(46, 46, 52))  # ring road
    for k in range(6):
        rect(x + 4 + k * w / 6, y + h * 0.87, w / 12, 1.6, fill=(220, 200, 120))
    # overturned tanker lying on its side, right half
    tx, ty, tw_, th = x + w * 0.42, y + h * 0.50, w * 0.40, h * 0.24
    rect(tx, ty, tw_, th, fill=(176, 176, 182), outline=(70, 70, 76), width=0.8, r=th / 2)
    rect(tx + tw_ - 2, ty + th * 0.05, w * 0.12, th * 0.9, fill=(150, 40, 40), outline=(70, 30, 30), width=0.6)
    for wx in (tx + tw_ * 0.25, tx + tw_ * 0.7):         # wheels pointing up
        ellipse(wx - 4, ty - 7, 8, 8, fill=(30, 30, 30))
    for fx, fh in [(0.40, 0.42), (0.52, 0.60), (0.64, 0.48), (0.76, 0.66), (0.90, 0.40)]:
        cx = x + w * fx
        base = y + h * 0.56
        poly([(cx - 9, base), (cx, base - h * fh), (cx + 9, base)], fill=(240, 120, 30))
        poly([(cx - 5, base), (cx, base - h * fh * 0.6), (cx + 5, base)], fill=(255, 210, 80))


def pic_gavel(x, y, w, h):
    sky(x, y, w, h, (232, 224, 206), (210, 196, 170))
    cx, cy = x + w * 0.5, y + h * 0.62
    rect(cx - w * 0.28, cy + 8, w * 0.56, h * 0.12, fill=(110, 70, 40), r=2)       # block
    rect(cx - w * 0.22, cy + 2, w * 0.44, h * 0.08, fill=(140, 92, 54), r=2)
    # gavel head rotated
    hx, hy = cx + w * 0.02, cy - h * 0.30
    ang = -0.5
    def rot(px, py):
        return (hx + px * math.cos(ang) - py * math.sin(ang), hy + px * math.sin(ang) + py * math.cos(ang))
    poly([rot(-22, -9), rot(22, -9), rot(22, 9), rot(-22, 9)], fill=(120, 76, 44))
    poly([rot(-24, -10), rot(-18, -10), rot(-18, 10), rot(-24, 10)], fill=(200, 160, 60))
    poly([rot(18, -10), rot(24, -10), rot(24, 10), rot(18, 10)], fill=(200, 160, 60))
    poly([rot(-3, 9), rot(3, 9), rot(3, 52), rot(-3, 52)], fill=(140, 92, 54))
    # three files, one crossed out
    for i in range(3):
        fx = x + 8 + i * 14
        rect(fx, y + 8, 11, 15, fill=(250, 248, 240), outline=GREY, width=0.6)
        if i == 0:
            line([(fx - 1, y + 7), (fx + 12, y + 24)], fill=RED, width=1.4)


def pic_sats(x, y, w, h):
    sky(x, y, w, h, (8, 12, 30), (24, 34, 70))
    ellipse(x + w * 0.10, y + h * 0.55, w * 0.80, h * 0.95, fill=(30, 90, 150))
    ellipse(x + w * 0.10, y + h * 0.55, w * 0.80, h * 0.95, outline=(120, 190, 240), width=1)
    poly([(x + w * 0.35, y + h * 0.70), (x + w * 0.5, y + h * 0.62), (x + w * 0.6, y + h * 0.75),
          (x + w * 0.45, y + h * 0.85)], fill=(60, 130, 80))
    for ring in range(3):
        rw, rh = w * (0.95 - ring * 0.12), h * (0.55 - ring * 0.08)
        ex, ey = x + (w - rw) / 2, y + h * 0.42 - rh / 2 + ring * 6
        n = 14 - ring * 3
        for k in range(n):
            a = math.pi * (0.05 + 0.9 * k / (n - 1))
            px = ex + rw / 2 - math.cos(a) * rw / 2
            py = ey + rh / 2 - math.sin(a) * rh / 2
            rect(px - 3, py - 1, 6, 2, fill=(90, 140, 220))
            rect(px - 1, py - 1.5, 2, 3, fill=(230, 230, 240))


def pic_energy(x, y, w, h):
    sky(x, y, w, h, (236, 230, 218), (214, 204, 188))
    cx, cy, r = x + w * 0.52, y + h * 0.80, h * 0.62
    for k in range(5):                     # dial bands green->red
        a0 = 180 + k * 36
        col = [(70, 150, 80), (150, 180, 60), (230, 190, 40), (230, 120, 40), (200, 40, 40)][k]
        d.pieslice(P(cx - r, cy - r, cx + r, cy + r), a0, a0 + 36, fill=col)
    ellipse(cx - r * 0.66, cy - r * 0.66, r * 1.32, r * 1.32, fill=(236, 230, 218))
    a = math.radians(180 + 150)
    line([(cx, cy), (cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9)], fill=INK, width=2.4)
    ellipse(cx - 4, cy - 4, 8, 8, fill=INK)
    # gas flame at left
    fx, fy = x + w * 0.12, y + h * 0.62
    poly([(fx - 7, fy + 12), (fx, fy - 10), (fx + 7, fy + 12)], fill=(40, 110, 220))
    poly([(fx - 3, fy + 12), (fx, fy), (fx + 3, fy + 12)], fill=(160, 210, 255))


def pic_garment(x, y, w, h):
    sky(x, y, w, h, (226, 236, 232), (196, 216, 208))
    cx, cy = x + w * 0.36, y + h * 0.18
    shirt = [(cx - 14, cy), (cx - 34, cy + 14), (cx - 26, cy + 26), (cx - 18, cy + 21), (cx - 18, cy + h * 0.66),
             (cx + 18, cy + h * 0.66), (cx + 18, cy + 21), (cx + 26, cy + 26), (cx + 34, cy + 14), (cx + 14, cy)]
    poly(shirt, fill=(40, 120, 110), outline=(20, 70, 64))
    poly([(cx - 14, cy), (cx, cy + 10), (cx + 14, cy)], fill=(226, 236, 232))
    # banknote stack (taka)
    bx, by = x + w * 0.62, y + h * 0.40
    for k in range(4):
        rect(bx + k * 2, by - k * 4, w * 0.30, h * 0.24, fill=(120, 170, 110), outline=(60, 100, 60), width=0.7)
    ellipse(bx + 6 + w * 0.15 - 6, by - 12 + h * 0.12 - 6, 12, 12, outline=(60, 100, 60), width=0.8)
    # up arrow
    ax = x + w * 0.55
    poly([(ax - 8, y + h * 0.28), (ax, y + h * 0.10), (ax + 8, y + h * 0.28)], fill=RED)
    rect(ax - 2.5, y + h * 0.27, 5, h * 0.14, fill=RED)


def pic_treaty(x, y, w, h):
    sky(x, y, w, h, (220, 232, 240), (190, 210, 226))
    rect(x, y + h * 0.72, w, h * 0.28, fill=(60, 120, 170))
    # document
    dx, dy = x + w * 0.46, y + h * 0.08
    rect(dx, dy, w * 0.40, h * 0.76, fill=(252, 250, 244), outline=GREY, width=0.7)
    for k in range(5):
        rect(dx + 6, dy + 8 + k * 7, w * 0.40 - 12 - (k % 2) * 8, 2, fill=(180, 180, 186))
    line([(dx + 6, dy + h * 0.62), (dx + 22, dy + h * 0.56), (dx + 30, dy + h * 0.64)], fill=NAVY, width=1)
    line([(dx + w * 0.22, dy + h * 0.62), (dx + w * 0.30, dy + h * 0.55), (dx + w * 0.36, dy + h * 0.63)],
         fill=NAVY, width=1)
    ellipse(dx + w * 0.40 - 16, dy + h * 0.66, 12, 12, fill=RED)
    # two small flags (generic: blue field / green field)
    for fx, col in ((x + w * 0.30, (30, 60, 140)), (x + w * 0.90, (40, 130, 80))):
        line([(fx, y + h * 0.18), (fx, y + h * 0.80)], fill=GREY, width=1.2)
        rect(fx, y + h * 0.18, 16, 11, fill=col)


def pic_grid(x, y, w, h):
    sky(x, y, w, h, (20, 22, 34), (52, 50, 70))
    # pylon
    cx, base = x + w * 0.42, y + h * 0.92
    top = y + h * 0.12
    line([(cx - 16, base), (cx, top)], fill=(190, 190, 200), width=1.3)
    line([(cx + 16, base), (cx, top)], fill=(190, 190, 200), width=1.3)
    for k in range(5):
        yy = top + (base - top) * (0.2 + k * 0.17)
        half = 16 * (yy - top) / (base - top)
        line([(cx - half, yy), (cx + half, yy)], fill=(160, 160, 170), width=0.8)
    for yy, arm in ((top + 10, 22), (top + 22, 30)):
        line([(cx - arm, yy), (cx + arm, yy)], fill=(190, 190, 200), width=1.2)
    # dark windows of houses
    for k in range(4):
        hx = x + w * (0.62 + k * 0.09)
        rect(hx, y + h * 0.60 - (k % 2) * 8, w * 0.08, h * 0.32 + (k % 2) * 8, fill=(40, 40, 52))
        rect(hx + 3, y + h * 0.66, 3, 3, fill=(60, 60, 70))
    # lightning bolt with slash
    bx, by = x + w * 0.16, y + h * 0.20
    poly([(bx + 8, by), (bx - 2, by + 22), (bx + 5, by + 22), (bx - 1, by + 40), (bx + 14, by + 16),
          (bx + 7, by + 16), (bx + 13, by)], fill=(250, 210, 60))
    line([(bx - 8, by + 2), (bx + 20, by + 38)], fill=RED, width=2)


def pic_court(x, y, w, h):
    sky(x, y, w, h, (236, 232, 222), (214, 208, 194))
    cx = x + w * 0.5
    poly([(cx - w * 0.38, y + h * 0.30), (cx, y + h * 0.08), (cx + w * 0.38, y + h * 0.30)], fill=(200, 194, 180),
         outline=GREY)
    rect(cx - w * 0.38, y + h * 0.30, w * 0.76, h * 0.06, fill=(206, 200, 186), outline=GREY, width=0.6)
    for k in range(6):
        px = cx - w * 0.33 + k * w * 0.13
        rect(px, y + h * 0.37, w * 0.05, h * 0.44, fill=(226, 222, 210), outline=GREY, width=0.5)
    rect(cx - w * 0.42, y + h * 0.81, w * 0.84, h * 0.07, fill=(196, 190, 176), outline=GREY, width=0.6)
    # stamped paper
    px, py = x + w * 0.70, y + h * 0.48
    rect(px, py, w * 0.24, h * 0.36, fill=(252, 250, 244), outline=GREY, width=0.6)
    line([(px + 2, py + 2), (px + w * 0.24 - 2, py + h * 0.36 - 2)], fill=RED, width=1.4)
    line([(px + w * 0.24 - 2, py + 2), (px + 2, py + h * 0.36 - 2)], fill=RED, width=1.4)


def pic_thermo(x, y, w, h):
    sky(x, y, w, h, (250, 230, 200), (236, 170, 120))
    gx, gy, gr = x + w * 0.40, y + h * 0.52, h * 0.38
    ellipse(gx - gr, gy - gr, 2 * gr, 2 * gr, fill=(70, 130, 190))
    poly([(gx - gr * 0.5, gy - gr * 0.5), (gx, gy - gr * 0.7), (gx + gr * 0.2, gy - gr * 0.1),
          (gx - gr * 0.2, gy + gr * 0.3), (gx - gr * 0.7, gy + gr * 0.1)], fill=(200, 150, 70))
    poly([(gx + gr * 0.3, gy + gr * 0.2), (gx + gr * 0.7, gy + gr * 0.25), (gx + gr * 0.5, gy + gr * 0.7)],
         fill=(200, 150, 70))
    ellipse(gx - gr, gy - gr, 2 * gr, 2 * gr, outline=(40, 70, 110), width=1)
    tx = x + w * 0.80
    rect(tx - 4, y + h * 0.10, 8, h * 0.66, fill=(255, 255, 255), outline=GREY, width=0.7, r=4)
    rect(tx - 2, y + h * 0.20, 4, h * 0.58, fill=RED)
    ellipse(tx - 7, y + h * 0.72, 14, 14, fill=RED)
    for k in range(6):
        line([(tx + 5, y + h * 0.16 + k * 7), (tx + 8, y + h * 0.16 + k * 7)], fill=GREY, width=0.6)


def pic_strike(x, y, w, h):
    sky(x, y, w, h, (214, 226, 240), (236, 236, 236))
    rect(x, y + h * 0.80, w, h * 0.20, fill=(150, 146, 140))
    # crowd silhouettes
    for k in range(13):
        px = x + 4 + k * (w - 8) / 12
        ph = h * (0.26 + (k * 5 % 4) * 0.03)
        ellipse(px - 4, y + h * 0.82 - ph - 8, 8, 8, fill=(50, 54, 66))
        rect(px - 5, y + h * 0.82 - ph, 10, ph, fill=(50, 54, 66), r=3)
    # placards
    for k, (px, col) in enumerate(((0.20, (200, 40, 40)), (0.55, (250, 250, 250)), (0.82, (30, 90, 170)))):
        bx = x + w * px
        line([(bx, y + h * 0.48), (bx, y + h * 0.26)], fill=(90, 70, 50), width=1)
        rect(bx - 14, y + h * 0.08, 28, 18, fill=col, outline=INK, width=0.6)
    # blocked ferry icon
    text(x + w * 0.55, y + h * 0.08 + 9.5, "STRIKE", font("heavy", 8), RED, anchor="mm")


PICS = {"tariff": pic_tariff, "rocket": pic_rocket, "markets": pic_markets, "fire": pic_fire,
        "gavel": pic_gavel, "sats": pic_sats, "energy": pic_energy, "garment": pic_garment,
        "treaty": pic_treaty, "grid": pic_grid, "court": pic_court, "thermo": pic_thermo,
        "strike": pic_strike}


def picture(s, x, y, w, h, big=False):
    global d
    layer = Image.new("RGB", img.size, PAPER)       # draw on a layer, paste only the box: clips spill
    main_d, d = d, ImageDraw.Draw(layer)
    PICS[s["pic"]](x, y, w, h)
    d = main_d
    box = tuple(P(x, y, x + w, y + h))
    img.paste(layer.crop(box), box[:2])
    # key figure, boxed for contrast, bottom-left
    f = font("black", 30 if big else 19)
    fw = tw(s["fig"], f)
    bh = 34 if big else 23
    rect(x + 4, y + h - bh - 4, fw + 10, bh, fill=(255, 255, 255))
    text(x + 9, y + h - 4 - bh / 2 + 1, s["fig"], f, INK, anchor="lm")
    lf = font("heavy", 10 if big else 8.5)
    chip(x + 4 + fw + 10, y + h - 4 - (15 if big else 12), s["lab"], INK, f=lf, h=15 if big else 12)
    # number badge
    ellipse(x + w - 22, y + 4, 18, 18, fill=RED)
    text(x + w - 13, y + 13.5, str(s["n"]), font("heavy", 10.5), (255, 255, 255), anchor="mm")
    rect(x, y, w, h, outline=INK, width=0.8)


def meta_row(s, x, y, w, small=False):
    f = font("demi", 9.5 if not small else 8.5)
    t = f"{s['place']} · {s['field'].upper()}"
    text(x, y, t, f, RED, maxw=w - 70, tag=t)
    chip(x + w, y - 0.5, s["status"], STATUS[s["status"]], anchor_right=True, h=11.5,
         f=font("heavy", 8))


def lead_card(s, x, y, w, h):
    rect(x, y, w, h, fill=(255, 253, 248), outline=RULE, width=0.8)
    pic_h = 100
    picture(s, x + 6, y + 6, w - 12, pic_h, big=True)
    cy = y + pic_h + 12
    meta_row(s, x + 8, cy, w - 16)
    hf = font("serif", 18)
    n = para(x + 8, cy + 14, s["head"], hf, w - 16, 20, 2, tag=s["head"])
    dy = cy + 14 + n * 20 + 3
    para(x + 8, dy, s["dek"], font("roman", 11), w - 16, 13.4, 3, GREY, tag="dek" + str(s["n"]))
    text(x + 8, y + h - 6, "Sources: " + s["src"], font("med", 8.5), GREY, anchor="ls")
    text(x + w - 8, y + h - 6, s["time"], font("med", 8.5), GREY, anchor="rs")


def small_card(s, x, y, w, h):
    rect(x, y, w, h, fill=(255, 253, 248), outline=RULE, width=0.8)
    pic_h = 70
    picture(s, x + 5, y + 5, w - 10, pic_h)
    cy = y + pic_h + 10
    meta_row(s, x + 6, cy, w - 12, small=True)
    hf = font("serif", 13)
    n = para(x + 6, cy + 13, s["head"], hf, w - 12, 14.5, 2, tag=s["head"])
    para(x + 6, cy + 13 + n * 14.5 + 1, s["dek"], font("roman", 9.5), w - 12, 11.2, 2, GREY,
         tag="dek" + str(s["n"]))
    text(x + 6, y + h - 5, s["src"], font("med", 8), GREY, anchor="ls")
    text(x + w - 6, y + h - 5, s["time"], font("med", 8), GREY, anchor="rs")


# ---------------------------------------------------------------- world map
LAND = [
    [(-168, 66), (-156, 71), (-140, 70), (-125, 70), (-95, 72), (-80, 73), (-62, 66), (-56, 52), (-66, 45),
     (-70, 42), (-76, 35), (-81, 31), (-80, 25), (-83, 29), (-90, 29), (-97, 26), (-97, 21), (-92, 18),
     (-88, 15), (-83, 9), (-78, 8), (-86, 12), (-92, 14), (-105, 20), (-110, 24), (-115, 30), (-118, 34),
     (-124, 40), (-124, 48), (-130, 55), (-140, 60), (-152, 58), (-165, 60)],
    [(-55, 60), (-44, 60), (-20, 70), (-20, 80), (-60, 82), (-72, 78), (-58, 70)],
    [(-78, 8), (-72, 12), (-62, 11), (-52, 5), (-35, -6), (-39, -15), (-48, -26), (-58, -38), (-65, -42),
     (-68, -52), (-74, -52), (-72, -40), (-71, -30), (-70, -18), (-76, -14), (-81, -5), (-80, 1)],
    [(-10, 36), (-9, 43), (-2, 44), (-5, 48), (2, 51), (8, 54), (10, 58), (5, 62), (14, 68), (25, 71),
     (40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72), (160, 70), (180, 68), (180, 65),
     (170, 60), (160, 55), (156, 51), (142, 47), (140, 40), (130, 35), (127, 38), (126, 34), (121, 31),
     (122, 25), (115, 22), (108, 21), (106, 17), (109, 12), (105, 9), (100, 13), (103, 1), (98, 8),
     (98, 16), (94, 17), (92, 22), (87, 21), (80, 15), (77, 8), (73, 17), (72, 21), (67, 25), (57, 25),
     (56, 27), (52, 24), (56, 18), (52, 15), (43, 12), (39, 20), (35, 28), (34, 31), (36, 36), (28, 37),
     (26, 40), (23, 36), (20, 40), (15, 38), (12, 44), (8, 44), (3, 43), (-1, 37)],
    [(-17, 21), (-6, 36), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12), (51, 12), (40, -2), (40, -15),
     (35, -25), (28, -33), (18, -35), (12, -17), (13, -5), (9, 4), (-8, 4), (-17, 14)],
    [(114, -22), (122, -17), (130, -12), (137, -12), (142, -11), (146, -19), (153, -26), (150, -37),
     (140, -38), (132, -31), (115, -34)],
    [(-6, 50), (2, 51), (0, 54), (-3, 59), (-6, 57)],
    [(130, 31), (141, 36), (142, 43), (140, 41), (135, 34)],
    [(95, 5), (106, -6), (102, -4)], [(109, 1), (117, 7), (119, 0), (116, -4), (110, -3)],
    [(106, -6), (114, -8), (106, -7.5)], [(131, -1), (141, -3), (150, -10), (141, -9)],
    [(172, -34), (178, -38), (174, -41), (167, -46), (171, -44)], [(44, -25), (50, -15), (49, -12), (44, -16)],
]


def inside(px, py, pg):
    c = False
    j = len(pg) - 1
    for i in range(len(pg)):
        xi, yi = pg[i]
        xj, yj = pg[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def world_map(x, y, w, h):
    rect(x, y, w, h, fill=(232, 238, 242), outline=RULE, width=0.8)
    lat0, lat1 = 78, -50

    def proj(lat, lon):
        return x + (lon + 180) / 360 * w, y + (lat0 - lat) / (lat0 - lat1) * h

    step = 4.2
    yy = y + step / 2
    while yy < y + h - 2:
        xx = x + step / 2
        while xx < x + w - 2:
            lon = (xx - x) / w * 360 - 180
            lat = lat0 - (yy - y) / h * (lat0 - lat1)
            if any(inside(lon, lat, pg) for pg in LAND):
                ellipse(xx - 1.1, yy - 1.1, 2.2, 2.2, fill=(150, 160, 170))
            xx += step
        yy += step
    for b in BRIEFS:
        if b[5]:
            px, py = proj(*b[5])
            ellipse(px - 1.8, py - 1.8, 3.6, 3.6, fill=STATUS[b[2]])
    # numbered pins pushed apart; leader line from true spot to label
    pins = [(s["n"], *proj(*s["pin"])) for s in ALL if s["pin"]]
    pos = {n: [px, py] for n, px, py in pins}
    for _ in range(200):
        for a in pos:
            for b in pos:
                if a >= b:
                    continue
                dx = pos[b][0] - pos[a][0]
                dy = pos[b][1] - pos[a][1]
                dist = math.hypot(dx, dy)
                if dist < 0.5:              # same spot: split along a fixed direction
                    dx, dy, dist = math.cos(a + b), math.sin(a + b), 1.0
                if dist < 15:
                    push = (15 - dist) / 2
                    ux, uy = dx / dist, dy / dist
                    pos[a][0] -= ux * push; pos[a][1] -= uy * push
                    pos[b][0] += ux * push; pos[b][1] += uy * push
        for n in pos:
            pos[n][0] = min(max(pos[n][0], x + 8), x + w - 8)
            pos[n][1] = min(max(pos[n][1], y + 8), y + h - 8)
    for n, px, py in pins:
        qx, qy = pos[n]
        if math.hypot(qx - px, qy - py) > 2:
            line([(px, py), (qx, qy)], fill=INK, width=0.7)
        ellipse(px - 1.6, py - 1.6, 3.2, 3.2, fill=INK)
    for n, px, py in pins:
        qx, qy = pos[n]
        ellipse(qx - 6.5, qy - 6.5, 13, 13, fill=RED, outline=(255, 255, 255), width=0.8)
        text(qx, qy + 0.5, str(n), font("heavy", 8.5), (255, 255, 255), anchor="mm")



# ---------------------------------------------------------------- page
M = 14  # outer margin

# masthead
text(M, 9, "THE WORLD IN ONE PAGE · DAILY NEWS SUMMARY", font("heavy", 10), RED)
text(M, 20, "Wednesday 25 November 2026", font("black", 38), INK, maxw=700)
box_w = 250
rect(W - M - box_w, 12, box_w, 44, fill=INK)
text(W - M - box_w / 2, 26, f"{N_STORIES} STORIES · {N_REGIONS} REGIONS", font("heavy", 15),
     (255, 255, 255), anchor="mm")
text(W - M - box_w / 2, 44, f"+ global · {N_FIELDS} fields · each tagged by status", font("med", 10.5),
     (220, 220, 220), anchor="mm")
line([(M, 66), (W - M, 66)], INK, 1.6)
strap = ("US proposes tariffs on 14 partners  ·  Pakistan's first astronaut docks at Tiangong  ·  "
         "AI jitters hit Asian markets  ·  31 die in Cairo tanker fire")
text(W / 2, 76, strap, font("roman", 12), INK, anchor="mm", maxw=W - 2 * M)
line([(M, 86), (W - M, 86)], INK, 0.6)

# THE DAY IN UTC
ty = 91
text(M, ty, "THE DAY IN UTC", font("heavy", 9.5), RED)
cw = (W - 2 * M - 92) / len(UTC)
for i, (t, s) in enumerate(UTC):
    cx = M + 92 + i * cw
    rect(cx, ty - 3, cw - 3, 36, fill=(255, 253, 248), outline=RULE, width=0.6)
    text(cx + 4, ty, t, font("heavy", 11), NAVY)
    para(cx + 4, ty + 12.5, s, font("med", 8.8), cw - 10, 9.4, 2, tag="utc" + t)
text(M, ty + 12, "~ = approximate", font("med", 8), GREY)

# THE DAY IN NUMBERS
ny = 132
text(M, ny + 2, "THE DAY IN", font("heavy", 9.5), RED)
text(M, ny + 13, "NUMBERS", font("heavy", 9.5), RED)
cw = (W - 2 * M - 92) / len(NUMBERS)
for i, (num, s) in enumerate(NUMBERS):
    cx = M + 92 + i * cw
    rect(cx, ny - 3, cw - 3, 32, fill=(255, 253, 248), outline=RULE, width=0.6)
    nf = font("black", 17)
    text(cx + 5, ny + 12, num, nf, RED, anchor="lm")
    para(cx + 10 + tw(num, nf), ny + 2, s, font("med", 9), cw - 18 - tw(num, nf), 10, 2, tag="num" + num)

# region bar
ry = 167
x0 = M
text(x0, ry, "REGIONS", font("heavy", 9.5), RED)
x0 += 64
for r in REGION_ORDER:
    lab = f"{r} {region_count[r]}"
    wch = chip(x0, ry - 1, lab, NAVY if r != "Global" else GREY, f=font("bold", 9.5), h=13, pad=5)
    x0 += wch + 5
if x0 > W - M:
    WARN.append(f"region bar overflow {x0}")

# leads
ly, lh = 184, 234
lw = (W - 2 * M - 2 * 8) / 3
for i, s in enumerate(LEADS):
    lead_card(s, M + i * (lw + 8), ly, lw, lh)

# cards: two rows of five
cy0, ch = ly + lh + 7, 170
cwid = (W - 2 * M - 4 * 6) / 5
for i, s in enumerate(CARDS):
    r, c = divmod(i, 5)
    small_card(s, M + c * (cwid + 6), cy0 + r * (ch + 6), cwid, ch)

# bottom band: map + briefs
by = cy0 + 2 * ch + 12
mw, mh = 330, 166
text(M, by, "WHERE IT HAPPENED", font("heavy", 9.5), RED)
text(M + 112, by + 1, "numbered pins = cards · dots = briefs · 12 is global", font("med", 8), GREY)
world_map(M, by + 13, mw, mh)

bx = M + mw + 12
text(bx, by, "ALSO ON 25 NOVEMBER", font("heavy", 9.5), RED)
colw = (W - M - bx - 10) / 2
bf = font("sans", 9.6)
of = font("med", 8.3)
per_col = math.ceil(len(BRIEFS) / 2)
for i, (reg, fld, st, t, src, _) in enumerate(BRIEFS):
    col, row = divmod(i, per_col)
    xx = bx + col * (colw + 10)
    yy = by + 9 + row * 14.6
    ellipse(xx, yy + 2.5, 6, 6, fill=STATUS[st])
    srcw = tw(src, of)
    text(xx + 9, yy, t, bf, INK, maxw=colw - 14 - srcw, tag=t)
    text(xx + colw, yy + 1.2, src, of, GREY, anchor="ra")

# date check + legend + sources
dy = by + mh + 19
rect(M, dy, W - 2 * M, 30, fill=(255, 250, 236), outline=RED, width=1)
text(M + 6, dy + 4, "DATE CHECK", font("heavy", 9.5), RED)
text(M + 6, dy + 16, "left out as earlier news:", font("med", 8.3), GREY)
dc = "  ·  ".join(DATE_CHECK)
para(M + 112, dy + 4, dc, font("med", 9.2), W - 2 * M - 120, 11, 2, tag="datecheck")

gy = dy + 40
x0 = M
for k, v in STATUS.items():
    x0 += chip(x0, gy - 6, k, v, f=font("heavy", 8), h=11.5) + 4
    desc = {"CONFIRMED": "2+ outlets", "OFFICIAL": "on-record statement", "REPORTED": "one outlet",
            "CLAIM": "one side's claim"}[k]
    text(x0, gy, desc, font("med", 8.5), GREY, anchor="lm")
    x0 += tw(desc, font("med", 8.5)) + 12
text(W - M, gy, "Sources: Al Jazeera, BBC, Guardian, Reuters, AP, AFP, NBC, Daily Star, Rio Times · times UTC",
     font("med", 8.5), GREY, anchor="rm")

for wmsg in WARN:
    print("WARN", wmsg)

out = img.resize((W, H), Image.LANCZOS).quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE)
out.save("entry.png", optimize=True)
print("wrote entry.png", out.size, "last y", gy)
