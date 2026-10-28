"""調査メモ（Markdown）から印刷用 HTML を組む。

usage: python build.py [pages.json]
  pages.json があれば目次にページ番号を入れる（make_pdf.ps1 が1回目の印刷後に作る）。
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "巨人の書_マニ教_調査報告-print.html"


def section(md_text, start, stop=None):
    """README から `## start` 以降、`## stop` の直前までを切り出す。"""
    body = md_text.split(f"## {start}\n", 1)[1]
    if stop:
        body = body.split(f"## {stop}\n", 1)[0]
    return body


def demote(md_text):
    """メモの見出しを1段下げ、先頭の `# タイトル` と調査日・関連行を落とす。"""
    lines = md_text.splitlines()
    out = []
    for ln in lines:
        if ln.startswith("# "):
            continue
        if ln.startswith("調査日：") or ln.startswith("関連："):
            continue
        # Python-Markdown は入れ子リストに4字下げが要る
        out.append(re.sub(r"^  (?=[-*] |\d+\. )", "    ", ln))
    return "\n".join(out)


readme = (ROOT / "README.md").read_text(encoding="utf-8")
giants = demote((ROOT / "巨人の書_調査メモ.md").read_text(encoding="utf-8"))
mani = demote((ROOT / "マニ教_調査メモ.md").read_text(encoding="utf-8"))
texts = section(readme, "クムラン アラム語本文", "作業記録")
texts = "## クムラン アラム語本文\n" + texts

# 4Q530 から夢の場面の見本を添える（CC BY-NC 4.0, 出典はファイル冒頭に明記）
sample_src = (ROOT / "原文/クムラン_アラム語/4Q530_aramaic.txt").read_text(encoding="utf-8")
m = re.search(r"== 4Q530 frag\. f2ii\+6_12\(\?\) ==\n(.*?)(?:\n\n|\Z)", sample_src, re.S)
sample = m.group(1) if m else ""

parts = [
    ("part1", "第1部　巨人の書", giants),
    ("part2", "第2部　原文テキストの収集", texts),
    ("part3", "第3部　マニ教", mani),
]

pages = {}
if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
    pages = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

md = markdown.Markdown(extensions=["tables"])
toc, body = [], []
for pid, title, text in parts:
    html = md.reset().convert(text)
    # h2 に id を振って目次へ
    subs = []

    def add_id(mo, pid=pid, subs=subs):
        sid = f"{pid}-{len(subs) + 1}"
        subs.append((sid, re.sub("<.*?>", "", mo.group(1))))
        return f'<h2 id="{sid}">{mo.group(1)}</h2>'

    html = re.sub(r"<h2>(.*?)</h2>", add_id, html)
    if pid == "part2" and sample:
        html += ('<h2 id="part2-sample">見本：4Q530 frag. 2 ii + 6–12（オフヤとハフヤの夢の場面）</h2>'
                 f'<pre class="aram" dir="rtl">{sample}</pre>'
                 '<p class="note">出典：ETCBC/dss v2.0.1（Abegg, Bowley, Cook 転写）, CC BY-NC 4.0。'
                 '右端の数字は行番号。［ ］内は現代の校訂者による復元。</p>'
                 '<ul class="note"><li>2行目：ギルガメシュ（גלגמיס）の名が現れる</li>'
                 '<li>3–4行目：二人の巨人が夢を見て、眠れなくなる</li>'
                 '<li>6–12行目：ハフヤ（ההיה）の夢。木々の茂る園が水と火で滅ぼされる</li>'
                 '<li>15–20行目：オフヤ（אוהיה）の夢。天の支配者が地に降り、玉座が据えられ、書物が開かれる</li>'
                 '<li>21–24行目：巨人たちはマハワイ（מהוי）をエノクのもとへ送り、夢の解き明かしを求める</li></ul>')
    if pid == "part2" and sample:
        subs.append(("part2-sample", "見本：4Q530 frag. 2 ii + 6–12"))
    toc.append(f'<li class="toc-part"><a href="#{pid}">{title}</a>'
               f'<span class="pg">{pages.get(pid, "")}</span></li>')
    for sid, st in subs:
        toc.append(f'<li class="toc-sub"><a href="#{sid}">{st}</a>'
                   f'<span class="pg">{pages.get(sid, "")}</span></li>')
    body.append(f'<section class="part"><h1 id="{pid}">{title}</h1>{html}</section>')

# 外部リンクはそのまま、相対リンク（.md）は文字だけ残す
body_html = re.sub(r'<a href="\./[^"]*">(.*?)</a>', r"\1", "\n".join(body))

doc = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<title>巨人の書・マニ教 調査報告</title>
<style>
@page {{ size: A4; margin: 18mm 17mm 20mm; }}
body {{ font-family: "Yu Mincho", "游明朝", serif; font-size: 10.5pt; line-height: 1.75; color: #222; }}
h1, h2, h3, h4, .cover, .toc {{ font-family: "Yu Gothic", "游ゴシック", sans-serif; }}
.cover {{ height: 245mm; display: flex; flex-direction: column; justify-content: center; text-align: center; page-break-after: always; }}
.cover .t {{ font-size: 30pt; font-weight: bold; letter-spacing: .1em; }}
.cover .s {{ font-size: 14pt; margin-top: 10mm; color: #555; }}
.cover .d {{ font-size: 11pt; margin-top: 40mm; color: #555; }}
.toc {{ page-break-after: always; }}
.toc h1 {{ border: none; }}
.toc ul {{ list-style: none; padding: 0; }}
.toc li {{ display: flex; border-bottom: 1px dotted #bbb; padding: 2px 0; }}
.toc li a {{ flex: 1; color: #222; text-decoration: none; }}
.toc .toc-part {{ font-weight: bold; margin-top: 8px; border-bottom: 1px solid #888; }}
.toc .toc-sub {{ padding-left: 2em; font-size: 10pt; }}
.toc .pg {{ min-width: 2.5em; text-align: right; }}
.part {{ page-break-before: always; }}
h1 {{ font-size: 18pt; border-bottom: 2px solid #6a4c2a; padding-bottom: 4px; margin: 0 0 10px; }}
h2 {{ font-size: 13.5pt; margin: 18px 0 6px; padding-left: 8px; border-left: 5px solid #6a4c2a; page-break-after: avoid; }}
h3 {{ font-size: 11.5pt; margin: 14px 0 4px; page-break-after: avoid; }}
h4 {{ font-size: 10.5pt; margin: 10px 0 2px; }}
table {{ border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.2pt; line-height: 1.5; page-break-inside: auto; }}
tr {{ page-break-inside: avoid; }}
th, td {{ border: 1px solid #aaa; padding: 3px 6px; vertical-align: top; }}
th {{ background: #efe8dd; font-family: "Yu Gothic", sans-serif; }}
a {{ color: #6a4c2a; word-break: break-all; }}
ul, ol {{ margin: 4px 0 8px; padding-left: 1.6em; }}
td code {{ word-break: break-all; }}
code {{ font-family: Consolas, monospace; font-size: 9pt; background: #f3f0ea; padding: 0 2px; }}
pre.aram {{ font-family: "Times New Roman", serif; font-size: 13pt; line-height: 1.9; background: #faf7f1; border: 1px solid #ddd; padding: 8px 12px; white-space: pre-wrap; }}
.note {{ font-size: 9pt; color: #555; }}
</style></head><body>
<div class="cover">
  <div class="t">巨人の書・マニ教<br>調査報告</div>
  <div class="s">The Book of Giants and Manichaeism — Research Notes</div>
  <div class="d">{date.today():%Y年%m月%d日}<br>github.com/Yuichi-Chinen/book-of-giants-research</div>
</div>
<nav class="toc"><h1>目次</h1><ul>{''.join(toc)}</ul></nav>
{body_html}
</body></html>
"""
OUT.write_text(doc, encoding="utf-8")
print("wrote", OUT)
