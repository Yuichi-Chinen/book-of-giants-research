"""ETCBC/dss (Abegg) Text-Fabric データから『巨人の書』写本を抽出する。

usage: python extract_giants.py <tf_dir> <out_dir>
"""
import sys
from pathlib import Path
from tf.fabric import Fabric

sys.stdout.reconfigure(encoding="utf-8")
tf_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)

SCROLLS = ["1Q23", "1Q24", "2Q26", "4Q203", "4Q206", "4Q530", "4Q531",
           "4Q532", "4Q533", "4Q556", "6Q8"]

TF = Fabric(locations=str(tf_dir), silent="deep")
api = TF.load("scroll fragment line full fulle after", silent="deep")
F, L, T = api.F, api.L, api.T

found = {F.scroll.v(s): s for s in F.otype.s("scroll")}
print("全写本数:", len(found))

summary = []
for name in SCROLLS:
    s = found.get(name)
    if s is None:
        print(f"{name}: データなし")
        summary.append((name, 0, 0))
        continue
    heb, lat = [], []
    nlines = 0
    for fr in L.d(s, otype="fragment"):
        fname = F.fragment.v(fr)
        heb.append(f"\n== {name} frag. {fname} ==")
        lat.append(f"\n== {name} frag. {fname} ==")
        for ln in L.d(fr, otype="line"):
            lno = F.line.v(ln)
            heb.append(f"{lno}\t{T.text(ln, fmt='text-orig-extra').strip()}")
            lat.append(f"{lno}\t{T.text(ln, fmt='text-trans-extra').strip()}")
            nlines += 1
    words = L.d(s, otype="word")
    header = (f"# {name} — Book of Giants (Qumran Aramaic)\n"
              f"# Source: ETCBC/dss v2.0.1 (Text-Fabric), based on transcriptions by "
              f"Martin G. Abegg, Jr., James E. Bowley, Edward M. Cook\n"
              f"# License: CC BY-NC 4.0 https://creativecommons.org/licenses/by-nc/4.0/\n"
              f"# https://github.com/ETCBC/dss\n")
    (out_dir / f"{name}_aramaic.txt").write_text(header + "\n".join(heb) + "\n", encoding="utf-8")
    (out_dir / f"{name}_translit.txt").write_text(header + "\n".join(lat) + "\n", encoding="utf-8")
    print(f"{name}: 断片 {len(L.d(s, otype='fragment'))}, 行 {nlines}, 語 {len(words)}")
    summary.append((name, nlines, len(words)))
