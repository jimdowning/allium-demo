# Presenter runbook

About 6 minutes. Nothing in the demo calls the model: every stage is a git tag,
and the Q&A and test runs are committed, so the demo runs the same way every
time.

Keep this file open somewhere other than the demo terminal (for example on
GitHub). The stages run from `.stages/`, so the main checkout never changes.

## Before the talk

```
git clone <your fork> allium-demo && cd allium-demo
./scripts/tag-stages.sh          # only if `git tag -l 'stage-*'` is empty
make setup                       # .venv, pytest, Hypothesis, .stages/
make stage-0 stage-2 stage-3     # warm-up run; also checks everything works
```

Terminal font large enough for about 90 columns. Have `docs/` open in an
editor or Markdown viewer in a second window for the fallback path.

## Stage 0: the brief and the obvious code (1 min)

```
cat docs/brief.md
sed -n '9,27p' .stages/stage-0-brief/src/allocation.py
make stage-0
```

Show: the five-sentence brief; the ten-line largest-remainder function;
`5 passed`.

Say: "This is what you get from a good developer working straight from the
brief: sensible code, sensible tests, all green."

## Stage 1: elicitation (1.5 min)

```
less docs/elicitation-transcript.md
```

Show: question 2 (40 units in packs of 6: reject, round down or round up?),
then question 7 (the 1:3:3 example where a bigger order takes a pack away),
then the table under question 8. Then show the spec's invariants:

```
grep -n -A4 '^invariant' spec/size-allocation.allium | less
```

Say: "Before judging any code, the elicit skill walked the brief against a
checklist of the decisions a brief usually leaves out, and each answer became
a line in the spec."

## Stage 2: tests generated from the spec (2 min)

```
make stage-2
make stage-2-counterexample
```

Show: `8 failed, 17 passed`. Point at the failures: part-pack order not
rejected, three `ZeroDivisionError`s, then the one property failure. On the
counterexample: curve 1:4:1, 4 packs. All three sizes are exactly two-thirds
of a pack short; the spec says the tie goes to the earlier size, but the naive
code's floating-point remainders are `0.6666666666666665` and
`0.6666666666666666`, so rounding error decides.

Say: "Nobody wrote these test cases by hand: the tests came from the spec, and
Hypothesis found and shrank the smallest order that breaks the rule."

If asked about the Alabama paradox: that test passed. The naive code can do it
(1:3:3 at 3 then 4 packs), but random testing did not hit such a case. We
reported that rather than tuning the test.

## Stage 3: code that meets the spec (1 min)

```
git diff --stat stage-2-propagate stage-3-fixed
make stage-3
```

Show: only `src/allocation.py` changed (plus the run record); `25 passed`.

Say: "The tests did not change: the code was rewritten until it met the spec,
and the spec, not the developer's judgement, says when it is done."

## Close (30 s)

Say: "The brief was five sentences; the spec settles about a dozen decisions
the brief was silent on, and each one is now a test."

Point to `README.md` for the three follow-on exercises.

## Fallback: no live commands

If the terminal, Python or `make` fails, present from the committed files only.
They are all in the main checkout and on GitHub:

| Stage | Open | Show |
|---|---|---|
| 0 | `docs/brief.md`, then `src/allocation.py` at tag `stage-0-brief` on GitHub | the brief and the naive function |
| 1 | `docs/elicitation-transcript.md`, `spec/size-allocation.allium` | questions 2, 7 and 8; the invariants |
| 2 | `docs/stage-2-failures.md` | the captured run and the shrunk counterexample |
| 3 | `docs/stage-3-pass.md` | `25 passed` and the before/after table |

The sentences to say are the same.
