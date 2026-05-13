"""Telegram bot command handlers（python-telegram-bot v22）"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.core import config
from src.user.models import UserStore
from src.user.portfolio import Portfolio
from src.market.a_share import fetch_prices
from src.strategy.grid import generate_signals, format_signals_text

logger = logging.getLogger(__name__)

_store = UserStore()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    user, is_new = _store.get_or_create(
        user_id=tg_user.id,
        username=tg_user.username or "",
        first_name=tg_user.first_name or "",
    )
    if is_new:
        await update.message.reply_markdown_v2(
            f"你好 {tg_user.first_name}\\! 🎉\n\n"
            "我是 *SniperBot* — 每日 ETF 网格交易信号助手。\n\n"
            "已为你创建账户，默认模式：*模拟盘*，套餐：*免费版*。\n\n"
            "发送 /signals 手动获取今日信号\n"
            "发送 /status 查看持仓\n"
            "发送 /help 查看全部命令",
        )
    else:
        await update.message.reply_text(
            f"欢迎回来，{tg_user.first_name}！发送 /signals 获取今日信号。"
        )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📖 *命令列表*\n\n"
        "/start — 注册/欢迎\n"
        "/signals — 手动触发今日信号分析\n"
        "/status — 查看持仓与盈亏\n"
        "/mode — 切换模拟盘/实盘\n"
        "/watchlist — 查看自选池\n"
        "/subscribe — 查看订阅方案\n"
        "/help — 本帮助"
    )
    await update.message.reply_markdown(text)


async def cmd_signals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    user, _ = _store.get_or_create(tg_user.id, tg_user.username or "", tg_user.first_name or "")

    await update.message.reply_text("⏳ 正在拉取行情，请稍候...")

    symbols = [w.symbol for w in user.watchlist]
    if not symbols:
        await update.message.reply_text("你的自选池为空，请先用 /watchlist 添加标的。")
        return

    try:
        prices = fetch_prices(symbols)
    except Exception as e:
        logger.error("fetch_prices failed: %s", e)
        await update.message.reply_text("⚠️ 行情获取失败，请稍后重试。")
        return

    portfolio = Portfolio(user.user_id, user.account_type)
    portfolio.update_prices({sym: d["current_price"] for sym, d in prices.items()})

    cfg = config.get()
    stop_loss = cfg["strategy"]["stop_loss"]
    signals = generate_signals(prices, portfolio, user.watchlist, stop_loss)
    text = format_signals_text(signals, user.account_type)
    await update.message.reply_markdown(text)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    user, _ = _store.get_or_create(tg_user.id, tg_user.username or "", tg_user.first_name or "")

    portfolio = Portfolio(user.user_id, user.account_type)
    summary = portfolio.get_summary()
    mode = "模拟盘" if user.account_type == "simulation" else "实盘"

    if not summary["holdings"]:
        await update.message.reply_text(f"📭 {mode}暂无持仓。发送 /signals 查看今日信号。")
        return

    lines = [f"📦 *持仓状态（{mode}）*\n"]
    for h in summary["holdings"]:
        pnl_emoji = "🟢" if h["pnl_amount"] >= 0 else "🔴"
        lines.append(
            f"{pnl_emoji} *{h['name']}*（{h['symbol']}）\n"
            f"  持仓 {h['quantity']:.0f}股 | 成本 {h['avg_cost']:.3f} | 现价 {h['current_price']:.3f}\n"
            f"  市值 {h['market_value']:.2f} | 浮盈 {h['pnl_amount']:+.2f}（{h['pnl_pct']:+.2f}%）\n"
        )

    lines.append(
        f"─────────────────\n"
        f"总成本：{summary['total_cost']:.2f} 元\n"
        f"总市值：{summary['total_market_value']:.2f} 元\n"
        f"浮动盈亏：{summary['unrealized_pnl']:+.2f} 元\n"
        f"已实现盈亏：{summary['realized_pnl']:+.2f} 元\n"
        f"累计盈亏：{summary['total_pnl']:+.2f} 元"
    )
    await update.message.reply_markdown("\n".join(lines))


async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    user, _ = _store.get_or_create(tg_user.id, tg_user.username or "", tg_user.first_name or "")

    keyboard = [
        [
            InlineKeyboardButton("📊 模拟盘", callback_data="mode_simulation"),
            InlineKeyboardButton("💰 实盘", callback_data="mode_real"),
        ]
    ]
    current = "模拟盘" if user.account_type == "simulation" else "实盘"
    await update.message.reply_text(
        f"当前模式：{current}\n请选择切换目标：",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def callback_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tg_user = query.from_user
    user, _ = _store.get_or_create(tg_user.id, tg_user.username or "", tg_user.first_name or "")

    new_mode = "simulation" if query.data == "mode_simulation" else "real"
    user.account_type = new_mode
    _store.upsert(user)

    label = "模拟盘" if new_mode == "simulation" else "实盘"
    await query.edit_message_text(f"✅ 已切换到 *{label}*", parse_mode="Markdown")


async def cmd_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    user, _ = _store.get_or_create(tg_user.id, tg_user.username or "", tg_user.first_name or "")

    if not user.watchlist:
        await update.message.reply_text("自选池为空。")
        return

    lines = [f"📋 *自选池*（{len(user.watchlist)}/{user.watchlist_limit}）\n"]
    for w in user.watchlist:
        lines.append(
            f"• *{w.name}*（{w.symbol}）\n"
            f"  买入触发 {w.buy_trigger:+.1f}% | 卖出触发 {w.sell_trigger:+.1f}%\n"
            f"  单次投入 {w.unit_capital:.0f}元 | 上限 {w.max_holding:.0f}元"
        )
    await update.message.reply_markdown("\n".join(lines))


async def cmd_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    user, _ = _store.get_or_create(tg_user.id, tg_user.username or "", tg_user.first_name or "")
    cfg = config.get()
    plans = cfg["plans"]

    lines = ["💳 *订阅方案*\n"]
    plan_labels = {"free": "免费版", "pro": "标准版", "elite": "专业版"}
    for key, plan in plans.items():
        current = " ✅（当前）" if key == user.plan else ""
        price = "免费" if plan["price_cny"] == 0 else f"¥{plan['price_cny']}/月"
        markets = "、".join(plan["markets"])
        lines.append(
            f"*{plan_labels[key]}* — {price}{current}\n"
            f"  自选池上限：{plan['watchlist_limit']}只 | 市场：{markets}\n"
        )
    lines.append("_付费订阅功能即将上线，敬请期待。_")
    await update.message.reply_markdown("\n".join(lines))
