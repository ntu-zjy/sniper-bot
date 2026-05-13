"""定时推送任务（14:40 A股 / 22:00 美股）"""
import datetime
import logging
import zoneinfo

from telegram.ext import Application

from src.user.models import UserStore
from src.user.portfolio import Portfolio
from src.market.a_share import fetch_prices
from src.strategy.grid import generate_signals, format_signals_text
from src.core import config

logger = logging.getLogger(__name__)

_store = UserStore()
_TZ_SHANGHAI = zoneinfo.ZoneInfo("Asia/Shanghai")


async def _push_signals_to_user(bot, user) -> None:
    symbols = [w.symbol for w in user.watchlist]
    if not symbols:
        return
    try:
        prices = fetch_prices(symbols)
    except Exception as e:
        logger.error("fetch_prices failed for user %s: %s", user.user_id, e)
        return

    portfolio = Portfolio(user.user_id, user.account_type)
    portfolio.update_prices({sym: d["current_price"] for sym, d in prices.items()})

    cfg = config.get()
    stop_loss = cfg["strategy"]["stop_loss"]
    signals = generate_signals(prices, portfolio, user.watchlist, stop_loss)
    text = format_signals_text(signals, user.account_type)

    try:
        await bot.send_message(chat_id=user.user_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logger.warning("send_message failed for user %s: %s", user.user_id, e)


async def job_a_share_push(context) -> None:
    """每个工作日 14:40 推送 A 股信号"""
    logger.info("A股定时推送开始")
    users = _store.all()
    for user in users:
        cfg = config.get()
        markets = cfg["plans"][user.plan]["markets"]
        if "A" not in markets:
            continue
        await _push_signals_to_user(context.bot, user)
    logger.info("A股定时推送完成，共 %d 位用户", len(users))


def register_jobs(app: Application) -> None:
    """在 Application 启动后注册定时任务"""
    jq = app.job_queue

    # 14:40 上海时间，工作日（1=Mon ... 5=Fri，ptb 的 days: 0=Sun）
    a_share_time = datetime.time(14, 40, tzinfo=_TZ_SHANGHAI)
    jq.run_daily(
        job_a_share_push,
        time=a_share_time,
        days=(1, 2, 3, 4, 5),
        name="a_share_daily",
    )
    logger.info("已注册 A股定时推送任务：工作日 14:40 上海时间")
