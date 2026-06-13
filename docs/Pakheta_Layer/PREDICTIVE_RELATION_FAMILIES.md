# Relational Archetypes and Predictive Families

**Date:** June 13, 2026  
**Status:** Completed Experiment  
**Executable Script:** [pakheta_predictive_relation_families.py](../../experiments/pakheta_predictive_relation_families.py)  
**JSON Output:** [predictive_relation_families_results.json](../../experiments/predictive_relation_families_results.json)  

---

## 1. Objective

This experiment moves the Pakheta Relational Coordinate Mathematics framework from a descriptive paradigm ("how does a relation fit?") to a **predictive** one. 

Instead of hand-authoring archetypes, we let cohesive families of mathematical identities define their own relational centroids. We then test whether these derived archetypes are strong enough to:
1. **Retrieve a withheld relation** from the non-exemplar candidate pool drawn from the 240-relation coordinate database (Leave-One-Out relation prediction).
2. **Predict a missing target constant** $B$ given a source anchor $A$ and the family archetype.
3. **Predict a missing source constant** $A$ given a target anchor $B$ and the family archetype.

---

## 2. Methodology & Families

We define four core relational families representing distinct identity sub-fields:

*   **Root Closures:** `one->sqrt2`, `one->sqrt3`, `one->sqrt5` (ratios that close exactly on integers under multiplication).
*   **Circle Scaling:** `pi->tau`, `tau->pi`, `one->two`, `two->one` (doubling and halving transitions).
*   **Golden Harmony:** `one->phi`, `phi_inverse_L0->one`, `phi->phi_squared`, `phi->one`, `one->phi_inverse_L0` (proportional growth, repairs, and inverses).
*   **Natural Growth:** `one->e`, `e->one`, `sqrt2->e`, `sqrt2->ln2_W0` (logarithmic and exponential scaling contexts).

For each relation $R = A \rightarrow B$ in a family:
1. We withhold $R$.
2. We compute the family's **archetype profile** (centroid) by averaging the coordinate profiles of the remaining family members (exemplars).
3. We rank all non-exemplar database relations against the archetype.
4. For the source anchor $A$, we rank all other constants $X \neq A$ for the candidate relation $A \rightarrow X$.
5. For the target anchor $B$, we rank all other constants $Y \neq B$ for the candidate relation $Y \rightarrow B$.

Because the exemplar relations are excluded during leave-one-out testing, the
relation-retrieval candidate pool is slightly smaller than the full 240-relation
database:

```text
candidate pool = 240 - number_of_exemplars
```

This gives candidate pools of 236-238 depending on family size.

---

## 3. Results Summary

### High-Level Metrics
*   **Total Relations in Database:** 240
*   **Total Relationships Evaluated:** 16
*   **Median Relation Retrieval LOO Rank:** 34.0 (median percentile 14.35% of the non-exemplar candidate pool)
*   **Target Prediction Median Rank:** 3.5 / 15
*   **Source Prediction Median Rank:** 3.5 / 15
*   **Target Prediction Rank-1 Accuracy:** 25.00% (4 / 16)
*   **Source Prediction Rank-1 Accuracy:** 37.50% (6 / 16)
*   **Baseline Random Target/Source Rank:** 8.0 (out of 15 candidates)

### Detailed Predictions by Family

