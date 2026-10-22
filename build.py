#!/usr/bin/env python3
"""寺田てら ないしょのお寺: data/timeline.json から docs/ に静的サイトを生成する。
（つくりは「Ado 非公式ワクワク秘密基地」~/ado-himitsukichi・「CLAN QUEEN 秘密の帝国」~/clanqueen-teikoku と同じ流れ）

- data/timeline.json … 年表。tools/mk_data.py が data/core.json（手書きのできごと）と data/mv.json（MV イラストの仕事）から作る。
  {date: "YYYY" | "YYYY-MM" | "YYYY-MM-DD", cat, title, note, big, videos?, x?}
  cat: mv（MV イラスト）/ work（ジャケット・キャラクター）/ book（本・漫画）/ exhibit（展覧会・ポップアップ・カフェ）/ collab（コラボ・グッズ）/ event（イベント・出演）/ milestone
- data/mv.json … 曲 → 公式 YouTube の動画。概要欄に「寺田てら」のクレジットがあるものだけ（tools/yt_credit.py で確認）。
- これからの予定 … ~/knowledge-os/oshi-events.js の artist が 寺田てら の行を docs/upcoming.js に書き出す。
- 画像 … 寺田てらさんのイラストの画像ファイルは置かない（複製・転載をしない）。MV は YouTube のサムネイルを i.ytimg.com から直接表示し、公式動画にリンクする。
  置いてよい画像ファイルは AI でつくったオリジナルのヘッダー（assets/header.jpg・2026-10-23 Gemini 作。原宿ポップなお寺とステッカーのコラージュ、人物・キャラクターなし。題名の白いラベルは PIL で入れた。上書きしない）。
非公式のファンサイト。アフィリエイト・広告は入れない。
"""
import html, json, os, re, shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
NAME = "寺田てら ないしょのお寺"
SITE = "https://tera-naisho.github.io/"
GA = "G-EHWF25C1RB"  # ほかのサイトと共通の測定 ID（GA4 でホスト名 tera-naisho.github.io で絞る）
EVENTS_JS = os.path.expanduser("~/knowledge-os/oshi-events.js")
TODAY = date.today().isoformat()
HEADER = os.path.exists(os.path.join(ROOT, "assets", "header.jpg"))

CATS = {
    "mv": ("MV イラスト", "#ff3d8b"),
    "work": ("ジャケット・キャラクター", "#8b5cf6"),
    "book": ("本・漫画", "#2563eb"),
    "exhibit": ("展覧会・ポップアップ", "#0ea5c6"),
    "collab": ("コラボ・グッズ", "#ea580c"),
    "event": ("イベント・出演", "#16a34a"),
    "milestone": ("できごと", "#64748b"),
}
# 時代区分（id, 名前, 説明, 開始, 終了, 代表の MV）
ERAS = [
    ("hajimari", "はじまりの鐘", "ドイツ生まれの少女が、漫画『メダ子さん』と「ダダダダ天使」でポップの扉を開くまで", "0000", "2017-12-31", "ダダダダ天使"),
    ("mv", "MV の絵の時代", "「ハローディストピア」「デジャヴ」「チューリングラブ」——歌とイラストが一緒に広がった日々", "2018-01-01", "2021-09-30", "チューリングラブ feat.Sou"),
    ("ashura", "阿修羅ちゃんとジャンクモール", "Ado さんの「阿修羅ちゃん」、ヨウジヤマモト、コラボカフェ。絵が街へ出ていく", "2021-10-01", "2023-07-31", "阿修羅ちゃん"),
    ("chroma", "Chroma から SensiouS へ", "初の作品集、ハローキティ 50 周年、松屋銀座と大丸梅田の大きな個展", "2023-08-01", "2025-12-31", "クロスワードパズル"),
    ("ima", "いま、そしてこれから", "「不死身ごっこ」の映像監督、PixTube、全国のポップアップ", "2026-01-01", "9999", "不死身ごっこ"),
]
CAT_PAGES = [("works", "MV・ジャケット", {"mv", "work"}), ("exhibit", "展覧会・ポップアップ", {"exhibit", "event"}),
             ("collab", "コラボ・グッズ", {"collab"}), ("books", "本・漫画", {"book"})]

