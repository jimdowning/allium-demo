"""Shared helpers for tests generated from spec/size-allocation.allium.

The spec's entities map onto the implementation like this:

    AllocationRequest(order_units, pack_size, curve)  ->  allocate(order_units, size_curve, pack_size)
    CurveSize(size, ratio, position)                  ->  one key/value of size_curve, in insertion order
    Allocation / AllocationLine(size, packs)          ->  the returned dict {size: packs}
    AllocationRejection(reason)                       ->  ValueError with a .reason attribute
"""

from hypothesis import strategies as st

SIZE_NAMES = ["XS", "S", "M", "L", "XL", "XXL", "3XL"]


@st.composite
def size_curves(draw, min_sizes=1, max_sizes=6, max_ratio=6):
    """A valid curve: unique sizes, ratios >= 0, at least one ratio > 0."""
    n = draw(st.integers(min_sizes, max_sizes))
    names = SIZE_NAMES[:n]
    ratios = draw(st.lists(st.integers(0, max_ratio), min_size=n, max_size=n).filter(lambda r: sum(r) > 0))
    return dict(zip(names, ratios))


pack_sizes = st.integers(1, 12)
total_packs = st.integers(0, 60)


def shortfall(total, ratio, packs, total_ratio):
    """AllocationLine.shortfall(total): distance below the exact share, scaled by total_ratio."""
    return total * ratio - packs * total_ratio


def keeps_shares_reachable(curve, packs_held, size, n):
    """Black box from rule PlaceNextPack: after giving `size` pack n, every size can
    still reach its share rounded down at each later total t in n .. n + total_ratio."""
    total_ratio = sum(curve.values())
    after = dict(packs_held)
    after[size] += 1
    for t in range(n, n + total_ratio + 1):
        owed = sum(max(0, t * curve[s] // total_ratio - after[s]) for s in curve)
        if owed > t - n:
            return False
    return True


def next_pack_goes_to(curve, packs_held, n):
    """Rule PlaceNextPack: the size that receives pack number n."""
    total_ratio = sum(curve.values())
    sizes = list(curve)
    eligible = [
        s for s in sizes
        if curve[s] > 0
        and packs_held[s] * total_ratio < n * curve[s]
        and keeps_shares_reachable(curve, packs_held, s, n)
    ]
    # Largest shortfall; max() keeps the first of equal values, i.e. the earlier size.
    return max(eligible, key=lambda s: shortfall(n, curve[s], packs_held[s], total_ratio))
