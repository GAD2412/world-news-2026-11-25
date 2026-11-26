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


def star(cx, cy, r, fill):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    poly(pts, fill=fill)


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
# Every story: number, dateline city, region, field, status. Sources in FACTS.md.
REGIONS = [  # name, short label, colour
    ("N. America", "N. AMERICA", (38, 70, 150)),
    ("S. America", "S. AMERICA", (196, 92, 40)),
    ("Europe", "EUROPE", (30, 112, 170)),
    ("Middle East", "MIDDLE EAST", (178, 52, 40)),
    ("N. Africa", "N. AFRICA", (150, 104, 44)),
    ("Sub-Sah. Africa", "SUB-SAH. AFRICA", (206, 146, 22)),
    ("South Asia", "S. ASIA", (128, 112, 36)),
    ("East Asia", "E. ASIA", (24, 128, 112)),
    ("SE Asia", "SE ASIA", (84, 142, 58)),
    ("Oceania", "OCEANIA", (92, 80, 160)),
    ("Global", "GLOBAL", (104, 104, 112)),
]
RCOL = {r[0]: r[2] for r in REGIONS}

LEADS = [
    dict(n=1, pic="tariff", fig="14", lab="TRADE PARTNERS", place="WASHINGTON", field="Trade",
         region="N. America", time="by 14:55 UTC", status="OFFICIAL", pin=(38.9, -77.0),
         head="US proposes new tariffs on 14 trading partners",
         dek="USTR targets China, the EU, India and Taiwan over 'excess capacity'; China "
             "faces an extra 20%.",
         why="First big tariff move since February's Supreme Court ruling.",
         src="Al Jazeera · Guardian · Reuters"),
    dict(n=2, pic="markets", fig="−6.2%", lab="KOSPI", place="SEOUL · TAIPEI · TOKYO", field="Markets",
         region="East Asia", time="Asia close · 21:00 UTC", status="CONFIRMED", pin=(37.5, 127.0),
         head="AI doubts sink Asian chip stocks: Kospi −6.2%",
         dek="SK hynix −11.1%, Samsung −9.9%, Taiex −4.8%, Nikkei −2.8%. The S&P 500 fell as much "
             "as 3.2% before closing 0.3% lower.",
         why="Reverses Tuesday's rally on Jensen Huang's return to Nvidia.",
         src="Al Jazeera · AP"),
    dict(n=3, pic="rocket", fig="00:18", lab="UTC LIFT-OFF", place="JIUQUAN, CHINA", field="Space",
         region="South Asia", time="00:18 UTC", status="CONFIRMED", pin=(40.0, 98.5),
         head="Pakistan's first astronaut docks at China's station",
         dek="Shenzhou-24 carries Muhammad Zeeshan Ali, 40, to Tiangong with Tang Hongbo and "
             "Wu Yi; he stays 5 to 10 days.",
         why="Tiangong takes its first foreign astronaut.",
         src="BBC · Al Jazeera · Reuters"),
]

