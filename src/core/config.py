import json
import os
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
_CONFIG_PATH = _ROOT / "config" / "config.json"

_cfg: dict = {}


def load() -> dict:
    global _cfg
    with open(_CONFIG_PATH) as f:
        _cfg = json.load(f)

    # 环境变量优先覆盖（方便 Docker/Sealos 部署时注入密钥）
    if token := os.environ.get("TELEGRAM_BOT_TOKEN"):
        _cfg.setdefault("telegram", {})["bot_token"] = token
    if data_dir := os.environ.get("DATA_DIR"):
        _cfg["data_dir"] = data_dir

    return _cfg


def get() -> dict:
    if not _cfg:
        load()
    return _cfg


def get_data_dir() -> Path:
    cfg = get()
    raw = cfg.get("data_dir", "data")
    # 支持绝对路径（容器内挂载点）和相对路径
    d = Path(raw) if Path(raw).is_absolute() else _ROOT / raw
    d.mkdir(parents=True, exist_ok=True)
    return d