esc = html.escape
MV = json.load(open(os.path.join(ROOT, "data", "mv.json"), encoding="utf-8"))
T = sorted(json.load(open(os.path.join(ROOT, "data", "timeline.json"), encoding="utf-8")), key=lambda e: e["date"])
YEARS = sorted({e["date"][:4] for e in T})
CSS = open(os.path.join(ROOT, "assets", "base.css"), encoding="utf-8").read()


def fmt(d):
    p = d.split("-")
    s = p[0] + "年"
    if len(p) > 1:
        s += str(int(p[1])) + "月"
    if len(p) > 2:
        s += str(int(p[2])) + "日"
    return s


def era_of(d):
    for e in ERAS:
        if e[3] <= d <= e[4] + "~":
            return e
    return ERAS[-1]


def thumb_url(vid, size="hqdefault"):
    return f"https://i.ytimg.com/vi/{vid}/{size}.jpg"


def watch(vid):
    return f"https://www.youtube.com/watch?v={vid}"


def thumb(k, cls="pic"):
    m = MV.get(k)
    if not m:
        return f'<div class="{cls} ph"></div>'
    return f'<img class="{cls}" src="{thumb_url(m["id"])}" alt="{esc(m["title"])} のサムネイル（YouTube）" loading="lazy">'


def mv_card(k):
    m = MV[k]
    return (f'<div class="mvw"><a class="mv" href="{watch(m["id"])}" target="_blank" rel="noopener">'
            f'<span class="th"><img src="{thumb_url(m["id"], "mqdefault")}" alt="" loading="lazy"><i>▶</i></span>'
            f'<span class="mt">{esc(m["title"])}<small>YouTube で見る（{esc(m["ch"])}）</small>'
            f'<small class="cr">概要欄のクレジット: {esc(m["credit"])}</small></span></a></div>')


def x_embed(url):
    return (f'<div class="xpost"><blockquote class="twitter-tweet" data-lang="ja" data-dnt="true">'
            f'<a href="{url}">公式 X のポストを見る</a></blockquote></div>')


def item(e):
    name, color = CATS.get(e["cat"], ("その他", "#64748b"))
    note = f'<p>{esc(e["note"])}</p>' if e.get("note") else ""
    note += "".join(mv_card(k) for k in e.get("videos", []) if k in MV)
    if e.get("x"):
        note += x_embed(e["x"])
    return (f'<li class="ev{" big" if e.get("big") else ""}"><div class="dt">{fmt(e["date"])}</div>'
            f'<div class="bd"><span class="chip" style="--c:{color}">{name}</span>'
            f'<h3>{esc(e["title"])}</h3>{note}</div></li>')


def year_stats(y):
    ev = [e for e in T if e["date"][:4] == y]
    c = lambda cats: sum(1 for e in ev if e["cat"] in cats)
    parts = [("MV", c({"mv"}), "本"), ("展覧会・ポップアップ", c({"exhibit"}), "件"), ("コラボ", c({"collab", "work"}), "件"),
             ("本", c({"book"}), "件"), ("イベント", c({"event"}), "件")]
    return " ／ ".join(f"{a} {n} {u}" for a, n, u in parts if n)


def timeline(events, by_year=True):
    if not events:
        return '<p class="empty">まだ記録がありません。</p>'
    out, cur = [], None
    for e in events:
        y = e["date"][:4]
        if by_year and y != cur:
            if cur:
                out.append("</ol>")
            st = year_stats(y)
            out.append(f'<h2 class="yr" id="y{y}"><a href="{{R}}year/{y}.html">{y}年</a> <small class="ys">{len([x for x in T if x["date"][:4] == y])} のできごと{"（" + st + "）" if st else ""}</small></h2><ol class="tl">')
            cur = y
        out.append(item(e))
    out.append("</ol>")
    if not by_year:
        out.insert(0, '<ol class="tl">')
    return "\n".join(out)


NAV = [("index.html", "お寺の入口"), ("timeline.html", "全部の年表"), ("mv.html", "MV ギャラリー"), ("works.html", "MV・ジャケット"),
       ("exhibit.html", "展覧会・ポップアップ"), ("collab.html", "コラボ・グッズ"), ("books.html", "本・漫画"),
       ("schedule.html", "これからの予定"), ("about.html", "このお寺について")]


