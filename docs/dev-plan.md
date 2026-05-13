# 开发计划

## Phase 1：MVP（目标：单用户跑通）
- [ ] Telegram Bot 基础框架（python-telegram-bot）
- [ ] 用户注册 /start 流程
- [ ] A股行情接入（复用 TailSniper akshare 逻辑）
- [ ] 网格策略信号生成
- [ ] 每日 14:40 自动推送
- [ ] 持仓查询 /status
- [ ] 本地 PostgreSQL 数据库

## Phase 2：多用户 + 订阅
- [ ] 用户数据隔离
- [ ] 自选池自定义（/watchlist 命令）
- [ ] 模拟盘/实盘切换
- [ ] 支付宝/微信支付接入
- [ ] 订阅状态管理（免费/标准/专业）

## Phase 3：美股 + Sealos 部署
- [ ] 美股 ETF 行情接入（yfinance）
- [ ] 22:00 美股推送
- [ ] Sealos 部署（新加坡）
- [ ] Stripe 支付接入
- [ ] Webhook 替代轮询

## Phase 4：产品完善
- [ ] 历史回测功能
- [ ] 全市场扫描推送
- [ ] 推荐好友返佣
- [ ] 数据看板（Web）
