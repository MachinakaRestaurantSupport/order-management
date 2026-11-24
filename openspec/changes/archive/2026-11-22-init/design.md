# 設計書: 注文管理（order-management）初期MVP

## アーキテクチャ概要

FastAPI を用いた軽量なステートフル（インメモリストア）HTTP API サービスとして構成する。

- `src/order_management/models.py`: Pydantic v2 モデル（`OrderItemInput`, `OrderCreateRequest`, `OrderStatusUpdateRequest`, `Order`, `TableBill` 等）および許可状態遷移マップの定義
- `src/order_management/store.py`: スレッドセーフまたは単一プロセス内インメモリリポジトリ（`OrderStore`）とビジネスロジック（合計金額算出、遷移バリデーション、未払い集計、支払済み更新）
- `src/order_management/main.py`: `create_app()` ファクトリと `app = create_app()` エントリポイント、各 HTTP エンドポイントおよびエラーハンドリング（404 / 409）

## USDM トレーサビリティ

| USDM 要求ID | 要求概要 | 設計要素 / エンドポイント |
| --- | --- | --- |
| `OrderManagement_R01.DM01-01` | 店内（I-1）・持ち帰り（I-2）注文の登録と合計金額自動算出 | `POST /orders`, `OrderCreateRequest`, `OrderStore.create_order` |
| `OrderManagement_R01.DM01-02` | かんばんステータス（`received`→`preparing`→`ready`→`served`）更新と不正遷移の HTTP 409 制御 | `PATCH /orders/{order_id}/status`, `GET /orders`, `ALLOWED_TRANSITIONS`, `OrderStore.update_status` |
| `OrderManagement_R01.DM01-03` | 会計管理（I-3）連携（注文詳細・未払い請求集計・支払済みマークと二重支払防止 HTTP 409） | `GET /orders/{order_id}`, `GET /tables/{table_id}/bill`, `POST /orders/{order_id}/mark-paid` |

## 状態遷移設計

許可される遷移は以下の単方向のみとし、逆転・スキップ・同一状態への遷移は HTTP 409 Conflict を返す。

- `received` → `preparing`
- `preparing` → `ready`
- `ready` → `served`
- `served` → （終端）
