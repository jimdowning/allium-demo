# Test targets for each stage. Output is kept short for a projector.
PY      := .venv/bin/python
PYTEST  := .venv/bin/pytest
SHORT   := --no-header -p no:cacheprovider --tb=no -rf

.PHONY: setup stage-0 stage-2 stage-2-counterexample stage-3 test spec-check clean

setup:            ## create .venv with pytest and Hypothesis
	python3.12 -m venv .venv
	$(PY) -m pip install -q -e '.[test]'

stage-0:          ## the hand-written example tests
	$(PYTEST) $(SHORT) tests/test_examples.py

stage-2:          ## all tests, one line per failure
	-$(PYTEST) $(SHORT) tests

stage-2-counterexample:  ## the shrunk counterexample from Hypothesis
	-$(PYTEST) --no-header -p no:cacheprovider --tb=short -rN \
	  tests/test_spec_properties.py::test_next_pack_goes_to_largest_eligible_shortfall \
	  2>&1 | sed -n '/AssertionError/p; /Failing test case/,/^E   )/p'

stage-3:          ## all tests, expected to pass
	$(PYTEST) $(SHORT) tests

test: stage-3

spec-check:       ## validate the Allium spec (needs the allium CLI)
	allium check spec/size-allocation.allium

clean:
	rm -rf .pytest_cache .hypothesis __pycache__ */__pycache__
