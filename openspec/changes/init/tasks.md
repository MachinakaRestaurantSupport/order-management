# タスク一覧: order-management 初期MVP

- [x] 0.1 初期設定ファイル・`.gitignore`・submodule 参照のコミット
- [x] 0.2 OpenSpec `init` 変更（proposal / spec / design / tasks）の作成と検証
- [x] 1.1 Python プロジェクト基盤（`pyproject.toml`）の追加
- [x] 1.2 ドメインモデル（`src/order_management/__init__.py`, `models.py`）の実装 `[OrderManagement_R01.DM01-01]`
- [x] 1.3 インメモリストア（`src/order_management/store.py`）の実装 `[OrderManagement_R01.DM01-01, 02, 03]`
- [ ] 1.4 FastAPI アプリケーション・エンドポイント（`src/order_management/main.py`）の実装 `[OrderManagement_R01.DM01-01, 02, 03]`
- [ ] 2.1 単体試験（`tests/test_orders.py`）の実装と pytest / ruff 検証 `[OrderManagement_R01.DM01-01, 02, 03]`
