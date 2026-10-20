# MARKET ATLAS — 経済の見取り図

公開市場データのみで作るモバイル対応の経済ダッシュボードです。個人の保有額、口数、取得価格、資産総額を登録しません。

- Webページ: `site/index.html`
- 投信データ: `site/data/funds.json` （基準日つきの参考値）
- 投信の試験的自動更新: `scripts/refresh_funds.py`
- 自動公開: `.github/workflows/pages.yml`

## 公開方法
GitHubの `Settings > Pages > Build and deployment > Source` で **GitHub Actions** を選択してください。成功した公開は `Actions` と `https://tatsuya-horie.github.io/market-atlas/` で確認します。

## 表示と制約
現在のインデックス数値カードは **2026-10-16を基準とした固定スナップショット** であり、日経平均とS&P500の最新値には自動更新されません。市場チャート（TradingView）は別途更新されます。為替の過去推移はFrankfurterの中央銀行由来の日次参考値でありリアルタイムの取引レートとは異なります。

投信の基準価額はデータに記載の基準日を確認してください。自動更新は三菱UFJ銀行のCSVフォーマットと外部アクセスに依存し、更新できない日は旧データが旧日付のまま表示されます。手動確認した値以外を推定で補完しません。ダッシュボードに表示されるのはeMAXIS Slimの2商品で、残りの保有5商品は今後の拡張対象です。

This public website uses no confidential credentials, holdings or personal portfolio values.


## Deployment retry
GitHub Pages Source is set to GitHub Actions. This commit triggers a new deployment after that setting was enabled.
