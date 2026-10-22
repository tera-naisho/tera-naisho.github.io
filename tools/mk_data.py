#!/usr/bin/env python3
"""data/core.json（手書きのできごと）と data/mv.json（寺田てらさんがイラストを描いた公式 MV）から data/timeline.json を作る。
mv.json の各 MV は、公開日に「MV イラスト」の項目として年表に入る（core.json に同じ動画を videos で書いた項目があればそちらを優先）。"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, "data", *p)

core = [json.loads(l.strip().rstrip(",")) for l in open(D("core.json"), encoding="utf-8") if l.strip().startswith("{")]
mv = json.load(open(D("mv.json"), encoding="utf-8"))
used = {v for e in core for v in e.get("videos", [])}
T = list(core)
for k, m in mv.items():
    if k in used:
        continue
    role = m.get("role", "イラスト")
    T.append({"date": m["yt_date"], "cat": "mv", "title": m.get("tl_title") or f'{m["artist"]}「{m["song"]}」MV の{role}を担当',
              "note": m.get("note", ""), "big": bool(m.get("big")), "videos": [k], "artist_x": m.get("artist_x", []), **({"x": m["x"]} if m.get("x") else {})})
T.sort(key=lambda e: e["date"])
json.dump(T, open(D("timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"timeline {len(T)} events（MV {sum(1 for e in T if e['cat'] == 'mv')}）")
