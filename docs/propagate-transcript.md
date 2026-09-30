# Propagation record (stage 2)

How the stage-2 tests were produced from `spec/size-allocation.allium`, so the
step can be shown without running the model.

This is a written record, not a verbatim log. The commands, the skill
invocation, the files produced and the test runs are as they happened. The
obligation-to-test table was written up afterwards, from the `allium plan`
output and the committed tests.

## 1. Test obligations: `allium plan` (deterministic, no model)

```
allium plan spec/size-allocation.allium
```

The Allium CLI reads the spec and lists every test the spec requires: 34
obligations. Full output: [`stage-2-plan.json`](stage-2-plan.json). One line
per obligation: [`stage-2-obligations.txt`](stage-2-obligations.txt).

A short summary, as shown in the demo:

```
allium plan spec/size-allocation.allium | jq -r '.obligations[] | .id'
```

| Kind | Count |
|---|---|
| invariants | 7 |
| rule success / failure / entity creation | 9 |
| entity fields and relationships | 7 |
| derived values | 7 |
| enum | 1 |
| surface (actor, exposure, provides) | 3 |

## 2. Writing the tests: the `allium:propagate` skill (model)

Invoked in Claude Code as:

```
Skill: allium:propagate
Args:  Generate Hypothesis property-based tests and pytest unit tests in tests/
       from spec/size-allocation.allium, targeting src/allocation.py
       (allocate(order_units, size_curve, pack_size) -> dict[str, int] of packs
       per size). Do not modify src/allocation.py.
```

The skill's process is: read the spec, read the obligations, explore the code,
map spec constructs to code (the "implementation bridge"), generate tests in
the project's conventions, run them, then check every obligation has a test.

### Discovery

| Question the skill asks | Answer in this repo |
|---|---|
| Test runner | pytest (`pyproject.toml`) |
| Property-based testing framework | Hypothesis (`pyproject.toml`) |
| Where tests live | `tests/` |
| Existing tests | `tests/test_examples.py`, 5 examples, kept as they are |
| How rules are invoked | one pure function, `allocate()` |
| Injectable clock needed? | no: the spec has no time-based rules |

### Implementation bridge

The spec describes entities and rules. The code is one function. The mapping
used by every generated test (also in the docstring of
[`tests/spec_support.py`](../tests/spec_support.py)):

| Spec | Code |
|---|---|
| `AllocationRequest(order_units, pack_size, curve)` | `allocate(order_units, size_curve, pack_size)` |
| `CurveSize(size, ratio, position)` | one entry of `size_curve`, in insertion order |
| `Allocation`, `AllocationLine(size, packs)` | the returned `{size: packs}` dict |
| `AllocationRejection(reason)` | a `ValueError` with a `.reason` attribute |

Rejections are checked as "raises `ValueError` with `.reason`" rather than by
importing an exception class that the stage-0 code does not have. So the
generated tests import cleanly and fail one by one, instead of all failing at
import.

### Files generated

- [`tests/test_spec_properties.py`](../tests/test_spec_properties.py): 7
  Hypothesis properties, one per invariant plus one for the `PlaceNextPack`
  rule. Each is labelled with the spec construct it covers.
- [`tests/test_spec_rules.py`](../tests/test_spec_rules.py): 13 unit tests,
  covering the rejection reasons, valid requests, tie-breaks and the result shape.
- [`tests/spec_support.py`](../tests/spec_support.py): Hypothesis generators
  for valid curves, pack sizes and totals, and the spec's `shortfall` and
  `keeps_shares_reachable` restated in Python.
- [`tests/conftest.py`](../tests/conftest.py): fixed Hypothesis seed, so every
  run shrinks to the same counterexample.

### Obligation to test

| Obligation(s) | Covered by |
|---|---|
| `invariant.AllocatedUnitsMatchOrder`, `derived.Allocation.allocated_units` | `test_allocated_units_match_order` |
| `invariant.OneLinePerCurveSize`, `entity-relationship.Allocation.lines`, `entity-relationship.AllocationRequest.curve`, `entity-fields.CurveSize` | `test_one_line_per_curve_size_in_curve_order` |
| `invariant.WithinOnePackOfExactShare`, `derived.AllocationLine.scaled_share`, `derived.AllocationLine.scaled_packs` | `test_within_one_pack_of_exact_share` |
| `invariant.ZeroRatioGetsNothing` | `test_zero_ratio_gets_nothing`, `test_zero_ratio_size_is_listed_with_zero_packs` |
| `invariant.LargerOrderNeverTakesPacksAway` | `test_larger_order_never_takes_packs_away` |
| `invariant.SameInputsSameAllocation` | `test_same_inputs_same_allocation` |
| `rule-success.PlaceNextPack`, `rule-failure.PlaceNextPack.2`, `rule-failure.PlaceNextPack.3`, `invariant.Allocation.PlacedPacksAreAllocated` | `test_next_pack_goes_to_largest_eligible_shortfall`, `test_equal_claims_go_to_the_size_earlier_in_the_curve` |
| `rule-failure.PlaceNextPack.1`, `derived.Allocation.is_complete` | `test_zero_unit_order_gives_zero_packs_everywhere`, `test_allocated_units_match_order` |
| `rule-success.RejectRequest`, `rule-entity-creation.RejectRequest.1`, `entity-fields.AllocationRejection`, `enum-comparable.RejectionReason`, `rule-failure.StartAllocation.1`, `derived.AllocationRequest.has_whole_packs` | the 6 `test_rejects_*` tests and `test_first_failing_check_is_the_reason_given` |
| `rule-success.StartAllocation`, `rule-failure.RejectRequest.1`, `derived.AllocationRequest.is_allocatable`, `entity-fields.AllocationRequest`, `entity-fields.Allocation`, `surface-provides.SizeAllocation` | `test_valid_request_is_allocated`, `test_small_order_leaves_some_sizes_without_a_pack` |
| `entity-fields.AllocationLine`, `derived.AllocationLine.units`, `surface-exposure.SizeAllocation` | `test_units_per_size_are_packs_times_pack_size`, `test_one_line_per_curve_size_in_curve_order` |
| `surface-actor.SizeAllocation` | **not covered**, see below |

**34 obligations, 33 covered, 1 uncovered.**

- `surface-actor.SizeAllocation` (unmappable construct): the spec says only
  the ordering system calls the allocation. The code is a plain function with
  no notion of who is calling, so there is nothing to test until the
  calculation sits behind a service.

## 3. Running the generated tests against the stage-0 code

```
pytest tests
```

8 failed, 17 passed. See [`stage-2-failures.md`](stage-2-failures.md).

## 4. Re-propagation after the spec changed

On the first run, the `PlaceNextPack` property failed on curve 2:1 with 2
packs, and the failure showed that the spec's first method was the problem, not
the code. The spec was revised (see question 8 in
[`elicitation-transcript.md`](elicitation-transcript.md)). The affected test
and its helpers were then generated again from the revised rule. Only
`test_next_pack_goes_to_largest_eligible_shortfall` and the helpers in
`spec_support.py` changed. The stage-2 commit contains the tests after this
second pass.
