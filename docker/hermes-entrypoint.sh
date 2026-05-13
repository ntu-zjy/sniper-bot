#!/bin/bash
set -e

HERMES_ENV="$HERMES_HOME/.env"
mkdir -p "$HERMES_HOME"

# 从环境变量写入 .env（幂等：每次启动覆盖）
cat > "$HERMES_ENV" << EOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
GATEWAY_ALLOW_ALL_USERS=${GATEWAY_ALLOW_ALL_USERS:-true}
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
KIMI_API_KEY=${KIMI_API_KEY}
KIMI_BASE_URL=${KIMI_BASE_URL}
TERMINAL_TIMEOUT=60
EOF

# 写入 config.yaml（使用 kimi 模型，与本地一致）
if [ ! -f "$HERMES_HOME/config.yaml" ]; then
  cat > "$HERMES_HOME/config.yaml" << 'YAML'
model:
  default: kimi-k2.6
  provider: custom
  base_url: ""
  api_key: ""
agent:
  max_turns: 90
telegram:
  reactions: false
  allowed_chats: ""
group_sessions_per_user: true
skills:
  external_dirs: []
YAML
fi

# 用 kimi 自定义 provider 覆盖（从环境变量注入 key）
if [ -n "$KIMI_API_KEY" ]; then
  python3 -c "
import yaml, os
path = os.environ['HERMES_HOME'] + '/config.yaml'
with open(path) as f:
    cfg = yaml.safe_load(f)
cfg.setdefault('model', {})['base_url'] = os.environ.get('KIMI_BASE_URL', 'https://aigc.sankuai.com/v1/openai/native')
cfg.setdefault('model', {})['api_key'] = os.environ['KIMI_API_KEY']
cfg['custom_providers'] = [{
    'name': 'kimi-k2.6',
    'base_url': os.environ.get('KIMI_BASE_URL', 'https://aigc.sankuai.com/v1/openai/native'),
    'api_key': os.environ['KIMI_API_KEY'],
    'model': 'kimi-k2.6',
}]
with open(path, 'w') as f:
    yaml.dump(cfg, f, allow_unicode=True)
print('config.yaml updated with kimi provider')
"
fi

echo "Starting hermes gateway..."
exec hermes gateway run
