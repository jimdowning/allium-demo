from hypothesis import settings

# Fixed seed and no example database, so every run (and every demo) finds and
# shrinks to the same counterexample.
settings.register_profile("demo", derandomize=True, database=None, max_examples=300, deadline=None)
settings.load_profile("demo")
