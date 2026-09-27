"""Check internal Markdown links and GitHub-style heading anchors.

Usage: python3 _build/linkcheck.py REPO_ROOT
Checks README.md and modules/*.md. Prints every broken link; exit code 1 if any.
"""
import glob
import os
import re
import sys
import unicodedata

root = sys.argv[1] if len(sys.argv) > 1 else "."


def gh_slug(text, counts):
    s = text.strip().lower()
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    out = []
    for ch in s:
        cat = unicodedata.category(ch)
        if ch in "-_ " or cat[0] in ("L", "N"):
            out.append(ch)
    s = "".join(out).replace(" ", "-")
    if s in counts:
        counts[s] += 1
        return f"{s}-{counts[s]}"
    counts[s] = 0
    return s


_anchor_cache = {}


def anchors(path):
    if path in _anchor_cache:
        return _anchor_cache[path]
    counts, res, fence = {}, set(), False
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.lstrip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
            if m:
                res.add(gh_slug(m.group(2), counts))
    _anchor_cache[path] = res
    return res


files = [os.path.join(root, "README.md")] + sorted(glob.glob(os.path.join(root, "modules", "*.md")))
files = [f for f in files if os.path.exists(f)]
broken = 0
link_re = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
for path in files:
    fence = False
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if line.lstrip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            for _, target in link_re.findall(line):
                if re.match(r"^(https?:|mailto:|tel:)", target):
                    continue
                file_part, _, anchor = target.partition("#")
                dest = path if not file_part else os.path.normpath(os.path.join(os.path.dirname(path), file_part))
                if not os.path.exists(dest):
                    print(f"BROKEN FILE  {path}:{lineno} -> {target}")
                    broken += 1
                    continue
                if anchor and dest.endswith(".md") and anchor not in anchors(dest):
                    print(f"BROKEN ANCHOR {path}:{lineno} -> {target}")
                    broken += 1
print(f"{broken} broken link(s) across {len(files)} file(s)")
sys.exit(1 if broken else 0)
