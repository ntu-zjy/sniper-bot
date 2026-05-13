# Sealos 部署指南（新加坡区）

## 一、推送镜像到 Docker Hub

### 方式 A：GitHub Actions 自动构建（推荐）

每次 push 到 `main` 分支自动构建并推送镜像，无需本地 Docker。

**前置步骤：**
1. 在 [hub.docker.com](https://hub.docker.com) 注册账号
2. 在 Docker Hub → Account Settings → Security → 创建 **Access Token**
3. 在 GitHub 仓库 → Settings → Secrets and variables → Actions → 添加两个 Secret：

| Secret 名称 | 值 |
|-------------|-----|
| `DOCKERHUB_USERNAME` | 你的 Docker Hub 用户名 |
| `DOCKERHUB_TOKEN` | 刚创建的 Access Token |

4. 推送代码到 main 分支，Actions 自动运行，约 2 分钟完成

### 方式 B：本地手动构建

```bash
cd sniper-bot
docker build -t your-dockerhub-username/sniper-bot:latest .
docker push your-dockerhub-username/sniper-bot:latest
```

> 需要本地安装 Docker Desktop。

---

## 二、在 Sealos AppLaunchpad 创建应用

1. 打开 [Sealos 控制台](https://cloud.sealos.run) → 选择**新加坡**区域
2. 点击 **AppLaunchpad** → **新建应用**
3. 填写配置：

| 字段 | 值 |
|------|----|
| 应用名称 | `sniper-bot` |
| 镜像 | `your-dockerhub-username/sniper-bot:latest` |
| CPU | 0.1 核（初期够用） |
| 内存 | 256 MB |
| 实例数 | 1 |

4. **环境变量**（点击"高级配置"→"环境变量"）：

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | `8665794950:AAFwvA3gG5qv10gfn2iKP7IPipPY04L3uEU` |
| `DATA_DIR` | `/app/data` |

5. **持久化存储**（点击"存储"→"新建存储"）：

| 挂载路径 | 容量 |
|----------|------|
| `/app/data` | 1 GB |

> `/app/data` 存放 `users.json` 和每用户持仓数据，重启不丢失。

6. **无需开放端口**（polling 模式不需要对外暴露 HTTP）

7. 点击**部署**

---

## 三、验证部署

在 Sealos 控制台查看日志，应看到类似：

```
INFO  telegram.ext.Application: Application started
INFO  src.scheduler.daily: 已注册 A股定时推送任务：工作日 14:40 上海时间
```

然后在 Telegram 找到你的机器人，发送 `/start` 测试。

---

## 四、更新部署

```bash
docker build -t your-dockerhub-username/sniper-bot:latest .
docker push your-dockerhub-username/sniper-bot:latest
```

在 Sealos 控制台点击**重新部署**（或修改镜像 tag 触发滚动更新）。

---

## 五、本地测试（无需网络）

```bash
# 使用 mock 数据测试核心逻辑
SNIPER_MOCK=1 python -c "
from src.core import config
from src.user.models import UserStore
from src.market.a_share import fetch_prices
from src.strategy.grid import generate_signals, format_signals_text
from src.user.portfolio import Portfolio

config.load()
store = UserStore()
user, _ = store.get_or_create(12345, 'test', 'Test')
prices = fetch_prices([w.symbol for w in user.watchlist])
port = Portfolio(user.user_id, user.account_type)
signals = generate_signals(prices, port, user.watchlist)
print(format_signals_text(signals, user.account_type))
"
```

---

## 六、后续 Phase 2（多用户 + 订阅）

Phase 1 使用 JSON 文件存储，单机可支撑约 1000 用户。
Phase 2 迁移 PostgreSQL 时，在 Sealos 同一命名空间创建 **Database** 应用即可，
连接串通过环境变量 `DATABASE_URL` 注入。