CARDS = [
    dict(n=4, pic="fire", fig="31", lab="KILLED", place="GIZA, EGYPT", field="Disaster",
         region="N. Africa", time="evening", status="CONFIRMED", pin=(30.0, 31.2),
         head="Fuel tanker blaze kills 31 on Cairo ring road",
         dek="Truck overturns and burns in Warraq; 21 injured.",
         src="Al Jazeera · BBC · AFP"),
    dict(n=5, pic="gavel", fig="1 of 3", lab="CASES", place="JERUSALEM", field="Justice",
         region="Middle East", time="by 19:47", status="CONFIRMED", pin=(31.8, 35.2),
         head="Judges urge dropping Netanyahu bribery case",
         dek="Court doubts the media-favours charge; he calls for the trial to end.",
         src="BBC · Al Jazeera"),
    dict(n=6, pic="sats", fig="1M", lab="ORBITAL MODULES", place="WASHINGTON", field="Tech",
         region="N. America", time="by 19:13", status="OFFICIAL", pin=(38.9, -77.0),
         head="FCC clears SpaceX data centres in orbit",
         dek="'Starmind' licence covers up to 1,000,000 compute modules.",
         src="Al Jazeera · Guardian"),
    dict(n=7, pic="energy", fig="+26%", lab="PRICE CAP", place="LONDON", field="Energy",
         region="Europe", time="by 00:03", status="OFFICIAL", pin=(51.5, -0.1),
         head="UK energy price cap to jump 26% in January",
         dek="Ofgem: typical bill rises from £1,723 to £2,166 a year.",
         src="BBC · Guardian"),
    dict(n=8, pic="garment", fig="+36%", lab="TK 17,000", place="DHAKA", field="Labour",
         region="South Asia", time="early hours", status="CONFIRMED", pin=(23.8, 90.4),
         head="Garment pay floor lifted; unions say too low",
         dek="Wage board: Tk 17,000 a month, up from 12,500.",
         src="Daily Star · Al Jazeera · AFP"),
    dict(n=9, pic="treaty", fig="No.1", lab="SECURITY PARTNER", place="CANBERRA", field="Diplomacy",
         region="Oceania", time="by 01:51", status="CONFIRMED", pin=(-9.4, 160.0),
         head="Solomon Islands signs Australia security treaty",
         dek="Australia named 'primary security partner'; China ties curbed.",
         src="Guardian · Al Jazeera · NBC"),
    dict(n=10, pic="grid", fig="5", lab="REGIONS HIT", place="KYIV", field="War",
         region="Europe", time="overnight", status="CONFIRMED", pin=(47.8, 35.2),
         head="Russian strikes cut power in five regions",
         dek="At least five killed; Zaporizhzhia and Dnipro worst hit.",
         src="Al Jazeera · BBC"),
    dict(n=11, pic="court", fig="2022", lab="REPORT UNLAWFUL", place="CAPE TOWN", field="Politics",
         region="Sub-Sah. Africa", time="by 15:35", status="CONFIRMED", pin=(-33.9, 18.4),
         head="Ramaphosa wins 'Farmgate' court fight",
         dek="High Court voids the panel report behind impeachment threat.",
         src="Al Jazeera · BBC"),
    dict(n=12, pic="thermo", fig="6", lab="DAYS ABOVE 2°C", place="GLOBAL", field="Climate",
         region="Global", time="by 14:52", status="REPORTED", pin=None,
         head="World logs six straight days 2°C above pre-industrial",
         dek="A first, the Guardian learns; peak 2.24°C on Monday.",
         src="Guardian"),
    dict(n=13, pic="strike", fig="~15k", lab="MARCH IN ATHENS", place="ATHENS", field="Labour",
         region="Europe", time="all day", status="CONFIRMED", pin=(38.0, 23.7),
         head="Greek general strike halts ferries and metro",
         dek="Wage protest; police count ~15,000 in Athens.",
         src="Reuters · AFP"),
]

