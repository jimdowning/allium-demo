"""Property-based tests for the invariants and rules in spec/size-allocation.allium."""

from hypothesis import given
from hypothesis import strategies as st

from allocation import allocate
from spec_support import next_pack_goes_to, pack_sizes, size_curves, total_packs


# invariant AllocatedUnitsMatchOrder
@given(curve=size_curves(), pack_size=pack_sizes, packs=total_packs)
def test_allocated_units_match_order(curve, pack_size, packs):
    order_units = packs * pack_size
    result = allocate(order_units, curve, pack_size)
    assert sum(result.values()) * pack_size == order_units


# invariant OneLinePerCurveSize, surface guarantee ResultInCurveOrder
@given(curve=size_curves(), pack_size=pack_sizes, packs=total_packs)
def test_one_line_per_curve_size_in_curve_order(curve, pack_size, packs):
    result = allocate(packs * pack_size, curve, pack_size)
    assert list(result) == list(curve)


# invariant WithinOnePackOfExactShare
@given(curve=size_curves(), pack_size=pack_sizes, packs=total_packs)
def test_within_one_pack_of_exact_share(curve, pack_size, packs):
    result = allocate(packs * pack_size, curve, pack_size)
    total_ratio = sum(curve.values())
    for size, ratio in curve.items():
        scaled_share = packs * ratio
        scaled_packs = result[size] * total_ratio
        assert abs(scaled_packs - scaled_share) < total_ratio, size


# invariant ZeroRatioGetsNothing
@given(curve=size_curves(), pack_size=pack_sizes, packs=total_packs)
def test_zero_ratio_gets_nothing(curve, pack_size, packs):
    result = allocate(packs * pack_size, curve, pack_size)
    for size, ratio in curve.items():
        if ratio == 0:
            assert result[size] == 0, size


# invariant LargerOrderNeverTakesPacksAway
@given(curve=size_curves(), pack_size=pack_sizes, packs=total_packs, extra=st.integers(1, 10))
def test_larger_order_never_takes_packs_away(curve, pack_size, packs, extra):
    smaller = allocate(packs * pack_size, curve, pack_size)
    larger = allocate((packs + extra) * pack_size, curve, pack_size)
    for size in curve:
        assert larger[size] >= smaller[size], size


# invariant SameInputsSameAllocation
@given(curve=size_curves(), pack_size=pack_sizes, packs=total_packs)
def test_same_inputs_same_allocation(curve, pack_size, packs):
    assert allocate(packs * pack_size, curve, pack_size) == allocate(packs * pack_size, dict(curve), pack_size)


# rule PlaceNextPack: going from n-1 to n packs adds exactly one pack, to the
# eligible size furthest below its exact share (ties to the earlier size).
@given(curve=size_curves(), pack_size=pack_sizes, packs=st.integers(1, 60))
def test_next_pack_goes_to_largest_eligible_shortfall(curve, pack_size, packs):
    before = allocate((packs - 1) * pack_size, curve, pack_size)
    after = allocate(packs * pack_size, curve, pack_size)
    expected = dict(before)
    expected[next_pack_goes_to(curve, before, packs)] += 1
    assert after == expected
