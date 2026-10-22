#!/usr/bin/env python3
"""動画の概要欄に「寺田てら」のクレジットがあるかを確かめる。
使い方: python3 tools/yt_credit.py 動画ID ... → 「ID | 公開日 | チャンネル | タイトル | クレジット行」"""
import json, re, sys, time, urllib.request

def info(vid):
    s = urllib.request.urlopen(urllib.request.Request("https://www.youtube.com/watch?hl=ja&v=" + vid,
        headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "ja"}), timeout=20).read().decode("utf-8", "ignore")
    p = json.loads(re.search(r"var ytInitialPlayerResponse = (\{.*?\});(?:var|</script>)", s).group(1))
    v = p["videoDetails"]; mf = p.get("microformat", {}).get("playerMicroformatRenderer", {})
    desc = v.get("shortDescription", "")
    cred = [l.strip() for l in desc.splitlines() if re.search(r"寺田てら|teradatera|Terada ?Tera", l, re.I)]
    return {"id": vid, "date": (mf.get("publishDate") or "")[:10], "ch": v.get("author"), "title": v.get("title"), "credit": cred}

if __name__ == "__main__":
    for vid in sys.argv[1:]:
        try:
            d = info(vid)
            print(f'{d["id"]} | {d["date"]} | {d["ch"]} | {d["title"][:50]} | {" / ".join(d["credit"])[:120] or "-"}')
        except Exception as e:
            print(vid, "ERR", e)
        time.sleep(0.6)
