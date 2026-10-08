"""Render a blueprint-style "spec sheet" of live GitHub stats.

Run in CI:  GITHUB_TOKEN=... python3 scripts/gen_stats.py <user> <out.svg>
Offline:    python3 scripts/gen_stats.py <user> <out.svg> --sample
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from xml.sax.saxutils import escape

INK, ACCENT, CYAN = "#cfe8ff", "#ffb703", "#5ee7ff"
BG0, BG1 = "#06203f", "#0b3a6b"
MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',monospace"

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}
"""


def fetch(login):
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(f"GraphQL errors: {payload['errors']}")
    return payload["data"]["user"]


def sample():
    rnd = random.Random(7)
    today = dt.date.today()
    start = today - dt.timedelta(days=364)
    days = [{"date": (start + dt.timedelta(d)).isoformat(),
             "contributionCount": max(0, int(rnd.gauss(2, 3)))} for d in range(365)]
    weeks = [{"contributionDays": days[i:i + 7]} for i in range(0, 365, 7)]
    return {
        "createdAt": "2024-09-16T03:55:24Z",
        "followers": {"totalCount": 12}, "pullRequests": {"totalCount": 8}, "issues": {"totalCount": 5},
        "repositories": {"totalCount": 6, "nodes": [
            {"stargazerCount": 3, "forkCount": 1, "languages": {"edges": [
                {"size": 52000, "node": {"name": "Python", "color": "#3572A5"}},
                {"size": 21000, "node": {"name": "C++", "color": "#f34b7d"}},
                {"size": 9000, "node": {"name": "JavaScript", "color": "#f1e05a"}},
                {"size": 4000, "node": {"name": "HTML", "color": "#e34c26"}},
                {"size": 1500, "node": {"name": "Shell", "color": "#89e051"}}]}}]},
        "contributionsCollection": {"totalCommitContributions": 214, "restrictedContributionsCount": 0,
                                    "contributionCalendar": {"totalContributions": 301, "weeks": weeks}},
    }


def streaks(days):
    cur = best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        best = max(best, run)
    # current streak: count back from today (today may still be empty)
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            cur += 1
        elif i == 0:
            continue
        else:
            break
    return cur, best