# (city, region, field, status, text, source, (lat, lon) or None)
BRIEFS = [
    ("Gaza City", "Middle East", "War", "CONFIRMED", "Israeli strike kills Hamas security chief and family", "AJ, BBC", (31.5, 34.5)),
    ("Ras Tanura", "Middle East", "War", "CONFIRMED", "Houthi drones target refinery; Saudis say 4 downed", "AJ, NBC", (26.6, 50.1)),
    ("Hormuz", "Middle East", "War", "CLAIM", "Iran's IRGC says two tankers hit mines, caught fire", "Arab News", (26.5, 56.3)),
    ("Jerusalem", "Middle East", "Politics", "REPORTED", "Knesset bloc backs independent 7 October probe", "AJ", (31.8, 35.2)),
    ("Baghdad", "Middle East", "Justice", "REPORTED", "Top court backs federal troops at Kurdish borders", "AJ", (33.3, 44.4)),
    ("Samara", "Europe", "War", "CONFIRMED", "Ukrainian drones set two Rosneft refineries ablaze", "Kyiv Ind., Meduza", (53.2, 50.1)),
    ("Moscow", "Europe", "War", "REPORTED", "Leaked Rosstat files point to ~500,000 war dead", "BBC Russian", (55.8, 37.6)),
    ("London", "Europe", "Business", "CONFIRMED", "Poundland collapses; 10,000+ jobs at risk", "Guardian, BBC", (51.5, -0.1)),
    ("London", "Europe", "Defence", "REPORTED", "RAF reportedly moves jets into hangars over drones", "Times, Sky", (51.5, -0.1)),
    ("Brussels", "Europe", "Business", "REPORTED", "EU and UK fine fragrance cartel over €570m", "AFP", (50.8, 4.4)),
    ("Brussels", "Europe", "Trade", "REPORTED", "EU offers UK new deal on 'Made in Europe'", "BBC", (50.8, 4.4)),
    ("Geneva", "Europe", "Sport", "REPORTED", "Chess title: Gukesh–Sindarov game 2 drawn, 1–1", "Guardian", (46.2, 6.1)),
    ("Paris", "Europe", "Sport", "CONFIRMED", "PSG 2–2 Roma; Sporting 2–2 Man Utd in Champions League", "AJ, Guardian", (48.9, 2.3)),
    ("Madrid", "Europe", "Migration", "CONFIRMED", "Kilmar Abrego Garcia lands after leaving the US", "AJ, Reuters", (40.4, -3.7)),
    ("Brussels", "Europe", "Politics", "REPORTED", "Puigdemont says he will return to Spain on 12 Dec", "AJ", (50.8, 4.4)),
    ("Basingstoke", "Europe", "Sport", "CONFIRMED", "Raheem Sterling avoids jail for dangerous driving", "Guardian, BBC", (51.3, -1.1)),
    ("Kharkiv", "Europe", "War", "CLAIM", "Ukraine says Blysk laser downed a Russian jet drone", "AJ", (50.0, 36.2)),
    ("Washington", "N. America", "Economy", "CONFIRMED", "Q3 growth revised up to 4.3%; jobless claims 189,000", "Boston Report, NTD", (38.9, -77.0)),
    ("Iowa", "N. America", "Environment", "CONFIRMED", "US Army detonates ~4,500 kg of lead azide", "AJ, BBC", (41.0, -91.0)),
    ("Albany", "N. America", "Tech", "OFFICIAL", "New York bans AI-chatbot toys for five years", "Guardian", (42.7, -73.8)),
    ("New York", "N. America", "Weather", "REPORTED", "Macy's parade moved to Saturday over high winds", "Guardian", (40.7, -74.0)),
    ("New York", "N. America", "Sport", "REPORTED", "MLB sues players' union ahead of likely lockout", "Guardian", (40.7, -74.0)),
    ("Quito", "S. America", "Security", "REPORTED", "Ecuador says US 'action plan' agreed after pause", "AJ", (-0.2, -78.5)),
    ("Caracas", "S. America", "Labour", "REPORTED", "Police clash with minimum-wage marchers", "AJ", (10.5, -66.9)),
    ("Brasília", "S. America", "Finance", "REPORTED", "Monetary Council curbs revolving card debt", "Rio Times", (-15.8, -47.9)),
    ("Curitiba", "S. America", "Disaster", "REPORTED", "Paraná storm toll reaches 6, civil defence says", "Rio Times, AFP", (-25.4, -49.3)),
    ("Valparaíso", "S. America", "Politics", "REPORTED", "Chile's lower house passes 2027 budget, 113–9", "Rio Times", (-33.0, -71.6)),
    ("Maiduguri", "Sub-Sah. Africa", "Politics", "REPORTED", "Tinubu vows peace at rally before 16 Jan vote", "AJ", (11.8, 13.2)),
    ("Pyongyang", "East Asia", "Diplomacy", "CONFIRMED", "North Korea shuts Switzerland's office", "AJ, BBC", (39.0, 125.8)),
    ("Phnom Penh", "SE Asia", "Defence", "REPORTED", "Cambodia, China start Golden Dragon drills", "AFP", (11.6, 104.9)),
    ("Canberra", "Oceania", "Economy", "OFFICIAL", "Inflation hits 4.9% in year to October", "Guardian", (-35.3, 149.1)),
    ("Canberra", "Oceania", "Rights", "REPORTED", "Defence minister apologises to LGBTQ veterans", "Guardian", (-35.3, 149.1)),
    ("Sydney", "Oceania", "Justice", "CONFIRMED", "Ex-police officer guilty of double murder", "Guardian, BBC", (-33.9, 151.2)),
    ("Space", "Global", "Science", "CONFIRMED", "Close-ups of asteroid Dimorphos, 4 years after DART", "Guardian, BBC", None),
]

