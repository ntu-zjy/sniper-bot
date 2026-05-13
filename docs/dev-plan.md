# 开发计划

## 当前状态（2026-05-13）

- ✅ hermes gateway 运行在腾讯云新加坡服务器（¥30/月）
- ✅ Telegram bot 可正常对话
- ✅ sniper-signals skill 接入，支持 A股 ETF 行情分析
- ✅ 按 user_id 会话隔离（group_sessions_per_user: true）
- ✅ 持仓数据按 user_id 分目录隔离
- 🚧 目前单用户自用

---

## Phase 1：MVP（已完成）

- [x] Telegram Bot 基础框架（hermes gateway）
- [x] A股行情接入（akshare）
- [x] 网格策略信号生成
- [x] 每日 14:40 自动推送（待配置 hermes cron）
- [x] 持仓查询
- [x] 服务器部署（腾讯云新加坡）

---

## Phase 2：多用户订阅制

### 核心问题
hermes 已支持多用户会话隔离，缺的是**订阅鉴权层**。

### 方案 A：手动白名单（轻量，适合早期）

- skill 执行前查 `subscriptions.json`，验证 user_id 是否付费
- 收费通过微信/支付宝手动核验，收到钱手动加白名单
- 实现快，适合用户 < 50 人阶段

```json
{
  "12345678": { "plan": "pro", "expires": "2026-06-13" },
  "87654321": { "plan": "free" }
}
```

### 方案 B：Telegram Payment API（自动化）

- Telegram 原生支持 Stars 付款（国际用户）
- 国内用户接支付宝/微信通过 Provider Token
- 用户在对话里直接点付款，付完自动解锁权限
- 需要实现 `/subscribe` command handler

### 用户分层

| 层级 | 价格 | 功能 |
|------|------|------|
| 免费版 | 0 | 每日推送默认自选池信号，限 5 只 ETF |
| 标准版 | ¥29/月 | 自定义自选池（≤10只）、模拟盘+实盘 |
| 专业版 | ¥99/月 | 无限自选池、A股+美股、历史回测 |

---

## Phase 3：功能完善

- [ ] 美股 ETF 行情接入（yfinance）
- [ ] 22:00 美股推送
- [ ] 自动复投（profits reinvested）
- [ ] 历史回测功能
- [ ] 全市场扫描推送

---

## Phase 4：产品化

- [ ] 推荐好友返佣
- [ ] 数据看板（Web）
- [ ] 自动续费提醒（到期前3天）
