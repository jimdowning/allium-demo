# Stage 2: generated tests against the naive implementation

The tests in `tests/test_spec_properties.py` and `tests/test_spec_rules.py`
were generated with the `allium:propagate` skill from
`spec/size-allocation.allium` (`allium plan` lists 34 obligations).
`src/allocation.py` is unchanged from stage 0.

Hypothesis runs with a fixed seed (`tests/conftest.py`), so the same run and
the same shrunk counterexample come out every time.

## Run: `make stage-2`

```
...........FFFFFFFF......                                                [100%]
=========================== short test summary info ============================
FAILED tests/test_spec_properties.py::test_next_pack_goes_to_largest_eligible_shortfall
FAILED tests/test_spec_rules.py::test_rejects_order_that_is_not_whole_packs
FAILED tests/test_spec_rules.py::test_rejects_pack_size_below_one - ZeroDivis...
FAILED tests/test_spec_rules.py::test_rejects_negative_order - Failed: DID NO...
FAILED tests/test_spec_rules.py::test_rejects_empty_curve - Failed: DID NOT R...
FAILED tests/test_spec_rules.py::test_rejects_negative_ratio - ZeroDivisionEr...
FAILED tests/test_spec_rules.py::test_rejects_curve_with_no_positive_ratio - ...
FAILED tests/test_spec_rules.py::test_first_failing_check_is_the_reason_given
8 failed, 17 passed
```

The 5 stage-0 example tests still pass.

## What failed and why

**Input the spec rejects (7 tests).** The naive code has no validation.
- 40 units in packs of 6 is silently rounded down to 36. The spec rejects it
  (`part_pack_order`), because allocated units must equal the order.
- A negative order and an empty curve are accepted.
- Pack size 0, a negative ratio and an all-zero curve crash with
  `ZeroDivisionError` instead of being rejected with a reason.

**Which size gets the next pack (1 property).** Hypothesis's shrunk minimal
counterexample, from `make stage-2-counterexample`:

```
E   AssertionError: assert {'XS': 1, 'S': 2, 'M': 1} == {'XS': 1, 'S': 3, 'M': 0}
E     
E     Omitting 1 identical items, use -vv to show
E     Differing items:
E     {'S': 2} != {'S': 3}
E     {'M': 1} != {'M': 0}
E     Use -v to get more diff
E   Failing test case: test_next_pack_goes_to_largest_eligible_shortfall(
E       curve={'XS': 1, 'S': 4, 'M': 1},
E       pack_size=1,  # or any other generated value
E       packs=4,
E   )
```

Curve XS:1, S:4, M:1 going from 3 packs to 4. At 4 packs the exact shares are
0.67, 2.67 and 0.67, and all three sizes are exactly 2/3 of a pack short, a
true tie. The spec gives the pack to the earlier size in the curve, S. The
naive code works in floating point: S's remainder comes out as
`0.6666666666666665` and M's as `0.6666666666666666`, so M wins by rounding
error. The answer to an exact tie depends on how the computer rounds, not on
any rule a buyer could look up.

## What did not fail

**Monotonicity (`test_larger_order_never_takes_packs_away`) passed.** The
naive largest-remainder method *can* take a pack away when the order grows. For
curve 1:3:3 with pack size 1, 3 packs gives 1/1/1 and 4 packs gives 0/2/2
(checked by hand). Hypothesis did not find a case like this in its 300
generated examples (up to 6 sizes, ratios 0-6, up to 60 packs). The test was
left as generated and not tuned to force a failure.

The pack-by-pack property also covers monotonicity: it requires each extra
pack to add exactly one pack to one size, so any case where a size loses a pack
fails it too. In this run it failed on the tie first.

The within-one-pack, zero-ratio, curve-order and determinism properties all
pass against the naive code. Largest remainder does satisfy those.
