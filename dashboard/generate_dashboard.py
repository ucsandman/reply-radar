#!/usr/bin/env python3
"""Regenerate dashboard.html from all radar/YYYY-MM-DD.md files.

Usage: python3 generate_dashboard.py
Reads radar/*.md (skips *-trial.md), newest first, and writes dashboard.html
at the repo root. Each opportunity card shows the post, link, why it fits,
the reply angle, and the draft reply with a copy button.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RADAR_DIR = ROOT / "radar"
OUT = ROOT / "dashboard.html"


def esc(t):
    return html.escape(t, quote=True)


def inline_md(t):
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def parse_opportunity(section):
    """Parse one '## N. @handle (...)' section into a dict."""
    lines = section.split("\n")
    header = lines[0]
    m = re.match(r"##\s+\d+\.\s+(@\S+)(?:\s+\(([^)]*)\))?", header)
    if not m:
        return None
    opp = {"handle": m.group(1), "reach": m.group(2) or "", "post": "", "link": "",
           "why": "", "angle": "", "draft": ""}
    body = "\n".join(lines[1:])

    def grab(marker):
        nonlocal body
        pat = re.compile(r"^" + re.escape(marker) + r"\s*(.*)$", re.M)
        mm = pat.search(body)
        if not mm:
            return ""
        idx = mm.start()
        rest = body[idx:].split("\n")
        paras = [rest[0][len(marker):].strip()]
        for ln in rest[1:]:
            if not ln.strip():
                break
            if re.match(r"^(Why it fits|Reply angle|\*\*Draft reply|\[Image|https?://)", ln):
                break
            paras.append(ln.strip())
        return " ".join(paras).strip()

    opp["post"] = grab("Post:")
    lm = re.search(r"^https?://\S+", body, re.M)
    if lm:
        opp["link"] = lm.group(0)
    opp["why"] = grab("Why it fits:")
    opp["angle"] = grab("Reply angle:")

    dm = re.search(r"^\*\*Draft reply:\*\*\s*$", body, re.M)
    if dm:
        draft_lines = []
        for ln in body[dm.end():].split("\n"):
            if ln.startswith("> "):
                draft_lines.append(ln[2:])
            elif ln.startswith(">"):
                draft_lines.append(ln[1:].lstrip())
            elif not ln.strip():
                if draft_lines:
                    break
            else:
                break
        opp["draft"] = "\n".join(draft_lines).strip()
    return opp


def split_sections(text):
    """Split a radar file into (heading, body) for top-level ## sections."""
    parts = re.split(r"(?m)^## ", text)
    title = parts[0].strip()
    sections = []
    for p in parts[1:]:
        nl = p.find("\n")
        heading = p[:nl].strip() if nl != -1 else p.strip()
        body = p[nl + 1:] if nl != -1 else ""
        sections.append((heading, body.strip()))
    return title, sections


def bullets(body):
    items = []
    for ln in body.split("\n"):
        ln = ln.strip()
        if ln.startswith("- "):
            items.append(ln[2:].strip())
    return items


def parse_file(path):
    text = path.read_text()
    title, sections = split_sections(text)
    day = {"date": path.stem, "title": title, "summary": [], "opps": [], "notes": [], "quiet": ""}
    for heading, body in sections:
        if re.match(r"\d+\.\s+@", heading):
            opp = parse_opportunity("## " + heading + "\n" + body)
            if opp:
                day["opps"].append(opp)
        elif heading.lower() == "scan summary":
            day["summary"] = bullets(body)
        elif heading.lower() == "notes":
            day["notes"] = bullets(body)
        elif heading.lower() == "the day was quiet":
            day["quiet"] = body
    return day


