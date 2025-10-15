.PHONY: setup dev db run clean test reasoning reasoning-ui examples examples-list

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

dev:
	. .venv/bin/activate && python main.py --dev

db:
	. .venv/bin/activate && python core/vector_store.py --rebuild

run:
	. .venv/bin/activate && python main.py

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