DATE_CHECK = ("Huawei convicted in Brooklyn (Tue 24) · Coalition strike on Hodeidah (Tue 24) · "
              "Serbia school shooting (Tue 24) · Cartagena siege began (Tue 24) · UN femicide report "
              "(Tue 24) · Probe of Politburo's Chen Jining (Tue 24) · Sinner knee surgery (Tue 24) · "
              "Huang back at Nvidia (Mon 23) · West Java mine flood (Mon 23)")
NOT_YET = ("US Thanksgiving (Thu 26) · MLB labour deal expires (1 Dec) · Puigdemont's return (12 Dec) · "
           "UK price cap rise (1 Jan) · Nigeria election (16 Jan)")

UTC = [
    ("00:18", "Shenzhou-24 lifts off"), ("~05:30", "Taiex closes −4.8%"), ("by 14:55", "USTR tariff plan"),
    ("15:00", "Iowa Army blast"), ("by 18:55", "Cairo tanker fire"), ("by 19:13", "FCC clears Starmind"),
    ("21:00", "S&P 500 ends −0.3%"),
]

NUMBERS = [
    ("14", "partners in new US tariff plan"),
    ("−6.2%", "Kospi close, worst in AI sell-off"),
    ("31", "killed in Cairo tanker fire"),
    ("+26%", "UK energy price cap from January"),
    ("1M", "orbital compute modules cleared"),
    ("4.3%", "US Q3 growth, revised up"),
]

ALL = LEADS + CARDS
region_count = {r[0]: 0 for r in REGIONS}
field_count = {}
for s in ALL:
    region_count[s["region"]] += 1
    field_count[s["field"]] = field_count.get(s["field"], 0) + 1
for b in BRIEFS:
    region_count[b[1]] += 1
    field_count[b[2]] = field_count.get(b[2], 0) + 1
N_STORIES = len(ALL) + len(BRIEFS)
N_REGIONS = sum(1 for r in REGIONS if r[0] != "Global" and region_count[r[0]])
N_FIELDS = len(field_count)
assert sum(region_count.values()) == N_STORIES



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
    # front row: the named targets
    names = [("CHINA", (196, 40, 40)), ("EU", (30, 70, 160)), ("INDIA", (220, 120, 30)), ("TAIWAN", (40, 120, 90))]
    fw_ = w * 0.18
    for i, (nm, col) in enumerate(names):
        fx = x + w * 0.13 + i * (fw_ + 2)
        rect(fx, hull_y - ch * 1.25, fw_, ch * 1.25, fill=col, outline=(20, 20, 24), width=0.5)
        text(fx + fw_ / 2, hull_y - ch * 0.62, nm, font("heavy", 9.5), (255, 255, 255), anchor="mm")
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
    text(sx + 11, sy + 16, "TIANGONG", font("heavy", 9), (255, 255, 255), anchor="mt")
    text(rx + 16, ry + 36, "SHENZHOU-24", font("heavy", 9), (255, 255, 255), anchor="lm")
    # flags: Pakistan and China
    fx, fy, fw_, fh = x + 8, y + 8, 30, 20
    rect(fx, fy, fw_, fh, fill=(255, 255, 255))
    rect(fx + fw_ * 0.25, fy, fw_ * 0.75, fh, fill=(1, 102, 56))
    cx_, cy_ = fx + fw_ * 0.62, fy + fh * 0.5
    ellipse(cx_ - 6, cy_ - 6, 12, 12, fill=(255, 255, 255))
    ellipse(cx_ - 4, cy_ - 7.5, 12, 12, fill=(1, 102, 56))
    star(cx_ + 3.5, cy_ - 2.5, 2.4, (255, 255, 255))
    gx = fx + fw_ + 5
    rect(gx, fy, fw_, fh, fill=(222, 41, 16))
    star(gx + 6, fy + 6, 3.6, (255, 222, 0))
    for sx2, sy2 in ((11.5, 2.5), (13.5, 5), (13.5, 8.5), (11.5, 11)):
        star(gx + sx2, fy + sy2, 1.2, (255, 222, 0))