def sidebar():
    eras = "".join(f'<li><a href="{{R}}era/{e[0]}.html">{e[1]}</a></li>' for e in ERAS)
    years = "".join(f'<li><a href="{{R}}year/{y}.html">{y}年</a></li>' for y in YEARS)
    return f"""<aside class="side">
<div class="box"><h2>🔔 このお寺について</h2><p class="note">イラストレーター・寺田てらさんの歩みを、あなたと一緒にこっそりたどれる<b>非公式</b>の年表サイトです。ファンがつくり、毎月のできごとごとに書き足していきます。ご本人・公式とは関係ありません。</p></div>
<div class="box"><h2>🎬 MV ギャラリー</h2><p class="note">寺田てらさんの絵が動く MV を、公式動画でまとめて見られます。</p><ul><li><a href="{{R}}mv.html">MV ギャラリー（{len(MV)} 本）</a></li></ul></div>
<div class="box"><h2>🗺 時代でたどる</h2><ul>{eras}</ul></div>
<div class="box sticky"><h2>📅 年でたどる</h2><ul>{years}</ul>
<h2 style="margin-top:14px">📣 公式はこちら</h2><ul>
<li><a href="https://www.teradaterasworld.com/" rel="noopener" target="_blank">公式サイト T-R.I.P teradatera works</a></li>
<li><a href="https://www.teradaterasworld.com/news.html" rel="noopener" target="_blank">公式サイトのニュース</a></li>
<li><a href="https://x.com/trcoot" rel="noopener" target="_blank">寺田てらさんの X（@trcoot）</a></li></ul>
<h2 style="margin-top:14px">🏠 姉妹サイト</h2><ul>
<li><a href="https://ado-himitsukichi.github.io/" rel="noopener" target="_blank">Ado 非公式ワクワク秘密基地</a></li>
<li><a href="https://yama-kossori.github.io/" rel="noopener" target="_blank">yamaファンのこっそり部屋</a></li>
<li><a href="https://clanqueen-teikoku.github.io/" rel="noopener" target="_blank">CLAN QUEEN 秘密の帝国</a></li></ul></div>
</aside>"""


def ga_tag():
    return (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>'
            f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA}');</script>")


def page(path, title, desc, body, crumb=None, hero=False):
    R = "../" * path.count("/")
    nav = "".join(f'<li><a href="{R}{h}"{" class=on" if h == path else ""}>{t}</a></li>' for h, t in NAV)
    cr = '<div class="crumb"><a href="' + R + 'index.html">お寺の入口</a> › ' + " › ".join(crumb) + "</div>" if crumb else ""
    full = NAME if path == "index.html" else f"{title}｜{NAME}"
    heroh = f'<div class="hero">{hero}</div>' if hero else ""
    og = SITE + "img/header.jpg" if HEADER else thumb_url(MV["阿修羅ちゃん"]["id"])
    widgets = '<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>' if "twitter-tweet" in body else ""
    doc = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(full)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{'' if path == 'index.html' else path}">
<meta property="og:title" content="{esc(full)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{og}"><meta name="twitter:card" content="summary_large_image">
{ga_tag()}
<style>{CSS}</style></head><body>
<header class="top"><div class="in"><a class="logo" href="{R}index.html">寺田てら <span>ないしょの</span>お寺</a><span class="badge">非公式ファンサイト</span></div></header>
<nav class="gnav"><ul>{nav}</ul></nav>
{heroh}
<div class="layout"><main>{cr}{body}</main>{sidebar()}</div>
<footer>{NAME} は、寺田てらさんを応援するファンによる<b>非公式</b>のファンサイトです。寺田てらさんご本人・関係する企業や団体とは関係ありません。<br>
掲載情報は公開されている報道・公式発表をもとにしています。最新・正確な情報は<a href="https://www.teradaterasworld.com/" target="_blank" rel="noopener">公式サイト</a>でご確認ください。<br>
寺田てらさんのイラストの複製・転載はしていません（トップのヘッダーは AI でつくったオリジナルのイラストです）。動画のサムネイルは YouTube から直接表示し、公式動画にリンクしています（権利は各権利者に帰属します）。 ／ <a href="{R}about.html">このお寺について・プライバシー</a><br>最終更新: {TODAY}</footer>
{widgets}</body></html>"""
    doc = doc.replace("{R}", R)
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(doc)
    PAGES.append(path)


def upcoming_box(limit, title="これからの予定", more=True):
    link = '<p style="margin:10px 0 0;text-align:right"><a href="{R}schedule.html">予定をもっと見る →</a></p>' if more else ""
    return f"""<section><h2 class="sec-t">{title}</h2>
