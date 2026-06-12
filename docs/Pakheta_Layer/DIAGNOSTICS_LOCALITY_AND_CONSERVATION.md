# Diagnostics, Locality, And Conservation

**Date:** June 12, 2026
**Status:** High-value direction completion pass
**Scripts:** `experiments/pakheta_wisdom_failure_modes.py`, `experiments/pakheta_false_partition_detector.py`, `experiments/pakheta_locality_phase_diagram.py`, `experiments/pakheta_cross_substrate_conservation.py`, `experiments/pakheta_recovery_loop.py`

---

## 1. Purpose

This pass completes the remaining high-value directions after hidden field inference and operator permutation grammar.

It asks:

```text
What happens when Wisdom selects the wrong context?
Can false partition be detected as a diagnostic pattern?
Does relational locality have phases?
Do Pakheta primitives conserve across substrates?
Can detection and Justice repair form a recovery loop?
```

---

## 2. Wisdom Failure Modes

Wisdom was previously under-tested. The new failure-mode sweep compares:

- correct context selection
- adjacent-but-wrong context
- object-first context
- overabstracted context

Results:

```text
correct_context              mean coherence=0.9775 drop=0.0000
adjacent_wrong_context       mean coherence=0.9364 drop=0.0410
object_first_context         mean coherence=0.2122 drop=0.7653
overabstracted_context       mean coherence=0.7963 drop=0.1811
```

Interpretation:

```text
Object-first Wisdom failure is catastrophic.
```

Adjacent contexts preserve much of the field. Overabstraction preserves shape but flattens distinction. Object-first context selection mistakes salience for participation and collapses coherence.

---

## 3. False Partition Detector

The false partition detector scores fields using:

- anchor agreement
- facet coverage
- context consistency
- identity continuity
- rival claims
- ledger split
- location overweight
- coherence drop

Results:

```text
accuracy=1.0000
precision=1.0000
recall=1.0000

false_partition mean score=0.7323
environment_noise mean score=0.3320
complementary_anchors mean score=0.2197
integrated_one_field mean score=0.1127
```

Interpretation:

```text
False partition is detectable as a pattern, not merely as low coherence.
```

The detector distinguishes complementary anchors from rival-field splits.

---

## 4. Relational Locality Phase Diagram

The locality phase experiment maps how spatial and relational distance correlate across regimes.

Results:

```text
aligned                  physical=0.9655  memory=0.9632   repair=0.9627   class=100.00%
independent              physical=-0.0097 memory=-0.0096  repair=0.0051   class=98.89%
inverted                 physical=-0.9629 memory=-0.9642  repair=-0.9628  class=100.00%
unstable_under_context   physical=0.9519  memory=-0.9538  repair=0.6071   class=100.00%
```

Interpretation:

```text
Relational locality has phase behavior.
```

Spatial distance and relational distance can align, decouple, invert, or change sign under context.

---

## 5. Cross-Substrate Primitive Conservation

The conservation experiment translates the same primitive through:

- semantic face
- mathematical face
- physical face

Primitives tested:

- anchor
- context
- actualization
- nonseparability
- decoherence

Results:

```text
overall conservation rate=100.00%
semantic accuracy=100.00%
mathematical accuracy=100.00%
physical accuracy=100.00%
```

Mean conservation margins:

```text
anchor             semantic=0.3807 math=0.3888 physical=0.4053
context            semantic=0.1913 math=0.1972 physical=0.1940
actualization      semantic=0.1968 math=0.1976 physical=0.2001
nonseparability    semantic=0.3320 math=0.3377 physical=0.3398
decoherence        semantic=0.3938 math=0.3942 physical=0.3999
```

Interpretation:

```text
Pakheta primitives can be made auditable as conserved relational signatures.
```

This strengthens the cross-substrate map by giving each primitive a measurable identity margin.

---

## 6. Pakheta Recovery Loop

The recovery loop combines:

```text
detect split -> identify primitive error -> apply Justice repair -> remeasure coherence
```

Results:

```text
false_partition_recovery_rate=100.00%
unnecessary_repair_rate=0.00%
false partition score mean: 0.7347 -> 0.3882
false partition coherence mean: 0.1039 -> 0.5377
mean coherence gain=0.4338
```

Dominant primitive errors repaired:

```text
rival_field_claim: 40
location_ledger_split: 32
object_first_location_bias: 8
```

Interpretation:

```text
Pakheta can now diagnose and repair false partition in the model.
```

The recovery loop repairs the score and the coherence, not only the label.

---

## 7. New Principles

### 7.1 Wisdom Level Principle

```text
Wisdom failure is level failure.
```

Wrong context is not merely a bad label. It changes what Power will actualize.

### 7.2 Diagnostic Pattern Principle

```text
False partition has a signature.
```

Rival claims, ledger splits, anchor disagreement, and location overweight together reveal the ontology shift.

### 7.3 Locality Phase Principle

```text
Relational distance can change phase relative to spatial distance.
```

Aligned, independent, inverted, and context-unstable locality are distinct regimes.

### 7.4 Primitive Conservation Principle

```text
The substrate changes, but the primitive can remain identifiable.
```

This turns cross-substrate mapping from analogy into a measurable conservation test.

### 7.5 Recovery Loop Principle

```text
Justice repair converts rival-field assumptions back toward one-field-many-facets.
```

Pakheta becomes a repair protocol: detect, identify, repair, remeasure.

---

## 8. Working Summary

```text
Wisdom selects the level.
False partition can be detected.
Relational locality has phases.
Primitives conserve across substrates.
Justice repair closes the loop.
```