def pic_markets(x, y, w, h):
    rect(x, y, w, h, fill=(24, 28, 36))
    for k in range(1, 5):
        line([(x, y + k * h / 5), (x + w, y + k * h / 5)], fill=(50, 56, 68), width=0.6)
    pts = []
    vals = [0.25, 0.22, 0.28, 0.20, 0.26, 0.30, 0.36, 0.44, 0.50, 0.62, 0.70, 0.78, 0.74, 0.82]
    cwid = w * 0.52                              # chart on the left, ticker board on the right
    for i, v in enumerate(vals):
        pts.append((x + 8 + i * (cwid - 16) / (len(vals) - 1), y + h * v))
    bx, bw = x + cwid + 6, w - cwid - 30
    rect(bx, y + 22, bw, h - 30, fill=(40, 44, 56), outline=(80, 86, 100), width=0.6)
    for k, (nm, val) in enumerate((("KOSPI", "−6.2%"), ("SK HYNIX", "−11.1%"), ("SAMSUNG", "−9.9%"),
                                   ("TAIEX", "−4.8%"))):
        yy = y + 30 + k * (h - 42) / 4
        text(bx + 6, yy, nm, font("heavy", 9.5), (210, 214, 224))
        text(bx + bw - 6, yy, val, font("heavy", 10.5), (255, 96, 80), anchor="ra")
    for i, (px, py) in enumerate(pts):          # volume bars
        bh = 6 + (i * 7 % 11)
        rect(px - 2.5, y + h - bh - 2, 5, bh, fill=(80, 60, 66) if i > 5 else (60, 80, 70))
    line(pts, fill=(235, 70, 60), width=2.2)
    ex, ey = pts[-1]
    ellipse(ex - 3, ey - 3, 6, 6, fill=(235, 70, 60))
    poly([(ex - 6, ey + 6), (ex + 6, ey + 6), (ex, ey + 14)], fill=(235, 70, 60))
    text(x + 8, y + 6, "SEOUL · TAIPEI · TOKYO", font("bold", 9), (170, 176, 190))


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
    # key figure on a white plate, bottom-left, with its label chip
    f = font("black", 28 if big else 18)
    fw = tw(s["fig"], f)
    bh = 32 if big else 22
    rect(x + 4, y + h - bh - 4, fw + 10, bh, fill=(255, 255, 255))
    text(x + 9, y + h - 4 - bh / 2 + 1, s["fig"], f, INK, anchor="lm")
    lf = font("heavy", 10 if big else 8.5)
    chip(x + 4 + fw + 10, y + h - 4 - (15 if big else 12), s["lab"], INK, f=lf, h=15 if big else 12)
    # story number in the region's colour
    r = 10 if big else 8.5
    ellipse(x + w - 2 * r - 4, y + 4, 2 * r, 2 * r, fill=RCOL[s["region"]], outline=(255, 255, 255), width=1)
    text(x + w - r - 4, y + 4 + r + 0.5, str(s["n"]), font("heavy", 11 if big else 9.5), (255, 255, 255),
         anchor="mm")
    rect(x, y, w, h, outline=INK, width=0.8)


def meta_row(s, x, y, w, big=False):
    f = font("demi", 10 if big else 8.8)
    t = f"{s['place']} · {s['field'].upper()}"
    text(x, y, t, f, RCOL[s["region"]], maxw=w - 66, tag=t)
    chip(x + w, y - 0.5, s["status"], STATUS[s["status"]], anchor_right=True, h=11.5, f=font("heavy", 8))


