# Presenter runbook

About 6 minutes. Nothing in the demo calls the model. Each stage is a git tag,
and the two model-driven steps (elicitation and test propagation) are shown
from committed records. `allium plan`, which is deterministic, runs live.

Keep this file open on GitHub, not in the demo terminal. Checking out an
earlier tag removes it from the working tree.
[DEMO.md on GitHub](https://github.com/jimdowning/allium-demo/blob/claude/pensive-clarke-i2f00l/DEMO.md)

## Before the talk

```
git clone https://github.com/jimdowning/allium-demo && cd allium-demo
python3.12 -m venv .venv && .venv/bin/pip install -q pytest hypothesis
allium --version                  # the Allium CLI, for stage 2

# Shorthands for the session
export DEMO=claude/pensive-clarke-i2f00l
alias stage='git -c advice.detachedHead=false checkout -q'
alias t='.venv/bin/pytest --no-header -p no:cacheprovider --tb=no -rf'
```

`.venv` is not tracked by git, so it stays in place as you switch tags.

Rehearse once end to end, then `stage $DEMO` to reset. Terminal font large
enough for about 90 columns.

## Stage 0: the brief and the obvious code (1 min)

```
stage stage-0-brief
echo; echo "=== The brief: docs/brief.md ==="; echo
cat docs/brief.md
echo; echo "=== The naive allocate(): src/allocation.py ==="; echo
sed -n '9,27p' src/allocation.py
echo; echo "=== The example tests ==="; echo
t tests/test_examples.py
```

Show: the five-sentence brief, the largest-remainder function, then
`5 passed`.

Links: [brief](https://github.com/jimdowning/allium-demo/blob/stage-0-brief/docs/brief.md) ·
[naive `allocate`](https://github.com/jimdowning/allium-demo/blob/stage-0-brief/src/allocation.py#L9-L27) ·
[example tests](https://github.com/jimdowning/allium-demo/blob/stage-0-brief/tests/test_examples.py)

Say: "This is what you get from a good developer working straight from the
brief: sensible code, sensible tests, all green."

## Stage 1: elicitation (1 min)

```
stage stage-1-elicit
less docs/elicitation-transcript.md
```

Show question 2 (40 units in packs of 6: reject, round down or round up?),
question 7 (curve 1:3:3, where a bigger order takes a pack away), and the
table under question 8. Then show one invariant in the spec:

```
sed -n '194,201p' spec/size-allocation.allium
```

Links: [elicitation transcript](https://github.com/jimdowning/allium-demo/blob/stage-1-elicit/docs/elicitation-transcript.md) ·
[spec](https://github.com/jimdowning/allium-demo/blob/stage-1-elicit/spec/size-allocation.allium) ·
[invariant `WithinOnePackOfExactShare`](https://github.com/jimdowning/allium-demo/blob/stage-1-elicit/spec/size-allocation.allium#L194-L201)

Say: "Before looking at the code, the elicit skill went through the brief
against a checklist of decisions briefs usually leave out, and each answer
became a line in the spec."

## Stage 2: tests generated from the spec (2.5 min)

**Step 1: what the spec says must be tested (runs live, about 1 second).**

```
stage stage-2-propagate
allium plan spec/size-allocation.allium | jq -r '.obligations[].category' | sort | uniq -c
```

Show: 34 obligations. 7 of them are invariants, and each invariant becomes a
property-based test.

**Step 2: how the tests were written (the propagate skill; show the record).**

```
git show $DEMO:docs/propagate-transcript.md | less
```

Show: the invocation, the "implementation bridge" table (spec entities mapped
to the one Python function), and the obligation-to-test table ending in
"34 obligations, 33 covered, 1 uncovered".

**Step 3: one Hypothesis test, next to the spec line it came from.**

```
echo; echo "=== The invariant: spec/size-allocation.allium ==="; echo
sed -n '194,201p' spec/size-allocation.allium
echo; echo "=== The test generated from it: tests/test_spec_properties.py ==="; echo
sed -n '25,33p' tests/test_spec_properties.py
echo; echo "=== How Hypothesis makes inputs: tests/spec_support.py ==="; echo
sed -n '16,27p' tests/spec_support.py
echo; echo "=== The function under test, still naive: src/allocation.py ==="; echo
sed -n '9,27p' src/allocation.py
```

Point out that the test does not list any cases. `@given` asks Hypothesis for
random valid curves (1-6 sizes, ratios 0-6), pack sizes and order sizes, and
checks the invariant on each one. The function under test is still the naive
one from stage 0.

**Step 4: run them against the unchanged stage-0 code.**

```
echo; echo "=== All tests against the naive code ==="; echo
make -s stage-2 2>/dev/null
echo; echo "=== Hypothesis's shrunk counterexample ==="; echo
make -s stage-2-counterexample
```

Show: `8 failed, 17 passed`. Seven failures are inputs the spec rejects: a
part-pack order silently rounded down, and three `ZeroDivisionError`s. The
counterexample: curve 1:4:1 at 4 packs is an exact three-way tie. The spec
gives the pack to the earlier size, but the naive code's floating-point
remainders (`0.6666666666666665` against `0.6666666666666666`) let rounding
error decide.

Links: [propagation record](https://github.com/jimdowning/allium-demo/blob/claude/pensive-clarke-i2f00l/docs/propagate-transcript.md) ·
[`allium plan` output](https://github.com/jimdowning/allium-demo/blob/claude/pensive-clarke-i2f00l/docs/stage-2-plan.json) ·
[obligation list](https://github.com/jimdowning/allium-demo/blob/claude/pensive-clarke-i2f00l/docs/stage-2-obligations.txt) ·
[property tests](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/tests/test_spec_properties.py) ·
[`test_within_one_pack_of_exact_share`](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/tests/test_spec_properties.py#L25-L33) ·
[`test_larger_order_never_takes_packs_away`](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/tests/test_spec_properties.py#L45-L51) ·
[generators](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/tests/spec_support.py#L16-L27) ·
[unit tests](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/tests/test_spec_rules.py) ·
[captured failing run](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/docs/stage-2-failures.md)

Say: "Nobody wrote these test cases by hand. The tests came from the spec,
and Hypothesis found and shrank the smallest order that breaks the rule."

If asked about the Alabama paradox: that test
([`test_larger_order_never_takes_packs_away`](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/tests/test_spec_properties.py#L45-L51),
from [this invariant](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/spec/size-allocation.allium#L209-L222))
passed. The naive code can do it (1:3:3 at 3 packs, then 4), but random
testing didn't hit such a case. We reported that rather than tuning the test.

## Stage 3: code that meets the spec (1 min)

```
stage stage-3-fixed
echo; echo "=== Files changed from stage 2 to stage 3 ==="; echo
git diff --stat stage-2-propagate stage-3-fixed
echo; echo "=== The new allocate(): src/allocation.py ==="; echo
sed -n '26,34p' src/allocation.py
echo; echo "=== All tests against the fixed code ==="; echo
make -s stage-3
```

Show: only `src/allocation.py` changed, plus the record of the run. The new
`allocate` places packs one at a time. Then `25 passed`.

Links: [fixed `allocate`](https://github.com/jimdowning/allium-demo/blob/stage-3-fixed/src/allocation.py#L26-L34) ·
[rejection checks](https://github.com/jimdowning/allium-demo/blob/stage-3-fixed/src/allocation.py#L37-L51) ·
[which size gets the next pack](https://github.com/jimdowning/allium-demo/blob/stage-3-fixed/src/allocation.py#L54-L78) ·
[stage 2 to 3 diff](https://github.com/jimdowning/allium-demo/compare/stage-2-propagate...stage-3-fixed) ·
[captured passing run](https://github.com/jimdowning/allium-demo/blob/stage-3-fixed/docs/stage-3-pass.md)

Say: "The tests did not change. The code was rewritten until it met the
spec, and the spec, not the developer's judgement, decides when it is done."

## Close (30 s)

```
stage $DEMO
```

Say: "The brief was five sentences. The spec settles about a dozen decisions
the brief didn't cover, and each one is now a test."

Point to [README.md](https://github.com/jimdowning/allium-demo/blob/claude/pensive-clarke-i2f00l/README.md#three-things-to-try)
for the three follow-on exercises.

## Fallback: no live commands

If the terminal, Python or `allium` fails, present from the links only. The
sentences to say are the same.

| Stage | Open | Show |
|---|---|---|
| 0 | [brief](https://github.com/jimdowning/allium-demo/blob/stage-0-brief/docs/brief.md), [naive `allocate`](https://github.com/jimdowning/allium-demo/blob/stage-0-brief/src/allocation.py#L9-L27) | the brief and the naive function |
| 1 | [elicitation transcript](https://github.com/jimdowning/allium-demo/blob/stage-1-elicit/docs/elicitation-transcript.md), [spec](https://github.com/jimdowning/allium-demo/blob/stage-1-elicit/spec/size-allocation.allium#L194-L201) | questions 2, 7 and 8; one invariant |
| 2 | [obligation list](https://github.com/jimdowning/allium-demo/blob/claude/pensive-clarke-i2f00l/docs/stage-2-obligations.txt), [propagation record](https://github.com/jimdowning/allium-demo/blob/claude/pensive-clarke-i2f00l/docs/propagate-transcript.md), [test](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/tests/test_spec_properties.py#L25-L33), [failing run](https://github.com/jimdowning/allium-demo/blob/stage-2-propagate/docs/stage-2-failures.md) | 34 obligations; spec line next to its test; `8 failed` and the counterexample |
| 3 | [fixed `allocate`](https://github.com/jimdowning/allium-demo/blob/stage-3-fixed/src/allocation.py#L26-L34), [passing run](https://github.com/jimdowning/allium-demo/blob/stage-3-fixed/docs/stage-3-pass.md) | `25 passed` and the before/after table |
