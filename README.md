# order-management

店内の席ごと・席発持ち帰り・店外持ち帰り注文を統合かんばんで管理し、受付・調理中・提供可能・完了の進行と席別会計金額を連携するツールです。  
店長・スタッフ共通ポータル（[ポータル画面イメージ](reference/system-integration/docs/images/portal/01-portal-dashboard.png)）におけるキッチン・注文管理の中核を担います。

## 画面遷移図

縮小画面キャプチャを用いた `order-management` の画面遷移図です（draw.io 編集用ソース: [transition.drawio](reference/system-integration/docs/images/order_management/transition.drawio)）。

![order-management 画面遷移図](reference/system-integration/docs/images/order_management/transition.svg)

## 代表機能イメージ

### 1. 統合注文かんばんボード (`GET /ui/orders/kanban`)
店内飲食・席発持ち帰り・店外持ち帰りすべての注文を `received`（受付済み）→ `preparing`（調理中）→ `ready`（提供可能）→ `served`（提供・完了）の4列で可視化し、ワンクリックで進行操作を行えます。

![統合注文かんばんボード](reference/system-integration/docs/images/order_management/01-order-kanban.png)

### 2. 注文詳細・進行操作 (`GET /ui/orders/detail`)
選択した注文の進捗ステッパー、注文種別、注文明細（単価・数量・小計）、支払い状態を確認できます。

![注文詳細・進行操作](reference/system-integration/docs/images/order_management/02-order-transition.png)

### 3. 席別会計金額サマリー (`GET /ui/orders/bills`)
テーブルごとに総注文数・未払い注文数・支払済み金額・未払い請求合計額を集計表示し、会計管理（I-3）の精算処理を支えます。

![席別会計金額サマリー](reference/system-integration/docs/images/order_management/03-table-bill.png)

## 提供 API・UI エンドポイント

| 種別 | メソッド & パス | 機能概要 |
|---|---|---|
| API | `GET /health` | ヘルスチェック |
| API | `POST /orders` | 店内・持ち帰り注文登録 (I-1, I-2) |
| API | `GET /orders` / `GET /orders/{order_id}` | 注文一覧・詳細取得 |
| API | `PATCH /orders/{order_id}/status` | かんばん状態遷移（409で不正遷移を防止） |
| API | `GET /tables/{table_id}/bill` | 席別未払い請求額算出 (I-3) |
| API | `POST /orders/{order_id}/mark-paid` | 支払済み更新・二重決済防止 |
| UI | `GET /ui/orders/kanban` | 統合注文かんばんボード画面 |
| UI | `GET /ui/orders/detail` | 注文詳細・進行操作画面 |
| UI | `GET /ui/orders/bills` | 席別会計金額サマリー画面 |

## テスト・静的解析の実行

```bash
../.venv/bin/python3 -m pytest -v
../.venv/bin/ruff check .
```
