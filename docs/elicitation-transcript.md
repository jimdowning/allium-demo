# Elicitation transcript

Session run with the `allium:elicit` skill (JUXT Allium plugin 3.16.0) against
`docs/brief.md`. Output: `spec/size-allocation.allium`, checked with
`allium check` and `allium analyse` (CLI 3.6.1), no errors.

The stakeholder answered question 1. At question 2 they said: "Take whatever
decisions seem most sensible - this is for a demo, it's not a real system.
Keep a log of these options and your decisions." From question 2 onwards each
entry therefore lists the options put forward and the decision Claude made,
marked **Decided by Claude**.

---

## 1. Scope

**Q.** What is the boundary of this spec? Everything outside it is treated as
supplied by another system.

- Calculation only: order quantity, size curve and pack size in; packs per size out.
- Calculation plus the order's life: placing, amending, cancelling, re-allocating.
- Calculation plus master data: who maintains curves and pack sizes.

**A (stakeholder).** Calculation only.

---

## 2. Orders that are not a whole number of packs

**Q.** What should happen when the ordered units are not a whole number of
packs, for example 40 units in packs of 6?

- Reject the order with a reason.
- Round down to 6 packs (36 units) and drop 4 units.
- Round up to 7 packs (42 units) and ship 2 extra.
- Round to the nearest whole number of packs.

**A (stakeholder).** "Take whatever decisions seem most sensible ... Keep a log
of these options and your decisions."

**Decided by Claude: reject**, with reason `part_pack_order`. Rounding either
way means the buyer gets a different quantity from the one ordered, and the
brief gives no basis for choosing which way. Rejecting makes the ordering
system decide, where the buyer can see it.

---

## 3. Must allocated units add up to the order exactly?

Options: exactly equal; may fall short; may exceed.

**Decided by Claude: exactly equal.** This follows from decision 2: once
part-pack orders are rejected, every accepted order is a whole number of packs,
and all of those packs are allocated. Invariant `AllocatedUnitsMatchOrder`.

---

## 4. Sizes whose claims are exactly equal

**Q.** When two sizes have an equal claim to the next pack, which gets it?

- The size listed earlier in the curve.
- The size listed later (larger sizes, if the curve runs small to large).
- The size with the larger ratio.
- Leave it unspecified.

**Decided by Claude: the size listed earlier in the curve.** Leaving it
unspecified means two correct implementations can give different answers for
the same order, which makes results hard to check. Curve order is something the
buyer can see and control. The naive version breaks ties by comparing
floating-point remainders, so ties that are exact on paper can go either way
depending on rounding error.

---

## 5. Sizes with ratio 0

Options: reject the curve; allow them and give them 0 packs; drop them from the result.

**Decided by Claude: allow them, give them 0 packs, and still list them in the
result.** A zero ratio is a normal way to switch a size off for one style
without editing the size range. Listing them keeps the result's shape the same
for every style. Invariants `ZeroRatioGetsNothing` and `OneLinePerCurveSize`.

A curve with no positive ratio at all is rejected (`no_positive_ratio`), as is
an empty curve, a negative ratio, a size listed twice, a pack size below 1, and
a negative order. A zero-unit order is accepted and gives 0 packs everywhere.

---

## 6. Orders too small to give every size a pack

Options: reject; allocate anyway and let some sizes get 0; enforce a minimum
of one pack per size.

**Decided by Claude: allocate anyway.** Some sizes get 0 packs. The brief sets
no minimum. A minimum-packs-per-size rule is left as one of the exercises in the
README.

---

## 7. Can a size ever get fewer packs when the order grows?

This question and the next were raised by Claude, not by the skill's standard
prompts. The skill's completeness gate asks about the core method, and these two
properties are what separate the candidate methods.

**Plain-English trade-off.** Suppose a curve of 1:3:3 and 3 packs. The naive
largest-remainder method gives 1/1/1. Add one pack, making 4, and it gives
0/2/2: the first size *loses* a pack even though the order got bigger. This is
the "Alabama paradox", named after a US census apportionment where Alabama
would have lost a seat if the House had grown. For a buyer it looks like an
error: they order more, and one size goes down.

Options:

- Accept it: keep largest remainder, which is simple and familiar.
- Require monotonicity: a larger order never takes a pack away from any size.

