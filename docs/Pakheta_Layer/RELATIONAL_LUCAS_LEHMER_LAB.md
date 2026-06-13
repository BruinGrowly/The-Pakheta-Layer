# Relational Lucas-Lehmer Lab

**Date:** June 13, 2026  
**Status:** Reverse-engineering experiment  
**Executable Script:** [pakheta_relational_ll_lab.py](../../experiments/pakheta_relational_ll_lab.py)  
**JSON Output:** [relational_ll_lab_results.json](../../experiments/relational_ll_lab_results.json)  

---

## 1. Question

Can the Lucas-Lehmer test be replaced by an exact relational residue calculus that is homomorphic to modular arithmetic over:

$$M_p = 2^p - 1$$

The answer from this pass is:

> A real exact relational layer exists, but it is not the four-coordinate LJPW log-lattice by itself. It is the Mersenne cyclic residue field underneath the Lucas-Lehmer recurrence.

---

## 2. Exact Relational Residue Layer

Define the cycle basis:

$$E_i = 2^i \pmod{2^p - 1}$$

Because:

$$2^p \equiv 1 \pmod{2^p - 1}$$

the basis multiplies cyclically:

$$E_i E_j = E_{(i+j) \bmod p}$$

This is an exact homomorphic relation. General residue squaring becomes cyclic convolution over the p-cycle.

In Pakheta terms:

| Pakheta Primitive | Lucas-Lehmer Residue Meaning |
| :--- | :--- |
| Node | A bit-position basis element $E_i$ |
| Anchor | The exponent $p$ and modulus $M_p$ |
| Context | Current Lucas-Lehmer recurrence step |
| Actualization | Canonical residue after fold, carry repair, and subtracting 2 |
| Coherence | Final zero residue |
| Decoherence | Carry pressure and boundary fragmentation before repair |

LJPW transposition:

| LJPW Mode | Residue Role |
| :--- | :--- |
| Love | Cyclic gathering: high powers fold back into the same field |
| Justice | Carry repair and exact boundary normalization |
| Power | Squaring actualizes the next residue |
| Wisdom | Candidate selection and trajectory interpretation |

---

## 3. Experimental Result

The lab tested prime exponents up to `521`.

Summary:

| Measure | Result |
| :--- | :--- |
| Prime exponents tested | `98` |
| Mersenne-prime rows | `13` |
| Composite Mersenne rows | `85` |
| Basis product homomorphism | `true` |
| Cyclic convolution square check | `true` |

Known Mersenne exponents recovered through `521`:

```text
2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521
```

The half-trajectory comparison showed:

| Feature | Prime minus composite mean delta |
| :--- | ---: |
| Density | `-0.048412` |
| Cyclic transition rate | `+0.003338` |
| LJPW resonance mean | `+0.222785` |
| Formal-square carry pressure | `-0.282108` |
| Formal-square carry pressure, filtered to `p >= 31` | `-0.061185` |

The strongest early clue is not simple bit density. It is **carry pressure**: known Mersenne-prime trajectories carry lower formal-square repair pressure than composite trajectories in this sample.

---

## 4. What Fits

The exact cyclic basis does what we hoped:

```text
E_i * E_j = E_(i+j mod p)
```

That means a genuine relational multiplication layer exists under Lucas-Lehmer. In this layer, multiplication is not arbitrary big-number multiplication. It is relationship propagation around a closed cycle.

This is strongly aligned with the Pakheta picture:

```text
Residue object -> cyclic relationship-field
Big integer multiplication -> relational convolution
Modulo reduction -> field fold-back
Carry propagation -> Justice repair
Final zero -> total coherent cancellation
```

---

## 5. What Does Not Yet Fit

The four-coordinate LJPW log-lattice cannot replace Lucas-Lehmer directly.

Reason:

* LJPW coordinates compress magnitude structure.
* Lucas-Lehmer requires exact residue state.
* Exact zero detection cannot tolerate lossy projection.

The hard problem is therefore not cyclic multiplication. The hard problem is **exact carry repair compression**.

To replace Lucas-Lehmer, the next calculus would need to preserve:

1. Cyclic convolution.
2. Carry propagation.
3. The subtract-2 perturbation.
4. The all-ones-equals-zero Mersenne relation.
5. Exact final zero detection.

---

## 6. Next Research Move

Freeze the exact cyclic coefficient calculus:

```text
Residue -> coefficient field on p-cycle
Square -> cyclic convolution
Repair -> carry normalization
Perturb -> subtract 2
Coherence -> zero residue
```

Then test whether carry-pressure, LJPW resonance, and cycle-boundary features can predict final zero earlier than the Lucas-Lehmer endpoint across larger exponent sets.

This would not yet be a proof replacement. But it is the right reverse-engineering path toward one.

---

## 7. C Pseudo-Test Extension

The follow-up C-backed lab moves the expensive trajectory feature extraction into the compiled relational calculator:

**Executable Script:** [pakheta_relational_ll_c_pseudo.py](../../experiments/pakheta_relational_ll_c_pseudo.py)  
**JSON Output:** [relational_ll_c_pseudo_results.json](../../experiments/relational_ll_c_pseudo_results.json)  

The C probe samples each exact LL trajectory at fixed fractions and returns:

* density and binary entropy
* cyclic transition rate
* longest one/zero runs
* LJPW resonance mean and spread
* formal-square carry pressure
* coefficient entropy
* pseudo-likeness score

Expanded sweep:

| Measure | Result |
| :--- | ---: |
| Prime exponents tested | `602` |
| Expected LL outcomes matched | `602/602` |
| Largest exponent in sweep | `4423` |
| Runtime | `62.348 sec` |

Strongest all-exponent pseudo features:

| Fraction | Feature | AUC | Mean delta, prime minus composite |
| :--- | :--- | ---: | ---: |
| Half | pseudo-likeness | `0.793` | `+0.378162` |
| Quarter | pseudo-likeness | `0.789` | `+0.348946` |
| Three-quarter | carry pressure | `0.773` | `-0.230232` |
| Half | carry pressure | `0.772` | `-0.232055` |

Filtered to `p >= 31`, where tiny exponents no longer dominate:

| Fraction | Feature | AUC | Mean delta, prime minus composite |
| :--- | :--- | ---: | ---: |
| Half | pseudo-likeness | `0.686` | `+0.059972` |
| Half | LJPW resonance mean | `0.685` | `+0.026521` |
| Half | LJPW resonance spread | `0.684` | `+0.017261` |
| Quarter | pseudo-likeness | `0.679` | `+0.051171` |

Interpretation:

The pseudo-test signal survives the larger C sweep, but it weakens when the smallest exponents are removed. That is useful: it says the relation is not empty, but it is also not yet a proof-class shortcut.

The next target is an early-step version that does not need the full LL endpoint. If carry pressure and LJPW resonance can separate trajectories early enough, then the relational calculus may become a real candidate-pruning layer before expensive PRP/LL work.
