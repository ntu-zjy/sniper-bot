"""网格交易策略引擎"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from src.user.models import WatchItem
from src.user.portfolio import Portfolio, Holding


@dataclass
class Signal:
    symbol: str
    name: str
    action: str           # BUY | SELL | HOLD
    quantity: float
    amount: float
    current_price: float
    daily_change_pct: float
    pnl_pct: float
    reason: str


def generate_signals(
    prices: dict[str, dict],
    portfolio: Portfolio,
    watchlist: list[WatchItem],
    stop_loss_pct: float = -15.0,
) -> list[Signal]:
    signals = []
    for item in watchlist:
        sym = item.symbol
        price_data = prices.get(sym)
        if price_data is None:
            continue

        current_price = price_data["current_price"]
        daily_change = price_data["daily_change_pct"]
        name = price_data.get("name", item.name)

        holding = portfolio.get_holding(sym)
        pnl_pct = holding.pnl_pct if holding else 0.0

        # 止损优先
        if holding and pnl_pct <= stop_loss_pct:
            qty = holding.quantity
            signals.append(Signal(
                symbol=sym, name=name, action="SELL",
                quantity=qty, amount=round(qty * current_price, 2),
                current_price=current_price, daily_change_pct=daily_change,
                pnl_pct=pnl_pct,
                reason=f"止损：浮亏{pnl_pct:.1f}%触发清仓",
            ))
            continue

        # 卖出：当日涨幅触发 → 卖 1/3
        if holding and daily_change >= item.sell_trigger:
            qty = max(1, round(holding.quantity / 3))
            # 按100股整数单位取整
            qty = max(100, round(qty / 100) * 100)
            signals.append(Signal(
                symbol=sym, name=name, action="SELL",
                quantity=qty, amount=round(qty * current_price, 2),
                current_price=current_price, daily_change_pct=daily_change,
                pnl_pct=pnl_pct,
                reason=f"日涨{daily_change:.1f}%触发卖出1/3",
            ))
            continue

        # 买入：当日跌幅触发 + 未超仓位上限
        if daily_change <= item.buy_trigger:
            current_holding_value = holding.cost_basis if holding else 0.0
            if current_holding_value >= item.max_holding:
                signals.append(Signal(
                    symbol=sym, name=name, action="HOLD",
                    quantity=0, amount=0,
                    current_price=current_price, daily_change_pct=daily_change,
                    pnl_pct=pnl_pct,
                    reason=f"日跌{daily_change:.1f}%但已达持仓上限({item.max_holding:.0f}元)",
                ))
            else:
                qty = round(item.unit_capital / current_price / 100) * 100
                qty = max(100, qty)
                signals.append(Signal(
                    symbol=sym, name=name, action="BUY",
                    quantity=qty, amount=round(qty * current_price, 2),
                    current_price=current_price, daily_change_pct=daily_change,
                    pnl_pct=pnl_pct,
                    reason=f"日跌{daily_change:.1f}%触发买入",
                ))
            continue

        signals.append(Signal(
            symbol=sym, name=name, action="HOLD",
            quantity=0, amount=0,
            current_price=current_price, daily_change_pct=daily_change,
            pnl_pct=pnl_pct,
            reason="涨跌幅未触发阈值",
        ))

    return signals


def format_signals_text(signals: list[Signal], account_type: str) -> str:
    """格式化为 Telegram 消息文本"""
    mode = "模拟盘" if account_type == "simulation" else "实盘"
    lines = [f"📊 *今日信号（{mode}）*\n"]
    buy_list = [s for s in signals if s.action == "BUY"]
    sell_list = [s for s in signals if s.action == "SELL"]
    hold_list = [s for s in signals if s.action == "HOLD"]

    if buy_list:
        lines.append("🟢 *买入信号*")
        for s in buy_list:
            lines.append(f"  {s.name}（{s.symbol}）")
            lines.append(f"  现价 {s.current_price} | 涨跌 {s.daily_change_pct:+.2f}%")
            lines.append(f"  建议买入 {s.quantity}股 ≈ {s.amount:.0f}元")
            lines.append(f"  📌 {s.reason}\n")

    if sell_list:
        lines.append("🔴 *卖出信号*")
        for s in sell_list:
            lines.append(f"  {s.name}（{s.symbol}）")
            lines.append(f"  现价 {s.current_price} | 涨跌 {s.daily_change_pct:+.2f}%")
            lines.append(f"  建议卖出 {s.quantity}股 ≈ {s.amount:.0f}元")
            lines.append(f"  📌 {s.reason}\n")

    if hold_list:
        lines.append("⚪ *观望*")
        for s in hold_list:
            lines.append(f"  {s.name}（{s.symbol}）{s.daily_change_pct:+.2f}%")

    if not signals:
        lines.append("今日无信号，继续观望。")

    return "\n".join(lines)
