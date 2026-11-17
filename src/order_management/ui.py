# ruff: noqa: E501
"""HTML UI router for order-management."""

from html import escape

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

from order_management.models import Order, OrderStatus
from order_management.store import OrderStore

PORTAL_LINKS = [
    ("portal", "ポータル", "/ui/portal"),
    ("product", "商品管理", "/ui/products"),
    ("menu", "メニュー", "/ui/menus"),
    ("guest", "座席・顧客", "/ui/tables"),
    ("order", "注文かんばん", "/ui/orders/kanban"),
    ("accounting", "会計", "/ui/accounting/checkout"),
    ("sales", "売上", "/ui/sales/daily"),
    ("dine_in", "店内QR", "/ui/dine-in/session"),
    ("takeout", "持ち帰り", "/ui/takeout/login"),
]

KANBAN_COLUMNS: list[tuple[OrderStatus, str, str, str]] = [
    ("received", "1. 受付済み", "#eff6ff", "#1d4ed8"),
    ("preparing", "2. 調理中", "#fffbeb", "#b45309"),
    ("ready", "3. 提供可能", "#f0fdf4", "#15803d"),
    ("served", "4. 提供・完了", "#f8fafc", "#475569"),
]

NEXT_STATUS: dict[OrderStatus, OrderStatus | None] = {
    "received": "preparing",
    "preparing": "ready",
    "ready": "served",
    "served": None,
}


def _source_badge(order: Order) -> str:
    if order.source == "takeout":
        return '<span class="badge" style="background:#fef3c7;color:#92400e">店外持ち帰り</span>'
    if order.is_takeout_from_table:
        return '<span class="badge" style="background:#ffedd5;color:#9a3412">席発持ち帰り</span>'
    return '<span class="badge" style="background:#dbeafe;color:#1e40af">店内飲食</span>'


