#!/bin/bash
set -e

HERMES_ENV="$HERMES_HOME/.env"
mkdir -p "$HERMES_HOME"

# 从环境变量写入 .env（幂等：每次启动覆盖）
cat > "$HERMES_ENV" << EOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
GATEWAY_ALLOW_ALL_USERS=${GATEWAY_ALLOW_ALL_USERS:-true}
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
TERMINAL_TIMEOUT=60
EOF

# 写入 config.yaml（每次启动重新生成，确保模型配置最新）
cat > "$HERMES_HOME/config.yaml" << YAML
model:
  default: ${HERMES_MODEL:-anthropic/claude-opus-4-5}
  provider: openrouter
agent:
  max_turns: 90
telegram:
  reactions: false
  allowed_chats: ""
group_sessions_per_user: true
skills:
  external_dirs: []
YAML

echo "Starting hermes gateway (model: ${HERMES_MODEL:-anthropic/claude-opus-4-5})..."
exec hermes gateway run
