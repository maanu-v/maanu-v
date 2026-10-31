#!/usr/bin/env python3
"""Renders the animated README cards into profile/. Needs GITHUB_TOKEN; `--test` runs the self-check."""
import collections, datetime as dt, json, os, pathlib, random, sys, urllib.request
from xml.sax.saxutils import escape

USER = "maanu-v"
EMAIL = "manuvenke06@gmail.com"
OUT = pathlib.Path(__file__).parent
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"

GIRL = """
....HHHH.........HHHH....
...HHHHHH.HHHHH.HHHHHH...
...HHHHHHHHHHHHHHHHHHH...
....HHHHHHHHHHHHHHHHH....
.....HHHHHHHHHHHHHHH.....
.....HHHSSSHHHSSSHHH.....
.....HHSSSSSSSSSSSHH.....
.....HSSSSSSSSSSSSSH.....
.....HSSEESSSSSEESSH.....
.....HSSEESSSSSEESSH.....
.....HSSSSSSSSSSSSSH.....
.....HHSSSSSMMSSSSHH.....
......HHSSSSSSSSSHH......
.........SSSSSSS.........
........CCCCCCCCC........
......CCCCCCCCCCCCC......
.....CCCCCCCCCCCCCCC.....
....CCCLLLLLLLLLLLCCC....
....SSCLLLLLLLLLLLCSS....
....SSCLLLLLLLLLLLCSS....
.....SSSLLLLLLLLLSSS.....
..TTTTTTTTTTTTTTTTTTTTT..
""".split()
# character and colour per pixel, so the girl reads as an ASCII scan
INK = {"H": ("#", "#38bdf8"), "S": ("+", "#e0f2fe"), "E": ("@", "#0ea5e9"), "M": ("~", "#7dd3fc"),
       "C": ("%", "#0ea5e9"), "L": ("=", "#bae6fd"), "T": ("#", "#7dd3fc")}

# no prefers-reduced-motion opt-out: the owner wants these moving on a Reduce Motion Mac
STYLE = """<style>
.ln{opacity:0;animation:in .5s ease-out forwards}
.cell{opacity:0;animation:cell 10s linear infinite}
.noise{opacity:0;animation:noise 10s linear infinite}
.sweep{animation:sweep 10s linear infinite}
.state{animation:state 10s step-end infinite}
.tw{animation:rise 12s cubic-bezier(.2,.9,.3,1.15) infinite both}
.front{opacity:0;animation:front 12s linear infinite}
.fact{opacity:0;animation:fact 12s linear infinite}
.star{animation:pulse 3s ease-in-out infinite}
.beacon{animation:pulse 2s ease-in-out infinite}
.beam{animation:beam 5s linear infinite}
.pulse{animation:pulse 1.6s ease-in-out infinite}
.blink{animation:blink 4s step-end infinite}
.float{animation:float 4s ease-in-out infinite}
.screen{animation:screen 2.4s ease-in-out infinite}
.bar{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .7s ease-out forwards}
.ring{stroke-dasharray:0 999;animation:ring 1.6s ease-out .3s forwards}
@keyframes cell{0%,2%{opacity:0}3%,72%{opacity:1}74%,100%{opacity:0}}
@keyframes noise{0%{opacity:0}.5%,2.5%{opacity:1}3%,100%{opacity:0}}
@keyframes sweep{0%{transform:translateY(0);opacity:1}38%{transform:translateY(340px);opacity:1}39%,100%{opacity:0}}
@keyframes fact{0%{opacity:0}2%,31%{opacity:1}33%,100%{opacity:0}}
@keyframes rise{0%{transform:scaleY(0)}7%,86%{transform:scaleY(1)}94%,100%{transform:scaleY(0)}}
@keyframes front{0%{opacity:1;transform:translate(0,0)}18%{opacity:1;transform:translate(650px,286px)}19%,100%{opacity:0}}
@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}
@keyframes beam{from{transform:translateY(-70px)}to{transform:translateY(VIEWpx)}}
@keyframes pulse{50%{opacity:.25}}
@keyframes blink{0%,92%,100%{opacity:1}94%,98%{opacity:0}}
@keyframes float{50%{transform:translateY(-5px)}}
@keyframes screen{50%{opacity:.55}}
@keyframes grow{to{transform:scaleY(1)}}
</style>"""


