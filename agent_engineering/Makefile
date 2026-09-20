.PHONY: install init-db run run-mysql test eval reset

PYTHON ?= .venv/bin/python
UVICORN ?= .venv/bin/uvicorn
PYTEST ?= .venv/bin/pytest

install:
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e '.[dev]'

init-db:
	$(PYTHON) -m db.init_db

run:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

run-mysql:
	DATABASE_URL='mysql+pymysql://agent:agent@127.0.0.1:3307/agent_interview' $(UVICORN) app.main:app --host 0.0.0.0 --port 8000

test:
	$(PYTEST)

eval:
	@test -f eval/runner.py || (echo '请先按 eval/README.md 实现自己的评测框架'; exit 2)
	$(PYTHON) -m eval.runner

reset:
	$(PYTHON) -m mock_boh_cli.boh reset
