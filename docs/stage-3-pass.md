# Stage 3: fixed implementation passes

`src/allocation.py` was rewritten to follow the spec: requests are checked in
the spec's order and rejected with an `AllocationRejected` (a `ValueError`)
carrying the reason. Packs are placed one at a time using Still's quota method
with a largest-shortfall priority, in whole-number arithmetic. No test was
changed between stage 2 and stage 3.

## Run: `make stage-3`

```
.........................                                                [100%]
25 passed
```

## The stage-2 cases, now

| Input | Naive (stage 0) | Fixed (stage 3) |
|---|---|---|
| 40 units, packs of 6 | 6 packs, 4 units dropped | rejected: `part_pack_order` |
| pack size 0 | `ZeroDivisionError` | rejected: `invalid_pack_size` |
| curve S:0, M:0 | `ZeroDivisionError` | rejected: `no_positive_ratio` |
| curve XS:1, S:4, M:1, 4 packs | XS 1, S 2, M 1 (tie decided by rounding error) | XS 1, S 3, M 0 (tie goes to the earlier size, S) |
| curve 1:3:3, 3 packs then 4 | 1/1/1 then 0/2/2 (first size loses a pack) | 1/1/1 then 1/2/1 |

## Note on the pack-by-pack property

`test_next_pack_goes_to_largest_eligible_shortfall` checks the rule
`PlaceNextPack` step by step, so its helper in `tests/spec_support.py` restates
the rule, and it is close to the implementation. The other properties (units
match the order, within one pack, never loses a pack, zero ratio gets nothing,
curve order, determinism) are checked independently of how the allocation is
computed.
