"""Size-ratio allocation of an order into whole packs per size.

Naive version, written from docs/brief.md only.
"""

from collections.abc import Mapping


def allocate(order_units: int, size_curve: Mapping[str, int], pack_size: int) -> dict[str, int]:
    """Return the number of packs to allocate to each size.

    Uses the largest-remainder method: give each size the whole-pack floor of its
    proportional share, then hand the leftover packs to the sizes with the largest
    fractional remainders.
    """
    total_packs = order_units // pack_size
    total_ratio = sum(size_curve.values())

    shares = {size: total_packs * ratio / total_ratio for size, ratio in size_curve.items()}
    packs = {size: int(share) for size, share in shares.items()}

    leftover = total_packs - sum(packs.values())
    by_remainder = sorted(shares, key=lambda size: shares[size] - packs[size], reverse=True)
    for size in by_remainder[:leftover]:
        packs[size] += 1

    return packs