**Decided by Claude: require monotonicity.** Invariant
`LargerOrderNeverTakesPacksAway`.

---

## 8. Must every size stay within one pack of its exact share?

**Plain-English trade-off.** A size's exact share is `packs × ratio ÷ total
ratio`. It is usually not a whole number, so the size gets it rounded down or up.
"Within one pack" (the quota rule) says it may never be further away than that.
Several well-known methods that fix the Alabama paradox, such as the divisor
methods (D'Hondt, Webster), can break this rule on some curves. They can give a
large size two or more packs above its exact share. So the usual choice is
between two failure modes: sizes that go *down* as the order grows, or sizes
that sit more than a pack away from their share.

Options:

- Keep the quota rule and give up monotonicity (largest remainder).
- Keep monotonicity and give up the quota rule (a divisor method).
- Keep both.

**Decided by Claude: keep both.** The general impossibility result (Balinski
and Young) concerns ratios that change between runs. Here the curve is fixed
and only the order size changes, and in that setting both properties can be
had at once, by placing packs one at a time: each larger order only adds packs
to the smaller one's result, so no size can lose one.

**Revised after stage 2.** The first version of the spec used Balinski and
Young's quota method, which gives each pack to the size with the largest
`ratio ÷ (packs so far + 1)`. When the generated tests ran at stage 2,
Hypothesis shrank a failure to curve 2:1 with 2 packs. The naive code gave 1/1,
but that method gave 2/0. Both are within one pack of the exact shares (1.33
and 0.67), but 1/1 is plainly closer. The method favours large sizes.

Claude then checked three alternatives by brute force over every curve with
up to 4 or 5 sizes, ratios 0-6 or 0-7, and up to 40-50 packs:

| Method | Within one pack | Never loses a pack | 2:1 at 2 packs |
|---|---|---|---|
| Quota method, `ratio ÷ (packs + 1)` (first version) | always (proven) | always | 2/0 |
| Quota method, `ratio ÷ (packs + ½)` (Webster) | fails, e.g. 1:1:1:3 at 4 packs | always | 1/1 |
| Next pack to the largest shortfall | fails in 5 of 1.87M cases, e.g. 1:1:1:6:6 at 10 packs | always | 1/1 |
| Largest shortfall plus Still's eligibility check | always (proven; 0 failures in 784,080 cases) | always | 1/1 |

The spec now uses the last one. Pack number *n* goes to the size furthest
below its exact share of *n* packs, among sizes that are eligible. A size is
eligible if taking the pack keeps it no more than its share rounded up, and
still lets every size reach its share rounded down at every later total.
Rule `PlaceNextPack`, invariants `WithinOnePackOfExactShare` and
`LargerOrderNeverTakesPacksAway`.

The cost: the eligibility check is harder to explain than largest remainder,
and for some orders the answer differs from largest remainder's. On the five
hand-picked examples in `tests/test_examples.py` both methods agree.

---

## 9. What does "as closely as possible" mean?

**Decided by Claude:** it means decisions 3, 7 and 8 together, plus the method
in decision 8 to choose among allocations that meet them. The brief's phrase is
not a measurable rule on its own, so the spec replaces it with these.

---

## 10. Arithmetic and precision

Options: floating point; exact whole-number arithmetic.

**Decided by Claude: exact.** The spec compares every share scaled by the
total ratio (`shortfall`, `scaled_share`), so only whole numbers are compared
and no rounding error can creep in. Floating-point shares are what make the naive
version's tie-breaking unreliable.

---

## 11. Result shape

**Decided by Claude:** one line per size in the curve, in curve order, each
with size, packs and units (packs × pack size), plus the total packs and total
units. A rejected request returns no allocation, and the caller is told the
first failing reason from `RejectionReason`, in the order listed in the spec.

---

## 12. The rest of the order's life

Amendment, cancellation, re-allocation and partial shipment were put out of
scope in question 1. The calculation is pure: the same inputs always give the
same result (invariant `SameInputsSameAllocation`). Re-allocating after an
amendment is a new call.

---

## Open questions

None recorded. Every decision class in the skill's completeness gate was either
answered by the stakeholder or decided by Claude under their instruction above.
