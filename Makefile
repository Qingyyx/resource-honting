.PHONY: check list eval-offline eval-selftest eval-route eval-smoke eval-core eval-deep eval-case eval-baseline

ID ?=

check:
	python3 scripts/check.py

list:
	python3 scripts/check.py --list

eval-offline:
	python3 tests/eval/run.py offline

eval-selftest:
	python3 tests/eval/run.py selftest

eval-route:
	python3 tests/eval/run.py route

eval-smoke:
	python3 tests/eval/run.py smoke

eval-core:
	python3 tests/eval/run.py core --repeat

eval-deep:
	python3 tests/eval/run.py deep --repeat

eval-case:
	python3 tests/eval/run.py case --id "$(ID)"

eval-baseline:
	python3 tests/eval/run.py baseline