def _render_shell(*, title: str, subtitle: str, active_subtab: str, body_html: str) -> str:
    nav_html = "".join(
        f'<a class="nav-pill{" active" if key == "order" else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in PORTAL_LINKS
    )
    subtabs = [
        ("kanban", "注文かんばんボード", "/ui/orders/kanban"),
        ("detail", "注文詳細・進行操作", "/ui/orders/detail"),
        ("bills", "席別会計金額サマリー", "/ui/orders/bills"),
    ]
    subtab_html = "".join(
        f'<a class="subtab{" active" if key == active_subtab else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in subtabs
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} | まちなか飲食店サポート</title>
  <style>
    :root {{ --bg:#f8fafc; --surface:#fff; --navy:#0f172a; --slate:#334155; --muted:#64748b; --border:#e2e8f0; --accent:#ea580c; --accent-soft:#fff7ed; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--navy); line-height:1.5; font-family:"Noto Sans CJK JP","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; }}
    .topbar {{ background:var(--navy); color:#fff; padding:0 24px; height:54px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .brand {{ display:flex; align-items:center; gap:10px; font-weight:700; font-size:15px; white-space:nowrap; }}
    .brand-badge {{ background:var(--accent); color:#fff; padding:2px 8px; border-radius:6px; font-size:11px; }}
    .nav-links {{ display:flex; gap:4px; overflow-x:auto; }}
    .nav-pill {{ color:#cbd5e1; text-decoration:none; font-size:12px; font-weight:600; padding:6px 10px; border-radius:6px; white-space:nowrap; }}
    .nav-pill.active {{ background:var(--accent); color:#fff; }}
    .subbar {{ background:var(--surface); border-bottom:1px solid var(--border); padding:12px 24px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .subbar h1 {{ margin:0; font-size:18px; }}
    .subbar .subtitle {{ margin:2px 0 0; font-size:12px; color:var(--muted); }}
    .subtabs {{ display:flex; gap:8px; }}
    .subtab {{ text-decoration:none; color:var(--slate); font-size:13px; font-weight:600; padding:7px 14px; border-radius:8px; border:1px solid var(--border); background:#fff; }}
    .subtab.active {{ background:var(--accent-soft); color:var(--accent); border-color:#fdba74; }}
    .container {{ max-width:1220px; margin:0 auto; padding:20px 24px 28px; }}
    .kanban-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; align-items:start; }}
    .col {{ background:#fff; border:1px solid var(--border); border-radius:12px; overflow:hidden; min-height:420px; }}
    .col-head {{ padding:10px 14px; font-weight:800; font-size:13px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); }}
    .col-body {{ padding:10px; display:flex; flex-direction:column; gap:10px; }}
    .k-card {{ border:1px solid var(--border); border-radius:10px; padding:11px 12px; background:#fff; box-shadow:0 1px 2px rgba(15,23,42,.04); }}
    .card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:16px 18px; box-shadow:0 1px 2px rgba(15,23,42,.04); }}
    .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; }}
    .btn {{ display:inline-block; text-decoration:none; font-size:12px; font-weight:700; padding:6px 12px; border-radius:8px; border:none; cursor:pointer; }}
    .btn-primary {{ background:var(--accent); color:#fff; }}
    .btn-secondary {{ background:#f1f5f9; color:var(--slate); border:1px solid var(--border); }}
    .grid-2 {{ display:grid; grid-template-columns:1.2fr 1fr; gap:18px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th {{ text-align:left; padding:10px 12px; background:#f8fafc; color:var(--muted); font-size:12px; border-bottom:1px solid var(--border); }}
    td {{ padding:10px 12px; border-bottom:1px solid var(--border); }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span>🍽️ まちなか飲食店サポート</span>
      <span class="brand-badge">店長・スタッフ共通ポータル</span>
    </div>
    <nav class="nav-links">{nav_html}</nav>
  </header>
  <section class="subbar">
    <div>
      <h1>{escape(title)}</h1>
      <p class="subtitle">{escape(subtitle)}</p>
    </div>
    <div class="subtabs">{subtab_html}</div>
  </section>
  <main class="container">{body_html}</main>
</body>
</html>
"""


def create_ui_router(store: OrderStore) -> APIRouter:
    """Create FastAPI router providing HTML UI screens for order-management."""
    router = APIRouter(tags=["ui"])

    @router.get("/ui/orders/kanban", response_class=HTMLResponse)
    def kanban_page() -> str:
        orders = store.list_orders()
        cols_html = []
        for status_key, col_title, bg, fg in KANBAN_COLUMNS:
            col_orders = [o for o in orders if o.status == status_key]
            cards = []
            for o in col_orders:
                items_html = "".join(
                    f'<div style="font-size:12px;color:#334155">• {escape(it.product_name)} × {it.quantity}</div>'
                    for it in o.items
                )
                target_label = f"席: {escape(o.table_id[:8])}" if o.table_id else f"顧客: {escape((o.customer_id or '-')[:12])}"
                nxt = NEXT_STATUS[o.status]
                action = (
                    f'<button class="btn btn-primary" style="padding:4px 9px;font-size:11px" '
                    f'onclick="advanceStatus(\'{escape(o.order_id)}\', \'{nxt}\')">次へ ({nxt})</button>'
                    if nxt
                    else '<span class="badge" style="background:#dcfce7;color:#166534">完了</span>'
                )
                paid_txt = "会計済" if o.paid else "未会計"
                cards.append(
                    f'<div class="k-card">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">'
                    f'{_source_badge(o)}<span style="font-size:11px;color:#64748b">{paid_txt}</span></div>'
                    f'<div style="font-weight:700;font-size:13px;margin-bottom:4px">'
                    f'<a href="/ui/orders/detail?order_id={escape(o.order_id)}" style="color:#0f172a;text-decoration:none">{escape(o.order_id)}</a></div>'
                    f'<div style="font-size:11px;color:#64748b;margin-bottom:6px">{target_label}</div>'
                    f'<div style="margin-bottom:8px">{items_html}</div>'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid #f1f5f9;padding-top:6px">'
                    f'<strong>¥{o.total_amount:,}</strong>{action}</div></div>'
                )
            cards_str = "".join(cards) or '<div style="font-size:12px;color:#94a3b8;text-align:center;padding:24px 8px">該当注文なし</div>'
            cols_html.append(
                f'<div class="col">'
                f'<div class="col-head" style="background:{bg};color:{fg}">'
                f'<span>{escape(col_title)}</span><span>{len(col_orders)}件</span></div>'
                f'<div class="col-body">{cards_str}</div></div>'
            )

        body = f"""
        <div class="kanban-grid">{"".join(cols_html)}</div>
        """ + """
        <script>
          async function advanceStatus(oid, nextStatus) {
            const res = await fetch('/orders/' + oid + '/status', {
              method: 'PATCH', headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({status: nextStatus})
            });
            if (res.ok) window.location.reload();
          }
        </script>
        """
        return _render_shell(
            title="注文管理 › 統合注文かんばんボード",
            subtitle="店内注文・席発持ち帰り・店外持ち帰り注文を「受付→調理中→提供可能→完了」で一元進行します",
            active_subtab="kanban",
            body_html=body,
        )

    @router.get("/ui/orders/detail", response_class=HTMLResponse)
    def order_detail_page(order_id: str | None = Query(default=None)) -> str:
        orders = store.list_orders()
        selected: Order | None = None
        if order_id:
            selected = next((o for o in orders if o.order_id == order_id), None)
        if selected is None and orders:
            selected = orders[-1]

        order_list_rows = "".join(
            f"<tr>"
            f'<td><a href="/ui/orders/detail?order_id={escape(o.order_id)}" style="font-weight:700;color:#ea580c">{escape(o.order_id)}</a></td>'
            f"<td>{_source_badge(o)}</td>"
            f"<td>{escape(o.status)}</td>"
            f"<td>¥{o.total_amount:,}</td></tr>"
            for o in orders
        ) or '<tr><td colspan="4" style="color:#64748b">注文がありません。</td></tr>'

        if selected is not None:
            steps = [("received", "受付"), ("preparing", "調理中"), ("ready", "提供可能"), ("served", "提供完了")]
            reached = True
            step_html = []
            for skey, slabel in steps:
                is_cur = skey == selected.status
                bg = "#ea580c" if is_cur else ("#16a34a" if reached else "#e2e8f0")
                fg = "#fff" if (is_cur or reached) else "#64748b"
                step_html.append(
                    f'<div style="flex:1;text-align:center;padding:8px;border-radius:8px;background:{bg};color:{fg};font-size:12px;font-weight:700">'
                    f"{escape(slabel)}</div>"
                )
                if is_cur:
                    reached = False
            item_rows = "".join(
                f"<tr><td>{escape(it.product_name)}</td><td>¥{it.unit_price:,}</td><td>{it.quantity}</td><td>¥{it.unit_price * it.quantity:,}</td></tr>"
                for it in selected.items
            )
            detail_panel = (
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
                f'<h2 style="margin:0;font-size:16px">注文詳細: <code>{escape(selected.order_id)}</code></h2>'
                f"{_source_badge(selected)}</div>"
                f'<div style="display:flex;gap:8px;margin-bottom:16px">{"".join(step_html)}</div>'
                f"<table><thead><tr><th>商品</th><th>単価</th><th>数量</th><th>小計</th></tr></thead><tbody>{item_rows}</tbody></table>"
                f'<div style="margin-top:14px;display:flex;justify-content:space-between;align-items:center">'
                f'<span style="font-size:13px;color:#64748b">会計状態: {"支払済" if selected.paid else "未払い"}</span>'
                f'<strong style="font-size:20px;color:#ea580c">合計 ¥{selected.total_amount:,}</strong></div>'
            )
        else:
            detail_panel = '<p style="color:#64748b">表示できる注文がありません。</p>'

        body = f"""
        <div class="grid-2">
          <div class="card">{detail_panel}</div>
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">受付済み注文一覧</h2>
            <table>
              <thead><tr><th>注文ID</th><th>種別</th><th>ステータス</th><th>金額</th></tr></thead>
              <tbody>{order_list_rows}</tbody>
            </table>
          </div>
        </div>
        """
        return _render_shell(
            title="注文管理 › 注文詳細・ステータス進行",
            subtitle="個別注文の調理ステップ進捗（received → preparing → ready → served）と明細を確認します",
            active_subtab="detail",
            body_html=body,
        )

    @router.get("/ui/orders/bills", response_class=HTMLResponse)
    def table_bills_page() -> str:
        orders = store.list_orders()
        table_ids = list(dict.fromkeys(o.table_id for o in orders if o.table_id))
        rows = []
        for tid in table_ids:
            bill = store.get_table_bill(tid)
            table_orders = [o for o in orders if o.table_id == tid]
            paid_total = sum(o.total_amount for o in table_orders if o.paid)
            status_badge = (
                '<span class="badge" style="background:#dcfce7;color:#166534">全額精算済</span>'
                if bill.total_amount == 0
                else '<span class="badge" style="background:#fef3c7;color:#92400e">未払い残高あり</span>'
            )
            rows.append(
                f"<tr><td><code>{escape(tid)}</code></td>"
                f"<td>{len(table_orders)} 件</td>"
                f"<td>{len(bill.order_ids)} 件</td>"
                f"<td>¥{paid_total:,}</td>"
                f"<td><strong style='color:#ea580c'>¥{bill.total_amount:,}</strong></td>"
                f"<td>{status_badge}</td></tr>"
            )
        rows_html = "".join(rows) or '<tr><td colspan="6" style="text-align:center;color:#64748b">テーブル別注文はありません。</td></tr>'

        body = f"""
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
            <h2 style="margin:0;font-size:16px">席別 未払い請求金額サマリー（I-3 会計連携）</h2>
            <a class="btn btn-primary" href="/ui/orders/kanban">かんばんボードへ</a>
          </div>
          <table>
            <thead><tr><th>席ID</th><th>総注文数</th><th>未払い件数</th><th>支払済み額</th><th>未払い請求額</th><th>精算状況</th></tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """
        return _render_shell(
            title="注文管理 › 席別会計金額サマリー",
            subtitle="会計管理サービスから参照される席ごとの未払い注文一覧と合計請求額を確認します",
            active_subtab="bills",
            body_html=body,
        )

    return router