<ul class="up" id="up" data-limit="{limit}"><li class="empty">読み込み中…</li></ul>{link}
<p class="notice" style="margin-top:12px">予定は公式発表・報道をもとに毎週まとめています。変わることがあるので、お出かけ前に公式の最新情報もあわせてご確認ください。</p></section>
<script src="{{R}}upcoming.js"></script><script>
(function(){{var el=document.getElementById('up'),lim=+el.dataset.limit,t=new Date(),pad=function(n){{return('0'+n).slice(-2)}},
today=t.getFullYear()+'-'+pad(t.getMonth()+1)+'-'+pad(t.getDate()),K={{live:'ライブ',release:'発売',tieup:'コラボ',event:'イベント',media:'テレビ・配信',ticket:'チケット'}},
W='日月火水木金土',it=(window.TERA_UPCOMING||[]).filter(function(e){{return e.date>=today}}).slice(0,lim);
if(!it.length){{el.innerHTML='<li class="empty">いま分かっている予定はありません。</li>';return}}
el.innerHTML=it.map(function(e){{var d=new Date(e.date+'T00:00:00');return '<li><div class="d">'+(d.getMonth()+1)+'/'+d.getDate()+'<small>'+d.getFullYear()+'（'+W[d.getDay()]+'）</small></div><div><span class="k">'+(K[e.kind]||'')+'</span><div>'+e.title.replace(/[<>&]/g,'')+'</div></div></li>'}}).join('')}})();
</script>"""


def write_upcoming():
    items = []
    if os.path.exists(EVENTS_JS):
        s = open(EVENTS_JS, encoding="utf-8").read()
        for m in re.finditer(r'\{\s*date:\s*"([\d-]+)",\s*artist:\s*"寺田てら",\s*title:\s*"((?:[^"\\]|\\.)*)",\s*kind:\s*"(\w+)"', s):
            if m.group(3) != "anniv":
                items.append({"date": m.group(1), "title": json.loads('"' + m.group(2) + '"'), "kind": m.group(3)})
    items.sort(key=lambda e: e["date"])
    open(os.path.join(OUT, "upcoming.js"), "w", encoding="utf-8").write("window.TERA_UPCOMING=" + json.dumps(items, ensure_ascii=False) + ";\n")
    return len(items)


def gcard(m):
    return (f'<div><a href="{watch(m["id"])}" target="_blank" rel="noopener"><img src="{thumb_url(m["id"])}" alt="" loading="lazy">{esc(m["title"])}</a>'
            f'<small style="display:block;font-weight:400;color:var(--sub)">{esc(m["ch"])}</small>'
            f'<small style="color:var(--sub);font-size:12px">{fmt(m["yt_date"])}</small></div>')


def build():
    if os.path.exists(OUT):
        for n in os.listdir(OUT):
            p = os.path.join(OUT, n)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    if HEADER:
        os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
        shutil.copy(os.path.join(ROOT, "assets", "header.jpg"), os.path.join(OUT, "img", "header.jpg"))
    n_up = write_upcoming()
    n_mv = len(MV)
    artists = sorted({m["artist"] for m in MV.values()})
    n_ex = sum(1 for e in T if e["cat"] == "exhibit")
    n_co = sum(1 for e in T if e["cat"] in ("collab", "work"))

    # 入口（トップ）
    era_cards = "".join(
        f'<a class="era" href="{{R}}era/{e[0]}.html">{thumb(e[5])}<div class="t"><span class="n">{sum(1 for x in T if era_of(x["date"]) == e)} のできごと</span><b>{e[1]}</b><small>{e[2]}</small></div></a>'
        for e in ERAS)
    year_cards = "".join(f'<a href="{{R}}year/{y}.html">{y}<small>{sum(1 for x in T if x["date"][:4] == y)} 件</small></a>' for y in YEARS)
    ys = [y for y in YEARS if y >= "2016"]
    mx = max(sum(1 for x in T if x["date"][:4] == y) for y in ys)
    bars = ""
    for i, y in enumerate(ys, 1):
        tot = sum(1 for x in T if x["date"][:4] == y)
        mvn = sum(1 for x in T if x["date"][:4] == y and x["cat"] == "mv")
        bars += (f'<a class="br" href="{{R}}year/{y}.html"><span class="by">{y}</span><span class="bt"><i class="b1" style="--w:{tot / mx * 100:.1f}%;--d:{i * 0.07:.2f}s"></i>'
                 f'<i class="b2" style="--w:{mvn / mx * 100:.1f}%;--d:{i * 0.07 + 0.25:.2f}s"></i></span><span class="bn">{tot}<small>（MV {mvn}）</small></span></a>')
    activity = (f'<section><h2 class="sec-t">お絵かきのあしあと</h2><p class="lead" style="margin-bottom:10px">これまでのできごと {len(T)} 件、そのうち MV イラスト {n_mv} 本。'
                f'年ごとにどれだけ描いてきたかを並べました（濃いピンクが MV）。</p><div class="bars" id="bars">{bars}</div></section>'
                '<script>(function(){var b=document.getElementById("bars");if(!b)return;function go(){b.classList.add("on")}'
                'if(!("IntersectionObserver" in window)||matchMedia("(prefers-reduced-motion: reduce)").matches){go();return}'
                'var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){go();o.disconnect()}})},{threshold:.25});o.observe(b)})()</script>')
    recent = [e for e in T if e["date"] <= TODAY][-6:][::-1]
    body = f"""<section><h1>ようこそ、ないしょのお寺へ。</h1>
