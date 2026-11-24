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

### Requirement: サブモジュール参照のコミット指定管理

本リポジトリは `.gitmodules` に `branch` 設定を持たせず `reference/system-integration` を確定コミット SHA（gitlink）指定で管理しなければならず（MUST）、`reference/system-integration/` 配下を読み取り専用として直接変更してはならない（SHALL）。

#### Scenario: サブモジュール参照の更新とマージ

- **WHEN** `system-integration` の確定コミット SHA（`<commit-sha>`）を `reference/system-integration` にチェックアウトし、`system-integration` PR の Merge commit マージ後に本リポジトリの PR を `main` にマージするとき
- **THEN** `.gitmodules` の書き換えやマージ後の `main` 戻し作業なしで、正しい仕様・画像参照を維持したままマージが完了する（SHALL）
