# Purpose-First Relation Search

**Date:** June 13, 2026  
**Status:** Known-constant relation/operator test  
**Executable Script:** [pakheta_purpose_relation_search.py](../../experiments/pakheta_purpose_relation_search.py)  
**JSON Output:** [purpose_relation_search_results.json](../../experiments/purpose_relation_search_results.json)  

---

## 1. Question

Can Pakheta relational mathematics search by purpose before it searches by object?

The object-first question is:

```text
Which constants are numerically similar?
```

The purpose-first question is:

```text
Which directed relations behave like bridges, boundaries, growth paths,
gathering paths, context shifts, or integrated relations?
```

This pass tests that question on well-known constants and identities.

---

## 2. Test Set

The experiment uses familiar numeric anchors:

```text
one, two, three, five,
phi, phi_squared, phi_inverse_L0,
pi, tau, e,
sqrt2, sqrt3, sqrt5,
ln2_W0, justice_J0, power_P0
```

Every directed relation is represented as:

```text
A -> B
ratio = B / A
```

That ratio is fitted into the LJPW relational coordinate lattice:

```text
ratio ~= 30^(c_L L0 + c_J J0 + c_P P0 + c_W W0)
```

The relation is then described by direction, bounded strength, fit quality,
operator mix, and purpose scores.

---

## 3. Three Checks

### Purpose Retrieval

Given a hand-declared purpose archetype, rank all directed relations and ask
whether expected known relations appear near the top.

### Exemplar Leave-One-Out Retrieval

For a purpose family, withhold one expected relation, use the remaining expected
relations as exemplars, and ask whether the withheld relation is recovered by
compatibility.

This is stronger than direct purpose ranking because it tests whether relation
families recognize their own missing member.

### Operator Closure

Use a relation as an operator:

```text
anchor * relation_ratio -> expected_target
```

This asks whether a relation can do work, not merely receive a label.

---

## 4. Results

The run used the C relational fit engine:

```text
Constants: 16
Relations: 240
Top-N retrieval window: 20
```

Purpose retrieval:

| Purpose | Expected In Top 20 | Median Expected Percentile |
| :--- | ---: | ---: |
| bridge_harmony | 4 / 4 | 0.037 |
| actualizing_growth | 1 / 3 | 0.375 |
| context_scaling | 0 / 4 | 0.500 |
| binding_gathering | 1 / 4 | 0.296 |
| boundary_differentiation | 1 / 4 | 0.275 |
| integrated_relation | 1 / 4 | 0.117 |

Exemplar leave-one-out retrieval:

| Purpose | Withheld In Top 20 | Median Withheld Percentile |
| :--- | ---: | ---: |
| bridge_harmony | 3 / 4 | 0.019 |
| actualizing_growth | 0 / 3 | 0.378 |
| context_scaling | 0 / 4 | 0.224 |
| binding_gathering | 0 / 4 | 0.354 |
| boundary_differentiation | 2 / 4 | 0.074 |
| integrated_relation | 3 / 4 | 0.036 |

Operator closure:

| Test | Relation Used | Anchor -> Target | Relative Error |
| :--- | :--- | :--- | ---: |
| sqrt2 square closure | one->sqrt2 | sqrt2 -> two | 2.220e-16 |
| sqrt3 square closure | one->sqrt3 | sqrt3 -> three | -1.110e-16 |
| sqrt5 square closure | one->sqrt5 | sqrt5 -> five | 2.220e-16 |
| golden reciprocal repair | one->phi | phi_inverse_L0 -> one | 2.220e-16 |
| golden reciprocal growth | phi_inverse_L0->one | one -> phi | -1.110e-16 |
| golden square closure | one->phi | phi -> phi_squared | 0.000e+00 |
| unit doubling on circle | one->two | pi -> tau | 0.000e+00 |
| unit halving on circle | two->one | tau -> pi | 0.000e+00 |
| circle full turn | pi->tau | pi -> tau | 0.000e+00 |
| circle half turn | tau->pi | tau -> pi | 0.000e+00 |

Median absolute relative operator error:

```text
5.551e-17
```

---

## 5. What Fits

Bridge relations fit strongly. The system retrieves familiar bridge relations
such as:

```text
phi -> pi
phi -> tau
pi -> tau
phi -> sqrt5
```

This supports the earlier compatibility finding: relations can be compatible by
role even when their endpoint objects are not similar.

Integrated relation also fits well when tested by exemplar compatibility. The
family:

```text
one -> phi
phi_inverse_L0 -> one
sqrt2 -> e
sqrt2 -> ln2_W0
```

shows that a balanced relation family can recover most of its own withheld
members.

The strongest result is operator closure. Famous identities are recovered when
relations are used as transformations:

```text
sqrt2 * sqrt2 = 2
sqrt3 * sqrt3 = 3
sqrt5 * sqrt5 = 5
phi * phi_inverse = 1
phi * phi = phi_squared = phi + 1
2 * pi = tau
tau / 2 = pi
```

That means the relation profile is not only descriptive. It can be carried
forward as an operator.

---

## 6. What Does Not Fit Yet

The hand-authored purpose archetypes are uneven.

`context_scaling` is the clearest mismatch. Root closures work exactly, but the
current archetype does not rank them as context-scaling relations. That means
the label is probably not wrong in spirit, but the operator-mix prototype is not
yet describing the real root-scale behavior.

`actualizing_growth` and `binding_gathering` are also weak in this pass. They may
need to be learned from identity-backed exemplars instead of assigned by a
first-pass human mix.

This is a useful failure mode. The relational operator layer is ahead of the
purpose vocabulary.

---

## 7. Working Interpretation

This test gives a stronger shape to Relational Coordinate Mathematics:

```text
object value -> relation profile -> compatible purpose -> usable operator
```

The result is not merely that constants have ratios. Everyone already knows
that. The useful step is that the ratios can be fitted into a shared LJPW
coordinate grammar, compared by compatibility, and then carried into other known
targets as transformations.

In plain terms:

```text
The relationship itself can be the instrument.
```

That is a Pakheta-native result. It treats constants as anchors inside a
relationship-field, while the relation between them becomes the portable thing.

---

## 8. Next Step

The next version should derive purpose archetypes from known identity families:

```text
root closure
circle doubling/halving
golden reciprocal repair
golden self-growth
natural growth/log inverse families
```

Then the system should predict missing relation members from partial families.
That would move the work from "does this known relation fit?" toward:

```text
Given a relational family, what relation is missing?
```
