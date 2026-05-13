import json
import os
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
_CONFIG_PATH = _ROOT / "config" / "config.json"

# 内置默认值，容器内无 config.json 时全靠环境变量 + 这里的默认值
_DEFAULTS: dict = {
    "telegram": {"bot_token": ""},
    "data_dir": "/app/data",
    "plans": {
        "free":  {"price_cny": 0,  "watchlist_limit": 5,   "markets": ["A"]},
        "pro":   {"price_cny": 29, "watchlist_limit": 10,  "markets": ["A"]},
        "elite": {"price_cny": 99, "watchlist_limit": 999, "markets": ["A", "US"]},
    },
    "schedule": {"a_share": "40 14 * * 1-5", "us_share": "0 22 * * 1-5"},
    "market": {
        "a_share_top_n": 100,
        "a_share_min_value_yi": 5.0,
        "default_watchlist": [
            {"symbol": "510300", "name": "沪深300ETF", "buy_trigger": -1.0, "sell_trigger": 1.5, "unit_capital": 1000, "max_holding": 5000},
            {"symbol": "510050", "name": "上证50ETF",  "buy_trigger": -1.0, "sell_trigger": 1.5, "unit_capital": 1000, "max_holding": 5000},
            {"symbol": "518880", "name": "黄金ETF",    "buy_trigger": -1.5, "sell_trigger": 2.0, "unit_capital": 1000, "max_holding": 5000},
            {"symbol": "159915", "name": "创业板ETF",  "buy_trigger": -2.0, "sell_trigger": 2.5, "unit_capital": 1000, "max_holding": 5000},
            {"symbol": "512880", "name": "证券ETF",    "buy_trigger": -2.0, "sell_trigger": 2.5, "unit_capital": 1000, "max_holding": 5000},
        ],
    },
    "strategy": {"stop_loss": -15.0},
}

_cfg: dict = {}


def load() -> dict:
    global _cfg
    import copy
    _cfg = copy.deepcopy(_DEFAULTS)

    # 若存在 config.json，用它覆盖默认值（本地开发用）
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH) as f:
            file_cfg = json.load(f)
        _deep_merge(_cfg, file_cfg)

    # 环境变量最高优先级
    if token := os.environ.get("TELEGRAM_BOT_TOKEN"):
        _cfg["telegram"]["bot_token"] = token
    if data_dir := os.environ.get("DATA_DIR"):
        _cfg["data_dir"] = data_dir

    return _cfg


def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def get() -> dict:
    if not _cfg:
        load()
    return _cfg


def get_data_dir() -> Path:
    cfg = get()
    raw = cfg.get("data_dir", "data")
    # 支持绝对路径（容器内挂载点）和相对路径
    d = Path(raw) if Path(raw).is_absolute() else _ROOT / raw
    d.mkdir(parents=True, exist_ok=True)
    return d
