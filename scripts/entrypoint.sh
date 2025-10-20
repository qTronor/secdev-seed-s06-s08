# scripts/entrypoint.sh
#!/usr/bin/env sh
set -euo pipefail
umask 027

: "${DB_PATH:=/data/app.db}"
: "${EVIDENCE_DIR:=/evidence/S06}"

# каталоги могут быть на volume — создаём (если есть права)
mkdir -p "$(dirname "$DB_PATH")" || true
mkdir -p "$EVIDENCE_DIR" || true

MODE="${MODE:-web}"

if [ "$MODE" = "tests" ]; then
  # ничего не запускаем: tests сервис сам передаёт команду
  exec sh -lc 'echo "MODE=tests"'
else
  [ -f scripts/init_db.py ] && python scripts/init_db.py || true
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
