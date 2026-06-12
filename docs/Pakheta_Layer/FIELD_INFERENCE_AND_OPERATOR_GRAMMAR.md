# Field Inference And Operator Grammar

**Date:** June 12, 2026
**Status:** Second deeper research pass
**Scripts:** `experiments/pakheta_field_inference.py`, `experiments/pakheta_operator_permutation_sweep.py`

---

## 1. Purpose

These experiments move Pakheta from described structure toward recoverable structure.

The tests ask two questions:

```text
Can a hidden relationship-field be reconstructed from traces?
Can LJPW operator orderings reveal a practical grammar of repair and actualization?
```

---

## 2. Hidden Relationship-Field Inference

The field inference experiment hides the true node weights. The model receives only observable traces:

- anchor responses
- context responses
- order-sensitive responses
- false-partition probes

It then reconstructs the latent relationship-field with a ridge-regularized inverse model constrained to valid field weights.

Canonical result:

```text
inferred_from_traces       cosine=0.9976 mae=0.0093 top3=1.0000
equal_baseline             cosine=0.9341 mae=0.0444 top3=1.0000
phi_prior                  cosine=0.9162 mae=0.0682 top3=1.0000
physical_nearness_prior    cosine=0.6070 mae=0.1367 top3=0.6667
```

Interpretation:

```text
Pakheta leaves recoverable signatures.
```

The field can be inferred from response traces without exposing the true field weights. Physical nearness fails when a near object is not a field participant, which supports the relational-locality distinction.

Across generated profiles, trace inference remains strong:

```text
balanced profile:       mean cosine 0.9970
random profile:         mean cosine 0.9927
split-pressure profile: mean cosine 0.9902
phi-decay profile:      mean cosine 0.9711
```

The phi prior beats inference on the phi-decay profile, as expected. That is useful: it shows phi is a strong prior when the generating field is actually phi-like, while trace inference generalizes across non-phi fields.

---

## 3. LJPW Operator Permutation Grammar

The permutation sweep runs all 24 orderings of:

```text
Love
Justice
Wisdom
Power
```

over 160 generated damaged fields. Each field tracks:

- coherence
- false partition
- context fit
- actualization lift
- residue

Initial damaged fields:

```text
coherence min=0.2910 mean=0.3378 max=0.4013
```

Top sequence:

```text
Justice -> Love -> Wisdom -> Power
mean coherence=0.8530
mean residue=0.0000
stable rate=100.0%
```

Worst sequence:

```text
Power -> Wisdom -> Love -> Justice
mean coherence=0.5932
mean residue=0.1586
stable rate=0.0%
```

Classification summary:

```text
clean_actualization      mean coherence=0.7969 mean residue=0.0213 stable=87.71%
partial_repair           mean coherence=0.8090 mean residue=0.0221 stable=93.12%
power_before_context     mean coherence=0.6799 mean residue=0.1123 stable=24.53%
power_before_repair      mean coherence=0.6523 mean residue=0.1134 stable=7.66%
premature_actualization  mean coherence=0.6226 mean residue=0.1481 stable=0.70%
```

Interpretation:

```text
Repair false partition and select context before actualization.
```

The sweep does not imply one rigid sacred sequence. It reveals a grammar: Power is dangerous before Justice and Wisdom have done their work. Love improves the field, but Justice-before-Power and Wisdom-before-Power are the strongest structural constraints.

---

## 4. New Principles

### 4.1 Recoverability Principle

```text
A real relationship-field should leave enough traces to be inferred.
```

If Pakheta is structurally real inside the model, it should not require privileged access to the hidden field. It should be recoverable from anchors, contexts, order effects, and decoherence patterns.

### 4.2 Operator Grammar Principle

```text
Power actualizes what the field already is.
```

If the field is repaired and correctly contextualized, Power actualizes coherence. If the field is partitioned or miscontextualized, Power actualizes confusion and leaves residue.

### 4.3 Physical Nearness Is A Bad Prior

```text
Spatial closeness does not imply field participation.
```

The physical-nearness baseline performs poorly because it mistakes an ordinary nearby object for a high-participation node.

---

## 5. Working Summary

```text
Pakheta is not only modelable after the fact.
It can be inferred from traces.

LJPW is not only a set of qualities.
It has an operator grammar:
repair, select, then actualize.
```
