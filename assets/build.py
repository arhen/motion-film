"""Builds the README diagrams as light and dark SVGs. No dependencies.

    python3 assets/build.py
"""

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent
W = 1200
SANS = "ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

LIGHT = dict(bg="#FBFAF7", panel="#FFFFFF", ink="#16130F", muted="#6B655C", faint="#A8A298", line="#E6E1D8",
             accent="#3355FF", voice="#0E9F8A", music="#D98E04", sfx="#E5484D", tint="#EEF1FF", device="#1F1B16")
DARK = dict(bg="#0E0D0B", panel="#171511", ink="#F3EFE7", muted="#A49E93", faint="#6E685F", line="#2B2822",
            accent="#7B93FF", voice="#2CC4AC", music="#F2B33D", sfx="#FF6B6F", tint="#1B2040", device="#3A352D")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=18, fill="#000", weight=400, mono=False, anchor="start", ls=0, opacity=1):
    fam = MONO if mono else SANS
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" opacity="{opacity}">{esc(s)}</text>')


def rect(x, y, w, h, fill="none", stroke="none", rx=0, sw=1, opacity=1, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}" {extra}/>'


def svg(h, body, title, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{esc(title)}">'
            f"<title>{esc(title)}</title><style>{style}</style>{body}</svg>\n")


def card(h, P):
    return rect(1, 1, W - 2, h - 2, P["bg"], P["line"], rx=24, sw=2)


def heading(P, title, sub):
    return text(64, 84, title, 34, P["ink"], 700, ls=-0.6) + text(64, 122, sub, 19, P["muted"])


# ---------------------------------------------------------------- hero: one clock drives every lane

