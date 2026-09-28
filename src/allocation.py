"""Size-ratio allocation of an order into whole packs per size.

Implements spec/size-allocation.allium. Packs are placed one at a time
(Still's quota method with a largest-shortfall priority), so:

- allocated units always equal the order,
- every size gets its exact share rounded down or up, never further away,
- a larger order never gives any size fewer packs,
- ties go to the size listed earlier in the curve.

All arithmetic is on whole numbers. Shares are compared scaled by the total
ratio, so there is no rounding error.
"""

from collections.abc import Mapping


class AllocationRejected(ValueError):
    """The request cannot be allocated. `reason` is one of the spec's RejectionReason values."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def allocate(order_units: int, size_curve: Mapping[str, int], pack_size: int) -> dict[str, int]:
    """Return the number of packs for each size, in curve order."""
    _check_request(order_units, size_curve, pack_size)

    total_packs = order_units // pack_size
    packs = {size: 0 for size in size_curve}
    for n in range(1, total_packs + 1):
        packs[_next_pack_goes_to(size_curve, packs, n)] += 1
    return packs


def _check_request(order_units: int, size_curve: Mapping[str, int], pack_size: int) -> None:
    # Checks run in the spec's order; the first failure is the reason given.
    # Duplicate sizes cannot occur: a Mapping has unique keys.
    if pack_size < 1:
        raise AllocationRejected("invalid_pack_size")
    if order_units < 0:
        raise AllocationRejected("negative_order")
    if not size_curve:
        raise AllocationRejected("empty_curve")
    if any(ratio < 0 for ratio in size_curve.values()):
        raise AllocationRejected("negative_ratio")
    if sum(size_curve.values()) == 0:
        raise AllocationRejected("no_positive_ratio")
    if order_units % pack_size != 0:
        raise AllocationRejected("part_pack_order")


def _next_pack_goes_to(size_curve: Mapping[str, int], packs: Mapping[str, int], n: int) -> str:
    """The size that receives pack number n (rule PlaceNextPack)."""
    total_ratio = sum(size_curve.values())
    eligible = [
        size
        for size, ratio in size_curve.items()
        if ratio > 0
        and packs[size] * total_ratio < n * ratio
        and _keeps_shares_reachable(size_curve, packs, size, n)
    ]
    # Largest shortfall below the exact share of n packs, scaled by total_ratio.
    # max() returns the first of equal values, so ties go to the earlier size.
    return max(eligible, key=lambda size: n * size_curve[size] - packs[size] * total_ratio)


def _keeps_shares_reachable(size_curve: Mapping[str, int], packs: Mapping[str, int], size: str, n: int) -> bool:
    """After giving `size` pack n, can every size still reach its share rounded down at every later total?"""
    total_ratio = sum(size_curve.values())
    after = dict(packs)
    after[size] += 1
    for t in range(n, n + total_ratio + 1):
        owed = sum(max(0, t * ratio // total_ratio - after[s]) for s, ratio in size_curve.items())
        if owed > t - n:
            return False
    return True
