# Test targets for each stage. Each stage runs from its own git worktree in
# .stages/, so nothing is checked out or switched during the demo.
# Output is kept short for a projector.

PY      := $(CURDIR)/.venv/bin/python
PYTEST  := $(CURDIR)/.venv/bin/pytest
SHORT   := --no-header -p no:cacheprovider --tb=no -rf
STAGES  := stage-0-brief stage-1-elicit stage-2-propagate stage-3-fixed

.PHONY: setup stages stage-0 stage-2 stage-2-counterexample stage-3 test spec-check clean

setup:            ## create .venv with pytest and Hypothesis, and the stage worktrees
	python3.12 -m venv .venv
	$(PY) -m pip install -q 'pytest>=8' 'hypothesis>=6.100'
	$(MAKE) stages

stages:           ## one worktree per stage tag in .stages/
	@git tag -l 'stage-*' | grep -q . || ./scripts/tag-stages.sh
	@for t in $(STAGES); do \
	  [ -d .stages/$$t ] || git worktree add -q --detach .stages/$$t $$t; \
	done
	@ls .stages

stage-0:          ## stage 0: the hand-written example tests pass
	cd .stages/stage-0-brief && $(PYTEST) $(SHORT) tests/test_examples.py

stage-2:          ## stage 2: generated tests against the naive code, one line per failure
	-cd .stages/stage-2-propagate && $(PYTEST) $(SHORT) tests

stage-2-counterexample:  ## stage 2: Hypothesis's shrunk counterexample
	-@cd .stages/stage-2-propagate && $(PYTEST) --no-header -p no:cacheprovider --tb=short -rN \
	  tests/test_spec_properties.py::test_next_pack_goes_to_largest_eligible_shortfall \
	  2>&1 | sed -n '/AssertionError/p; /Failing test case/,/^E   )/p'

stage-3:          ## stage 3: fixed code, all tests pass
	cd .stages/stage-3-fixed && $(PYTEST) $(SHORT) tests

test:             ## the current checkout's tests
	$(PYTEST) $(SHORT) tests

spec-check:       ## validate the Allium spec (needs the allium CLI)
	allium check spec/size-allocation.allium

clean:
	-for t in $(STAGES); do git worktree remove --force .stages/$$t 2>/dev/null; done
	rm -rf .stages .pytest_cache .hypothesis