<p class="lead">イラストレーター・寺田てらさんの歩みを、あなたの「好き」と一緒にこっそりたどれます。漫画『メダ子さんの恋スル侵略計画』、ナナヲアカリさんの「ダダダダ天使」「チューリングラブ」、まふまふさんの「デジャヴ」、Ado さんの「阿修羅ちゃん」、そして作品集『Chroma』や松屋銀座の個展「SensiouS」まで。ビビッドでポップ、それでいてちょっぴりダークな絵で、たくさんの歌と街を彩ってきた寺田てらさんと、一緒に作品をつくってきた作り手の皆さんへの拍手を込めて、ファンがまとめた非公式のお寺です。毎月、新しいできごとを書き足していきます。</p>
<div class="stats"><div><b>{n_mv}</b>MV イラスト</div><div><b>{len(artists)}</b>組のアーティスト</div><div><b>{n_ex}</b>展覧会・ポップアップ</div><div><b>{n_co}</b>コラボ</div></div>
<p class="lead" style="margin-top:12px">あなたが寺田てらさんの絵に出会ったのは、どの一枚ですか？　お参りに来てくださって、ありがとうございます。</p></section>
{upcoming_box(5)}
{activity}
<section><h2 class="sec-t">時代でたどる寺田てらさんの歩み</h2><div class="eras">{era_cards}</div></section>
<section><h2 class="sec-t">最近のできごと</h2>{timeline(recent, by_year=False)}
<p style="margin:6px 0 0;text-align:right"><a href="{{R}}timeline.html">全部の年表を見る →</a></p></section>
<section><h2 class="sec-t">年でたどる</h2><div class="years">{year_cards}</div></section>"""
    top = ["阿修羅ちゃん", "チューリングラブ feat.Sou", "ダダダダ天使", "デジャヴ", "不死身ごっこ", "メルヘル小惑星", "クロスワードパズル", "メルティックヘル feat. 超学生"]
    mosaic = '<div class="mosaic">' + "".join(
        f'<a href="{watch(MV[k]["id"])}" target="_blank" rel="noopener" title="{esc(MV[k]["title"])}"><img src="{thumb_url(MV[k]["id"])}" alt="{esc(MV[k]["title"])}"></a>'
        for k in top if k in MV) + "</div>"
    hdr = f'<img class="hdr" src="img/header.jpg" alt="{esc(NAME)}" width="1600" height="640">' if HEADER else ""
    page("index.html", NAME, f"イラストレーター寺田てらさんの歩みを、MV {n_mv} 本と展覧会・コラボの年表でこっそりたどれる非公式ファンサイト。毎月更新。", body, hero=hdr + mosaic)

    # 全部の年表
    jump = " ".join(f'<a href="#y{y}">{y}</a>' for y in YEARS)
    page("timeline.html", "全部の年表", "寺田てらさんの活動を、生まれた年から最新のコラボまで、すべて時系列で。",
         f'<section><h1>全部の年表</h1><p class="lead">寺田てらさんの歩みを、最初から通してたどれます。水色の印は特に大きなできごとです。 年へジャンプ: {jump}</p></section><section>{timeline(T)}</section>',
         crumb=["全部の年表"])

    # 時代ページ
    for i, e in enumerate(ERAS):
        ev = [x for x in T if era_of(x["date"]) == e]
        pv = f'<a href="{ERAS[i-1][0]}.html">← {ERAS[i-1][1]}</a>' if i else "<span></span>"
        nx = f'<a href="{ERAS[i+1][0]}.html">{ERAS[i+1][1]} →</a>' if i + 1 < len(ERAS) else "<span></span>"
        m = MV[e[5]]
        page(f"era/{e[0]}.html", e[1], f"寺田てらさんの「{e[1]}」— {e[2]}。",
             f'<section><a href="{watch(m["id"])}" target="_blank" rel="noopener">{thumb(e[5])}</a><p class="credit">画像: 「{esc(m["title"])}」のサムネイル（YouTube・{esc(m["ch"])}）</p><h1 style="margin-top:14px">{e[1]}</h1><p class="lead">{e[2]}</p></section>'
             f'<section>{timeline(ev)}<div class="pager">{pv}{nx}</div></section>', crumb=[e[1]])

    # 年ページ
    for i, y in enumerate(YEARS):
        ev = [x for x in T if x["date"][:4] == y]
        pv = f'<a href="{YEARS[i-1]}.html">← {YEARS[i-1]}年</a>' if i else "<span></span>"
        nx = f'<a href="{YEARS[i+1]}.html">{YEARS[i+1]}年 →</a>' if i + 1 < len(YEARS) else "<span></span>"
        page(f"year/{y}.html", f"{y}年の寺田てら", f"{y}年の寺田てらさんのできごと（{len(ev)}件）を年表で。",
             f'<section><h1>{y}年の寺田てら</h1><p class="lead">{len(ev)} 件のできごと</p><p class="ys2">{year_stats(y)}</p></section>'
             f'<section>{timeline(ev, by_year=False)}<div class="pager">{pv}{nx}</div></section>', crumb=[f"{y}年"])

    # カテゴリページ
    leads = {"works": f"寺田てらさんの絵と一緒に、あの歌をもう一度聴けます。{len(artists)} 組のアーティストの MV {n_mv} 本と、ジャケット・キャラクターの仕事。",
             "exhibit": "あの会場で見た絵の記憶を、もう一度たどれます。個展・刊行記念展・ポップアップ・コラボカフェ・イベントの記録。",
             "collab": "街で出会ったあのグッズの物語を、たどれます。キャラクター・ブランド・企業とのコラボの記録。",
             "books": "手もとで何度でも開ける寺田てらさんの本を、たどれます。漫画・作品集・ポストカードブック・参加した画集。"}
    for k, t, cats in CAT_PAGES:
        ev = [x for x in T if x["cat"] in cats]
        page(f"{k}.html", t, f"寺田てらさんの{t}の年表。{leads[k]}",
             f'<section><h1>{t}</h1><p class="lead">{leads[k]}</p></section><section>{timeline(ev)}</section>', crumb=[t])

    # MV ギャラリー（アーティストごと）
    by = {}
    for m in sorted(MV.values(), key=lambda m: m["yt_date"]):
        by.setdefault(m["artist"], []).append(m)
    order = sorted(by, key=lambda a: (-len(by[a]), by[a][0]["yt_date"]))
    sec = "".join(f'<section><h2 class="sec-t">{esc(a)}（{len(by[a])}）</h2><div class="mvgrid">{"".join(gcard(m) for m in by[a])}</div></section>' for a in order)
    page("mv.html", "MV ギャラリー", f"寺田てらさんがイラストを描いた MV {n_mv} 本を、アーティストの公式 YouTube へのリンクでまとめました。",
         f'<section><h1>MV ギャラリー</h1><p class="lead">寺田てらさんの絵が動き出す MV を、まとめて楽しめます。どれも、アーティストの公式チャンネルの概要欄に「寺田てら」とクレジットされている動画だけです。サムネイルを押すと YouTube で開きます。アーティストごとに、公開された順に並べました。あなたのお気に入りの MV は、どれですか？</p>'
         f'<div class="stats"><div><b>{n_mv}</b>MV</div><div><b>{len(artists)}</b>組</div><div><b>{min(m["yt_date"] for m in MV.values())[:4]}〜{max(m["yt_date"] for m in MV.values())[:4]}</b>年</div></div></section>' + sec,
         crumb=["MV ギャラリー"])

    page("schedule.html", "これからの予定", "寺田てらさんのこれからの展覧会・ポップアップ・グッズ発売などの予定。毎週更新。",
         '<section><h1>これからの予定</h1><p class="lead">次に寺田てらさんの絵に会える日が、ひと目でわかります。展覧会・ポップアップ・グッズ発売の予定をまとめています。</p></section>'
         + upcoming_box(80, "予定一覧", more=False), crumb=["これからの予定"])

    page("about.html", "このお寺について", "寺田てら ないしょのお寺について、運営方針とプライバシーポリシー。", f"""<section><h1>このお寺について</h1>