def render_opp(opp, date, idx):
    draft_id = f"draft-{date}-{idx}"
    parts = [f'<div class="card">']
    reach = f' <span class="reach">{esc(opp["reach"])}</span>' if opp["reach"] else ""
    parts.append(f'<div class="card-head"><span class="handle">{esc(opp["handle"])}</span>{reach}</div>')
    if opp["post"]:
        parts.append(f'<div class="post">{inline_md(opp["post"])}</div>')
    if opp["link"]:
        parts.append(f'<a class="postlink" href="{esc(opp["link"])}" target="_blank" rel="noopener">Open post</a>')
    if opp["why"]:
        parts.append(f'<div class="meta"><strong>Why it fits:</strong> {inline_md(opp["why"])}</div>')
    if opp["angle"]:
        parts.append(f'<div class="meta"><strong>Angle:</strong> {inline_md(opp["angle"])}</div>')
    if opp["draft"]:
        parts.append(
            f'<div class="draftbox"><div class="draftlabel">Draft reply '
            f'<button class="copybtn" onclick="copyDraft(this, \'{draft_id}\')">Copy</button></div>'
            f'<div class="draft" id="{draft_id}">{esc(opp["draft"])}</div></div>'
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_day(day):
    parts = [f'<section class="day" id="{esc(day["date"])}">']
    parts.append(f'<h2>{esc(day["date"])}</h2>')
    if day["summary"]:
        parts.append('<ul class="summary">')
        for s in day["summary"]:
            parts.append(f"<li>{inline_md(s)}</li>")
        parts.append("</ul>")
    if day["quiet"]:
        parts.append('<div class="quiet"><strong>Quiet day.</strong></div>')
        for ln in day["quiet"].split("\n"):
            ln = ln.strip()
            if ln:
                parts.append(f"<p>{inline_md(ln)}</p>")
    for i, opp in enumerate(day["opps"], 1):
        parts.append(render_opp(opp, day["date"], i))
    if day["notes"]:
        parts.append('<div class="notes"><strong>Notes</strong><ul>')
        for n in day["notes"]:
            parts.append(f"<li>{inline_md(n)}</li>")
        parts.append("</ul></div>")
    parts.append("</section>")
    return "\n".join(parts)


CSS = """
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
max-width:860px;margin:0 auto;padding:24px;color:#1a1a1a;background:#fafafa;line-height:1.55}
h1{font-size:28px;margin-bottom:4px}
.sub{color:#666;margin-bottom:28px}
.day{margin-bottom:48px;padding-bottom:24px;border-bottom:2px solid #e2e2e2}
.day h2{font-size:22px;margin-bottom:8px}
.summary{color:#444;margin:0 0 16px 20px;padding:0}
.card{background:#fff;border:1px solid #e5e5e5;border-radius:10px;padding:16px 18px;margin:14px 0}
.card-head{font-size:17px;font-weight:700;margin-bottom:6px}
.reach{color:#666;font-weight:400;font-size:14px;margin-left:8px}
.post{margin:8px 0;color:#222}
.postlink{font-size:14px}
.meta{font-size:14px;color:#444;margin-top:8px}
.draftbox{margin-top:12px;background:#f4f6f8;border:1px solid #dfe3e8;border-radius:8px;padding:12px 14px}
.draftlabel{font-size:13px;font-weight:700;color:#555;margin-bottom:6px}
.draft{white-space:pre-wrap;font-size:15px;color:#111}
.copybtn{margin-left:10px;font-size:13px;padding:3px 12px;border-radius:6px;border:1px solid #bbb;
background:#fff;cursor:pointer}
.copybtn:hover{background:#eee}
.quiet{background:#fff8e6;border:1px solid #f0dfae;border-radius:8px;padding:12px 16px;margin:12px 0}
.notes{font-size:14px;color:#444;margin-top:14px}
.notes ul{margin:6px 0 0 20px;padding:0}
"""

JS = """
function copyDraft(btn, id){
  var el = document.getElementById(id);
  var text = el.innerText;
  function done(){ var o = btn.textContent; btn.textContent = "Copied";
    setTimeout(function(){ btn.textContent = o; }, 1200); }
  function fallback(){
    var ta = document.createElement("textarea");
    ta.value = text; document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); done(); } catch(e) {}
    document.body.removeChild(ta);
  }
  if (navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(done, fallback);
  } else { fallback(); }
}
"""


def main():
    files = sorted(
        (p for p in RADAR_DIR.glob("*.md")
         if re.match(r"^\d{4}-\d{2}-\d{2}", p.stem) and "-trial" not in p.stem),
        key=lambda p: p.stem, reverse=True,
    )
    days = [parse_file(p) for p in files]
    body = "\n".join(render_day(d) for d in days) or "<p>No radar files yet.</p>"
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reply Radar Dashboard</title>
<style>{CSS}</style>
</head>
<body>
<h1>Reply Radar</h1>
<div class="sub">Daily X reply opportunities for @ucsandman. Drafts are in wes's voice; he posts them himself.</div>
{body}
<script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(page)
    total_opps = sum(len(d["opps"]) for d in days)
    print(f"Wrote {OUT} from {len(days)} radar files, {total_opps} opportunities.")


if __name__ == "__main__":
    main()
