# 寺田てら ないしょのお寺（非公式ファンサイト）

イラストレーター・寺田てらさんの歩みを、MV イラスト・展覧会・コラボ・本の年表でたどれる非公式ファンサイト。
公開先: https://tera-naisho.github.io/
保管庫（リポジトリ）: tera-naisho/tera-naisho.github.io（GitHub 組織 tera-naisho）
つくりは「Ado 非公式ワクワク秘密基地」（~/ado-himitsukichi）・「CLAN QUEEN 秘密の帝国」（~/clanqueen-teikoku）と同じ流れ。

- `data/core.json` … 手で書くできごと（1 行 1 件。毎月、前の月のできごとを追記。ネタ元は公式サイトの News https://www.teradaterasworld.com/news.html）
- `data/mv.json` … 寺田てらさんがイラストを描いた公式 MV。**概要欄に「寺田てら」のクレジットがあるか、本人の X（@trcoot）で告知された動画だけ**（告知ポストは "x" に入れる）。"artist_x" = そのアーティストの公式 X アカウント [[名前, ハンドル], ...]（MV の概要欄に書かれたものだけ）。本人ボタンの横にリンクで出る
  - 確認: `python3 tools/yt_credit.py 動画ID ...`（クレジット行を表示）
  - 探し方: `python3 tools/yt_uploads.py channel/<チャンネルID> > data/raw/ch_<名前>.json` でチャンネルの全動画を出し、yt_credit.py にかける
    （これまでに全件確認したチャンネル: ナナヲアカリ・まふまふ・ピノキオピー・ナユタン星人・Ado・猫又おかゆ・ピンキーポップヘップバーン・そらる。`python3 tools/scan_channel.py <名前> <チャンネルID>` で一気に確認できる）
- 公式 X まとめ（x.html）… core.json / mv.json の "x"（本人 @trcoot・公式スタッフ @teradateras のポスト URL）から作る。ポストの本文確認は publish.twitter.com/oembed で
  - CD グッズのクレジットだけの動画（MV の絵ではない）は入れない
- `python3 tools/mk_data.py` … core.json と mv.json から `data/timeline.json` を作る（MV は公開日に年表へ）
- `python3 build.py` … docs/ を生成（これからの予定は ~/knowledge-os/oshi-events.js の 寺田てら 分）
- 画像ファイルは置かない（AI 画像も置かない・2026-10-29 本人指示。トップのヘッダーは文字だけ）。寺田てらさんのイラストの複製・転載はしない。MV は YouTube サムネイルを直接表示して公式動画にリンク
- 広告・アフィリエイトなし。Google アナリティクスはほかのサイトと共通の測定 ID（ホスト名 tera-naisho.github.io で絞る）
