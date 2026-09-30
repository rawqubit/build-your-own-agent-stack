.PHONY: install test test-01 test-02 test-03 test-04 test-05 test-06 test-capstone peek-check progress demo ci

install:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest

test-01:
	python3 -m pytest tests/test_01_tools.py

test-02:
	python3 -m pytest tests/test_02_sandbox.py

test-03:
	python3 -m pytest tests/test_03_permissions.py

test-04:
	python3 -m pytest tests/test_04_memory.py

test-05:
	python3 -m pytest tests/test_05_spend.py

test-06:
	python3 -m pytest tests/test_06_evals.py

test-capstone:
	python3 -m pytest tests/test_capstone.py

peek-check:
	AGENTSTACK_PEEK=1 PYTHONPATH=solutions:$$PYTHONPATH python3 -m pytest

progress:
	python3 scripts/progress.py

demo:
	python3 scripts/demo.py

ci:
	python3 scripts/expect_red.py
	AGENTSTACK_PEEK=1 python3 -m pytest
