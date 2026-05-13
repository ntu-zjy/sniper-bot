"""
每用户持仓管理（JSON 文件，按 user_id + account_type 隔离）
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from src.core import config


@dataclass
class Holding:
    symbol: str
    name: str
    quantity: float
    avg_cost: float
    current_price: float = 0.0

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.quantity * self.avg_cost

    @property
    def pnl_amount(self) -> float:
        return self.market_value - self.cost_basis

    @property
    def pnl_pct(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return (self.pnl_amount / self.cost_basis) * 100


@dataclass
class Trade:
    symbol: str
    name: str
    action: str          # BUY | SELL
    quantity: float
    price: float
    amount: float
    account_type: str
    timestamp: float = field(default_factory=time.time)


def _portfolio_path(user_id: int, account_type: str) -> Path:
    d = config.get_data_dir() / str(user_id) / account_type
    d.mkdir(parents=True, exist_ok=True)
    return d / "portfolio.json"


def _trades_path(user_id: int, account_type: str) -> Path:
    d = config.get_data_dir() / str(user_id) / account_type
    d.mkdir(parents=True, exist_ok=True)
    return d / "trades.json"


class Portfolio:
    def __init__(self, user_id: int, account_type: str):
        self.user_id = user_id
        self.account_type = account_type
        self._port_path = _portfolio_path(user_id, account_type)
        self._trades_path = _trades_path(user_id, account_type)
        self._holdings: dict[str, Holding] = {}
        self._trades: list[Trade] = []
        self._realized_pnl: float = 0.0
        self._load()

    def _load(self):
        if self._port_path.exists():
            raw = json.loads(self._port_path.read_text())
            self._realized_pnl = raw.get("realized_pnl", 0.0)
            for h in raw.get("holdings", []):
                obj = Holding(**h)
                self._holdings[obj.symbol] = obj
        if self._trades_path.exists():
            raw = json.loads(self._trades_path.read_text())
            self._trades = [Trade(**t) for t in raw]

    def _save(self):
        port_data = {
            "realized_pnl": self._realized_pnl,
            "holdings": [asdict(h) for h in self._holdings.values()],
        }
        self._port_path.write_text(json.dumps(port_data, ensure_ascii=False, indent=2))
        self._trades_path.write_text(
            json.dumps([asdict(t) for t in self._trades], ensure_ascii=False, indent=2)
        )

    def get_holding(self, symbol: str) -> Optional[Holding]:
        return self._holdings.get(symbol)

    def update_prices(self, prices: dict[str, float]):
        for symbol, price in prices.items():
            if symbol in self._holdings:
                self._holdings[symbol].current_price = price

    def apply_trade(self, trade: Trade):
        self._trades.append(trade)
        h = self._holdings.get(trade.symbol)
        if trade.action == "BUY":
            if h is None:
                self._holdings[trade.symbol] = Holding(
                    symbol=trade.symbol,
                    name=trade.name,
                    quantity=trade.quantity,
                    avg_cost=trade.price,
                    current_price=trade.price,
                )
            else:
                total_qty = h.quantity + trade.quantity
                h.avg_cost = (h.avg_cost * h.quantity + trade.price * trade.quantity) / total_qty
                h.quantity = total_qty
                h.current_price = trade.price
        elif trade.action == "SELL" and h is not None:
            self._realized_pnl += (trade.price - h.avg_cost) * trade.quantity
            h.quantity -= trade.quantity
            if h.quantity <= 0:
                del self._holdings[trade.symbol]
        self._save()

    def get_summary(self) -> dict:
        unrealized = sum(h.pnl_amount for h in self._holdings.values())
        total_cost = sum(h.cost_basis for h in self._holdings.values())
        total_market = sum(h.market_value for h in self._holdings.values())
        holdings_list = []
        for h in self._holdings.values():
            d = asdict(h)
            d["market_value"] = round(h.market_value, 2)
            d["pnl_amount"] = round(h.pnl_amount, 2)
            d["pnl_pct"] = round(h.pnl_pct, 2)
            holdings_list.append(d)
        return {
            "holdings": holdings_list,
            "total_cost": round(total_cost, 2),
            "total_market_value": round(total_market, 2),
            "unrealized_pnl": round(unrealized, 2),
            "realized_pnl": round(self._realized_pnl, 2),
            "total_pnl": round(unrealized + self._realized_pnl, 2),
            "trade_count": len(self._trades),
        }
