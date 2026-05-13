---
name: tail-sniper-status
description: "Use when user asks about current portfolio, holdings, trade history, profit/loss, account balance, or says '看看持仓', '账户情况', '盈亏怎么样', '有多少钱', '交易记录'. Shows simulation and real account status with P&L."
version: 1.0.0
author: TailSniper
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [finance, etf, portfolio, holdings, pnl, china-market]
    related_skills: [tail-sniper-analyze, tail-sniper-scout]
---

# TailSniper 账户持仓查询

## Overview

查询模拟盘和实盘的当前持仓、浮盈亏、已实现盈亏和历史交易记录。支持手动记录买卖交易。

TailSniper 项目路径：`/Users/zhangjingyuan/Downloads/TailSniper`

## When to Use

- 用户说"看看持仓"、"账户情况"、"盈亏怎么样"、"有多少钱"、"交易记录"
- 用户在券商App操作后想手动记录实盘交易
- 用户想对比模拟盘和实盘的表现
- Don't use for: 每日行情分析（用 tail-sniper-analyze）

## 查询持仓

```bash
cd /Users/zhangjingyuan/Downloads/TailSniper

# 终端表格显示
python bin/tail-sniper status --account simulation
python bin/tail-sniper status --account real

# JSON格式（含更多字段）
python bin/tail-sniper data --account simulation
python bin/tail-sniper data --account real

# 对比两个账户
python bin/tail-sniper compare
```

## 手动记录交易

用户在券商App完成实盘操作后，记录到系统：

```bash
# 记录买入
python bin/tail-sniper buy --account real <symbol> <quantity> <price>
# 例：python bin/tail-sniper buy --account real 510300 200 4.966

# 记录卖出
python bin/tail-sniper sell --account real <symbol> <quantity> <price>
# 例：python bin/tail-sniper sell --account real 518880 50 9.85
```

模拟盘交易由 tail-sniper-analyze 自动记录，一般不需要手动操作。

## 输出格式

查询后以清晰表格呈现：

**持仓概览：**
| 标的 | 数量 | 成本价 | 现价 | 市值 | 浮盈亏 |
|------|------|--------|------|------|--------|

**账户汇总：**
- 总成本 / 总市值 / 浮动盈亏 / 浮盈比例 / 已实现盈亏 / 总交易笔数

若用户没有指定账户，同时展示模拟盘和实盘。

## 生成 Dashboard

如需可视化查看，生成并打开本地网页：

```bash
python bin/tail-sniper dashboard --account simulation --signals-json '[]'
python bin/tail-sniper dashboard --account real --signals-json '[]'
```

## Common Pitfalls

1. **现价可能过时**：portfolio.json 中的 current_price 是上次交易时的价格，不是实时价。查询实时浮盈需先拉 prices 再计算
2. **手动记录实盘时核对数量和价格**：成交价以券商App实际成交为准，不要用当前行情价
3. **模拟盘和实盘数据隔离**：两个账户的 portfolio.json 分别存在 data/simulation/ 和 data/real/ 下

## Verification Checklist

- [ ] 已指定正确的 --account 参数
- [ ] 持仓表格数据完整（symbol、数量、成本、现价、盈亏）
- [ ] 账户汇总数据包含浮盈和已实现盈亏
- [ ] 手动记录时已确认 symbol、数量、价格无误