def lead_card(s, x, y, w, h):
    pic_h = 104
    picture(s, x, y, w, pic_h, big=True)
    cy = y + pic_h + 6
    meta_row(s, x, cy, w, big=True)
    n = para(x, cy + 13, s["head"], font("black", 18.5), w, 20.5, 2, tag=s["head"])
    dy = cy + 13 + n * 20.5 + 2
    m = para(x, dy, s["dek"], font("sans", 10.6), w, 12.6, 2, (60, 60, 66), tag="dek" + str(s["n"]))
    wy = dy + m * 12.6 + 3
    text(x, wy, "WHY IT MATTERS", font("heavy", 9), RED)
    para(x + 74, wy, s["why"], font("med", 9.6), w - 74, 11, 1, INK, tag="why" + str(s["n"]))
    text(x, y + h, s["src"], font("med", 8.5), GREY, anchor="ls")
    text(x + w, y + h, s["time"], font("med", 8.5), GREY, anchor="rs")


def small_card(s, x, y, w, h):
    pic_h = 62
    picture(s, x, y, w, pic_h)
    cy = y + pic_h + 5
    meta_row(s, x, cy, w)
    n = para(x, cy + 12, s["head"], font("black", 12.6), w, 14, 2, tag=s["head"])
    para(x, cy + 12 + n * 14 + 1, s["dek"], font("sans", 9.4), w, 11, 2, (60, 60, 66), tag="dek" + str(s["n"]))
    text(x, y + h, s["src"], font("med", 8), GREY, anchor="ls")
    text(x + w, y + h, s["time"], font("med", 8), GREY, anchor="rs")



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
    rect(x, y, w, h, fill=(228, 235, 240))
    lat0, lat1 = 76, -48

    def proj(lat, lon):
        return x + (lon + 180) / 360 * w, y + (lat0 - lat) / (lat0 - lat1) * h

    step = 4.0
    yy = y + step / 2
    while yy < y + h - 2:
        xx = x + step / 2
        while xx < x + w - 2:
            lon = (xx - x) / w * 360 - 180
            lat = lat0 - (yy - y) / h * (lat0 - lat1)
            if any(inside(lon, lat, pg) for pg in LAND):
                ellipse(xx - 1.1, yy - 1.1, 2.2, 2.2, fill=(160, 168, 178))
            xx += step
        yy += step
    for b in BRIEFS:
        if b[6]:
            px, py = proj(*b[6])
            ellipse(px - 2.2, py - 2.2, 4.4, 4.4, fill=RCOL[b[1]], outline=(255, 255, 255), width=0.5)
    # numbered pins for leads and cards, pushed apart; leader line to the true spot
    pins = [(s["n"], s["region"], *proj(*s["pin"])) for s in ALL if s["pin"]]
    pos = {n: [px, py] for n, _, px, py in pins}
    for _ in range(300):
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
    for n, _, px, py in pins:
        qx, qy = pos[n]
        if math.hypot(qx - px, qy - py) > 2:
            line([(px, py), (qx, qy)], fill=INK, width=0.7)
        ellipse(px - 1.5, py - 1.5, 3, 3, fill=INK)
    for n, reg, px, py in pins:
        qx, qy = pos[n]
        ellipse(qx - 6.5, qy - 6.5, 13, 13, fill=RCOL[reg], outline=(255, 255, 255), width=0.8)
        text(qx, qy + 0.5, str(n), font("heavy", 8.5), (255, 255, 255), anchor="mm")


# ---------------------------------------------------------------- page
M = 14  # outer margin
NAVYBAR = (22, 30, 52)

# top band
rect(0, 0, W, 19, fill=NAVYBAR)
text(M, 9.8, "THE WORLD IN ONE DAY", font("heavy", 10.5), (255, 255, 255), anchor="lm")
text(W - M, 9.8, f"{N_STORIES} STORIES · {N_REGIONS} REGIONS · {N_FIELDS} FIELDS · ALL FIRST REPORTED ON "
     "WEDNESDAY 25 NOVEMBER 2026", font("heavy", 10.5), (255, 214, 120), anchor="rm")

