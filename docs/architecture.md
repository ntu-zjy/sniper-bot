# Sniper Bot 架构设计

## 产品定位

基于 Hermes Agent + Telegram 的量化交易信号订阅服务。
用户通过 Telegram 机器人订阅每日 A股/美股 ETF 网格交易信号，支持模拟盘和实盘两种模式。

## 用户分层

| 层级 | 价格 | 功能 |
|------|------|------|
| 免费版 | 0 | 每日推送默认自选池信号（模拟盘）、基础持仓查询 |
| 标准版 | ¥29/月 | 自定义自选池（≤10只）、模拟盘+实盘、全市场扫描 |
| 专业版 | ¥99/月 | 无限自选池、A股+美股双市场、优先推送、历史回测 |

## 市场范围

- **A股 ETF**：通过 akshare 获取，覆盖沪深两市 ETF
- **美股 ETF**：通过 yfinance 获取，覆盖纳斯达克/标普500等主流 ETF（SPY、QQQ、ARKK 等）
- **不支持**：加密货币、个股（风险控制）

## 技术架构

```
Telegram Bot API
      ↓
Hermes Agent (Sealos - 新加坡)
      ↓
sniper-bot 核心服务
  ├── bot/          Telegram 消息收发
  ├── scheduler/    定时任务（14:40 A股 / 22:00 美股）
  ├── strategy/     网格策略引擎（复用 TailSniper 逻辑）
  ├── market/       行情获取（akshare + yfinance）
  ├── user/         用户管理 + 订阅状态
  └── payment/      支付宝/微信支付 + Stripe
      ↓
PostgreSQL (Sealos)
  ├── users         用户信息、订阅状态、到期时间
  ├── portfolios    每用户持仓（支持多账户）
  ├── trades        交易记录
  └── watchlists    自选池配置
```

## 定时推送时间

| 市场 | 推送时间 | 说明 |
|------|---------|------|
| A股  | 14:40 工作日 | 尾盘信号 |
| 美股 | 22:00 工作日 | 美股开盘后1.5小时（东部时间 9:30 开盘）|

## 支付方案

- **国内**：支付宝（当面付/手机网站付款）+ 微信支付
- **海外**：Stripe（信用卡 + Apple Pay）
- 订阅到期前3天自动提醒续费

## 部署方案（Sealos 新加坡）

```
├── sniper-bot-api    Python FastAPI 服务（处理 Telegram webhook）
├── sniper-bot-worker 定时任务 Worker（行情拉取 + 信号生成 + 推送）
├── postgresql        用户数据持久化
└── redis             订阅状态缓存 + 任务队列
```

## 数据隔离

每个用户的持仓数据完全隔离：
- 数据库表通过 `user_id` 分区
- 模拟盘/实盘通过 `account_type` 字段区分
- 用户只能查看和修改自己的数据

## Telegram Bot 命令

```
/start          注册账号，引导订阅
/status         查看今日持仓和盈亏
/signals        手动触发今日信号分析
/watchlist      查看/修改自选池
/subscribe      订阅付费方案
/mode           切换模拟盘/实盘
/history        查看历史交易记录
/help           帮助
```
