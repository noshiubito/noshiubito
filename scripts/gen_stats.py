"""Génère assets/stats.svg à partir du calendrier de contributions GitHub.

Variables d'environnement :
  GH_TOKEN  token GitHub (GITHUB_TOKEN suffit pour les contributions publiques)
  GH_LOGIN  pseudo GitHub
  DEMO=1    données factices (test local, sans réseau)
"""
import json, os, random, urllib.request
from datetime import date, datetime, timedelta, timezone

ACC = "#8fb4d9"
SANS = "'Inter','Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Consolas,'DejaVu Sans Mono',monospace"
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]

QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req))
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(date.fromisoformat(d["date"]), d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def demo():
    today = date.today()
    return [(today - timedelta(days=i), max(0, int(random.gauss(6, 9)))) for i in range(364, -1, -1)]


def fr(d):
    return f"{d.day} {MOIS[d.month - 1]}"


def streaks(days):
    best = (0, None, None)
    run, start = 0, None
    for d, c in days:
        if c:
            run, start = run + 1, start or d
            if run > best[0]:
                best = (run, start, d)
        else:
            run, start = 0, None
    # série actuelle : on tolère aujourd'hui à 0
    cur, i = 0, len(days) - 1
    if days[i][1] == 0:
        i -= 1
    end = days[i][0] if i >= 0 else None
    while i >= 0 and days[i][1]:
        cur, i = cur + 1, i - 1
    cstart = days[i + 1][0] if cur else None
    return cur, cstart, end, best


def build(days):
    total = sum(c for _, c in days)
    active = [c for _, c in days if c]
    best_day = max(days, key=lambda x: x[1])
    months = {}
    for d, c in days:
        months[(d.year, d.month)] = months.get((d.year, d.month), 0) + c
    (by, bm), bmv = max(months.items(), key=lambda x: x[1])
    cur, cs, ce, (lng, ls, le) = streaks(days)
    avg = total / len(active) if active else 0

    kpis = [
        (f"{total:,}".replace(",", " "), "Contributions", "12 derniers mois", "#e6ebf2"),
        (str(cur), "Série actuelle", f"{fr(cs)} → {fr(ce)}" if cur else "à relancer", ACC),
        (str(lng), "Plus longue série", f"{fr(ls)} → {fr(le)}" if lng else "—", "#e6ebf2"),
        (str(best_day[1]), "Record / jour", fr(best_day[0]), "#e6ebf2"),
        (f"{avg:.1f}".replace(".", ","), "Moy. / jour actif", f"{len(active)} jours actifs", "#e6ebf2"),
        (str(bmv), "Meilleur mois", f"{MOIS[bm - 1]} {by}", "#e6ebf2"),
    ]

    W, H = 1200, 560
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="#0b0f15" stroke="#222a36" stroke-width="2"/>']
    now = datetime.now(timezone.utc)
    out.append(f'<text x="60" y="66" font-family="{MONO}" font-size="14" letter-spacing="5" fill="{ACC}">ACTIVITÉ</text>')
    out.append(f'<text x="{W-60}" y="66" text-anchor="end" font-family="{MONO}" font-size="12" fill="#5b6678">'
               f'màj {now.day} {MOIS[now.month-1]} {now.year} · {now:%H:%M} UTC</text>')

    # KPI : 6 colonnes
    cw = (W - 120) / 6
    for i, (v, lab, sub, col) in enumerate(kpis):
        x = 60 + cw * i + cw / 2
        if i:
            out.append(f'<rect x="{60+cw*i:.0f}" y="112" width="1" height="96" fill="#1d2430"/>')
        out.append(f'<text x="{x:.0f}" y="158" text-anchor="middle" font-family="{SANS}" font-size="44" font-weight="800" fill="{col}">{v}</text>')
        out.append(f'<text x="{x:.0f}" y="186" text-anchor="middle" font-family="{SANS}" font-size="14" fill="#9aa3b2">{lab}</text>')
        out.append(f'<text x="{x:.0f}" y="206" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#5b6678">{sub}</text>')

    # courbe : moyenne glissante 7 j sur 90 j
    last = days[-96:]
    vals = [sum(c for _, c in last[i - 6:i + 1]) / 7 for i in range(6, len(last))]
    dts = [d for d, _ in last[6:]]
    x0, x1, y0, y1 = 90, W - 60, 500, 280
    mx = max(vals) or 1
    pts = [(x0 + (x1 - x0) * i / (len(vals) - 1), y0 - (y0 - y1) * v / mx) for i, v in enumerate(vals)]
    for f in (0, .5, 1):
        y = y0 - (y0 - y1) * f
        out.append(f'<rect x="{x0}" y="{y:.0f}" width="{x1-x0}" height="1" fill="#161c26"/>')
        out.append(f'<text x="{x0-12}" y="{y+4:.0f}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#5b6678">{mx*f:.0f}</text>')
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    out.append(f'<polygon points="{x0},{y0} {line} {x1},{y0}" fill="{ACC}" fill-opacity=".08"/>')
    out.append(f'<polyline points="{line}" fill="none" stroke="{ACC}" stroke-width="2.2" stroke-linejoin="round"/>')
    pi = max(range(len(vals)), key=vals.__getitem__)
    px, py = pts[pi]
    out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="#ffffff"/>')
    out.append(f'<text x="{px:.1f}" y="{py-12:.1f}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#e6ebf2">' + f"{vals[pi]:.1f}".replace(".", ",") + "</text>")
    for i, d in enumerate(dts):
        if d.day == 1:
            x = x0 + (x1 - x0) * i / (len(dts) - 1)
            out.append(f'<text x="{x:.0f}" y="{y0+22}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#5b6678">{MOIS[d.month-1]}</text>')
    out.append(f'<text x="{x1}" y="{H-14}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#5b6678">moyenne glissante 7 j · 90 derniers jours</text>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    days = demo() if os.getenv("DEMO") else fetch(os.environ["GH_LOGIN"], os.environ["GH_TOKEN"])
    days = [x for x in days if x[0] <= date.today()]
    os.makedirs("assets", exist_ok=True)
    open("assets/stats.svg", "w", encoding="utf-8").write(build(days))
    print("assets/stats.svg OK")