| Family & Withheld Relation | Relation Rank (non-exemplar pool) | Target Prediction Rank (of 15) | Source Prediction Rank (of 15) | Top Predicted Target / Source |
| :--- | :---: | :---: | :---: | :--- |
| **Root Closures** | | | | |
| `one->sqrt3` | **3** | **1** | **1** | Target: `sqrt3` (1st), Source: `one` (1st) |
| `one->sqrt5` | 18 | 3 | 4 | Target: `sqrt3` (1st: `sqrt5` is 3rd) |
| `one->sqrt2` | 123 | 8 | 7 | Target: `sqrt3` (1st: `sqrt2` is 8th) |
| **Golden Harmony** | | | | |
| `one->phi` | **1** | **1** | **1** | Target: `phi` (1st), Source: `one` (1st) |
| `phi_inverse_L0->one` | **1** | **1** | **1** | Target: `one` (1st), Source: `phi_inverse_L0` (1st) |
| `phi->phi_squared` | **1** | **1** | **1** | Target: `phi_squared` (1st), Source: `phi` (1st) |
| `one->phi_inverse_L0` | 124 | 8 | 8 | Target: `phi` (1st: `phi_inverse_L0` is 8th) |
| `phi->one` | 124 | 10 | 12 | Target: `phi_squared` (1st: `one` is 10th) |
| **Natural Growth** | | | | |
| `sqrt2->ln2_W0` | 26 | 4 | **1** | Source: `sqrt2` (1st), Target: `e` (1st: `ln2_W0` is 4th) |
| `sqrt2->e` | 63 | 3 | **1** | Source: `sqrt2` (1st), Target: `ln2_W0` (1st: `e` is 3rd) |
| `e->one` | 90 | 4 | 10 | Target: `tau` (1st) |
| `one->e` | 108 | 7 | 6 | Target: `power_P0` (1st) |
| **Circle Scaling** | | | | |
| `pi->tau` | 34 | 4 | 2 | Target: `sqrt2` (1st), Source: `phi` (1st) |
| `tau->pi` | 34 | 2 | 4 | Target: `phi` (1st), Source: `sqrt2` (1st) |
| `one->two` | 34 | 3 | 4 | Target: `power_P0` (1st), Source: `five` (1st) |
| `two->one` | 34 | 4 | 3 | Target: `five` (1st), Source: `power_P0` (1st) |

---

## 4. Key Insights

### 1. Cohort Coherence With Uneven Exact Prediction
The derived archetypes show real clustering, but not uniform exact prediction.
The relation-retrieval median rank is 34.0, which lands at the 14.35th
percentile of the non-exemplar candidate pool. Target/source prediction is
better than the random mean rank of 8.0 in median terms:

```text
target median rank = 3.5 / 15
source median rank = 3.5 / 15
```

The exact rank-1 hit rate is meaningful but still incomplete:

```text
target rank-1 accuracy = 4 / 16
source rank-1 accuracy = 6 / 16
```

So the finding is not "the system predicts every missing constant exactly."
The finding is that family-derived relation profiles pull the correct constants
above random expectation while exposing which identity families need sharper
subdivision.

### 2. Direction Mixture Is A Real Feature
Families that contain both amplifying ($ratio > 1$) and compressing ($ratio <
1$) relations must not be collapsed into an arbitrary single direction. The
experiment now represents archetype direction as a distribution, so mixed
families keep their directional structure.

This improves the result sharply, especially in Golden Harmony:

```text
one -> phi                  relation rank 1
phi_inverse_L0 -> one       relation rank 1
phi -> phi_squared          relation rank 1
```

The remaining weak golden rows are the inverse/compressing members:

```text
phi -> one                  relation rank 124
one -> phi_inverse_L0       relation rank 124
```

**Design Insight:** relational families are highly sensitive to directional
transition vectors. Future prediction models should split sub-families such as
golden growth, golden repair, and golden compression before deriving centroids.

### 3. Local Cross-Anchor Hits
The top predicted source for both natural-growth relations anchored at `sqrt2`
was exactly `sqrt2` (Rank 1). The top predicted target and source for
`one->sqrt3` were exactly `sqrt3` and `one`. The main golden growth/repair
relations also reconstruct exactly at rank 1.

These are genuine exact hits, but they are local successes inside a broader
mixed result. They show that some family centroids are sharp enough to
reconstruct the withheld structure exactly, not that all families already do so.

---

## 5. Conclusion

This experiment supports a narrower and more useful claim: **the relationship
itself can become a predictive instrument**, but the current family grammar is
not yet sufficient for broad exact target/source prediction.

Given a partial relational family, the Pakheta coordinate grammar can often
retrieve the missing relation into a much smaller region of the candidate field,
and it moves target/source constants above random expectation in median rank.
The next mathematical step is to split mixed-direction families and learn
direction-aware sub-archetypes before claiming stronger exact prediction.
