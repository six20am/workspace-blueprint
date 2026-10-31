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
    s = re.sub(r"\b(github\.com/[\w./-]*[\w/])", r'<a href="https://\1">\1</a>', s)
    s = s.replace("open an issue on GitHub", f'<a href="{REPO_URL}/issues">open an issue on GitHub</a>')  # both paths report to the core repo
    s = s.replace("tell us on GitHub", f'tell us <a href="{REPO_URL}/issues">on GitHub</a>')
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
        if l.startswith("```prompt"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            prompt = esc("\n".join(buf).strip())
            out.append(f'<div class="prompt"><pre>{prompt}</pre><button type="button" class="copy" data-copy>Copy</button></div>')
            i += 1; continue
        if l.startswith("# "):
            out.append(f"<h1>{inline(l[2:])}</h1>")
        elif l.startswith("## "):
            out.append(f"<h2>{inline(l[3:])}</h2>")
        elif re.fullmatch(r"\[(.+)\]", l):
            label = re.fullmatch(r"\[(.+)\]", l).group(1)
            if label == "Copy the prompt":
                out.append(f'<p class="cta"><button type="button" class="button" data-main>{esc(label)}</button></p>')
            else:
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
    """Shipped skills from skills/ (plain lines from skills.json), plus designed-but-not-built ones from
    roadmap.json marked as coming. A roadmap entry whose folder already exists is dropped, so nothing shows twice."""
    meta = json.load(open(os.path.join(HERE, "skills.json"), encoding="utf-8"))
    road = json.load(open(os.path.join(HERE, "roadmap.json"), encoding="utf-8"))["skills"]
    groups = {g: [] for g in meta["groups"]}
    skills_dir = os.path.join(ROOT, "skills")  # INDEX.md sits here too; it has no SKILL.md, so the loop skips it
    shipped = []
    for d in sorted(os.listdir(skills_dir)):
        p = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isfile(p):
            continue
        shipped.append(d)
        if d in meta["skills"]:
            group, line = meta["skills"][d]
        else:
            s = open(p, encoding="utf-8").read()
            m = re.search(r"^description:\s*>?-?\s*(.*?)(?=^\w+:|^---)", s, re.S | re.M)
            desc = re.sub(r"\s+", " ", (m.group(1) if m else "")).strip().strip('"').strip("'")
            line = re.split(r"(?<=[.!?])\s", desc)[0] if desc else "New skill."
            group = "More"
        groups.setdefault(group, []).append((d, line, False))
    coming = 0
    for d, (group, line) in road.items():
        if d in shipped:
            continue
        groups.setdefault(group, []).append((d, line, True))
        coming += 1
    count = len(shipped)
    out = []
    first = True
    for g, items in groups.items():
        if not items:
            continue
        have = sum(1 for _, _, c in items if not c)
        soon = len(items) - have
        headline = meta.get("headlines", {}).get(g, g)
        meta_line = (f"{have} ready" if have else "") + (f"{', ' if have else ''}{soon} coming" if soon else "")
        rows = []
        for name, line, is_coming in items:
            cls = ' class="coming"' if is_coming else ""
            rows.append(f'<tr{cls}><td><code>{esc(name)}</code></td><td>{esc(line)}</td><td>{"Coming" if is_coming else "Ready"}</td></tr>')
        cls = "sched" + (" all-coming" if not have else "")
        out.append(f'<details class="{cls}"{" open" if first else ""}><summary><span>{esc(headline)}</span><small>{meta_line}</small></summary>'
                   f'<table><thead><tr><th scope="col">Skill</th><th scope="col">What it does</th><th scope="col">Status</th></tr></thead><tbody>{"".join(rows)}</tbody></table></details>')
        first = False
    return count, coming, "\n".join(out)


def pipe_rows(text):
    """Lines of `left | right`, for the hero's status table and job picker."""
    return [tuple(p.strip() for p in l.split("|", 1)) for l in text.strip().splitlines() if "|" in l]


# Plain words for the reader, keyed by the start of the tools.json `name` (which the installer also uses,
# so the names stay as they are). SIGNIN is the visible sign-in list; PLAIN is the full tool list.
SIGNIN = {
    "Claude Code": "Claude Code (the AI itself)",
    "NotebookLM": "NotebookLM (a research tool)",
    "Agent Reach": "Agent Reach (reads posts behind logins)",
    "Connect image search": "Image search (free photo keys)",
    "Claude in Chrome": "Claude in Chrome (your own browser)",
}
PLAIN = {
    "RTK hook": "Command-output trimmer, hooked into Claude Code",
    "rtk": "Command-output trimmer",
    "Defuddle": "Web page cleaner",
    "Trafilatura": "Web page cleaner (Python)",
    "ccusage": "Shows what Claude Code sessions cost",
    "Repomix": "Packs a folder into one file for an AI to read",
    "CodeBurn": "Shows where AI usage goes",
    "Ghostscript": "PDF engine, used by the scan reader",
}


def mapped(name, table):
    for key, plain in table.items():  # longest keys first where one starts another ("RTK hook" before "rtk")
        if name == key or name.startswith(key + " "):
            return plain
    return None


def label(t, short=False):
    """The name a reader sees. An `mcp` entry is named for the installer ("Connect image search to Claude");
    the page shows the thing itself ("Image search"). `short` also drops a trailing parenthetical, for the
    sign-in list ("NotebookLM (Google Notebook)" reads "NotebookLM")."""
    name = t["name"]
    plain = mapped(name, SIGNIN if short else PLAIN)
    if plain:
        return plain
    if short:
        name = re.sub(r"\s*\([^)]*\)$", "", name)
    if t.get("area") == "mcp":
        name = re.sub(r"^Connect\s+", "", name)
        name = re.sub(r"\s+to Claude$", "", name)
        name = name[:1].upper() + name[1:]
    return name


def tools():
    data = json.load(open(os.path.join(ROOT, "setup", "tools.json"), encoding="utf-8"))
    names = [label(t) for t in data if t.get("area") in ("base", "claude", "plugins", "tools", "mcp", "programs")]
    logins = [label(t, short=True) for t in data if t.get("login")]
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
    count, coming, skills_html = skills()
    tool_names, logins = tools()
    sha, date = version()
    page = sections.pop("page-level", "")
    title = re.search(r"title:\s*(.+)", page).group(1).strip()
    meta = re.search(r"meta:\s*(.+)", page).group(1).strip()

    status_rows = "".join(f'<tr><th scope="row">{esc(a)}</th><td>{esc(b)}</td></tr>' for a, b in pipe_rows(sections.pop("hero-status")))
    jobs = pipe_rows(sections.pop("hero-jobs"))
    job_inputs = "".join(f'<input type="radio" name="job" id="job{i}"{" checked" if i == 1 else ""}><label for="job{i}">{esc(a)}</label>' for i, (a, _) in enumerate(jobs, 1))
    job_caps = "".join(f'<p class="cap cap{i}">{esc(b)}</p>' for i, (_, b) in enumerate(jobs, 1))
    hero_figure = esc(sections.pop("hero-figure").strip())

    body = {}
    for sid, text in sections.items():
        if sid == "can-do":
            text = text.replace("<!-- generated skill list goes here -->", "")
            text = re.sub(r"knowing how to do [A-Za-z-]+ things", f"knowing how to do {num_word(count).lower()} things", text)
            if coming == 0:  # nothing left on the roadmap: drop the sentence about what is on the way
                text = re.sub(r"\s*Another \{\{coming\}\}[^.]*?where it's going\.", "", text)
            text = text.replace("{{coming}}", str(coming))
        body[sid] = md_block(text, sid)
    body["can-do"] += f'\n<div class="schedule">{skills_html}</div>'
    tool_list = "".join(f"<li>{esc(n)}</li>" for n in tool_names)
    login_list = "".join(f"<li>{esc(n)}</li>" for n in logins)

    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    out = tpl
    for k, v in body.items():
        out = out.replace("{{" + k + "}}", v)
    out = (out.replace("{{title}}", esc(title)).replace("{{meta}}", esc(meta))
              .replace("{{hero-status}}", status_rows).replace("{{hero-jobs}}", job_inputs)
              .replace("{{hero-caps}}", job_caps).replace("{{hero-figure}}", hero_figure)
              .replace("{{tools}}", tool_list).replace("{{logins}}", login_list)
              .replace("{{download}}", DOWNLOAD).replace("{{repo}}", REPO_URL)
              .replace("{{sha}}", esc(sha)).replace("{{date}}", esc(date)).replace("{{count}}", str(count)).replace("{{coming}}", str(coming)))
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
    tens = {20: "Twenty", 30: "Thirty", 40: "Forty"}
    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    if 20 <= n <= 40:
        t, o = n - n % 10, n % 10
        return tens[t] + ("-" + ones[o] if o else "")
    return str(n)


if __name__ == "__main__":
    main()
