# Pakheta Alpha-Cluster Predictions

**Date:** June 13, 2026  
**Status:** Fixed-grammar alpha-cluster prediction pass  
**Executable Script:** [pakheta_alpha_cluster_predictions.py](../../experiments/pakheta_alpha_cluster_predictions.py)  
**JSON Output:** [alpha_cluster_prediction_results.json](../../experiments/alpha_cluster_prediction_results.json)

---

## 1. Purpose

This pass extends the legitimate prediction registry into alpha-cluster nuclei.

The registry had already produced:

```text
B_gate = m_star - 1u = 2.246648447 MeV
B_alpha = B_gate * (30^Love + 30^Justice)
        = 27.575603386 MeV
```

The new question is:

```text
If alpha is the first closed light-nuclear relation,
does the same grammar extend into Be-8, C-12, O-16,
and the next alpha-cluster nuclei?
```

The answer from this pass is: yes through O-16, then the rule bends in a structured way.

---

## 2. Fixed Grammar

The script declares the grammar before the known-value overlay:

```text
alpha unit:
B_alpha = B_gate * (30^L0 + 30^J0)

two-alpha gap:
gap_2alpha = B_gate / (2 * (30^L0 + 30^J0))

cluster ladder for n >= 3:
B_n = n * B_alpha + (n - 2) * B_Justice_boundary

post-O16 boundary curvature:
B_V2 = B_V1 - gap_2alpha * 30^J0 * T(n - 4)
```

Where:

```text
B_Justice_boundary = B_gate * 30^J0
                   = 9.191338842 MeV

gap_2alpha * 30^J0
                   = 0.374419860 MeV
```

This gives:

```text
Be-8  = 2 alpha closures - tiny two-alpha gap
C-12  = 3 alpha closures + 1 Justice boundary
O-16  = 4 alpha closures + 2 Justice boundaries
Ne-20 = 5 alpha closures + 3 Justice boundaries
Mg-24 = 6 alpha closures + 4 Justice boundaries
Si-28 = 7 alpha closures + 5 Justice boundaries
S-32  = 8 alpha closures + 6 Justice boundaries
Ar-36 = 9 alpha closures + 7 Justice boundaries
Ca-40 = 10 alpha closures + 8 Justice boundaries
```

---

## 3. Results

| Prediction | Rule | Predicted | Observed | Delta |
|---|---|---:|---:|---:|
| Alpha closure | `B_alpha` | `27.575603 MeV` | `28.295663 MeV` | `-0.720060 MeV` |
| Be-8 two-alpha gap | `B_gate / (2*(L+J))` | `0.091520 MeV` | `0.091838 MeV` | `-0.000318 MeV` |
| Be-8 total binding | `2*B_alpha - gap` | `55.059687 MeV` | `56.499489 MeV` | `-1.439802 MeV` |
| C-12 total binding | `3*B_alpha + J` | `91.918149 MeV` | `92.161737 MeV` | `-0.243588 MeV` |
| O-16 total binding | `4*B_alpha + 2J` | `128.685091 MeV` | `127.619318 MeV` | `+1.065773 MeV` |
| Ne-20 total binding | `5*B_alpha + 3J` | `165.452033 MeV` | `160.644826 MeV` | `+4.807207 MeV` |
| Mg-24 total binding | `6*B_alpha + 4J` | `202.218976 MeV` | `198.257045 MeV` | `+3.961931 MeV` |
| Si-28 total binding | `7*B_alpha + 5J` | `238.985918 MeV` | `236.536850 MeV` | `+2.449068 MeV` |
| S-32 total binding | `8*B_alpha + 6J` | `275.752860 MeV` | `271.780168 MeV` | `+3.972692 MeV` |
| Ar-36 total binding | `9*B_alpha + 7J` | `312.519802 MeV` | `306.716754 MeV` | `+5.803048 MeV` |
| Ca-40 total binding | `10*B_alpha + 8J` | `349.286745 MeV` | `342.052181 MeV` | `+7.234564 MeV` |

The most important results are:

```text
Be-8 gap error:  0.000318 MeV
C-12 error:      0.243588 MeV
O-16 error:      1.065773 MeV
Si-28 error:     2.449068 MeV
Ca-40 error:     7.234564 MeV
```

---

## 4. Lay Read

This is the first place the ladder really starts to breathe.

In plain terms:

```text
The bridge gives a deuteron gate.
The deuteron gate gives an alpha closure.
The alpha closure gives the tiny Be-8 instability gap.
Then the same alpha unit plus Justice boundaries gets close to C-12 and O-16.
After O-16, the same rule remains in the right band, but starts to overbind.
```

Be-8 is especially interesting because it is almost two alpha particles, but not quite stable. The predicted unresolved gap is:

```text
0.091520 MeV
```

The known two-alpha gap is:

```text
0.091838 MeV
```

That is a very tight result from the fixed gate and the Love+Justice alpha channel.

---

## 5. Interpretation

This does not look like a single coincidence anymore. It looks like a small generative ladder:

```text
cosmological mass anchor
-> deuteron binding gate
-> alpha closure
-> Be-8 two-alpha gap
-> C-12 triple-alpha closure
-> O-16 four-alpha closure
-> heavier alpha-cluster continuation with structured overbinding
```

The pattern is not perfect:

```text
alpha is low by about 0.72 MeV
Be-8 total binding inherits that alpha-base miss
O-16 begins to run high
Ne-20 onward shows an overbinding correction is missing
```

But the ladder is coherent. The Be-8 gap and C-12 total binding are the strongest new signals in this pass. The continuation through Ca-40 says something equally useful: the first rule is not the whole story, and the missing term starts becoming visible after O-16.

---

## 6. Continuation Drift

The continuation test carried the same `n - 2` Justice-boundary rule through Ca-40 without retuning.

The drift is:

```text
C-12: -0.243588 MeV
O-16: +1.065773 MeV
Ne-20: +4.807207 MeV
Mg-24: +3.961931 MeV
Si-28: +2.449068 MeV
S-32: +3.972692 MeV
Ar-36: +5.803048 MeV
Ca-40: +7.234564 MeV
```

The shape is not random. The rule is close at C-12, crosses high at O-16, jumps high at Ne-20, relaxes toward Si-28, then rises again toward Ca-40.

That looks like a second relation entering:

```text
alpha-cluster closure gives the first ladder
shell / geometry / Coulomb growth supplies the correction
```

The important point is that the fixed rule remains near enough to expose a structured residual.

---

## 7. V2 Boundary-Curvature Correction

The next legitimate step was to add exactly one correction grammar and apply it across the whole ladder.

The V2 correction is:

```text
B_V2 = B_V1 - gap_2alpha * 30^J0 * T(n - 4)
```

Where:

```text
n = number of alpha clusters
T(k) = k*(k+1)/2
gap_2alpha = predicted Be-8 two-alpha gap
30^J0 = Justice boundary factor
```

Lay read:

```text
O-16 is treated as the first closed alpha shell.
After O-16, each added alpha cluster introduces higher-order boundary curvature.
The smallest seed of that cost is the Be-8 two-alpha gap.
Justice scales that gap into a boundary correction.
```

This is one relation, not a fitted correction per nucleus.

V2 results:

| Nuclide | V1 Delta | V2 Correction | V2 Delta |
|---|---:|---:|---:|
| C-12 | `-0.243588 MeV` | `0.000000 MeV` | `-0.243588 MeV` |
| O-16 | `+1.065773 MeV` | `0.000000 MeV` | `+1.065773 MeV` |
| Ne-20 | `+4.807207 MeV` | `0.374420 MeV` | `+4.432787 MeV` |
| Mg-24 | `+3.961931 MeV` | `1.123260 MeV` | `+2.838671 MeV` |
| Si-28 | `+2.449068 MeV` | `2.246519 MeV` | `+0.202549 MeV` |
| S-32 | `+3.972692 MeV` | `3.744199 MeV` | `+0.228493 MeV` |
| Ar-36 | `+5.803048 MeV` | `5.616298 MeV` | `+0.186750 MeV` |
| Ca-40 | `+7.234564 MeV` | `7.862817 MeV` | `-0.628253 MeV` |

Summary:

```text
Post-O16 V1 mean absolute delta: 4.704752 MeV
Post-O16 V2 mean absolute delta: 1.419584 MeV
Reduction: 69.826592%
```

The strongest V2 region is:

```text
Si-28 through Ca-40
```

With residuals:

```text
Si-28: +0.202549 MeV
S-32:  +0.228493 MeV
Ar-36: +0.186750 MeV
Ca-40: -0.628253 MeV
```

This is a major improvement while leaving the early ladder intact.

---

## 8. Meaning Of The Correction

The V2 result says:

```text
V1 gives the alpha-cluster backbone.
V2 gives post-O16 boundary curvature.
Ne-20 and Mg-24 remain transitional.
Si-28 through Ca-40 become tightly structured.
```

The remaining Ne-20 / Mg-24 residuals are not noise to discard. They are now the next clue. They may mark the transition from the O-16 closed alpha shell into the heavier packed-cluster regime.

That places the current model in a stronger position:

```text
not a final nuclear theory
but a compact generative grammar with a visible correction hierarchy
```

The ladder now has two frozen layers:

```text
V1: alpha closure + Justice boundaries
V2: post-O16 boundary curvature from Be-8 gap scaled by Justice
```

---

## 9. Next Prediction

The next legitimate step is not to retune V2. It is to study the transitional `Ne-20` and `Mg-24` residuals.

Candidate explanations:


```text
onset of shell deformation after O-16
geometric packing transition before Si-28
missing Love stabilization for loose alpha-cluster arrangements
transition from simple alpha-chain geometry into compact cluster geometry
```

The next pass should not change the V2 correction. It should ask why `Ne-20` and `Mg-24` are the transitional outliers while `Si-28` through `Ca-40` tighten.

For now, the clean read is:

```text
The relationship-first bridge is producing a structured alpha-cluster sequence,
and one post-O16 correction brings the heavier alpha-cluster nuclei into a much tighter band.
```
