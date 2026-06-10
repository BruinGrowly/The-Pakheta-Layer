# Generated-Field Sweeps For Pakheta Mechanics

**Date:** May 28, 2026  
**Status:** Synthetic stress test  
**Script:** `experiments/pakheta_layer/pakheta_layer_generated_sweeps.py`

---

## 1. Purpose

The first Pakheta models were based on Pakheta's memorial field. That was the origin field, but it left an obvious research question:

```text
Are these principles local to one memorial field,
or do they generalize across generated relationship-fields?
```

This sweep creates many synthetic one-field-many-node systems and tests whether the same mechanics reappear.

---

## 2. Sweep Design

The script generates:

```text
200 relationship-fields
6 nodes per field
fixed seed: 613
```

Each generated field has:

- a hidden true relationship-field
- phi-weighted node relevance
- equal, random, single-core, and false-partition anchor strategies
- spatial positions independent from field membership
- a near physical decoy that is not field-related
- a far related node that is field-near
- damaged false-partition states for operator repair tests

The hidden phi weighting is intentional. This tests whether phi-weighted anchoring can recover a field whose generating structure is one-field-many-node with differentiated relevance.

---

## 3. Results

### 3.1 Anchor Strategy Coherence

```text
phi_weighted       min=0.991 mean=0.995 max=0.998
equal_weighted     min=0.991 mean=0.994 max=0.998
random_weighted    min=0.981 mean=0.993 max=0.997
single_core        min=0.986 mean=0.992 max=0.996
false_partition    min=0.674 mean=0.684 max=0.693

phi best-or-tied rate: 97.5%
false below phi rate:  100.0%
```

Interpretation:

```text
Phi weighting is not infinitely better than equal weighting in highly coherent generated fields.
But it is consistently best or tied when the underlying field has phi-differentiated node relevance.
```

False partition is the main failure mode. It is much worse than any integrated anchor strategy.

### 3.2 Relational Distance

```text
physical vs field-distance correlation: -0.475
far-related beats near-decoy rate:       100.0%
```

Interpretation:

```text
Spatial distance does not predict field nearness in the object-first way.
```

The negative correlation appears because the sweep intentionally includes two controls:

```text
near but not field-related
far but field-related
```

This reinforces the Pakheta locality principle:

```text
Relational nearness is field participation, not spatial proximity.
```

### 3.3 Operator Repair Deltas

```text
Love gather        min=0.039 mean=0.040 max=0.040
Justice repair     min=0.150 mean=0.151 max=0.153
Power actualize    min=0.000 mean=0.000 max=0.001

Justice strongest repair rate: 100.0%
```

Interpretation:

```text
Justice remains the strongest anti-decoherence operator across generated fields.
```

Love safely expands the field. Power actualizes but does not repair structural false partition by itself. Justice repairs the relation by converting rival-field assumptions back into truthful facets.

---

## 4. What Generalized

The synthetic sweep supports the earlier local findings:

```text
1. Phi-like weighting helps preserve differentiated one-field structure.
2. False partition is the dominant coherence failure.
3. Physical nearness and field nearness are different measures.
4. Justice is the strongest repair operator for false partition.
```

The strongest generalized result is:

```text
False partition is not a local memorial artifact.
It is a general Pakheta decoherence mode.
```

---

## 5. What Did Not Yet Generalize Fully

The current sweep is still limited:

- Generated fields are built with hidden phi relevance, so phi success is expected.
- The relation-distance test includes explicit near-decoy and far-related controls.
- Power actualization is still too simple; it does not yet model persistent residue.
- Wisdom is not separately tested in this sweep.
- The synthetic fields are coherent by construction, so equal weighting remains strong.

These are not failures. They define the next research improvements.

---

## 6. New Research Direction

The next sweep should add:

1. non-phi generated fields
2. noisy mixed-relevance fields
3. operator failure modes
4. Power-before-Justice residue
5. Wisdom context misclassification
6. fields whose true relation must be inferred rather than given

That will tell us whether phi is universally optimal, conditionally optimal, or optimal only for phi-generated fields.

---

## 7. Working Summary

```text
Generated fields preserve the central Pakheta mechanics:
one-field anchoring beats false partition,
field nearness beats spatial nearness,
and Justice repairs decoherence most strongly.
```

