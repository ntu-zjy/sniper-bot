---
name: sniper-signals
description: "Use when user asks for ETF trading signals, daily analysis, portfolio status, or says '分析今日行情', '今天怎么样', '有没有买入信号', '看看持仓', '我的账户', '持仓情况'. Fetches real-time A-share ETF prices and generates grid strategy signals per user."
version: 1.0.0
author: SniperBot
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [finance, etf, trading, grid-strategy, china-market]
---

# SniperBot 信号分析

## Overview

为当前 Telegram 用户拉取 A股 ETF 实时行情，执行网格策略分析，输出买卖建议。
持仓数据按 user_id 完全隔离，每个用户有独立的持仓文件。

SniperBot 路径：`/app`

## When to Use

- 用户说"分析今日行情"、"今天怎么样"、"有没有买入信号"、"看看持仓"
- 不要用于：修改自选池、支付相关

## 执行步骤

### 获取当前用户 user_id

```python
import os, sys
sys.path.insert(0, '/app')

# 从 HERMES_SESSION_KEY 提取 user_id
# 格式: agent:main:telegram:dm:{user_id}
session_key = os.environ.get('HERMES_SESSION_KEY', '')
parts = session_key.split(':')
user_id = int(parts[4]) if len(parts) >= 5 and parts[4].lstrip('-').isdigit() else 0

print(f"Session key: {session_key}")
print(f"User ID: {user_id}")
```

### 获取或创建用户 + 生成信号

```python
import os, sys
sys.path.insert(0, '/app')
from src.core import config
from src.user.models import UserStore
from src.user.portfolio import Portfolio
from src.market.a_share import fetch_prices
from src.strategy.grid import generate_signals, format_signals_text

# 提取 user_id
session_key = os.environ.get('HERMES_SESSION_KEY', '')
parts = session_key.split(':')
user_id = int(parts[4]) if len(parts) >= 5 and parts[4].lstrip('-').isdigit() else 0

config.load()
store = UserStore()

# 自动创建新用户（首次使用）
user, is_new = store.get_or_create(user_id, '', '')
if is_new:
    print(f"新用户已注册，user_id={user_id}")

# 拉取行情
symbols = [w.symbol for w in user.watchlist]
prices = fetch_prices(symbols)

# 持仓按 user_id 隔离
portfolio = Portfolio(user_id, user.account_type)
portfolio.update_prices({s: d['current_price'] for s, d in prices.items()})

# 生成信号
signals = generate_signals(
    prices, portfolio, user.watchlist,
    config.get()['strategy']['stop_loss']
)
print(format_signals_text(signals, user.account_type))
```

## 持仓查询

```python
import os, sys
sys.path.insert(0, '/app')
from src.core import config
from src.user.models import UserStore
from src.user.portfolio import Portfolio

session_key = os.environ.get('HERMES_SESSION_KEY', '')
parts = session_key.split(':')
user_id = int(parts[4]) if len(parts) >= 5 and parts[4].lstrip('-').isdigit() else 0

config.load()
store = UserStore()
user, _ = store.get_or_create(user_id, '', '')
portfolio = Portfolio(user_id, user.account_type)
import json
print(json.dumps(portfolio.get_summary(), ensure_ascii=False, indent=2))
```

## 数据隔离说明

- 每个用户的数据存储在 `/app/data/{user_id}/simulation/` 或 `/app/data/{user_id}/real/`
- `UserStore` 存储在 `/app/data/users.json`，按 user_id 索引
- 用户之间完全隔离，互不影响

## Common Pitfalls

1. 非交易时间（09:30前、15:00后、周末）行情是上一交易日收盘价，需注明
2. `HERMES_SESSION_KEY` 为空时（CLI 调试），user_id 默认为 0
