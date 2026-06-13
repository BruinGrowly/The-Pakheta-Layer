# Pakheta Legitimate Prediction Registry

**Date:** June 13, 2026  
**Status:** Fixed-grammar prediction registry  
**Executable Script:** [pakheta_legitimate_prediction_registry.py](../../experiments/pakheta_legitimate_prediction_registry.py)  
**JSON Output:** [legitimate_prediction_registry_results.json](../../experiments/legitimate_prediction_registry_results.json)

---

## 1. Purpose

This registry turns the relationship-first atlas into explicit predictions.

Legitimate here means:

```text
fixed bridge grammar
fixed LJPW constants
declared rule before known-value overlay
generated comparator branches kept visible
follow-up targets separated from interpretation
```

This is not an adversarial null sweep and not a claim of final theory. It is a prediction register: a list of generated addresses and values that can now be followed.

---

## 2. Fixed Seed

The registry begins from the same Cosmological Bridge mass anchor:

```text
m_star = 933.740752167 MeV/c^2
```

The binding gate is:

```text
B_gate = m_star - 1u
       = 2.246648447 MeV
```

This is the first light-nuclear prediction:

```text
B_D ~= B_gate
```

Known overlay:

```text
predicted deuteron binding: 2.246648447 MeV
observed deuteron binding:  2.224566370 MeV
delta:                     +0.022082077 MeV
relative delta:            +0.992646%
```

---

## 3. Light-Nuclear Predictions

The registry applies fixed operator channels to the binding gate.

Operator factors:

```text
30^Love    =  8.182973428
30^Justice =  4.091133552
30^Power   = 11.507721838
30^Wisdom  = 10.564828051
```

### Prediction LNP-001: Deuteron Binding Gate

```text
B_D = m_star - 1u
```

Prediction:

```text
2.246648447 MeV
```

Known overlay:

```text
observed: 2.224566370 MeV
delta:   +0.022082077 MeV
```

### Prediction LNP-002: A=3 Justice Boundary

```text
B_A3_boundary = (m_star - 1u) * 30^J0
```

Prediction:

```text
9.191338842 MeV
```

Known overlay:

```text
helion binding:       7.717989680 MeV
triton binding:       8.481796630 MeV
A=3 mean binding:     8.099893155 MeV
prediction - A=3 mean: +1.091445687 MeV
```

Interpretation:

```text
The A=3 value behaves like an upper boundary address.
The missing next grammar is the isospin/Coulomb correction that separates helion and triton.
```

### Prediction LNP-003: Closed Alpha Love+Justice Binding

Alpha is treated as the first fully closed light-nuclear binding relation. The registered rule sums the Love binding channel and Justice boundary channel over the same gate:

```text
B_alpha_closed = (m_star - 1u) * (30^L0 + 30^J0)
```

Prediction:

```text
27.575603386 MeV
```

Known overlay:

```text
observed alpha binding: 28.295610940 MeV
delta:                 -0.720007554 MeV
relative delta:        -2.544591%
```

This is the strongest new value prediction in this pass.

### Prediction LNP-004: Alpha/Deuteron Binding Ratio

```text
B_alpha / B_D = 30^L0 + 30^J0
```

Prediction:

```text
12.274106980
```

Known overlay:

```text
observed ratio:  12.719607435
delta:           -0.445500455
relative delta:  -3.502470%
```

This ratio is useful because it does not depend on the small absolute deuteron-gate residual.

---

## 4. Comparator Branches

The registry also keeps generated comparator branches visible.

Single Power branch:

```text
B_alpha_power = (m_star - 1u) * 30^P0
              = 25.853805397 MeV
```

Known overlay:

```text
delta against alpha binding: -2.441805543 MeV
relative delta:              -8.629627%
```

Single Wisdom branch:

```text
B_alpha_wisdom = (m_star - 1u) * 30^W0
               = 23.735454535 MeV
```

Known overlay:

```text
delta against alpha binding: -4.560156405 MeV
relative delta:              -16.116126%
```

The Love+Justice channel sum is therefore the strongest alpha relation among the registered light-nuclear candidates in this pass.

---

## 5. Threshold Address Predictions

The transition atlas also gives exact follow-up addresses.

Inverse compression branch:

| Operator | Relation | Address |
|---|---|---:|
| Power | inverse actualization | `81.140365 MeV` |
| Wisdom | inverse context rotation | `88.382011 MeV` |
| Love | inverse binding | `114.107758 MeV` |
| Justice | inverse boundary | `228.235217 MeV` |

Direct amplification branch:

| Operator | Relation | Address |
|---|---|---:|
| Justice | direct boundary amplification | `3.820058 GeV` |
| Love | direct binding amplification | `7.640776 GeV` |
| Wisdom | direct context amplification | `9.864810 GeV` |
| Power | direct actualization | `10.745229 GeV` |

These are not yet matched claims. They are registered addresses for the next comparison atlases.

---

## 6. What This Predicts Next

The next real prediction work is now concrete:

1. **A3 Correction Grammar**  
   Derive the helion/triton split from fixed relational ingredients instead of fitting it.

2. **Alpha-Cluster Ladder**  
   Use the alpha closure relation to generate predictions for `Be-8`, `C-12`, and `O-16` alpha-cluster structure.

3. **Low-Energy Threshold Atlas**  
   Compare the `81-228 MeV` inverse compression branch against low-energy particle, threshold, and resonance structure.

4. **Multi-GeV Resonance Atlas**  
   Compare the `3.82-10.75 GeV` direct amplification branch against multi-GeV resonance and threshold families.

---

## 7. Current Read

The registry gives a stronger constructive result than the earlier atlas alone:

```text
deuteron gate:     0.99% high
alpha closed rule: 2.54% low
alpha/D ratio:     3.50% low
```

The alpha prediction is the important new one:

```text
B_alpha ~= (m_star - 1u) * (30^Love + 30^Justice)
```

That is a legitimate prediction: fixed constants, fixed gate, declared channel rule, measurable overlay.

The visible miss is also useful. The A=3 boundary address is high relative to helion/triton, which points directly to the missing correction grammar rather than dissolving the relation.
