.PHONY: all fit physics mutant-physics leak-check schema

all: fit physics mutant-physics schema leak-check

fit:
	PYTHONPATH=src python3 src/generate_synthetic.py
	PYTHONPATH=src python3 src/fit.py

physics:
	PYTHONPATH=src python3 src/fit.py --check-physics

mutant-physics:
	@PYTHONPATH=src python3 src/fit.py --check-physics --vth 1.2; \
	if [ $$? -eq 0 ]; then echo "mutant should fail"; exit 1; fi; \
	echo "MUTANT PHYSICS: caught"

leak-check:
	python3 scripts/leak_check.py

schema:
	@printf 'x,y\n1,2\n' > /tmp/bad-iv.csv
	@if PYTHONPATH=src python3 src/fit.py --csv /tmp/bad-iv.csv >/tmp/bad-iv.out 2>&1; then \
	  echo "schema should fail"; exit 1; fi
	@echo "SCHEMA CHECK: PASS"
