# 変更提案: 注文管理（order-management）初期MVP実装

## 背景・目的

MachinakaRestaurantSupportTools のサブシステム「注文管理（order-management）」について、店内注文（I-1）および持ち帰り注文（I-2）の統合受付、キッチン・ホール向けのかんばんステータス管理、ならびに会計管理（I-3）向けの請求金額算出・支払済みマーク機能を提供する初期MVPを実装する。

## 変更内容

- Python / FastAPI による REST API 基盤（`pyproject.toml`, `src/order_management/`）の構築
- 注文登録（`POST /orders`）、一覧・詳細取得（`GET /orders`, `GET /orders/{order_id}`）の実装
- かんばんステータス遷移（`PATCH /orders/{order_id}/status`）および不正遷移時の HTTP 409 制御の実装
- テーブル別未払い請求集計（`GET /tables/{table_id}/bill`）および支払済みマーク（`POST /orders/{order_id}/mark-paid`）の実装
- 単体試験（`tests/test_orders.py`）の整備

## 影響範囲

- 本リポジトリ内の `pyproject.toml`, `src/order_management/`, `tests/` を新規作成する
- `reference/system-integration/` 配下は読み取り専用とし変更しない
