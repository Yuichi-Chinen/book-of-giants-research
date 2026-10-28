"""1回目に印刷した PDF の目次リンクから、各見出しのページ番号を読み取る。

usage: python pages.py <pdf> <pages.json>
"""
import json
import sys

import fitz

doc = fitz.open(sys.argv[1])
pages = {}
for link in doc[1].get_links():  # 2ページ目が目次
    dest = link.get("nameddest") or link.get("uri", "").lstrip("#")
    if dest and "page" in link and link["page"] >= 0:
        pages[dest] = link["page"] + 1
with open(sys.argv[2], "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, indent=1)
print(f"{len(pages)} entries, {len(doc)} pages")
