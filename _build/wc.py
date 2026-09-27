"""Prose word count for Markdown files (ignores table pipes, separator rows, heading marks, link targets).

Usage: python3 _build/wc.py FILE [FILE ...]
"""
import re
import sys

total = 0
for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"^\s*\|?[\s:|-]*-{3,}[\s:|-]*$", " ", text, flags=re.M)  # table separator rows
    text = re.sub(r"\]\([^)]*\)", "]", text)  # link targets
    text = re.sub(r"[|#>*_`]", " ", text)
    n = sum(1 for w in text.split() if re.search(r"[A-Za-z0-9]", w))
    total += n
    print(f"{n}\t{path}")
if len(sys.argv) > 2:
    print(f"{total}\tTOTAL")
