---
name: tail-sniper-scout
description: "Use when user asks to scan the market for ETF opportunities, says '看看机会', '有什么可以买的', '扫描全市场', '推荐ETF', or wants to find new ETFs to add to watchlist. Scans top 100 ETFs by volume and recommends 2-5 worth watching."
version: 1.0.0
author: TailSniper
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [finance, etf, market-scan, china-market, investment]
    related_skills: [tail-sniper-analyze, tail-sniper-status]
---

# TailSniper 全市场 ETF 机会扫描

## Overview

扫描全市场成交额前100只ETF的当日涨跌幅、规模、换手率，结合当前持仓和自选池，用网格交易视角挖掘值得关注的投资机会，推荐2-5只标的并给出建仓建议。

TailSniper 项目路径：`/Users/zhangjingyuan/Downloads/TailSniper`

## When to Use

- 用户说"看看机会"、"有什么可以买的"、"扫描全市场"、"推荐ETF"
- 用户想在自选池外发现新标的
- 市场出现大涨或大跌行情后想找机会
- Don't use for: 自选池日常分析（用 tail-sniper-analyze）

## 执行步骤

### 第一步：获取全市场行情

```bash
cd /Users/zhangjingyuan/Downloads/TailSniper
python bin/tail-sniper scout --account simulation --top 100
```

输出含：symbol、name、current_price、daily_change_pct、total_value_yi（规模亿元）、turnover_rate、in_watchlist、already_holding

### 第二步：加载当前配置（了解已有持仓，避免重复推荐）

```bash
python bin/tail-sniper data --account simulation
```

### 第三步：分析筛选

推荐维度（按优先级）：

**当日行情（重点）：**
- 大幅下跌（≤ -2%）且规模 > 20亿：短期超卖，网格建仓机会
- 涨幅异常放大（换手率是均值2倍以上）：资金异动，值得追踪
- 规模 < 5亿的 ETF 流动性风险高，不推荐

**资产配置：**
- 已在自选池的标的不重复推荐（除非有特别理由）
- 当前持仓集中某行业时，优先推荐其他行业分散风险

**基本面（结合知识）：**
- 当前宏观环境利好的行业方向
- 政策驱动的主题（AI、新能源、军工、低空经济等）

### 第四步：输出推荐报告

对每只推荐标的给出：
- 推荐理由（必须结合当天具体数据：跌幅、规模、换手率）
- 操作建议：**立即关注**（今天跌幅触发，适合建仓）/ **加入自选池观望**
- 参考建仓金额及理由

最后总结今日市场整体情绪（1-2句话：涨跌结构、资金流向方向）。

## 推荐参数参考

加入自选池时建议的参数范围（按标的波动性）：

| 类型 | 典型标的 | buy_trigger | sell_trigger | stop_loss |
|------|---------|-------------|-------------|-----------|
| 宽基 | 沪深300、上证50 | -1.0% | +1.5% | -12% |
| 中等波动 | 中证500、黄金、纳指 | -1.5% | +2.0% | -13% |
| 高波动 | 科创、芯片、机器人 | -2.5% | +3.5% | -18% |
| 极高波动 | 单一行业主题ETF | -3.0% | +4.0% | -20% |

## Common Pitfalls

1. **不要只看跌幅**：跌幅大但规模 < 5亿的ETF流动性差，不适合网格策略
2. **不要推荐已在自选池的标的**：除非今天有特别强的信号
3. **上涨的标的不追高**：大涨标的应加入观察等回调，不是"立即关注"
4. **推荐数量控制在2-5只**：太多反而没有重点

## Verification Checklist

- [ ] scout 数据已获取
- [ ] 已排除规模 < 5亿的标的
- [ ] 已排除已在自选池的标的（除非特别理由）
- [ ] 每只推荐标的有具体数据支撑（非泛泛而谈）
- [ ] 操作建议明确（立即关注 or 加入自选池观望）
- [ ] 包含市场整体情绪总结