# masthead
text(W / 2, 54, "Wednesday 25 November 2026", font("black", 60), INK, anchor="mm", maxw=W - 2 * M)
strap = ("US proposes tariffs on 14 partners · AI doubts sink Asian chip stocks · "
         "Pakistan's first astronaut docks at Tiangong")
text(W / 2, 98, strap, font("roman", 14), RED, anchor="mm", maxw=W - 2 * M)

# region bar: segments sized by story count
ry = 108
tot = N_STORIES
x0 = M
avail = W - 2 * M
minw = 64
used = [r for r in REGIONS if region_count[r[0]]]
extra = avail - minw * len(used)
for name, lab, col in used:
    segw = minw + extra * region_count[name] / tot
    rect(x0, ry, segw - 1.5, 15, fill=col)
    text(x0 + segw / 2, ry + 7.8, f"{lab} {region_count[name]}", font("heavy", 9), (255, 255, 255),
         anchor="mm", maxw=segw - 4, tag=lab)
    x0 += segw
fy = ry + 22
flist = sorted(field_count.items(), key=lambda kv: (-kv[1], kv[0]))
ftxt = f"{N_FIELDS} FIELDS   " + "  ·  ".join(f"{k} {v}" for k, v in flist)
text(M, fy, ftxt, font("med", 9), GREY, anchor="lm", maxw=W - 2 * M, tag="fields")

# the day in numbers
ny = 140
cw = (W - 2 * M) / len(NUMBERS)
for i, (num, s) in enumerate(NUMBERS):
    cx = M + i * cw
    if i:
        line([(cx, ny + 2), (cx, ny + 30)], fill=RULE, width=0.8)
    nf = font("black", 25)
    text(cx + 6, ny + 16, num, nf, RED if num[0] in "−+" else INK, anchor="lm")
    para(cx + 12 + tw(num, nf), ny + 5, s, font("med", 9.6), cw - 18 - tw(num, nf), 10.8, 2,
         tag="num" + num)
line([(M, ny + 36), (W - M, ny + 36)], INK, 1.2)

# the day in UTC, one strip
uy = ny + 41
rect(M, uy, W - 2 * M, 17, fill=NAVYBAR)
text(M + 6, uy + 8.8, "THE DAY IN UTC", font("heavy", 9.5), (255, 214, 120), anchor="lm")
ux = M + 92
seg = (W - M - ux) / len(UTC)
for i, (t, s) in enumerate(UTC):
    text(ux + i * seg, uy + 8.8, t, font("heavy", 9.5), (255, 255, 255), anchor="lm")
    text(ux + i * seg + tw(t, font("heavy", 9.5)) + 4, uy + 8.8, s, font("med", 9.5), (200, 208, 224),
         anchor="lm", maxw=seg - tw(t, font("heavy", 9.5)) - 8, tag="utc" + t)

# leads
ly, lh = uy + 21, 220
gap = 12
lw = (W - 2 * M - 2 * gap) / 3
for i, s in enumerate(LEADS):
    lead_card(s, M + i * (lw + gap), ly, lw, lh)
line([(M, ly + lh + 6), (W - M, ly + lh + 6)], RULE, 0.8)

# cards: two rows of five
cy0, ch = ly + lh + 10, 140
cg = 10
cwid = (W - 2 * M - 4 * cg) / 5
for i, s in enumerate(CARDS):
    r, c = divmod(i, 5)
    small_card(s, M + c * (cwid + cg), cy0 + r * (ch + 8), cwid, ch)