def hero(P):
    H, X0, X1, SEC = 600, 210, 1108, 20.0
    px = (X1 - X0) / SEC
    X = lambda t: X0 + t * px
    b = [card(H, P)]
    b.append(text(64, 92, "AGENT SKILLS FOR REMOTION", 15, P["accent"], 700, mono=True, ls=1.6))
    b.append(text(62, 166, "motion-film", 70, P["ink"], 750, ls=-2.4))
    b.append(text(64, 212, "Motion videos in code, built like a product:", 23, P["muted"]))
    b.append(text(64, 244, "one clock, one design system, critique and evidence.", 23, P["muted"]))

    cx, cy, cw, ch = 748, 56, 388, 200
    b.append(rect(cx, cy, cw, ch, P["panel"], P["line"], rx=16, sw=1.5))
    b.append(text(cx + 22, cy + 34, "clock.json", 15, P["faint"], 600, mono=True))
    lines = [
        [("{", P["muted"])],
        [('  "bpm": ', P["muted"]), ("96", P["music"]), (",", P["muted"])],
        [('  "vo": [{"id": ', P["muted"]), ('"V1"', P["voice"]), (', "at": ', P["muted"]), ("0.6", P["voice"]), ("}],", P["muted"])],
        [('  "cues": {"turn": ', P["muted"]), ("6.2", P["accent"]), (",", P["muted"])],
        [('           "insight": ', P["muted"]), ("9.5", P["accent"]), ("}", P["muted"])],
        [("}", P["muted"])],
    ]
    for i, parts in enumerate(lines):
        spans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in parts)
        b.append(f'<text x="{cx + 22}" y="{cy + 66 + i * 23}" font-family="{MONO}" font-size="16" xml:space="preserve">{spans}</text>')

    py, ph = 288, 282
    b.append(rect(64, py, W - 128, ph, P["panel"], P["line"], rx=18, sw=1.5))
    lanes = [("Picture", 376, P["accent"]), ("Voice", 422, P["voice"]), ("Music", 468, P["music"]), ("SFX", 514, P["sfx"])]
    for name, y, col in lanes:
        b.append(f'<circle cx="94" cy="{y + 17}" r="5" fill="{col}"/>')
        b.append(text(108, y + 23, name, 17, P["ink"], 600))
    for s in range(0, 21, 2):
        b.append(f'<line x1="{X(s):.1f}" y1="356" x2="{X(s):.1f}" y2="362" stroke="{P["faint"]}" stroke-width="1.5"/>')
        b.append(text(X(s), 349, f"{s}s" if s in (0, 20) else str(s), 13, P["faint"], 500, mono=True, anchor="middle"))

    scenes = [("opening", 0, 3.2), ("problem", 3.2, 6.2), ("turn", 6.2, 9.5), ("insight", 9.5, 12.8), ("action", 12.8, 17.6), ("sign-off", 17.6, 20)]
    for i, (nm, a, z) in enumerate(scenes):
        b.append(rect(X(a) + 2, 376, X(z) - X(a) - 4, 34, P["accent"], rx=8, opacity=0.14 + 0.06 * (i % 2)))
        b.append(text(X(a) + 12, 398, nm, 14, P["accent"], 600))
    for vid, a, z in [("V1", 0.6, 3.0), ("V2", 4.0, 6.0), ("V3", 8.6, 11.4), ("V4", 12.9, 15.6)]:
        b.append(rect(X(a), 422, X(z) - X(a), 34, P["voice"], rx=17, opacity=0.16))
        n = int((X(z) - X(a) - 44) / 6)
        for k in range(n):
            amp = 4 + 9 * abs(math.sin(k * 1.7 + a * 3.1)) * (0.55 + 0.45 * math.sin(k * 0.45 + a))
            x = X(a) + 36 + k * 6
            b.append(f'<line x1="{x:.1f}" y1="{439 - amp:.1f}" x2="{x:.1f}" y2="{439 + amp:.1f}" stroke="{P["voice"]}" stroke-width="2.4" stroke-linecap="round"/>')
        b.append(text(X(a) + 12, 444, vid, 13, P["voice"], 700, mono=True))
    pts = []
    for k in range(0, 451):
        t = k / 450 * SEC
        env = 0.35 + 0.65 * min(1, max(0, (t - 2) / 3)) - (0.4 if 17.4 < t < 18 else 0)
        amp = 13 * env * (0.6 + 0.4 * abs(math.sin(t * 9.1)) ) * (0.75 + 0.25 * math.cos(t * 2 * math.pi * 96 / 60))
        pts.append((X(t), amp))
    top = " ".join(f"{x:.1f},{485 - a:.1f}" for x, a in pts)
    bot = " ".join(f"{x:.1f},{485 + a:.1f}" for x, a in reversed(pts))
    b.append(f'<polygon points="{top} {bot}" fill="{P["music"]}" opacity="0.22"/>')
    beat = 60 / 96
    for k in range(int(SEC / beat) + 1):
        x = X(k * beat)
        bar = k % 4 == 0
        b.append(f'<line x1="{x:.1f}" y1="{470 if bar else 476}" x2="{x:.1f}" y2="{500 if bar else 494}" stroke="{P["music"]}" stroke-width="{2.2 if bar else 1.2}" opacity="{0.95 if bar else 0.6}"/>')

    sfx = [(1.2, 7), (1.6, 7), (2.0, 7), (2.4, 7), (6.2, 10), (9.5, 10), (12.8, 10), (13.2, 8), (17.6, 10)]
    for t, r in sfx:
        x = X(t)
        b.append(f'<path class="hit" style="animation-delay:{t / SEC * 10:.3f}s" d="M{x:.1f} {531 - r} L{x + r} 531 L{x:.1f} {531 + r} L{x - r} 531 Z" fill="{P["sfx"]}"/>')

    for nm, t in [("turn", 6.2), ("insight", 9.5), ("action", 12.8)]:
        x = X(t)
        b.append(f'<line class="cf" style="animation-delay:{t / SEC * 10:.3f}s" x1="{x:.1f}" y1="330" x2="{x:.1f}" y2="552" stroke="{P["ink"]}" stroke-width="1.5" stroke-dasharray="4 5" opacity="0.45"/>')
        label = f"{nm} {t:.1f}s"
        w = len(label) * 8.6 + 18
        b.append(rect(x - w / 2, 300, w, 24, P["ink"], rx=12))
        b.append(text(x, 317, label, 13, P["panel"], 600, mono=True, anchor="middle"))

    b.append(f'<g class="ph"><line x1="{X0}" y1="334" x2="{X0}" y2="554" stroke="{P["ink"]}" stroke-width="2.4"/>'
             f'<path d="M{X0 - 7} 328 L{X0 + 7} 328 L{X0} 338 Z" fill="{P["ink"]}"/></g>')
    style = (
        ".ph{animation:ph 10s linear infinite}"
        f"@keyframes ph{{from{{transform:translateX(0px)}}to{{transform:translateX({X1 - X0}px)}}}}"
        ".hit{transform-box:fill-box;transform-origin:center;animation:hit 10s linear infinite}"
        "@keyframes hit{0%{transform:scale(2);opacity:1}8%{transform:scale(1);opacity:.85}100%{transform:scale(1);opacity:.85}}"
        ".cf{animation:cf 10s linear infinite}"
        "@keyframes cf{0%{opacity:1}10%{opacity:.45}100%{opacity:.45}}"
        f"@media (prefers-reduced-motion:reduce){{.ph,.hit,.cf{{animation:none}}.ph{{transform:translateX({9.5 * px:.0f}px)}}}}"
    )
    return svg(H, "".join(b), "motion-film: picture, voice, music and sound effects on one clock", style)


