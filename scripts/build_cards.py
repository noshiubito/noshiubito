"""Génère les cartes SVG du profil (hero, projets, pied de page).

Modifie uniquement le bloc CONFIG, puis lance :  python scripts/build_cards.py
(la GitHub Action le fait aussi automatiquement à chaque push)
"""
import math, os
from html import escape

# ============================ CONFIG ============================
CONFIG = {
    "name": "MAYRON",
    "kicker": "CYBERSECURITY ENGINEER · IN PROGRESS",
    "subtitle": "Élève ingénieur cybersécurité — Bac+5 · ESAIP",
    "tags": ["PENTEST", "BLUE TEAM", "AUTOMATISATION", "JAPON"],
    "location": "aix-en-provence, fr",
    # rapport de scan : (port, service, détails)
    "scan": [
        ("22/tcp", "pentest", "web · active directory"),
        ("443/tcp", "blue-team", "soc · détection · réponse"),
        ("8080/tcp", "automation", "python · bash · powershell"),
    ],
    "projects": [
        {"name": "PROJET_1", "desc": "Problème résolu et résultat obtenu, en une ou deux phrases courtes.",
         "stack": ["Python", "Docker"], "status": "en cours"},
        {"name": "PROJET_2", "desc": "Problème résolu et résultat obtenu, en une ou deux phrases courtes.",
         "stack": ["Bash"], "status": "terminé"},
    ],
    "motto": "protéger · comprendre · automatiser",
}
# ================================================================

ACC = "#8fb4d9"
BG, LINE, MUTED, TEXT, SOFT = "#0b0f15", "#222a36", "#6b7686", "#e6ebf2", "#9aa3b2"
SANS = "'Inter','Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Consolas,'DejaVu Sans Mono',monospace"
E = lambda s: escape(str(s))


def hexpts(cx, cy, r):
    return " ".join(f"{cx + r * math.cos(math.radians(a)):.1f},{cy + r * math.sin(math.radians(a)):.1f}"
                    for a in range(30, 390, 60))


def wrap(text, n):
    lines, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur] if cur else lines


ANIM = """<style>
 .in{animation:in 1s ease-out both}.d1{animation-delay:.15s}.d2{animation-delay:.35s}.d3{animation-delay:.55s}
 .breath{animation:breath 5s ease-in-out infinite}.cur{animation:blink 1.1s steps(1) infinite}
 @keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
 @keyframes breath{0%,100%{opacity:.6}50%{opacity:1}}@keyframes blink{50%{opacity:0}}
</style>"""


def hero(c):
    cx, cy = 945, 205
    rows = "".join(
        f'<text y="{492 + 30 * i}" fill="#cbd2dc"><tspan x="112">{E(p)}</tspan><tspan x="262" fill="{ACC}">open</tspan>'
        f'<tspan x="402">{E(s)}</tspan><tspan x="602" fill="#8a94a3">{E(d)}</tspan></text>'
        for i, (p, s, d) in enumerate(c["scan"]))
    h = 470 + 30 * len(c["scan"]) + 60
    sep = '  <tspan fill="#3a4454">/</tspan>  '
    spokes = "".join(
        f'<line x1="{cx + 26 * math.cos(math.radians(a)):.1f}" y1="{cy + 26 * math.sin(math.radians(a)):.1f}" '
        f'x2="{cx + 70 * math.cos(math.radians(a)):.1f}" y2="{cy + 70 * math.sin(math.radians(a)):.1f}"/>'
        for a in range(30, 390, 60))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {h}" width="1200" height="{h}">
<defs>
 <linearGradient id="silver" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f6fa"/><stop offset="1" stop-color="#9aa3b2"/></linearGradient>
 <linearGradient id="name" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#aab3c2"/></linearGradient>
 <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{ACC}" stop-opacity=".22"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>