def text(x, y, s, size=14, fill="#e0f2fe", weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{escape(str(s))}</text>')


def panel(name, title, h, body, w=860, label=""):
    """The shared window: gradient glass, title bar, live dot and a sweeping scan beam."""
    style = STYLE.replace("VIEW", str(h))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label or title)}">
{style}
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#082f49"/><stop offset=".55" stop-color="#0b1e33"/><stop offset="1" stop-color="#0c4a6e"/></linearGradient>
<linearGradient id="bm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#38bdf8" stop-opacity="0"/><stop offset=".5" stop-color="#38bdf8" stop-opacity=".3"/><stop offset="1" stop-color="#38bdf8" stop-opacity="0"/></linearGradient>
<clipPath id="clip"><rect width="{w}" height="{h}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#clip)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<rect width="{w}" height="34" fill="#0a1626"/>
<circle cx="20" cy="17" r="5" fill="#ff5f56"/><circle cx="38" cy="17" r="5" fill="#ffbd2e"/><circle cx="56" cy="17" r="5" fill="#27c93f"/>
{text(w / 2, 22, title, 12, "#7dd3fc", anchor="middle")}
<circle class="pulse" cx="{w - 52}" cy="17" r="4" fill="#38bdf8"/>{text(w - 42, 21, "LIVE", 10, "#7dd3fc")}
{body}
<rect class="beam" width="{w}" height="70" fill="url(#bm)"/>
</g>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="14" fill="none" stroke="#38bdf8" stroke-opacity=".7" stroke-width="1.5"/>
</svg>
"""


def lines_card(title, rows):
    body = "".join(
        f'<g class="ln" style="animation-delay:{i * 350}ms">{text(28, 68 + i * 28, "›", 15, "#38bdf8", 700)}{text(48, 68 + i * 28, r, 15)}</g>'
        for i, r in enumerate(rows))
    return panel("lines", title, 68 + len(rows) * 28, body, label=" ".join(rows))


def scan_card(info):
    cell = 12.5
    rnd = random.Random(USER)  # fixed seed: the card only changes when the data does
    art = []
    for y, row in enumerate(GIRL):
        for x, c in enumerate(row):
            if c == ".":
                continue
            ch, col = INK[c]
            px, py = round(26 + x * cell, 1), 84 + y * 14.5
            # the portrait prints top-down: a random glyph flashes, then the real one settles
            delay = f"{y * 0.16 + rnd.random() * 0.45:.2f}s"
            art.append(f'<g class="noise" style="animation-delay:{delay}">{text(px, py, rnd.choice("#%@&*$+=/01"), 14, "#7dd3fc")}</g>')
            cls = "blink" if c == "E" else "screen" if c == "L" else ""
            art.append(f'<g class="cell" style="animation-delay:{delay}"><g class="{cls}">{text(px, py, ch, 14, col)}</g></g>')
    box = f'<rect x="18" y="48" width="340" height="382" rx="10" fill="#0a1626" fill-opacity=".55" stroke="#38bdf8" stroke-opacity=".5"/>'
    girl = f'{text(32, 66, "VISUAL.MAP", 10, "#7dd3fc", 700)}<g transform="translate(0,14)"><g class="float">{"".join(art)}</g></g><rect class="sweep" x="19" y="72" width="338" height="3" fill="#7dd3fc"/><g class="pulse">{text(344, 66, "GENERATING", 10, "#38bdf8", 700, "end")}</g>'
    side = f'<rect x="372" y="48" width="470" height="382" rx="10" fill="#0a1626" fill-opacity=".55" stroke="#38bdf8" stroke-opacity=".5"/>{text(388, 66, "SYSTEM.INFO", 10, "#7dd3fc", 700)}'
    rows = "".join(
        f'<g class="ln" style="animation-delay:{i * 180}ms">{text(388, 92 + i * 30, k, 13, "#38bdf8", 700)}'
        f'{text(500, 92 + i * 30, "·" * 5, 13, "#0ea5e9")}{text(560, 92 + i * 30, v, 13)}</g>'
        for i, (k, v) in enumerate(info))
    return panel("scan", f"{USER}@github ~ $ ./profile-scan --live", 448, box + girl + side + rows,
                 label=" · ".join(f"{k}: {v}" for k, v in info))


def stats_card(total, cur, longest, active, recent):
    def tile(x, value, label, sub, y=124, size=42):
        return (f'<rect x="{x}" y="50" width="264" height="150" rx="10" fill="#0a1626" fill-opacity=".55" stroke="#38bdf8" stroke-opacity=".5"/>'
                f'{text(x + 132, y, f"{value:,}", size, "#e0f2fe", 700, "middle")}'
                f'{text(x + 132, 154, label, 12, "#38bdf8", 700, "middle", "letter-spacing=\"2\"")}'
                f'{text(x + 132, 176, sub, 11, "#7dd3fc", anchor="middle")}')
    frac = min(cur / longest, 1) if longest else 0
    ring = (f'<circle cx="430" cy="98" r="40" fill="none" stroke="#0c4a6e" stroke-width="5"/>'
            f'<style>@keyframes ring{{to{{stroke-dasharray:{frac * 251.3:.1f} 999}}}}</style>'
            f'<circle class="ring" cx="430" cy="98" r="40" fill="none" stroke="#38bdf8" stroke-width="5" stroke-linecap="round" transform="rotate(-90 430 98)"/>')
    peak = max(recent, default=0) or 1
    bars = "".join(
        f'<rect class="bar" style="animation-delay:{i * 12}ms" x="{18 + i * (824 / len(recent)):.1f}" y="{290 - 66 * v / peak:.1f}" '
        f'width="{max(824 / len(recent) - 2, 1):.1f}" height="{max(66 * v / peak, 2):.1f}" rx="1" fill="{"#38bdf8" if v else "#0c4a6e"}"/>'
        for i, v in enumerate(recent))
    body = (tile(18, total, "TOTAL CONTRIBUTIONS", f"{active:,} active days") +
            tile(298, cur, "CURRENT STREAK", "days in a row", 108, 30) + ring +
            tile(578, longest, "LONGEST STREAK", "personal best") +
            text(18, 218, f"LAST {len(recent)} DAYS", 10, "#7dd3fc", 700) + bars)
    return panel("stats", f"{USER}@github ~ $ ./contributions --watch", 306, body,
                 label=f"{total} total contributions, current streak {cur} days, longest streak {longest} days")


def city_card(days):
    """Isometric skyline: one tower per day of the last year, raised week by week behind a light front."""
    days = days[-364:]
    a, b, x0, y0 = 12.5, 5.5, 110, 150
    first = dt.date.fromisoformat(days[0][0]).isoweekday() % 7
    peak = max(n for _, n in days)
    shades = [("#7dd3fc", "#0ea5e9", "#0369a1"), ("#bae6fd", "#38bdf8", "#0284c7"),
              ("#e0f2fe", "#7dd3fc", "#0ea5e9"), ("#ffffff", "#bae6fd", "#38bdf8")]
    cells = sorted(((i + first) // 7, (i + first) % 7, n) for i, (_, n) in enumerate(days))
    floor, towers, beacon = [], [], ""
    for w, d, n in sorted(cells, key=lambda c: c[0] + c[1]):
        x, y = x0 + (w - d) * a, y0 + (w + d) * b
        top = f"M{x} {y}l{a} {b}l{-a} {b}l{-a} {-b}z"
        if not n:
            floor.append(top)
            continue
        frac = (n / peak) ** .5
        h = round(8 + frac * 96, 1)
        lit, left, right = shades[min(int(frac * 4), 3)]
        ty = round(y - h, 1)
        faces = (f'<path fill="{left}" d="M{x - a} {ty + b}l{a} {b}v{h}l{-a} {-b}z"/>'
                 f'<path fill="{right}" d="M{x + a} {ty + b}l{-a} {b}v{h}l{a} {-b}z"/>'
                 f'<path fill="{lit}" d="M{x} {ty}l{a} {b}l{-a} {b}l{-a} {-b}z"/>')
        towers.append(f'<g class="tw" style="animation-delay:{w * 41}ms;transform-origin:{x}px {y + 2 * b}px">{faces}</g>')
        if n == peak and not beacon:
            beacon = (f'<rect class="beacon" x="{x - 1.5}" y="{max(ty - 90, 40)}" width="3" height="{ty + b - max(ty - 90, 40)}" fill="url(#ray)"/>'
                      f'<circle class="beacon" cx="{x}" cy="{ty + b}" r="5" fill="#fff"/>')
    rnd = random.Random(USER)
    stars = "".join(f'<circle class="star" style="animation-delay:{rnd.random() * 3:.2f}s" cx="{rnd.randint(20, 840)}" '
                    f'cy="{rnd.randint(44, 170)}" r="{rnd.choice((1, 1, 1.6))}" fill="#bae6fd"/>' for _ in range(36))
    total = sum(n for _, n in days)
    months, weekdays = collections.Counter(), collections.Counter()
    for day, n in days:
        when = dt.date.fromisoformat(day)
        months[when.strftime("%B %Y")] += n
        weekdays[when.strftime("%A")] += n
    facts = [f"{sum(1 for _, n in days if n)} of {len(days)} days lit up",
             f"Boom time: {months.most_common(1)[0][0]}",
             f"Favourite building day: {weekdays.most_common(1)[0][0]}"]
    body = (f'<defs><linearGradient id="ray" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7dd3fc" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>'
            f'<linearGradient id="fr" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7dd3fc"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>'
            f'{stars}<path d="{"".join(floor)}" fill="#0c4a6e" fill-opacity=".7"/>{"".join(towers)}{beacon}'
            f'<path class="front" d="M{x0} {y0 - 40}l{-7 * a} {7 * b}v40l{7 * a} {-7 * b}z" fill="url(#fr)" fill-opacity=".55"/>'
            + text(24, 408, f"{total:,}", 44, "#e0f2fe", 700) + text(24, 432, "CONTRIBUTIONS, LAST 12 MONTHS", 11, "#38bdf8", 700, extra='letter-spacing="2"')
            + "".join(f'<g class="fact" style="animation-delay:{i * 4}s">{text(24, 456, f, 12, "#7dd3fc")}</g>' for i, f in enumerate(facts)))
    return panel("city", f"{USER}@github ~ $ ./contributions --render city", 490, body,
                 label=f"3D city of {total} contributions over the last 12 months")


def heading(title):
    """Section title in the same language as the cards: pulsing chevrons, printed letters, a light running along the rule."""
    letters = "".join(
        f'<g class="ln" style="animation-delay:{i * 45}ms">{text(36 + i * 15, 29, c, 20, "#0ea5e9", 700)}</g>'
        for i, c in enumerate(title.upper()) if c != " ")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="860" height="52" viewBox="0 0 860 52" role="img" aria-label="{escape(title)}">
<style>
.ln{{opacity:0;animation:in .3s ease-out forwards}}
.pulse{{animation:pulse 1.6s ease-in-out infinite}}
.run{{animation:run 4s linear infinite}}
@keyframes in{{to{{opacity:1}}}}
@keyframes pulse{{50%{{opacity:.25}}}}
@keyframes run{{from{{transform:translateX(-220px)}}to{{transform:translateX(860px)}}}}
</style>
<defs><linearGradient id="g"><stop offset="0" stop-color="#7dd3fc" stop-opacity="0"/><stop offset=".5" stop-color="#7dd3fc"/><stop offset="1" stop-color="#7dd3fc" stop-opacity="0"/></linearGradient></defs>
<path class="pulse" d="M2 14l8 8-8 8" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path class="pulse" style="animation-delay:.25s" d="M14 14l8 8-8 8" fill="none" stroke="#7dd3fc" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>{letters}
<rect y="44" width="860" height="1.5" fill="#0c4a6e"/><rect class="run" y="43" width="220" height="3" fill="url(#g)"/>
</svg>
"""


