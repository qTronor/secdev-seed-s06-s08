#!/usr/bin/env sh
set -euo pipefail

# Переносим ровно ваш one-liner S06:
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
mkdir -p EVIDENCE/S06
python -m pytest tests/ -v --junitxml=EVIDENCE/S06/test-report.xml
