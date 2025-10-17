.PHONY: setup dev db db-acled db-cia db-wbi run api clean test reasoning reasoning-ui examples examples-list hawk stop

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

dev:
	. .venv/bin/activate && python main.py --dev

db:
	. .venv/bin/activate && python core/vector_store.py --rebuild

db-acled:
	. .venv/bin/activate && python core/vector_store.py --ingest-acled

db-cia:
	. .venv/bin/activate && python core/vector_store.py --ingest-cia-facts

db-wbi:
	. .venv/bin/activate && python core/vector_store.py --ingest-wbi

run:
	. .venv/bin/activate && python main.py

api:
	. .venv/bin/activate && python api_server.py --reload

api-prod:
	. .venv/bin/activate && python api_server.py --host 0.0.0.0 --port 8000

examples:
	. .venv/bin/activate && python examples_showcase.py

examples-list:
	. .venv/bin/activate && python examples_showcase.py --list

reasoning:
	. .venv/bin/activate && python tools/reasoning_viewer.py --mode cli

reasoning-ui:
	. .venv/bin/activate && python tools/reasoning_viewer.py --mode streamlit

clean:
	rm -rf .venv
	rm -rf data/vector_index/*
	rm -rf logs/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

test:
	. .venv/bin/activate && python -m pytest tests/ -v

hawk:
	./script/start_hawk.sh

stop:
	./script/stop_hawk.sh
