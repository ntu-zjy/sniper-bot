"""
用户数据模型（Phase 1 用 JSON 文件持久化，Phase 2 迁移到 PostgreSQL）
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
import time

from src.core import config


@dataclass
class WatchItem:
    symbol: str
    name: str
    buy_trigger: float
    sell_trigger: float
    unit_capital: float
    max_holding: float


@dataclass
class User:
    user_id: int
    username: str
    first_name: str
    plan: str = "free"
    account_type: str = "simulation"   # simulation | real
    watchlist: list[WatchItem] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    subscription_expires: Optional[float] = None

    @property
    def watchlist_limit(self) -> int:
        cfg = config.get()
        return cfg["plans"][self.plan]["watchlist_limit"]

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "User":
        watchlist = [WatchItem(**w) for w in d.pop("watchlist", [])]
        return cls(watchlist=watchlist, **d)


class UserStore:
    def __init__(self):
        self._path = config.get_data_dir() / "users.json"
        self._data: dict[int, User] = {}
        self._load()

    def _load(self):
        if self._path.exists():
            raw = json.loads(self._path.read_text())
            self._data = {int(k): User.from_dict(v) for k, v in raw.items()}

    def _save(self):
        raw = {str(k): v.to_dict() for k, v in self._data.items()}
        self._path.write_text(json.dumps(raw, ensure_ascii=False, indent=2))

    def get(self, user_id: int) -> Optional[User]:
        return self._data.get(user_id)

    def upsert(self, user: User) -> User:
        self._data[user.user_id] = user
        self._save()
        return user

    def get_or_create(self, user_id: int, username: str, first_name: str) -> tuple[User, bool]:
        if user_id in self._data:
            return self._data[user_id], False
        cfg = config.get()
        default_watchlist = [WatchItem(**w) for w in cfg["market"]["default_watchlist"]]
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            watchlist=default_watchlist,
        )
        self.upsert(user)
        return user, True

    def all(self) -> list[User]:
        return list(self._data.values())
