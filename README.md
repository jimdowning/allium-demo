# Spec-first allocation demo

A small worked example of spec-first development with Claude Code and the
[Allium](https://github.com/juxt/allium) plugin from JUXT.

The system allocates an apparel order across sizes. A buyer orders a style as
a number of units. The style has a size curve (for example S:1, M:2, L:2, XL:1),
and units ship in packs of a fixed size. The system decides how many packs each
size gets.

## What the demo shows

The starting point is a five-sentence brief (`docs/brief.md`) that leaves out
most of the hard cases, as real briefs do. The demo runs in four stages, each a
git tag:

| Tag | What happens |
|---|---|
| `stage-0-brief` | A developer implements the brief directly, using the obvious largest-remainder method, and writes five reasonable example tests. They pass. |
| `stage-1-elicit` | The `allium:elicit` skill interviews the stakeholder about the brief and writes a formal spec (`spec/size-allocation.allium`). The questions and decisions are in `docs/elicitation-transcript.md`. |
| `stage-2-propagate` | `allium plan` lists the 34 tests the spec requires, and the `allium:propagate` skill writes them as property-based tests (Hypothesis) and unit tests. Run against the unchanged stage-0 code, 8 of 25 fail. See `docs/propagate-transcript.md` and `docs/stage-2-failures.md`. |
| `stage-3-fixed` | The code is rewritten to meet the spec. All 25 tests pass. See `docs/stage-3-pass.md`. |

The point is not the allocation method. It is that:

- the example tests at stage 0 look fine and pass, but the code accepts orders
  it cannot fill correctly, crashes on some inputs, and settles exact ties by
  floating-point rounding error;
- the questions that expose this come from working through the brief
  systematically, before any code is judged;
- once decisions are written down as a spec, tests can be generated from it,
  and those tests find the gaps without anyone having to think of the cases.

Two honest notes:

- The generated monotonicity test ("a bigger order never takes a pack away
  from a size") did **not** fail against the naive code, even though the naive
  code can do this (curve 1:3:3: 3 packs gives 1/1/1, 4 packs gives 0/2/2).
  Random testing found other failures first. The test was not tuned to force it.
- The first method chosen at stage 1 turned out to give poor answers (a 2:1
  curve with 2 packs gave 2/0 instead of 1/1). The stage-2 tests exposed this,
  and the spec was revised before stage 2 was committed. Both versions are in
  the git history and the transcript explains the change.

## Layout

```
docs/brief.md                     the original brief, unchanged
docs/elicitation-transcript.md    stage 1 questions and decisions
docs/stage-2-plan.json            stage 2 `allium plan` output (34 test obligations)
docs/stage-2-obligations.txt      the same, one line per obligation
docs/propagate-transcript.md      stage 2 record of how the tests were generated
docs/stage-2-failures.md          stage 2 test run, with the shrunk counterexample
docs/stage-3-pass.md              stage 3 test run
spec/size-allocation.allium       the spec
src/allocation.py                 allocate(order_units, size_curve, pack_size) -> {size: packs}
tests/test_examples.py            stage 0 hand-written examples
tests/test_spec_*.py              stage 2 generated tests
DEMO.md                           presenter runbook
```

## Running it

You need Python 3.12 and `make`.

```
make setup      # creates .venv, installs pytest and Hypothesis, creates .stages/
make stage-0    # 5 passed
make stage-2    # 8 failed, 17 passed (naive code against the generated tests)
make stage-2-counterexample
make stage-3    # 25 passed
make test       # the tests in your current checkout
```

`make setup` checks out each stage tag into its own git worktree under
`.stages/`, so you can compare stages side by side without switching branches.

The stage tags are on GitHub and come with a clone or fork. If
`git tag -l 'stage-*'` prints nothing, run `./scripts/tag-stages.sh` to
recreate them.

To look at one stage in your own checkout instead:

```
git checkout stage-2-propagate
.venv/bin/pytest
git checkout -          # back to where you were
```

To validate the spec, install the Allium CLI (`cargo install allium-cli` or
`brew tap juxt/allium && brew install allium`) and run `make spec-check`.

## Using the Allium skills in your own Claude Code

`.claude/settings.json` enables the JUXT plugin marketplace and the `allium`
plugin for this project. When you open the repo in Claude Code and trust the
project settings, you should be offered the plugin. If not:

```
/plugin marketplace add juxt/claude-plugins
/plugin install allium@juxt-plugins
```

The skills used here are `allium:elicit` (interview to spec),
`allium:propagate` (spec to tests), `allium:tend` (targeted spec edits) and
`allium:weed` (find where spec and code disagree).

## Three things to try

Each one takes 15-30 minutes. Work on a branch.

1. **Add a minimum-packs-per-size rule.** Buyers want every size with a
   positive ratio to get at least one pack, when the order is big enough. Ask
   Claude Code to run `allium:elicit` on the change. It should ask you what
   "big enough" means, what happens when it isn't, and how this interacts with
   the within-one-pack rule. Then run `allium:propagate` to update the tests,
   watch them fail, and ask Claude to implement it.

2. **Accept part-pack orders.** The spec currently rejects 40 units in packs
   of 6. Change the decision: round down and report the units left over. Use
   `allium:tend` to change the spec, including what the result must report,
   then `allium:propagate` and implement. Check which existing tests change and
   why.

3. **Break the code and let the spec find it.** Change one line in
   `src/allocation.py` so that ties go to the *later* size in the curve. Run
   `make test` and see which test catches it. Then ask Claude Code to run
   `allium:weed` and see whether it finds the same divergence by reading the
   spec and the code.
