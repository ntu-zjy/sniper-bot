"""SniperBot 入口"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
)

from src.core import config
from src.bot.handlers import (
    cmd_start,
    cmd_help,
    cmd_signals,
    cmd_status,
    cmd_mode,
    cmd_watchlist,
    cmd_subscribe,
    callback_mode,
)
from src.scheduler.daily import register_jobs

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    cfg = config.load()
    token = cfg["telegram"]["bot_token"]

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("help",      cmd_help))
    app.add_handler(CommandHandler("signals",   cmd_signals))
    app.add_handler(CommandHandler("status",    cmd_status))
    app.add_handler(CommandHandler("mode",      cmd_mode))
    app.add_handler(CommandHandler("watchlist", cmd_watchlist))
    app.add_handler(CommandHandler("subscribe", cmd_subscribe))
    app.add_handler(CallbackQueryHandler(callback_mode, pattern="^mode_"))

    register_jobs(app)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
