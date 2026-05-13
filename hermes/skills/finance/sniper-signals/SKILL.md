---
name: sniper-signals
description: "Use when user asks for ETF trading signals, daily analysis, portfolio status, or says '分析今日行情', '今天怎么样', '有没有买入信号', '看看持仓', '我的账户'. Fetches real-time A-share ETF prices and generates grid strategy signals."
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

为当前用户拉取 A股 ETF 实时行情，执行网格策略分析，输出买卖建议。
数据按 Telegram user_id 隔离，每个用户有独立的自选池和持仓。

SniperBot 路径：`/app`

## When to Use

- 用户说"分析今日行情"、"今天怎么样"、"有没有买入信号"、"看看持仓"
- 不要用于：修改自选池、支付相关

## 执行步骤

### 第一步：获取当前用户信息

```python
import sys
sys.path.insert(0, '/app')
from src.core import config
from src.user.models import UserStore

config.load()
store = UserStore()

# 通过 hermes context 获取 telegram user_id
# user_id 在 hermes 里通过 {{USER_ID}} 或环境变量传入
import os
user_id = int(os.environ.get('HERMES_USER_ID', '0'))
user = store.get(user_id)
if not user:
    print("用户未注册，请先发送 /start")
    exit()

print(f"用户: {user.first_name}, 模式: {user.account_type}, 自选池: {len(user.watchlist)}只")
```

### 第二步：拉取行情 + 生成信号

```python
import sys
sys.path.insert(0, '/app')
from src.core import config
from src.user.models import UserStore
from src.user.portfolio import Portfolio
from src.market.a_share import fetch_prices
from src.strategy.grid import generate_signals, format_signals_text
import os

config.load()
store = UserStore()
user_id = int(os.environ.get('HERMES_USER_ID', '0'))
user = store.get(user_id)

symbols = [w.symbol for w in user.watchlist]
prices = fetch_prices(symbols)

portfolio = Portfolio(user.user_id, user.account_type)
portfolio.update_prices({s: d['current_price'] for s, d in prices.items()})

signals = generate_signals(prices, portfolio, user.watchlist,
                           config.get()['strategy']['stop_loss'])
print(format_signals_text(signals, user.account_type))
```

## 输出格式

以 Markdown 表格输出：
- 买入信号（绿色）：标的、现价、涨跌幅、建议买入数量和金额、原因
- 卖出信号（红色）：标的、现价、涨跌幅、建议卖出数量、原因
- 观望：简短列出

## Common Pitfalls

1. 非交易时间（09:30前、15:00后、周末）行情数据是上一交易日收盘价，需注明
2. user_id 必须正确传入，否则找不到用户数据
