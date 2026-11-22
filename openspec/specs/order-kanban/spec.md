# order-kanban Specification

## Purpose
店内・持ち帰り注文の受付、かんばん方式による調理・提供ステータス管理、未払い請求集計および支払済み管理の仕様を定義する。

## Requirements

### Requirement: 注文登録
システムは `dine_in` と `takeout` 注文を登録し合計金額を自動算出しなければならない（SHALL）。

#### Scenario: 注文登録
- **WHEN** `POST /orders` に明細を送信する
- **THEN** `status="received"`、`paid=false`、合計金額を HTTP 201 で返す

### Requirement: かんばん遷移
システムは `received`→`preparing`→`ready`→`served` のみ遷移を許可しなければならない（MUST）。

#### Scenario: 遷移制御
- **WHEN** `PATCH /orders/{order_id}/status` を呼ぶ
- **THEN** 許可遷移は 200、不正遷移は 409 を返す

### Requirement: 会計連携
システムは未払い請求集計と支払済みマークを提供しなければならない（SHALL）。

#### Scenario: 二重支払防止
- **WHEN** `GET /tables/{table_id}/bill` と `POST /orders/{order_id}/mark-paid` を呼ぶ
- **THEN** 未払い合計を返し、既払い再実行は 409 を返す
