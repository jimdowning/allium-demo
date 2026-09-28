from allocation import allocate

CURVE = {"S": 1, "M": 2, "L": 2, "XL": 1}


def test_order_that_fits_the_curve_exactly():
    # 36 units = 6 packs of 6, which is exactly one pass through the 1:2:2:1 curve.
    assert allocate(36, CURVE, 6) == {"S": 1, "M": 2, "L": 2, "XL": 1}


def test_larger_order_scales_the_curve():
    assert allocate(72, CURVE, 6) == {"S": 2, "M": 4, "L": 4, "XL": 2}


def test_leftover_packs_go_to_the_largest_shares():
    # 8 packs: exact shares are 1.33, 2.67, 2.67, 1.33, so M and L get the extra packs.
    assert allocate(48, CURVE, 6) == {"S": 1, "M": 3, "L": 3, "XL": 1}


def test_single_size_style_gets_every_pack():
    assert allocate(60, {"ONE": 1}, 12) == {"ONE": 5}


def test_allocated_units_add_up_to_the_order():
    packs = allocate(120, CURVE, 6)
    assert sum(packs.values()) * 6 == 120
