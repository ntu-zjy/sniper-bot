"""A股 ETF 行情获取（基于 akshare）"""
import os
import akshare as ak
import pandas as pd


def fetch_prices(symbols: list[str]) -> dict[str, dict]:
    """
    返回 {symbol: {"current_price": float, "daily_change_pct": float, "name": str}}
    SNIPER_MOCK=1 时返回测试数据
    """
    if os.environ.get("SNIPER_MOCK") == "1":
        return _mock_prices(symbols)

    df = ak.fund_etf_spot_em()
    df = df.rename(columns={
        "代码": "symbol",
        "名称": "name",
        "最新价": "price",
        "涨跌幅": "change_pct",
    })
    df["symbol"] = df["symbol"].astype(str)
    result = {}
    for sym in symbols:
        row = df[df["symbol"] == sym]
        if row.empty:
            continue
        r = row.iloc[0]
        result[sym] = {
            "current_price": float(r["price"]),
            "daily_change_pct": float(r["change_pct"]),
            "name": str(r["name"]),
        }
    return result


def scan_top_etfs(top_n: int = 100, min_value_yi: float = 5.0) -> list[dict]:
    """扫描成交额最大的 ETF，返回列表"""
    df = ak.fund_etf_spot_em()
    df = df.rename(columns={
        "代码": "symbol",
        "名称": "name",
        "最新价": "price",
        "涨跌幅": "change_pct",
        "成交额": "amount",
    })
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df = df[df["amount"] >= min_value_yi * 1e8]
    df = df.sort_values("amount", ascending=False).head(top_n)
    result = []
    for _, r in df.iterrows():
        result.append({
            "symbol": str(r["symbol"]),
            "name": str(r["name"]),
            "current_price": float(r["price"]),
            "daily_change_pct": float(r["change_pct"]),
        })
    return result


def _mock_prices(symbols: list[str]) -> dict[str, dict]:
    mock = {
        "510300": {"current_price": 4.05, "daily_change_pct": -1.2, "name": "沪深300ETF"},
        "510050": {"current_price": 2.91, "daily_change_pct": -0.8, "name": "上证50ETF"},
        "518880": {"current_price": 9.92, "daily_change_pct": 0.3,  "name": "黄金ETF"},
        "159915": {"current_price": 2.15, "daily_change_pct": -2.1, "name": "创业板ETF"},
        "512880": {"current_price": 1.43, "daily_change_pct": -3.5, "name": "证券ETF"},
    }
    return {s: mock[s] for s in symbols if s in mock}