<p>「寺田てら ないしょのお寺」は、イラストレーター・寺田てらさんの歩みを、ファンのあなたが好きなときにたどれるようにつくった<b>非公式</b>のファンサイトです。寺田てらさんご本人、所属先、関係する企業・団体とは一切関係ありません。</p>
<h2>このお寺でやっていること</h2><ul>
<li>生まれた年から今までのできごとを、年表にまとめています。MV は 1 本ずつ、公開日に年表へのせています</li>
<li>MV は、アーティストの公式 YouTube の概要欄に「寺田てら」とクレジットがあるものだけをのせています</li>
<li>毎月、前の月のできごとを書き足します。これからの予定は毎週更新します</li>
<li>情報は公式サイト・公式 YouTube・報道・プレスリリース・Wikipedia などの公開情報をもとにしています。まちがいに気づいたときは直します</li></ul>
<h2>やらないこと</h2><ul>
<li>広告・アフィリエイトは載せません</li>
<li>寺田てらさんのイラスト・写真・ロゴの複製・転載はしません。画像は、YouTube の公式動画のサムネイル（YouTube から直接表示し、動画にリンク）と、Gemini でつくったオリジナルのヘッダーイラスト（人物やキャラクター、寺田てらさんの絵柄は描いていません）だけです。権利は各権利者に帰属します。削除のご依頼があればすぐに対応します</li>
<li>ご本人の私生活に関することや、うわさ話は書きません</li></ul>
<h2>お参りに来てくださって、ありがとうございます</h2>
<p>色あざやかな絵でたくさんの歌と街を彩ってきた寺田てらさん、一緒に作品をつくってきたアーティストや作り手の皆さん、そして応援を続けるファンの皆さんに、心から感謝しています。このお寺が、あなたの「好き」をもう一度たしかめる場所になればうれしいです。</p>
<p>あなたのいちばん好きな寺田てらさんの絵は、どれですか？</p>
<h2>プライバシーポリシー</h2>
<p>動画のサムネイルは YouTube（Google）から直接表示しているため、YouTube が Cookie などで情報を取得する場合があります。アクセスの傾向を知るために Google アナリティクスを使っています。Cookie を使って匿名のアクセス情報を集めますが、個人を特定する情報は集めません。ブラウザの設定で Cookie を無効にできます。</p>
<h2>参考にしている情報源</h2><ul>
<li><a href="https://www.teradaterasworld.com/" target="_blank" rel="noopener">寺田てら 公式サイト</a>（News・Biography）</li>
<li>各アーティストの公式 YouTube チャンネル（MV の概要欄のクレジット）</li>
<li><a href="https://ja.wikipedia.org/wiki/%E5%AF%BA%E7%94%B0%E3%81%A6%E3%82%89" target="_blank" rel="noopener">寺田てら - Wikipedia</a></li>
<li>KAI-YOU、SPICE、ぴあ、PR TIMES、各会場・各社の告知ページ</li></ul></section>""", crumb=["このお寺について"])

    sm = "".join(f"<url><loc>{SITE}{'' if p == 'index.html' else p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(open(os.path.join(OUT, "index.html"), encoding="utf-8").read())
    print(f"built {len(PAGES)} pages, {len(T)} timeline events, {n_mv} MV, {n_up} upcoming")


PAGES = []
if __name__ == "__main__":
    build()