def render(u):
    W, H = 1200, 500
    repos = u["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    forks = sum(r["forkCount"] for r in repos)
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            size, colour = langs.get(n, (0, e["node"]["color"] or INK))
            langs[n] = (size + e["size"], colour)
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    total_size = sum(v[0] for _, v in top) or 1

    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    cur, best = streaks(days)
    since = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    age_days = (dt.datetime.now(dt.timezone.utc) - since).days

    rows = [
        ("REPOSITORIES", u["repositories"]["totalCount"]),
        ("STARS EARNED", stars),
        ("FORKS", forks),
        ("COMMITS (12 MO)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("PULL REQUESTS", u["pullRequests"]["totalCount"]),
        ("ISSUES", u["issues"]["totalCount"]),
        ("FOLLOWERS", u["followers"]["totalCount"]),
        ("IN SERVICE", f"{age_days} DAYS"),
    ]

    # --- left panel: spec table -------------------------------------------
    L = []
    x0, y0 = 50, 92
    for i, (k, v) in enumerate(rows):
        y = y0 + i * 32
        d = 0.3 + i * 0.12
        L.append(f'''<g class="fade" style="animation-delay:{d:.2f}s">
      <text x="{x0}" y="{y}" class="k">{escape(k)}</text>
      <line x1="{x0 + 190}" y1="{y - 4}" x2="{x0 + 400}" y2="{y - 4}" class="lead"/>
      <text x="{x0 + 470}" y="{y}" class="v" text-anchor="end">{escape(str(v))}</text>
    </g>''')

    # --- right panel: material composition (languages) --------------------
    R = []
    rx, ry, bw = 640, 92, 500
    if not top:
        R.append(f'<text x="{rx}" y="{ry}" class="k">NO CODE YET — STOCK ON ORDER</text>')
    for i, (name, (size, colour)) in enumerate(top):
        pct = 100 * size / total_size
        y = ry + i * 40
        d = 0.5 + i * 0.15
        w = max(4, bw * pct / 100)
        R.append(f'''<g>
      <text x="{rx}" y="{y}" class="k">{escape(name.upper())}</text>
      <text x="{rx + bw}" y="{y}" class="v" text-anchor="end">{pct:.1f}%</text>
      <rect x="{rx}" y="{y + 8}" width="{bw}" height="10" class="track"/>
      <rect x="{rx}" y="{y + 8}" width="0" height="10" fill="{colour}">
        <animate attributeName="width" from="0" to="{w:.1f}" begin="{d:.2f}s" dur="1.2s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>
      </rect>
    </g>''')

    # --- bottom: 52-week contribution histogram ---------------------------
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]][-52:]
    peak = max(weeks) or 1
    hx, hy, hh = 50, 470, 74
    slot = (W - 100) / max(1, len(weeks))
    bars = []
    for i, c in enumerate(weeks):
        h = max(1.5, hh * c / peak)
        d = 0.8 + i * 0.02
        fill = ACCENT if c == peak else CYAN
        bars.append(f'<rect x="{hx + i * slot + 2:.1f}" y="{hy}" width="{slot - 4:.1f}" height="0" fill="{fill}" fill-opacity=".85">'
                    f'<animate attributeName="height" to="{h:.1f}" begin="{d:.2f}s" dur=".6s" fill="freeze"/>'
                    f'<animate attributeName="y" to="{hy - h:.1f}" begin="{d:.2f}s" dur=".6s" fill="freeze"/></rect>')

    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub stats spec sheet">
  <title>Spec sheet — live GitHub stats</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
    <pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="{INK}" stroke-opacity=".07"/></pattern>
  </defs>
  <style>
    text {{ font-family: {MONO}; fill: {INK}; }}
    .h {{ font-size: 15px; font-weight: 800; letter-spacing: 3px; fill: {ACCENT}; }}
    .k {{ font-size: 15px; letter-spacing: 2px; fill-opacity: .8; }}
    .v {{ font-size: 18px; font-weight: 800; fill: #ffffff; }}
    .s {{ font-size: 11px; letter-spacing: 1.5px; fill-opacity: .6; }}
    .big {{ font-size: 30px; font-weight: 800; fill: {ACCENT}; }}
    .lead {{ stroke: {INK}; stroke-opacity: .35; stroke-dasharray: 2 5; }}
    .track {{ fill: {INK}; fill-opacity: .08; stroke: {INK}; stroke-opacity: .25; }}
    .fade {{ opacity: 0; animation: f .6s ease-out forwards; }}
    @keyframes f {{ to {{ opacity: 1; }} }}
  </style>
  <rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#g)"/>
  <rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="none" stroke="{INK}" stroke-width="2" stroke-opacity=".8"/>
  <path d="M600 30 V330 M30 342 H{W - 30}" stroke="{INK}" stroke-opacity=".35" stroke-dasharray="14 4 3 4"/>

  <text x="50" y="52" class="h">◤ SPEC SHEET</text>
  <text x="{W - 60}" y="328" class="s" text-anchor="end">AUTO-MEASURED · {updated}</text>
  <text x="640" y="52" class="h">◤ MATERIAL COMPOSITION</text>
  {"".join(L)}
  {"".join(R)}

  <text x="50" y="{hy - hh - 18}" class="h">◤ OUTPUT — LAST 52 WEEKS</text>
  <text x="{W - 50}" y="{hy - hh - 18}" class="s" text-anchor="end">TOTAL {cal["totalContributions"]} · STREAK {cur}D · BEST {best}D</text>
  <line x1="{hx}" y1="{hy + 0.5}" x2="{W - 50}" y2="{hy + 0.5}" stroke="{INK}" stroke-opacity=".5"/>
  {"".join(bars)}
</svg>
'''


def main():
    login, out = sys.argv[1], sys.argv[2]
    data = sample() if "--sample" in sys.argv else fetch(login)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(data))
    print("wrote", out)


if __name__ == "__main__":
    main()
