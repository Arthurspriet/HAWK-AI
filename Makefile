.PHONY: setup dev db run clean test

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

dev:
	. .venv/bin/activate && python main.py --dev

db:
	. .venv/bin/activate && python core/vector_store.py --rebuild

run:
	. .venv/bin/activate && python main.py

clean:
	rm -rf .venv
	rm -rf data/vector_index/*
	rm -rf logs/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

test:
	. .venv/bin/activate && python -m pytest tests/ -v