# ---------------------------------------------------------------- pipeline: eight phases, eight gates

def pipeline(P):
    H = 700
    b = [card(H, P), heading(P, "Nine skills, eight gates", "Each phase has an output and a gate. Work moves on only when the gate passes.")]
    phases = [
        ("0", "Preflight", "motion-film", ["tools, keys, fonts,", "voices present"], ["every check passes"], []),
        ("1", "Brief", "motion-film-brief", ["kind, story, script,", "direction sheet, clock"], ["owner agrees on kind,", "story, length, voice"], []),
        ("2", "Design system", "motion-film-system", ["theme, components,", "catalogue board"], ["catalogue passes one", "critique round"], ["impeccable", "browser-use"]),
        ("3", "Voice or footage", "motion-film-voice | footage", ["AI or own voice, or a", "cut of your footage"], ["speech-to-text matches,", "no cut inside a word"], []),
        ("4", "Music", "motion-film-score", ["synthesized score or", "a supplied track"], ["loudness met, voice", "clear of the bed"], []),
        ("5", "Picture", "motion-film-build", ["Remotion compositions,", "one per format"], ["key frames pass one", "critique round"], ["animate"]),
        ("6", "Critique and QA", "motion-film-qa", ["evidence pack from", "the real file"], ["all checks pass,", "fixed in one batch"], ["impeccable", "review-animations"]),
        ("7", "Deliver", "motion-film-deliver", ["renders, encodes,", "posters, README"], ["files probe right,", "no media in git"], []),
    ]
    cw, chh, gap = 262, 224, 20
    x0 = (W - (4 * cw + 3 * gap)) / 2
    for i, (num, name, skill, out, gate, chips) in enumerate(phases):
        r, c = divmod(i, 4)
        x, y = x0 + c * (cw + gap), 160 + r * (chh + 46)
        b.append(rect(x, y, cw, chh, P["panel"], P["line"], rx=16, sw=1.5))
        b.append(f'<circle cx="{x + 34}" cy="{y + 34}" r="16" fill="{P["accent"]}"/>')
        b.append(text(x + 34, y + 40, num, 17, P["panel"], 700, mono=True, anchor="middle"))
        b.append(text(x + 60, y + 40, name, 21, P["ink"], 700, ls=-0.3))
        b.append(text(x + 20, y + 74, skill, 14 if len(skill) < 24 else 12.5, P["faint"], 500, mono=True))
        for k, line in enumerate(out):
            b.append(text(x + 20, y + 104 + k * 22, line, 17, P["muted"]))
        b.append(rect(x + 20, y + 144, 44, 20, P["tint"], rx=10))
        b.append(text(x + 42, y + 158, "gate", 12, P["accent"], 700, mono=True, anchor="middle"))
        for k, line in enumerate(gate):
            b.append(text(x + 72, y + 159 + k * 21, line, 15, P["ink"], 500))
        cxp = x + 20
        for chip in chips:
            w = len(chip) * 7.3 + 16
            b.append(rect(cxp, y + chh - 34, w, 22, "none", P["line"], rx=11, sw=1.5))
            b.append(text(cxp + w / 2, y + chh - 19, chip, 12, P["muted"], 600, mono=True, anchor="middle"))
            cxp += w + 8
        if c < 3:
            ax = x + cw + gap / 2
            b.append(f'<path d="M{ax - 5} {y + chh / 2 - 7} L{ax + 3} {y + chh / 2} L{ax - 5} {y + chh / 2 + 7}" fill="none" stroke="{P["faint"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
    y1, y2 = 160 + chh, 160 + chh + 46
    xa, xb = x0 + 3 * (cw + gap) + cw / 2, x0 + cw / 2
    ym = (y1 + y2) / 2
    b.append(f'<path d="M{xa} {y1 + 4} L{xa} {ym} L{xb} {ym} L{xb} {y2 - 8}" fill="none" stroke="{P["faint"]}" stroke-width="2" stroke-dasharray="5 6"/>')
    b.append(f'<path d="M{xb - 6} {y2 - 12} L{xb} {y2 - 4} L{xb + 6} {y2 - 12}" fill="none" stroke="{P["faint"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(H, "".join(b), "The eight phases with their outputs and gates")


# ---------------------------------------------------------------- formats: one layout per format

def formats(P):
    H = 640
    b = [card(H, P), heading(P, "One story, one layout per format", "Never a crop. Type minimums come from the size the video is seen at; vertical keeps clear of the app's own interface.")]
    fx, fy, fw, fh = 64, 168, 600, 338
    b.append(rect(fx, fy, fw, fh, P["panel"], P["line"], rx=10, sw=2))
    b.append(rect(fx + 40, fy + 46, 150, 228, P["device"], rx=22))
    b.append(rect(fx + 50, fy + 60, 130, 200, P["accent"], rx=14, opacity=0.25))
    for k in range(3):
        b.append(rect(fx + 230, fy + 60 + k * 66, 320, 52, P["accent"], rx=12, opacity=0.14 + 0.06 * k))
    capw = 300
    b.append(rect(fx + (fw - capw) / 2, fy + fh * 0.937 - 22, capw, 40, P["tint"], P["line"], rx=12))
    b.append(text(fx + fw / 2, fy + fh * 0.937 + 5, "Captions are the voice-over", 16, P["ink"], 600, anchor="middle"))
    b.append(text(fx, fy + fh + 34, "16:9  1920 × 1080", 17, P["ink"], 700, mono=True))
    b.append(text(fx, fy + fh + 60, "Seen in a ~900 px card (× 0.47): captions ≥ 56 px, UI text ≥ 26 px.", 16, P["muted"]))

    vh = 400
    vw = vh * 9 / 16
    vx, vy = 700, 160
    b.append(rect(vx, vy, vw, vh, P["panel"], P["line"], rx=12, sw=2))
    for k in range(2):
        for j in range(2):
            b.append(rect(vx + 22 + j * 92, vy + 82 + k * 92, 80, 80, P["accent"], rx=12, opacity=0.18 + 0.05 * (k + j)))
    b.append(rect(vx + 22, vy + 58, 140, 14, P["device"], rx=7))
    capw = vw * 0.66
    b.append(rect(vx + (vw - capw) / 2, vy + vh * 0.7 - 18, capw, 34, P["tint"], P["line"], rx=10))
    b.append(text(vx + vw / 2, vy + vh * 0.7 + 4, "Shorter chunks", 14, P["ink"], 600, anchor="middle"))
    zones = [(0, 0, 1, 0.115), (0.87, 0.35, 1, 0.75), (0, 0.75, 1, 1)]
    for x0, y0, x1, y1 in zones:
        b.append(rect(vx + x0 * vw, vy + y0 * vh, (x1 - x0) * vw, (y1 - y0) * vh, P["sfx"], rx=0, opacity=0.16))
    b.append(rect(vx, vy, vw, vh, "none", P["line"], rx=12, sw=2))
    lx = vx + vw + 36
    notes = [
        (vy + vh * 0.06, "status bar, tabs"),
        (vy + vh * 0.55, "like, comment, share"),
        (vy + vh * 0.88, "username, caption, music"),
    ]
    for y, label in notes:
        b.append(f'<line x1="{vx + vw + 6}" y1="{y:.1f}" x2="{lx - 8}" y2="{y:.1f}" stroke="{P["sfx"]}" stroke-width="1.5" opacity="0.7"/>')
        b.append(text(lx, y + 6, label, 15, P["sfx"], 600))
    b.append(text(vx, vy + vh + 34, "9:16  1080 × 1920", 17, P["ink"], 700, mono=True))
    b.append(text(vx, vy + vh + 60, "Full width on a phone (× 0.36): captions ≥ 72 px.", 16, P["muted"]))
    return svg(H, "".join(b), "Landscape and vertical layouts with caption bands and safe zones")


# ---------------------------------------------------------------- music: snap cues onto a supplied track

def music(P):
    H = 500
    b = [card(H, P), heading(P, "Bring your own track", "beats.py reads the beat grid and the drop. snap.py moves every cue onto a beat. The mixer ducks the song under the voice.")]
    X0, X1, SEC, bpm = 120, 1136, 9.0, 128
    px = (X1 - X0) / SEC
    X = lambda t: X0 + t * px
    beat = 60 / bpm
    drop = 1.875
    b.append(rect(64, 160, W - 128, 300, P["panel"], P["line"], rx=18, sw=1.5))
    pts = []
    for k in range(0, 601):
        t = k / 600 * SEC
        env = 0.22 if t < drop else 1.0
        pulse = math.exp(-((t - drop) % beat) * 7) if t >= drop else 0.3
        amp = 52 * env * (0.45 + 0.55 * pulse) * (0.8 + 0.2 * abs(math.sin(t * 31)))
        pts.append((X(t), amp))
    top = " ".join(f"{x:.1f},{360 - a:.1f}" for x, a in pts)
    bot = " ".join(f"{x:.1f},{360 + a:.1f}" for x, a in reversed(pts))
    b.append(f'<polygon points="{top} {bot}" fill="{P["music"]}" opacity="0.3"/>')
    for k in range(int(SEC / beat) + 1):
        t = k * beat
        x = X(t)
        bar = k % 4 == 0
        b.append(f'<line x1="{x:.1f}" y1="{246 if bar else 262}" x2="{x:.1f}" y2="430" stroke="{P["ink"] if bar else P["faint"]}" stroke-width="{1.8 if bar else 1}" opacity="{0.55 if bar else 0.45}"/>')
        if bar:
            b.append(text(x + 6, 258, f"bar {k // 4 + 1}", 13, P["muted"], 600, mono=True))
    xd = X(drop)
    b.append(rect(xd - 2, 188, 188, 26, P["music"], rx=13))
    b.append(text(xd + 92, 206, "drop: video starts here", 14, P["panel"], 700, anchor="middle"))
    for name, a in [("turn", 2.70), ("insight", 4.12), ("action", 5.55), ("result", 7.10)]:
        z = round(a / beat) * beat
        xa, xz = X(a), X(z)
        b.append(f'<circle cx="{xa:.1f}" cy="296" r="8" fill="none" stroke="{P["accent"]}" stroke-width="2" stroke-dasharray="3 3"/>')
        b.append(f'<path d="M{xa:.1f} 306 Q{(xa + xz) / 2:.1f} 322 {xz:.1f} 318" fill="none" stroke="{P["accent"]}" stroke-width="1.6" opacity="0.8"/>')
        b.append(f'<circle cx="{xz:.1f}" cy="326" r="8" fill="{P["accent"]}"/>')
        b.append(text(xz, 452, name, 14, P["accent"], 700, mono=True, anchor="middle"))
    lx = 88
    b.append(f'<circle cx="{lx}" cy="208" r="7" fill="none" stroke="{P["accent"]}" stroke-width="2" stroke-dasharray="3 3"/>')
    b.append(text(lx + 14, 213, "cue as written", 14, P["muted"]))
    b.append(f'<circle cx="{lx + 142}" cy="208" r="7" fill="{P["accent"]}"/>')
    b.append(text(lx + 156, 213, "on the beat", 14, P["muted"]))
    return svg(H, "".join(b), "A supplied track with its beat grid; cues move onto beats")


# ---------------------------------------------------------------- evidence: checks on the real file

def evidence(P):
    H = 556
    b = [card(H, P), heading(P, "Evidence, not “it rendered”", "Every check runs on the real output file. Values below were measured on real renders made with this process.")]
    checks = [
        ("Loop seam", "first vs last frame", "44.7 dB", "pass at ≥ 40 dB PSNR"),
        ("Word sync", "speech-to-text of the mix", "0.03 s", "median offset, 45/45 words heard"),
        ("Loudness", "integrated, from the MP4", "-16.0 LUFS", "web loop target -16"),
        ("True peak", "after the AAC encode", "-1.7 dB", "under the -1.5 dB ceiling"),
        ("Cue onsets", "SFX stem vs the clock", "≤ 4 ms", "pass within one frame (33 ms)"),
        ("Beat grid", "supplied track, re-read", "128.02", "BPM after the mix (track: 128)"),
    ]
    cw, chh, gap = 336, 166, 24
    x0 = (W - (3 * cw + 2 * gap)) / 2
    for i, (name, what, value, note) in enumerate(checks):
        r, c = divmod(i, 3)
        x, y = x0 + c * (cw + gap), 164 + r * (chh + gap)
        b.append(rect(x, y, cw, chh, P["panel"], P["line"], rx=16, sw=1.5))
        b.append(f'<circle cx="{x + 30}" cy="{y + 34}" r="11" fill="{P["voice"]}"/>')
        b.append(f'<path d="M{x + 24.5} {y + 34.5} L{x + 28.5} {y + 38.5} L{x + 35.5} {y + 30}" fill="none" stroke="{P["panel"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
        b.append(text(x + 52, y + 40, name, 20, P["ink"], 700))
        b.append(text(x + 52, y + 62, what, 14, P["faint"], 500))
        b.append(text(x + 22, y + 116, value, 36, P["ink"], 700, mono=True, ls=-1))
        b.append(text(x + 22, y + 146, note, 15, P["muted"]))
    return svg(H, "".join(b), "Example evidence pack: seam, sync, loudness, onsets, beat grid, frames")


for name, fn in [("hero", hero), ("pipeline", pipeline), ("formats", formats), ("music", music), ("evidence", evidence)]:
    for mode, P in [("light", LIGHT), ("dark", DARK)]:
        (OUT / f"{name}-{mode}.svg").write_text(fn(P))
print("wrote", len(list(OUT.glob("*.svg"))), "svgs to", OUT)
