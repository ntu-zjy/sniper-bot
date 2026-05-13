---
name: tail-sniper-analyze
description: "Use when user asks for daily ETF analysis, trading signals, portfolio review, or says '分析今日行情', '尾盘分析', '今天怎么样', '有没有买入信号'. Runs full grid-strategy analysis for both simulation and real accounts, auto-executes simulation trades, generates dashboard."
version: 1.0.0
author: TailSniper
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [finance, etf, trading, grid-strategy, china-market]
    related_skills: [tail-sniper-scout, tail-sniper-status]
---

# TailSniper 每日尾盘分析

## Overview

对模拟盘和实盘两个账户的 ETF 自选池执行完整网格策略分析，结合当日实时行情和持仓状态，自主推理买卖建议。模拟盘自动执行交易记录，实盘只给建议。同时扫描全市场 ETF 寻找自选池外的机会。

TailSniper 项目路径：`/Users/zhangjingyuan/Downloads/TailSniper`

## When to Use

- 用户说"分析今日行情"、"今天怎么样"、"有没有买入信号"、"尾盘分析"
- 每日 14:40 前后触发的定时任务
- 用户想知道当前持仓状态和操作建议
- Don't use for: 查看持仓详情（用 tail-sniper-status）、市场机会扫描（用 tail-sniper-scout）

## 执行步骤

### 第一步：加载两个账户配置与持仓

```bash
cd /Users/zhangjingyuan/Downloads/TailSniper
python bin/tail-sniper data --account simulation
python bin/tail-sniper data --account real
```

关注输出中的：`watchlist`（买卖阈值）、`portfolio.holdings`（当前持仓）、`unit_capital_compounded`（复投金额）

### 第二步：拉取实时行情

```bash
python bin/tail-sniper prices --account simulation
```

### 第三步：全市场扫描

```bash
python bin/tail-sniper scout --account simulation --top 100
```

### 第四步：自主推理

对每只标的综合判断（网格交易理念，非硬性规则）：

- `daily_change_pct <= buy_trigger`：短期超卖，考虑买入
- `daily_change_pct >= sell_trigger`：短期反弹，考虑减仓
- `pnl_pct <= stop_loss`：止损信号，优先于买入判断
- `market_value >= max_holding`：已满仓，即使触发也观望
- 结合全市场情绪、宏观背景综合判断，不机械套用阈值

买入数量：`floor(unit_capital_compounded / current_price / 100) * 100`

### 第五步：模拟盘自动执行

对判断为买入/卖出的标的，自动写入模拟盘账本：

```bash
python bin/tail-sniper buy --account simulation <symbol> <quantity> <price>
python bin/tail-sniper sell --account simulation <symbol> <quantity> <price>
```

卖出规则：默认卖持仓50%；涨幅超卖出阈值2倍则全仓卖出；止损则全仓卖出。
实盘（real）跳过此步骤，只输出建议。

### 第六步：生成 Dashboard

```bash
python bin/tail-sniper dashboard --account simulation --no-browser --signals-json '<JSON>'
python bin/tail-sniper dashboard --account real --no-browser --signals-json '<JSON>'
```

signals-json 格式：
```json
[{"symbol":"510300","name":"沪深300ETF","action":"BUY","quantity":200,"amount":1000.0,
  "current_price":5.0,"daily_change_pct":-1.5,"pnl_pct":0,"reason":"跌幅触发买入"}]
```

### 第七步：汇报

分三块输出：

**【模拟盘】** 表格：标的 / 现价 / 涨跌 / 操作 / 推理；说明自动执行了哪些交易

**【实盘】** 表格：标的 / 现价 / 涨跌 / 操作建议 / 推理；提醒用户在券商App操作后手动记录

**【市场扫描】** 2-3只自选池外机会：推荐理由 + 是否建议加入自选池

最后一段总结今日市场整体情绪。

## Common Pitfalls

1. **不要机械套用阈值**：跌幅刚好等于阈值时，结合整体市场情绪判断，而不是无脑触发
2. **止损优先于买入**：持仓浮亏超过 stop_loss 时，先止损再考虑其他操作
3. **满仓不加仓**：`market_value >= max_holding` 时明确说明"已满仓，建议观望"
4. **实盘绝不自动记账**：mode == "real" 时只输出建议，等用户确认后手动记录
5. **行情数据延迟**：非交易时间拉到的是上一个交易日收盘价，需在汇报中注明

## Verification Checklist

- [ ] 两个账户的 data 和 prices 均已拉取
- [ ] 全市场 scout 已执行
- [ ] 每只标的均有明确操作和推理
- [ ] 模拟盘买卖已通过 CLI 执行并确认
- [ ] 两个账户的 dashboard 均已生成
- [ ] 汇报包含模拟盘、实盘、市场扫描三块
