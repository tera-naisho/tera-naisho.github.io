#!/usr/bin/env python3
"""チャンネルの動画を全部たどり、MV らしい動画の概要欄に「寺田てら」のクレジットがあるかを調べる。
使い方: python3 tools/scan_channel.py <名前> <チャンネルID> [--all]
  data/raw/ch_<名前>.json に動画一覧を保存し、クレジットがあった動画だけを「ID | 公開日 | チャンネル | タイトル | クレジット行」で出す。
  --all を付けないときは、配信・切り抜き・ショートなど MV でなさそうな題名を飛ばす。"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_uploads import main as uploads
from yt_credit import info

SKIP = re.compile(r"#shorts|切り抜き|配信|雑談|歌枠|ゲーム実況|Live|LIVE|ライブ|THE FIRST TAKE|ティザー|Teaser|告知|XFD|クロスフェード|試聴|生放送|カラオケ|Instrumental|off vocal|メイキング|Making|ダイジェスト|【.*?(実況|コラボ配信|朝活|ASMR).*?】", re.I)
name, ch = sys.argv[1], sys.argv[2]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vids = uploads(f"channel/{ch}")
json.dump(vids, open(os.path.join(root, "data", "raw", f"ch_{name}.json"), "w"), ensure_ascii=False)
cand = [v for v in vids if "--all" in sys.argv or not SKIP.search(v["title"])]
print(f"# {name}: {len(vids)} 本中 {len(cand)} 本を確認", flush=True)
for v in cand:
    for _ in range(3):
        try:
            d = info(v["id"]); break
        except Exception as e:
            d = None; time.sleep(5)
    if d and d["credit"]:
        print(f'{d["id"]} | {d["date"]} | {d["ch"]} | {d["title"][:60]} | {" / ".join(d["credit"])[:140]}', flush=True)
    time.sleep(0.5)
print(f"# {name}: 完了", flush=True)
