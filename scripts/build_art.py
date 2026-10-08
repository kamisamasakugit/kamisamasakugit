"""Build the hand-made animated SVGs for the profile README.

Run:  python3 scripts/build_art.py
Writes assets/hero.svg, assets/terminal.svg and assets/footer.svg.
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

INK = "#cfe8ff"      # blueprint line colour
ACCENT = "#ffb703"   # safety orange
CYAN = "#5ee7ff"
BG0, BG1 = "#06203f", "#0b3a6b"
MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',monospace"


def gear_path(cx, cy, teeth, module, phase=0.0):
    """Simple trapezoid-tooth spur gear outline + hub, as one path."""
    rp = teeth * module / 2          # pitch radius
    ro, rr = rp + module, rp - 1.25 * module
    pts = []
    step = 2 * math.pi / teeth
    for i in range(teeth):
        a = i * step + phase
        for frac, r in ((0.0, rr), (0.18, rr), (0.32, ro), (0.68, ro), (0.82, rr)):
            ang = a + frac * step
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    hub = rp * 0.28
    d += f" M{cx + hub:.1f},{cy:.1f} A{hub:.1f},{hub:.1f} 0 1,0 {cx - hub:.1f},{cy:.1f} A{hub:.1f},{hub:.1f} 0 1,0 {cx + hub:.1f},{cy:.1f}"
    return d, rp


def gear(cx, cy, teeth, module, period, direction, phase=0.0, colour=INK, spokes=5):
    d, rp = gear_path(cx, cy, teeth, module, phase)
    spoke_r = rp * 0.62
    holes = ""
    for k in range(spokes):
        a = 2 * math.pi * k / spokes + phase
        hx, hy = cx + spoke_r * math.cos(a), cy + spoke_r * math.sin(a)
        holes += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{rp * 0.16:.1f}"/>'
    to = 360 * direction
    return f'''
  <g fill="none" stroke="{colour}" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="{to} {cx} {cy}" dur="{period:.2f}s" repeatCount="indefinite"/>
    <path d="{d}" fill="{colour}" fill-opacity="0.06"/>
    <circle cx="{cx}" cy="{cy}" r="{rp * 0.86:.1f}" stroke-opacity="0.5" stroke-dasharray="4 4"/>
    {holes}
    <circle cx="{cx}" cy="{cy}" r="4" fill="{colour}"/>
  </g>'''


def frame_ticks(w, h, m):
    """Drawing-sheet zone markers (A-D down the sides, 1-8 along the top)."""
    out = []
    cols, rows = 8, 4
    for i in range(cols):
        x = m + (w - 2 * m) * (i + 0.5) / cols
        out.append(f'<text x="{x:.0f}" y="{m - 6}" class="zone">{i + 1}</text>')
        out.append(f'<text x="{x:.0f}" y="{h - m + 16}" class="zone">{i + 1}</text>')
        if i:
            xx = m + (w - 2 * m) * i / cols
            out.append(f'<line x1="{xx:.0f}" y1="{m - 18}" x2="{xx:.0f}" y2="{m}"/>')
            out.append(f'<line x1="{xx:.0f}" y1="{h - m}" x2="{xx:.0f}" y2="{h - m + 18}"/>')
    for j in range(rows):
        y = m + (h - 2 * m) * (j + 0.5) / rows
        out.append(f'<text x="{m - 9}" y="{y + 4:.0f}" class="zone">{"ABCD"[j]}</text>')
        out.append(f'<text x="{w - m + 9}" y="{y + 4:.0f}" class="zone">{"ABCD"[j]}</text>')
    return "\n    ".join(out)


def hero():
    W, H, M = 1200, 480, 26
    # three meshing gears: modules equal, centre distance = sum of pitch radii
    mod = 6
    g1 = (230, 250, 28)
    r1 = g1[2] * mod / 2
    g2_t = 16
    r2 = g2_t * mod / 2
    ang = math.radians(-38)
    g2 = (g1[0] + (r1 + r2) * math.cos(ang), g1[1] + (r1 + r2) * math.sin(ang), g2_t)
    g3_t = 12
    r3 = g3_t * mod / 2
    ang3 = math.radians(52)
    g3 = (g1[0] + (r1 + r3) * math.cos(ang3), g1[1] + (r1 + r3) * math.sin(ang3), g3_t)
    base = 24.0
    gears = (
        gear(g1[0], g1[1], g1[2], mod, base, 1, 0.0, INK, 6)
        + gear(g2[0], g2[1], g2[2], mod, base * g2_t / g1[2], -1, math.pi / g2_t, CYAN, 5)
        + gear(g3[0], g3[1], g3[2], mod, base * g3_t / g1[2], -1, math.pi / g3_t + 0.1, ACCENT, 4)
    )

    roles = ["MAKER", "DEVELOPER", "GUNMAKER", "BUILDER OF THINGS"]
    cycle = 3.0 * len(roles)
    role_svg = ""
    for i, r in enumerate(roles):
        s = i / len(roles)
        e = (i + 1) / len(roles)
        kt = f"0;{s:.4f};{s + 0.02:.4f};{e - 0.02:.4f};{e:.4f};1"
        role_svg += f'''
    <text x="0" y="0" class="role" opacity="0">{escape(r)}
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite"/>
    </text>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="SAKU — Maker, Developer, Gunmaker from Thailand">
  <title>SAKU — Maker · Developer · Gunmaker</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/>
    </linearGradient>
    <pattern id="minor" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M20 0H0V20" fill="none" stroke="{INK}" stroke-opacity="0.07"/>
    </pattern>
    <pattern id="major" width="100" height="100" patternUnits="userSpaceOnUse">
      <path d="M100 0H0V100" fill="none" stroke="{INK}" stroke-opacity="0.16"/>
    </pattern>
    <linearGradient id="laser" x1="0" x2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
      <stop offset="0.85" stop-color="{CYAN}" stop-opacity="0.18"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0.9"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.25"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    text {{ font-family: {MONO}; fill: {INK}; }}
    .zone {{ font-size: 10px; text-anchor: middle; fill-opacity: .6; }}
    .ticks line {{ stroke: {INK}; stroke-opacity: .5; }}
    .name {{ font-size: 132px; font-weight: 800; letter-spacing: 18px; fill: {INK}; fill-opacity: 0;
             stroke: {INK}; stroke-width: 2; stroke-dasharray: 900; stroke-dashoffset: 900;
             animation: draw 3.2s ease-out .3s forwards, fill 1.2s ease-in 2.6s forwards; }}
    .role {{ font-size: 30px; font-weight: 700; letter-spacing: 6px; fill: {ACCENT}; }}
    .label {{ font-size: 12px; letter-spacing: 2px; fill-opacity: .75; }}
    .tb {{ font-size: 11px; letter-spacing: 1px; }}
    .tbv {{ font-size: 13px; font-weight: 700; fill: #fff; }}
    .dim {{ stroke: {INK}; stroke-opacity: .7; fill: none; }}
    .fade {{ opacity: 0; animation: fadein 1s ease-out forwards; }}
    .blink {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    @keyframes fill {{ to {{ fill-opacity: 1; stroke-opacity: .35; }} }}
    @keyframes fadein {{ to {{ opacity: 1; }} }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
  </style>

  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#minor)"/>
  <rect width="{W}" height="{H}" fill="url(#major)"/>

  <!-- sheet frame -->
  <rect x="{M - 18}" y="{M - 18}" width="{W - 2 * M + 36}" height="{H - 2 * M + 36}" fill="none" stroke="{INK}" stroke-opacity=".55"/>
  <rect x="{M}" y="{M}" width="{W - 2 * M}" height="{H - 2 * M}" fill="none" stroke="{INK}" stroke-width="2" stroke-opacity=".85"/>
  <g class="ticks">
    {frame_ticks(W, H, M)}
  </g>

  <!-- gear train -->
  <circle cx="{g1[0]}" cy="{g1[1]}" r="190" fill="url(#glow)"/>
  <g filter="url(#soft)">{gears}
  </g>
  <!-- centre-line crosshairs -->
  <g stroke="{INK}" stroke-opacity=".35" stroke-dasharray="14 4 3 4">
    <line x1="{g1[0] - 130}" y1="{g1[1]}" x2="{g1[0] + 130}" y2="{g1[1]}"/>
    <line x1="{g1[0]}" y1="{g1[1] - 130}" x2="{g1[0]}" y2="{g1[1] + 130}"/>
  </g>
  <text x="{g1[0] - 120}" y="{g1[1] + 150}" class="label fade" style="animation-delay:1.5s">Z1=28  Z2=16  Z3=12  m=6</text>
  <text x="{g1[0] - 120}" y="{g1[1] + 168}" class="label fade" style="animation-delay:1.8s">DETAIL A — DRIVE TRAIN</text>

  <!-- name -->
  <text x="470" y="220" class="name">SAKU</text>

  <!-- dimension line under name -->
  <g class="fade" style="animation-delay:2.4s">
    <path class="dim" d="M470 250 v22 M935 250 v22 M478 262 H927"/>
    <path d="M470 262 l12 -5 v10 z M935 262 l-12 -5 v10 z" fill="{INK}"/>
    <rect x="626" y="253" width="148" height="18" fill="{BG1}"/>
    <text x="700" y="266" text-anchor="middle" class="label">MAKER · DEV · TH</text>
  </g>

  <!-- rotating role -->
  <g transform="translate(470 330)">
    <text x="0" y="0" class="label" dy="-38" opacity=".8">// SPECIALISATION</text>{role_svg}
  </g>
  <rect x="470" y="342" width="22" height="4" fill="{ACCENT}" class="blink"/>

  <!-- drafting notes -->
  <g transform="translate({W - M - 330} {M + 34})" class="fade" style="animation-delay:3.4s">
    <text class="label" x="0" y="0">NOTES:</text>
    <text class="label" x="0" y="20">1. ALL DIMENSIONS IN IDEAS.</text>
    <text class="label" x="0" y="40">2. TOLERANCE: ±0 EXCUSES.</text>
    <text class="label" x="0" y="60">3. BUILT, NOT BOUGHT.</text>
  </g>

  <!-- title block -->
  <g transform="translate({W - M - 330} {H - M - 96})" class="fade" style="animation-delay:3s">
    <rect width="330" height="96" fill="{BG0}" fill-opacity=".85" stroke="{INK}" stroke-width="1.5"/>
    <path d="M0 32 H330 M0 64 H330 M110 0 V96 M220 32 V96" stroke="{INK}" stroke-opacity=".7"/>
    <text x="10" y="14" class="tb" fill-opacity=".7">DRAWN BY</text><text x="10" y="27" class="tbv">SAKU</text>
    <text x="120" y="14" class="tb" fill-opacity=".7">PROJECT</text><text x="120" y="27" class="tbv">@kamisamasakugit</text>
    <text x="10" y="46" class="tb" fill-opacity=".7">ORIGIN</text><text x="10" y="59" class="tbv">THAILAND</text>
    <text x="120" y="46" class="tb" fill-opacity=".7">SCALE</text><text x="120" y="59" class="tbv">1 : 1</text>
    <text x="230" y="46" class="tb" fill-opacity=".7">SHEET</text><text x="230" y="59" class="tbv">01 / 01</text>
    <text x="10" y="78" class="tb" fill-opacity=".7">DWG NO.</text><text x="10" y="91" class="tbv">SK-0001</text>
    <text x="120" y="78" class="tb" fill-opacity=".7">MATERIAL</text><text x="120" y="91" class="tbv">CODE+STEEL</text>
    <text x="230" y="78" class="tb" fill-opacity=".7">REV</text><text x="230" y="91" class="tbv" fill="{ACCENT}" style="fill:{ACCENT}">A</text>
  </g>

  <!-- laser scan sweep -->
  <g>
    <rect x="-160" y="{M}" width="160" height="{H - 2 * M}" fill="url(#laser)">
      <animate attributeName="x" values="-160;{W};{W}" keyTimes="0;0.55;1" dur="7s" repeatCount="indefinite"/>
    </rect>
  </g>

  <!-- wandering crosshair cursor -->
  <g stroke="{ACCENT}" stroke-width="1.2" fill="none" opacity=".9">
    <animateTransform attributeName="transform" type="translate"
      values="560 120; 880 150; 1010 300; 700 380; 520 300; 560 120" dur="16s" repeatCount="indefinite"/>
    <circle r="9"/><path d="M-18 0 H-5 M5 0 H18 M0 -18 V-5 M0 5 V18"/>
  </g>
</svg>
'''
    (OUT / "hero.svg").write_text(svg, encoding="utf-8")


def terminal():
    W = 1200
    lines = [
        ("cmd", "whoami"),
        ("out", "saku  —  maker / developer / gunmaker"),
        ("cmd", "cat ~/.location"),
        ("out", "Thailand  (UTC+7)"),
        ("cmd", "ls ~/workshop"),
        ("dir", "code/   firmware/   cad/   prototypes/   tools/   ideas.txt"),
        ("cmd", "cat ideas.txt | wc -l"),
        ("out", "∞"),
        ("cmd", "./build --everything"),
        ("bar", ""),
        ("ok", "✔ ready. let's make something."),
    ]
    LH, TOP, LEFT = 30, 78, 40
    H = TOP + LH * len(lines) + 40
    CW = 12.0          # approx glyph advance at 20px mono
    total = 0.0
    t = 0.6
    body = []
    for idx, (kind, txt) in enumerate(lines):
        y = TOP + idx * LH
        if kind == "cmd":
            prompt = '<tspan class="p">saku@workshop</tspan><tspan class="w">:</tspan><tspan class="d">~</tspan><tspan class="w">$ </tspan>'
            n = len(txt)
            dur = max(0.4, n * 0.06)
            prompt_w = CW * 17 + 2
            # discrete typing: the clip grows one glyph at a time; last step opens fully
            vals = ";".join(f"{prompt_w + k * CW:.1f}" for k in range(n)) + f";{W:.0f}"
            body.append(f'''
    <g opacity="0"><set attributeName="opacity" to="1" begin="loop.begin+{t:.2f}s" fill="freeze"/>
      <clipPath id="c{idx}"><rect x="{LEFT - 4}" y="{y - 24}" height="32" width="{prompt_w:.1f}">
        <animate attributeName="width" values="{vals}" calcMode="discrete" begin="loop.begin+{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>
      </rect></clipPath>
      <text x="{LEFT}" y="{y}" clip-path="url(#c{idx})">{prompt}<tspan class="w">{escape(txt)}</tspan></text>
    </g>''')
            t += dur + 0.35
        elif kind == "bar":
            segs = 30
            seg_w = 14
            dur = 2.0
            rects = ""
            for k in range(segs):
                bt = t + dur * k / segs
                rects += f'<rect x="{LEFT + 14 + k * (seg_w + 3)}" y="{y - 16}" width="{seg_w}" height="18" fill="#5ee7ff" opacity="0"><set attributeName="opacity" to="1" begin="loop.begin+{bt:.2f}s" fill="freeze"/></rect>'
            body.append(f'''
    <g opacity="0"><set attributeName="opacity" to="1" begin="loop.begin+{t:.2f}s" fill="freeze"/>
      <text x="{LEFT}" y="{y}" class="w">[</text>{rects}
      <text x="{LEFT + 14 + segs * (seg_w + 3) + 4}" y="{y}" class="w">]</text>
      <text x="{LEFT + 14 + segs * (seg_w + 3) + 30}" y="{y}" class="o" opacity="0">100%<set attributeName="opacity" to="1" begin="loop.begin+{t + dur:.2f}s" fill="freeze"/></text>
    </g>''')
            t += dur + 0.3
        else:
            cls = {"out": "o", "dir": "dir", "ok": "ok"}[kind]
            body.append(f'''
    <text x="{LEFT}" y="{y}" class="{cls}" opacity="0">{escape(txt)}<set attributeName="opacity" to="1" begin="loop.begin+{t:.2f}s" fill="freeze"/></text>''')
            t += 0.45
    total = t + 5.0
    last_y = TOP + (len(lines) - 1) * LH

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal: saku — maker, developer, gunmaker from Thailand">
  <title>saku@workshop</title>
  <defs>
    <linearGradient id="tbg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#071a33"/><stop offset="1" stop-color="#04101f"/>
    </linearGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="2" fill="#ffffff" fill-opacity=".025"/>
    </pattern>
  </defs>
  <style>
    text {{ font-family: {MONO}; font-size: 20px; fill: #d7e9ff; white-space: pre; }}
    .p {{ fill: #7ee787; font-weight: 700; }} .d {{ fill: #79c0ff; font-weight: 700; }} .w {{ fill: #e6edf3; }}
    .o {{ fill: #a5b4cb; }} .dir {{ fill: #79c0ff; }} .ok {{ fill: #ffb703; font-weight: 700; }}
    .title {{ font-size: 14px; fill: #8aa4c4; }}
  </style>
  <!-- master clock: everything restarts each loop -->
  <rect width="0" height="0"><animate id="loop" attributeName="x" from="0" to="0" begin="0s;loop.end" dur="{total:.2f}s"/></rect>

  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="url(#tbg)" stroke="#5ee7ff" stroke-opacity=".35" stroke-width="2"/>
  <rect x="1" y="1" width="{W - 2}" height="40" rx="14" fill="#0e2a4f"/>
  <rect x="1" y="28" width="{W - 2}" height="13" fill="#0e2a4f"/>
  <circle cx="28" cy="21" r="7" fill="#ff5f57"/><circle cx="52" cy="21" r="7" fill="#febc2e"/><circle cx="76" cy="21" r="7" fill="#28c840"/>
  <text x="{W / 2}" y="26" text-anchor="middle" class="title">saku@workshop: ~ — zsh — 120×{len(lines)}</text>
  {''.join(body)}
  <rect x="{LEFT}" y="{last_y + 12}" width="12" height="22" fill="#e6edf3" opacity="0">
    <set attributeName="opacity" to="1" begin="loop.begin+{t:.2f}s"/>
    <animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
  </rect>
  <rect x="1" y="41" width="{W - 2}" height="{H - 42}" rx="14" fill="url(#scan)"/>
</svg>
'''
    # each loop: hide everything again, then let the timed <set>s reveal it
    svg = svg.replace('<set attributeName="opacity" to="1" begin="loop.begin+',
                      '<set attributeName="opacity" to="0" begin="loop.begin" fill="freeze"/>'
                      '<set attributeName="opacity" to="1" begin="loop.begin+')
    svg = svg.replace('<animate attributeName="width"',
                      '<set attributeName="width" to="0" begin="loop.begin" fill="freeze"/>'
                      '<animate attributeName="width"')
    (OUT / "terminal.svg").write_text(svg, encoding="utf-8")


def footer():
    W, H = 1200, 90
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="End of drawing">
  <style>
    text {{ font-family: {MONO}; fill: {INK}; font-size: 13px; letter-spacing: 4px; }}
    .run {{ stroke-dasharray: 18 10; animation: run 1.2s linear infinite; }}
    @keyframes run {{ to {{ stroke-dashoffset: -28; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="10" fill="{BG0}"/>
  <line x1="40" y1="45" x2="{W - 40}" y2="45" stroke="{CYAN}" stroke-opacity=".5" stroke-width="2" class="run"/>
  <rect x="{W / 2 - 230}" y="30" width="460" height="30" fill="{BG0}"/>
  <text x="{W / 2}" y="50" text-anchor="middle">END OF DRAWING · SK-0001 · <tspan fill="{ACCENT}">KEEP BUILDING</tspan></text>
  <path d="M40 30 v30 M{W - 40} 30 v30" stroke="{INK}" stroke-width="2"/>
</svg>
'''
    (OUT / "footer.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    hero()
    terminal()
    footer()
    print("wrote hero.svg, terminal.svg, footer.svg to", OUT)
