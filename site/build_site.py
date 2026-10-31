"""Renders site/dist/index.html from site/copy.md, site/template.html, the skill files and tools.json.

    python site/build_site.py

The copy is the deliverable from the copywriter; this script only places it. The skill list and
the installed-tools list are read from the repo at build time, so the page follows the repo.
Standard library only.
"""
import datetime as dt
import html
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "dist")
DOWNLOAD = "https://github.com/six20am/workspace-blueprint/releases/latest/download/Six20AM-Workspace-Blueprint.zip"
REPO_URL = "https://github.com/six20am/workspace-blueprint"


def esc(s):
    return html.escape(s, quote=False)


def inline(s):
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\b(github\.com/[\w./-]+)", r'<a href="https://\1">\1</a>', s)
    s = s.replace("open an issue on GitHub", f'<a href="{REPO_URL}/issues">open an issue on GitHub</a>')
    return s


def md_block(text, section):
    """A small Markdown subset: #/## headings, paragraphs, - lists, 1. lists, **Q** / answer pairs, [Button]."""
    out = []
    lines = [l.rstrip() for l in text.strip().splitlines()]
    i = 0
    while i < len(lines):
        l = lines[i]
        if not l:
            i += 1; continue
        if l.startswith("# "):
            out.append(f"<h1>{inline(l[2:])}</h1>")
        elif l.startswith("## "):
            out.append(f"<h2>{inline(l[3:])}</h2>")
        elif re.fullmatch(r"\[(.+)\]", l):
            label = re.fullmatch(r"\[(.+)\]", l).group(1)
            out.append(f'<p class="cta"><a class="button" href="{DOWNLOAD}">{esc(label)}</a></p>')
        elif l.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>"); i += 1
            cls = ' class="outcomes"' if section == "what-you-get" else ""
            out.append(f"<ul{cls}>" + "".join(items) + "</ul>"); continue
        elif re.match(r"\d+\. ", l):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^\d+\. ', '', lines[i]))}</li>"); i += 1
            cls = "week" if section == "first-week" else "steps"
            out.append(f'<ol class="{cls}">' + "".join(items) + "</ol>"); continue
        elif section == "faq" and l.startswith("**") and l.endswith("**"):
            q = l.strip("*")
            a = lines[i + 1] if i + 1 < len(lines) else ""
            out.append(f"<details><summary>{inline(q)}</summary><p>{inline(a)}</p></details>")
            i += 2; continue
        else:
            out.append(f"<p>{inline(l)}</p>")
        i += 1
    return "\n".join(out)


def read_copy():
    text = open(os.path.join(HERE, "copy.md"), encoding="utf-8").read()
    text = re.sub(r"^```.*?```\s*", "", text, flags=re.S)  # the writer's header block
    parts = re.split(r"<!--\s*([a-z-]+)\s*-->", text)
    sections = {}
    for i in range(1, len(parts), 2):
        sections[parts[i]] = parts[i + 1]
    return sections


def skills():
    meta = json.load(open(os.path.join(HERE, "skills.json"), encoding="utf-8"))
    groups = {g: [] for g in meta["groups"]}
    skills_dir = os.path.join(ROOT, ".claude", "skills")
    for d in sorted(os.listdir(skills_dir)):
        p = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isfile(p):
            continue
        if d in meta["skills"]:
            group, line = meta["skills"][d]
        else:
            s = open(p, encoding="utf-8").read()
            m = re.search(r"^description:\s*>?-?\s*(.*?)(?=^\w+:|^---)", s, re.S | re.M)
            desc = re.sub(r"\s+", " ", (m.group(1) if m else "")).strip().strip('"').strip("'")
            line = re.split(r"(?<=[.!?])\s", desc)[0] if desc else "New skill."
            group = "More"
        groups.setdefault(group, []).append((d, line))
    count = sum(len(v) for v in groups.values())
    out = []
    for g, items in groups.items():
        if not items:
            continue
        out.append(f'<div class="group"><h3>{esc(g)}</h3><ul class="skills">')
        for name, line in items:
            out.append(f'<li><code>{esc(name)}</code><span>{esc(line)}</span></li>')
        out.append("</ul></div>")
    return count, "\n".join(out)


def tools():
    data = json.load(open(os.path.join(ROOT, "setup", "tools.json"), encoding="utf-8"))
    names = [t["name"] for t in data if t.get("area") in ("base", "claude", "plugins", "tools", "mcp")]
    logins = [t["name"] for t in data if t.get("login")]
    return names, logins


def version():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
        date = subprocess.check_output(["git", "log", "-1", "--format=%cs"], cwd=ROOT, text=True).strip()
    except Exception:
        sha, date = "local", dt.date.today().isoformat()
    return sha, date


def main():
    sections = read_copy()
    count, skills_html = skills()
    tool_names, logins = tools()
    sha, date = version()
    page = sections.pop("page-level", "")
    title = re.search(r"title:\s*(.+)", page).group(1).strip()
    meta = re.search(r"meta:\s*(.+)", page).group(1).strip()

    body = {}
    for sid, text in sections.items():
        if sid == "can-do":
            text = text.replace("<!-- generated skill list goes here -->", "")
            text = re.sub(r"knowing how to do twenty-one things", f"knowing how to do {num_word(count).lower()} things", text)
        body[sid] = md_block(text, sid)
        if sid == "two-ways":
            # the two bold-led paragraphs become side-by-side cards
            body[sid] = re.sub(r"(<p><strong>.*?</p>\s*<p><strong>.*?</p>)", r'<div class="paths">\1</div>', body[sid], flags=re.S)
    body["can-do"] += f'\n<div class="skillgrid">{skills_html}</div>'
    tool_list = "".join(f"<li>{esc(n)}</li>" for n in tool_names)
    login_list = "".join(f"<li>{esc(n)}</li>" for n in logins)

    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    out = tpl
    for k, v in body.items():
        out = out.replace("{{" + k + "}}", v)
    out = (out.replace("{{title}}", esc(title)).replace("{{meta}}", esc(meta))
              .replace("{{tools}}", tool_list).replace("{{logins}}", login_list)
              .replace("{{download}}", DOWNLOAD).replace("{{repo}}", REPO_URL)
              .replace("{{sha}}", esc(sha)).replace("{{date}}", esc(date)).replace("{{count}}", str(count)))
    left = re.findall(r"{{[a-z-]+}}", out)
    if left:
        raise SystemExit(f"unfilled placeholders: {left}")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    assets = os.path.join(HERE, "assets")
    if os.path.isdir(assets):
        import shutil
        shutil.copytree(assets, os.path.join(OUT, "assets"), dirs_exist_ok=True)
    with open(os.path.join(OUT, "_headers"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: DENY\n  Referrer-Policy: strict-origin-when-cross-origin\n")
    print(f"wrote {OUT}/index.html: {count} skills, {len(tool_names)} tools, {sha} {date}")


def num_word(n):
    words = {20: "Twenty", 21: "Twenty-one", 22: "Twenty-two", 23: "Twenty-three", 24: "Twenty-four", 25: "Twenty-five",
             26: "Twenty-six", 27: "Twenty-seven", 28: "Twenty-eight", 29: "Twenty-nine", 30: "Thirty"}
    return words.get(n, str(n))


if __name__ == "__main__":
    main()
