"""Unit tests for the rules, derived values and surface in spec/size-allocation.allium."""

import pytest

from allocation import allocate

CURVE = {"S": 1, "M": 2, "L": 2, "XL": 1}


def rejection_reason(order_units, curve, pack_size):
    with pytest.raises(ValueError) as excinfo:
        allocate(order_units, curve, pack_size)
    return getattr(excinfo.value, "reason", None)


# rule RejectRequest / AllocationRequest.rejection_reason, one test per reason
def test_rejects_order_that_is_not_whole_packs():
    assert rejection_reason(40, CURVE, 6) == "part_pack_order"


def test_rejects_pack_size_below_one():
    assert rejection_reason(36, CURVE, 0) == "invalid_pack_size"


def test_rejects_negative_order():
    assert rejection_reason(-6, CURVE, 6) == "negative_order"


def test_rejects_empty_curve():
    assert rejection_reason(36, {}, 6) == "empty_curve"


def test_rejects_negative_ratio():
    assert rejection_reason(36, {"S": 1, "M": -1}, 6) == "negative_ratio"


def test_rejects_curve_with_no_positive_ratio():
    assert rejection_reason(36, {"S": 0, "M": 0}, 6) == "no_positive_ratio"


def test_first_failing_check_is_the_reason_given():
    # Both a bad pack size and a negative order: pack size is checked first.
    assert rejection_reason(-5, CURVE, 0) == "invalid_pack_size"


# rule StartAllocation: a valid request is allocated
def test_valid_request_is_allocated():
    assert allocate(36, CURVE, 6) == {"S": 1, "M": 2, "L": 2, "XL": 1}


def test_zero_unit_order_gives_zero_packs_everywhere():
    assert allocate(0, CURVE, 6) == {"S": 0, "M": 0, "L": 0, "XL": 0}


# rule PlaceNextPack: tie-break on equal claims goes to the earlier size
def test_equal_claims_go_to_the_size_earlier_in_the_curve():
    assert allocate(1, {"S": 1, "M": 1}, 1) == {"S": 1, "M": 0}
    assert allocate(1, {"M": 1, "S": 1}, 1) == {"M": 1, "S": 0}


# Order too small to give every size a pack
def test_small_order_leaves_some_sizes_without_a_pack():
    result = allocate(12, CURVE, 6)
    assert sum(result.values()) == 2
    assert result["S"] == 0 and result["XL"] == 0


# invariant ZeroRatioGetsNothing, surface guarantee ResultInCurveOrder
def test_zero_ratio_size_is_listed_with_zero_packs():
    assert allocate(24, {"S": 0, "M": 1, "L": 1}, 6) == {"S": 0, "M": 2, "L": 2}


# surface SizeAllocation exposes line.units = packs * pack_size
def test_units_per_size_are_packs_times_pack_size():
    result = allocate(48, CURVE, 6)
    assert {size: packs * 6 for size, packs in result.items()} == {"S": 6, "M": 18, "L": 18, "XL": 6}