</defs>{ANIM}
<rect x="1" y="1" width="1198" height="{h - 2}" rx="22" fill="{BG}" stroke="{LINE}" stroke-width="2"/>
<circle cx="{cx}" cy="{cy}" r="190" fill="url(#glow)" class="breath"/>
<circle cx="{cx}" cy="{cy}" r="138" fill="none" stroke="#3a4454" stroke-width="1.5"/>
<circle cx="{cx}" cy="{cy}" r="146" fill="none" stroke="#3a4454" stroke-width=".8" stroke-dasharray="2 6"/>
<polygon points="{hexpts(cx, cy, 112)}" fill="url(#silver)"/>
<polygon points="{hexpts(cx, cy, 92)}" fill="{BG}"/>
<polygon points="{hexpts(cx, cy, 70)}" fill="none" stroke="url(#silver)" stroke-width="3"/>
<polygon points="{hexpts(cx, cy, 26)}" fill="{ACC}"/>
<g stroke="#5b6678" stroke-width="1.5">{spokes}</g>
<g font-family="{SANS}">
 <text x="80" y="110" font-family="{MONO}" font-size="15" letter-spacing="5" fill="{ACC}" class="in">{E(c["kicker"])}</text>
 <text x="74" y="208" font-size="104" font-weight="800" letter-spacing="2" fill="url(#name)" class="in d1">{E(c["name"])}</text>
 <text x="80" y="256" font-size="21" fill="{SOFT}" class="in d2">{E(c["subtitle"])}</text>
 <text x="80" y="306" font-family="{MONO}" font-size="14" letter-spacing="3" fill="#cbd2dc" class="in d3" xml:space="preserve">{sep.join(E(t) for t in c["tags"])}</text>
</g>
<g font-family="{MONO}" class="in d3">
 <rect x="80" y="372" width="1040" height="{h - 426}" rx="12" fill="#070a0f" stroke="#1d2430"/>
 <circle cx="106" cy="400" r="4" fill="{ACC}"/>
 <text x="122" y="405" font-size="14" fill="{MUTED}">scan report · {E(c["name"].lower())}.local</text>
 <text x="1096" y="405" font-size="14" fill="{MUTED}" text-anchor="end">{E(c["location"])}</text>
 <rect x="80" y="420" width="1040" height="1" fill="#1d2430"/>
 <g font-size="16">
  <text y="458" fill="{MUTED}"><tspan x="112">PORT</tspan><tspan x="262">STATE</tspan><tspan x="402">SERVICE</tspan><tspan x="602">DETAILS</tspan></text>
  {rows}
 </g>
 <rect x="1080" y="{492 + 30 * (len(c["scan"]) - 1) - 13}" width="9" height="17" fill="{ACC}" class="cur"/>
</g>
</svg>'''


def project(p, i):
    W, H = 590, 230
    lines = wrap(p["desc"], 52)[:3]
    desc = "".join(f'<text x="32" y="{124 + 24 * k}" font-size="16" fill="{SOFT}">{E(l)}</text>' for k, l in enumerate(lines))
    x, pills = 32, ""
    for t in p["stack"]:
        w = 16 + 8.6 * len(t)
        pills += (f'<rect x="{x:.0f}" y="176" width="{w:.0f}" height="26" rx="13" fill="none" stroke="#2c3646"/>'
                  f'<text x="{x + w / 2:.0f}" y="193" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#cbd2dc">{E(t)}</text>')
        x += w + 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{ANIM}
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{BG}" stroke="{LINE}" stroke-width="2"/>
<g font-family="{SANS}" class="in">
 <text x="32" y="48" font-family="{MONO}" font-size="12" letter-spacing="4" fill="{ACC}">PROJET {i:02d}</text>
 <text x="{W - 32}" y="48" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">● {E(p["status"])}</text>
 <text x="32" y="88" font-size="28" font-weight="800" fill="{TEXT}">{E(p["name"])}</text>
 {desc}
 {pills}
</g>
<polygon points="{hexpts(W - 44, 92, 14)}" fill="none" stroke="#3a4454" stroke-width="1.5"/>
<polygon points="{hexpts(W - 44, 92, 5)}" fill="{ACC}"/>
</svg>'''


def footer(c):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 90" width="1200" height="90">
<rect x="0" y="44" width="560" height="1" fill="#2a3240"/><rect x="640" y="44" width="560" height="1" fill="#2a3240"/>
<polygon points="{hexpts(600, 44, 14)}" fill="none" stroke="{SOFT}" stroke-width="1.5"/>
<polygon points="{hexpts(600, 44, 5)}" fill="{ACC}"/>
<text x="1194" y="80" text-anchor="end" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{MUTED}">// {E(c["motto"])}</text>
</svg>'''


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    out = {"hero.svg": hero(CONFIG), "footer.svg": footer(CONFIG)}
    for i, p in enumerate(CONFIG["projects"], 1):
        out[f"project-{i}.svg"] = project(p, i)
    for f, svg in out.items():
        open(f"assets/{f}", "w", encoding="utf-8").write(svg)
    print("OK :", ", ".join(out))