def streaks(days):
    """days: oldest-first [(date, count)], ending today. Today at zero doesn't break the current streak yet."""
    best = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        best = max(best, run)
    counts = [n for _, n in days]
    if counts and counts[-1] == 0:
        counts.pop()
    cur = 0
    for n in reversed(counts):
        if not n:
            break
        cur += 1
    return cur, best


def gql(query):
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": query}).encode(),
                                 {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"})
    res = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in res:
        sys.exit(f"GitHub API error: {res['errors']}")
    return res["data"]["user"]


def fetch():
    u = gql(f'''{{user(login:"{USER}"){{name bio createdAt followers{{totalCount}}
      repositories(first:100,ownerAffiliations:OWNER,isFork:false){{totalCount nodes{{stargazerCount primaryLanguage{{name}}}}}}}}}}''')
    today = dt.datetime.now(dt.timezone.utc)
    days = {}
    for year in range(int(u["createdAt"][:4]), today.year + 1):
        c = gql(f'''{{user(login:"{USER}"){{contributionsCollection(from:"{year}-01-01T00:00:00Z",to:"{min(dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc), today).strftime("%Y-%m-%dT%H:%M:%SZ")}"){{
          contributionCalendar{{weeks{{contributionDays{{date contributionCount}}}}}}}}}}}}''')
        for w in c["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    return u, sorted(days.items())


HEADINGS = {"about": "About Me", "up-to": "What I'm Up To", "stack": "Tech Stack",
            "activity": "GitHub Activity", "fun-fact": "Fun Fact", "connect": "Connect With Me"}


def main():
    for name, title in HEADINGS.items():
        (OUT / f"heading-{name}.svg").write_text(heading(title))
    u, days = fetch()
    repos = u["repositories"]
    langs = collections.Counter(r["primaryLanguage"]["name"] for r in repos["nodes"]
                                if r["primaryLanguage"] and r["primaryLanguage"]["name"] != "Jupyter Notebook")
    total = sum(n for _, n in days)
    active = sum(1 for _, n in days if n)
    cur, longest = streaks(days)
    (OUT / "scan.svg").write_text(scan_card([
        ("Subject", u["name"]), ("Handle", f"@{USER}"), ("Role", u["bio"] or "Developer"),
        ("Status", "Building | Learning | Shipping"), ("Languages", ", ".join(l for l, _ in langs.most_common(3))),
        ("Repositories", repos["totalCount"]), ("Contributions", f"{total:,}"),
        ("Stars", sum(r["stargazerCount"] for r in repos["nodes"])), ("Followers", u["followers"]["totalCount"]),
        ("Active Days", f"{active:,}"), ("Contact", EMAIL)]))
    (OUT / "stats.svg").write_text(stats_card(total, cur, longest, active, [n for _, n in days[-90:]]))
    (OUT / "city.svg").write_text(city_card(days))
    (OUT / "about.svg").write_text(lines_card(f"{USER}@github ~ $ cat about.md", [
        "AI & Data Science student at Amrita Vishwa Vidyapeetham, Coimbatore",
        "I love turning ideas into things that actually run",
        "Worked across machine learning, full-stack apps, and hardware",
        "Getting hooked on DevOps: automating, deploying, keeping systems reliable",
        "I learn best by building, breaking, and rebuilding"]))
    (OUT / "now.svg").write_text(lines_card(f"{USER}@github ~ $ ./whats-up --now", [
        "Diving into DevOps: Docker, Kubernetes, CI/CD, infra as code",
        "Always up for learning something new and experimenting",
        "Open to collaborations, internships and interesting problems",
        "Ask me about AI/ML, Data Science, or hardware"]))


def test():
    d = lambda *c: list(enumerate(c))
    assert streaks(d(1, 1, 0, 1, 1, 1)) == (3, 3)
    assert streaks(d(1, 1, 1, 0, 1, 0)) == (1, 3)  # today empty: yesterday's streak still counts
    assert streaks(d(1, 0, 0)) == (0, 1)
    assert streaks([]) == (0, 0)
    start = dt.date(2026, 1, 1)
    sample = [((start + dt.timedelta(i)).isoformat(), i % 5) for i in range(400)]
    assert city_card(sample).count('class="tw"') == sum(1 for _, n in sample[-364:] if n)


if __name__ == "__main__":
    test() if "--test" in sys.argv else main()