# bottom band: map + numbered briefs
by = cy0 + 2 * ch + 8 + 8
line([(M, by - 4), (W - M, by - 4)], INK, 1.2)
mw, mh = 292, 150
text(M, by + 4, "WHERE IT HAPPENED", font("heavy", 9.5), RED)
text(M + mw, by + 4.5, "pins = story numbers · dots = briefs", font("med", 8), GREY, anchor="ra")
world_map(M, by + 16, mw, mh)
lx = M
lgy = by + 16 + mh + 5
for name, lab, col in REGIONS:
    if not region_count[name]:
        continue
    t = lab.title().replace("Sub-Sah.", "Sub-Sah.").replace("Se ", "SE ").replace("E. Asia", "E. Asia")
    wv = tw(t, font("med", 7.8)) + 12
    if lx + wv > M + mw:
        lx = M
        lgy += 10
    ellipse(lx, lgy + 1, 6, 6, fill=col)
    text(lx + 8, lgy, t, font("med", 7.8), GREY)
    lx += wv + 4

bx = M + mw + 14
text(bx, by + 4, "ALSO ON WEDNESDAY 25 NOVEMBER", font("heavy", 9.5), RED)
colw = (W - M - bx - 12) / 2
per_col = math.ceil(len(BRIEFS) / 2)
cityf = font("demi", 9.2)
bf = font("sans", 8.9)
LETTER = {"CONFIRMED": "C", "OFFICIAL": "O", "REPORTED": "R", "CLAIM": "CL"}
for i, (city, reg, fld, st, t, src, _) in enumerate(BRIEFS):
    n = len(ALL) + 1 + i
    col, row = divmod(i, per_col)
    xx = bx + col * (colw + 12)
    yy = by + 17 + row * 11.45
    ellipse(xx, yy - 0.5, 11, 11, fill=RCOL[reg])
    text(xx + 5.5, yy + 5, str(n), font("heavy", 7.2), (255, 255, 255), anchor="mm")
    text(xx + 14, yy + 5, city, cityf, RCOL[reg], anchor="lm")
    tx = xx + 14 + tw(city, cityf) + 4
    lt = LETTER[st]
    lw_ = tw(lt, font("heavy", 7.5)) + 5
    text(tx, yy + 5, t, bf, INK, anchor="lm", maxw=xx + colw - tx - lw_ - 3, tag=t)
    chip(xx + colw, yy, lt, STATUS[st], f=font("heavy", 7.5), h=10, pad=2.5, anchor_right=True)

# date check
dy = by + 17 + per_col * 11.45 + 5
dh = 50
rect(M, dy, W - 2 * M, dh, fill=(255, 250, 236), outline=RED, width=1.2)
text(M + 7, dy + 5, "DATE CHECK", font("heavy", 10.5), RED)
text(M + 92, dy + 5, "Every story above happened, or was first reported, on Wednesday 25 November 2026.",
     font("demi", 10), INK, maxw=W - 2 * M - 100)
text(M + 7, dy + 19, "LEFT OUT", font("heavy", 8.6), GREY)
para(M + 92, dy + 18.5, DATE_CHECK, font("med", 8.8), W - 2 * M - 100, 10, 2, (60, 60, 66), tag="dc")
text(M + 7, dy + 39.5, "NOT YET", font("heavy", 8.6), GREY)
text(M + 92, dy + 39, NOT_YET, font("med", 8.8), (60, 60, 66), maxw=W - 2 * M - 100, tag="notyet")

# legend + sources
gy = dy + dh + 8
x0 = M
for k, v in STATUS.items():
    x0 += chip(x0, gy - 5.5, k, v, f=font("heavy", 7.8), h=11) + 4
    desc = {"CONFIRMED": "2+ outlets", "OFFICIAL": "on-record statement", "REPORTED": "one outlet",
            "CLAIM": "one side's claim"}[k]
    text(x0, gy, desc, font("med", 8.3), GREY, anchor="lm")
    x0 += tw(desc, font("med", 8.3)) + 10
text(W - M, gy, "Sources: Al Jazeera, BBC, Guardian, Reuters, AP, AFP, NBC, Daily Star, Kyiv Independent, "
     "Rio Times · times UTC", font("med", 8.3), GREY, anchor="rm")

for wmsg in WARN:
    print("WARN", wmsg)

out = img.resize((W, H), Image.LANCZOS).quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE)
out.save("entry.png", optimize=True)
print("wrote entry.png", out.size, "last y", gy)
