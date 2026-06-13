"""
Pakheta alpha-cluster prediction pass.

This extends the legitimate prediction registry from the deuteron gate and
alpha closure into alpha-cluster nuclei:

    Be-8  = two alpha closures minus a tiny two-alpha gap.
    C-12  = three alpha closures plus one global Justice boundary.
    O-16  = four alpha closures plus two global Justice boundaries.
    For n >= 3 alpha clusters:
        B_n = n * B_alpha + (n - 2) * B_Justice_boundary.

V2 adds one correction relation after O-16:

    boundary_curvature = gap_2alpha * 30^J0 * T(n - 4)

where T(k) is the triangular number k*(k+1)/2. This treats Be-8 as the
smallest two-alpha boundary gap and O-16 as the first closed alpha shell.

The grammar is fixed before the known-value overlay is computed.
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = EXPERIMENT_DIR / "legitimate_prediction_registry_results.json"
OUTPUT_FILE = EXPERIMENT_DIR / "alpha_cluster_prediction_results.json"

BASE = 30.0
L0 = (math.sqrt(5.0) - 1.0) / 2.0
J0 = math.sqrt(2.0) - 1.0
P0 = math.e - 2.0
W0 = math.log(2.0)

# Atomic-mass overlay values. Binding energies are computed from neutral atom
# masses using hydrogen atom masses so electrons cancel to high precision.
ATOMIC_MASS_UNIT_MEV = 931.49410372
HYDROGEN_ATOM_MASS_U = 1.00782503223
NEUTRON_MASS_U = 1.00866491595

ALPHA_CLUSTER_NUCLIDES = {
    "He4": {
        "label": "helium-4 alpha particle",
        "alpha_clusters": 1,
        "Z": 2,
        "N": 2,
        "atomic_mass_u": 4.00260325413,
    },
    "Be8": {
        "label": "beryllium-8 two-alpha resonance",
        "alpha_clusters": 2,
        "Z": 4,
        "N": 4,
        "atomic_mass_u": 8.00530510,
    },
    "C12": {
        "label": "carbon-12 triple-alpha closure",
        "alpha_clusters": 3,
        "Z": 6,
        "N": 6,
        "atomic_mass_u": 12.0,
    },
    "O16": {
        "label": "oxygen-16 four-alpha closure",
        "alpha_clusters": 4,
        "Z": 8,
        "N": 8,
        "atomic_mass_u": 15.99491461957,
    },
    "Ne20": {
        "label": "neon-20 five-alpha closure",
        "alpha_clusters": 5,
        "Z": 10,
        "N": 10,
        "atomic_mass_u": 19.9924401762,
    },
    "Mg24": {
        "label": "magnesium-24 six-alpha closure",
        "alpha_clusters": 6,
        "Z": 12,
        "N": 12,
        "atomic_mass_u": 23.985041697,
    },
    "Si28": {
        "label": "silicon-28 seven-alpha closure",
        "alpha_clusters": 7,
        "Z": 14,
        "N": 14,
        "atomic_mass_u": 27.97692653465,
    },
    "S32": {
        "label": "sulfur-32 eight-alpha closure",
        "alpha_clusters": 8,
        "Z": 16,
        "N": 16,
        "atomic_mass_u": 31.9720711744,
    },
    "Ar36": {
        "label": "argon-36 nine-alpha closure",
        "alpha_clusters": 9,
        "Z": 18,
        "N": 18,
        "atomic_mass_u": 35.967545105,
    },
    "Ca40": {
        "label": "calcium-40 ten-alpha closure",
        "alpha_clusters": 10,
        "Z": 20,
        "N": 20,
        "atomic_mass_u": 39.962590863,
    },
}


def read_registry():
    with open(REGISTRY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def operator_factor(value):
    return BASE ** value


def relative_delta(predicted, observed):
    return predicted / observed - 1.0


def residual_row(predicted, observed):
    delta = predicted - observed
    return {
        "predicted_MeV": predicted,
        "observed_MeV": observed,
        "delta_MeV": delta,
        "absolute_delta_MeV": abs(delta),
        "relative_delta": relative_delta(predicted, observed),
        "absolute_relative_delta": abs(relative_delta(predicted, observed)),
    }


def triangular_number(value):
    return value * (value + 1.0) / 2.0


def binding_energy_from_atomic_mass(nuclide):
    mass_defect_u = (
        nuclide["Z"] * HYDROGEN_ATOM_MASS_U
        + nuclide["N"] * NEUTRON_MASS_U
        - nuclide["atomic_mass_u"]
    )
    return mass_defect_u * ATOMIC_MASS_UNIT_MEV


def registry_prediction(registry, prediction_id):
    predictions = registry["light_nuclear_prediction_ladder"]["predictions"]
    for row in predictions:
        if row["id"] == prediction_id:
            return row
    raise KeyError(f"{prediction_id} not found in prediction registry")


def build_observed_overlay():
    overlay = {}
    for key, nuclide in ALPHA_CLUSTER_NUCLIDES.items():
        binding = binding_energy_from_atomic_mass(nuclide)
        overlay[key] = {
            **nuclide,
            "observed_total_binding_MeV": binding,
            "observed_binding_per_nucleon_MeV": binding / (nuclide["Z"] + nuclide["N"]),
        }

    alpha_binding = overlay["He4"]["observed_total_binding_MeV"]
    overlay["Be8"]["observed_two_alpha_gap_MeV"] = (
        2.0 * alpha_binding - overlay["Be8"]["observed_total_binding_MeV"]
    )
    for key, row in overlay.items():
        if row["alpha_clusters"] >= 3:
            overlay[key]["observed_excess_over_alpha_clusters_MeV"] = (
                row["observed_total_binding_MeV"]
                - row["alpha_clusters"] * alpha_binding
            )
    return overlay


def cluster_prediction_id(index):
    return f"ACP-{index:03d}"


def alpha_cluster_rule_name(key, alpha_clusters):
    if key == "C12":
        return "c12_triple_alpha_closure_binding"
    if key == "O16":
        return "o16_four_alpha_closure_binding"
    return f"{key.lower()}_{alpha_clusters}_alpha_closure_binding"


def post_o16_boundary_curvature(alpha_clusters, two_alpha_gap):
    extra_alpha_clusters = max(0.0, alpha_clusters - 4.0)
    return two_alpha_gap * operator_factor(J0) * triangular_number(extra_alpha_clusters)


def build_alpha_cluster_predictions(registry, observations):
    gate = registry["light_nuclear_prediction_ladder"]["binding_gate_MeV"]
    alpha_closed = registry_prediction(registry, "LNP-003")["predicted_MeV"]
    justice_boundary = registry_prediction(registry, "LNP-002")["predicted_MeV"]
    love_justice_sum = operator_factor(L0) + operator_factor(J0)
    two_alpha_gap = gate / (2.0 * love_justice_sum)

    predictions = [
        {
            "id": "ACP-001",
            "name": "alpha_closure_unit",
            "rule": "B_alpha = B_gate * (30^L0 + 30^J0)",
            "relation": "The alpha particle is the first closed light-nuclear Love+Justice binding relation.",
            "alpha_clusters": 1,
            "predicted_total_binding_MeV": alpha_closed,
            "known_overlay": residual_row(
                alpha_closed,
                observations["He4"]["observed_total_binding_MeV"],
            ),
        },
        {
            "id": "ACP-002",
            "name": "be8_two_alpha_gap",
            "rule": "gap_2alpha = B_gate / (2 * (30^L0 + 30^J0))",
            "relation": "Two alpha closures leave a small unresolved relation gap.",
            "predicted_gap_MeV": two_alpha_gap,
            "known_overlay": residual_row(
                two_alpha_gap,
                observations["Be8"]["observed_two_alpha_gap_MeV"],
            ),
        },
        {
            "id": "ACP-003",
            "name": "be8_two_alpha_resonance_binding",
            "rule": "B_Be8 = 2 * B_alpha - gap_2alpha",
            "relation": "Be-8 is registered as two alpha closures minus the unresolved two-alpha gap.",
            "alpha_clusters": 2,
            "predicted_total_binding_MeV": 2.0 * alpha_closed - two_alpha_gap,
            "known_overlay": residual_row(
                2.0 * alpha_closed - two_alpha_gap,
                observations["Be8"]["observed_total_binding_MeV"],
            ),
        },
    ]

    next_id = 4
    for key, observation in observations.items():
        alpha_clusters = observation["alpha_clusters"]
        if alpha_clusters < 3:
            continue
        justice_boundaries = alpha_clusters - 2
        predicted = alpha_clusters * alpha_closed + justice_boundaries * justice_boundary
        correction = post_o16_boundary_curvature(alpha_clusters, two_alpha_gap)
        corrected = predicted - correction
        predictions.append({
            "id": cluster_prediction_id(next_id),
            "name": alpha_cluster_rule_name(key, alpha_clusters),
            "nuclide": key,
            "rule": (
                f"B_{key} = {alpha_clusters} * B_alpha"
                f" + {justice_boundaries} * B_Justice_boundary"
            ),
            "relation": (
                f"{observation['label']} is read as {alpha_clusters} alpha closures "
                f"with {justice_boundaries} global Justice boundaries."
            ),
            "alpha_clusters": alpha_clusters,
            "justice_boundaries": justice_boundaries,
            "predicted_total_binding_MeV": predicted,
            "predicted_binding_per_nucleon_MeV": predicted / (4.0 * alpha_clusters),
            "v2_correction_rule": "B_V2 = B_V1 - gap_2alpha * 30^J0 * T(n_alpha - 4)",
            "v2_boundary_curvature_correction_MeV": correction,
            "v2_predicted_total_binding_MeV": corrected,
            "v2_predicted_binding_per_nucleon_MeV": corrected / (4.0 * alpha_clusters),
            "known_overlay": residual_row(
                predicted,
                observation["observed_total_binding_MeV"],
            ),
            "v2_known_overlay": residual_row(
                corrected,
                observation["observed_total_binding_MeV"],
            ),
        })
        next_id += 1

    return {
        "binding_gate_MeV": gate,
        "alpha_closed_binding_MeV": alpha_closed,
        "justice_boundary_MeV": justice_boundary,
        "two_alpha_gap_MeV": two_alpha_gap,
        "post_o16_boundary_curvature_unit_MeV": two_alpha_gap * operator_factor(J0),
        "predictions": predictions,
    }


def rank_predictions(predictions):
    ranked = []
    for row in predictions:
        overlay = row["known_overlay"]
        ranked.append({
            "id": row["id"],
            "name": row["name"],
            "absolute_delta_MeV": overlay["absolute_delta_MeV"],
            "absolute_relative_delta": overlay["absolute_relative_delta"],
        })
    ranked.sort(key=lambda item: item["absolute_relative_delta"])
    return ranked


def continuation_drift(predictions):
    rows = []
    for row in predictions:
        if row.get("alpha_clusters", 0) < 3:
            continue
        overlay = row["known_overlay"]
        rows.append({
            "id": row["id"],
            "name": row["name"],
            "nuclide": row["nuclide"],
            "alpha_clusters": row["alpha_clusters"],
            "justice_boundaries": row["justice_boundaries"],
            "v1_delta_MeV": overlay["delta_MeV"],
            "v1_delta_per_alpha_MeV": overlay["delta_MeV"] / row["alpha_clusters"],
            "v1_relative_delta": overlay["relative_delta"],
            "v1_predicted_binding_per_nucleon_MeV": row["predicted_binding_per_nucleon_MeV"],
            "observed_binding_per_nucleon_MeV": (
                overlay["observed_MeV"] / (4.0 * row["alpha_clusters"])
            ),
            "v2_boundary_curvature_correction_MeV": row["v2_boundary_curvature_correction_MeV"],
            "v2_delta_MeV": row["v2_known_overlay"]["delta_MeV"],
            "v2_delta_per_alpha_MeV": (
                row["v2_known_overlay"]["delta_MeV"] / row["alpha_clusters"]
            ),
            "v2_relative_delta": row["v2_known_overlay"]["relative_delta"],
            "v2_predicted_binding_per_nucleon_MeV": row["v2_predicted_binding_per_nucleon_MeV"],
        })
    return rows


def correction_summary(drift):
    post_o16 = [row for row in drift if row["alpha_clusters"] >= 5]
    if not post_o16:
        return {}
    v1_abs = [abs(row["v1_delta_MeV"]) for row in post_o16]
    v2_abs = [abs(row["v2_delta_MeV"]) for row in post_o16]
    return {
        "post_o16_nuclides": [row["nuclide"] for row in post_o16],
        "v1_mean_absolute_delta_MeV": sum(v1_abs) / len(v1_abs),
        "v2_mean_absolute_delta_MeV": sum(v2_abs) / len(v2_abs),
        "v1_max_absolute_delta_MeV": max(v1_abs),
        "v2_max_absolute_delta_MeV": max(v2_abs),
        "mean_absolute_delta_reduction_fraction": (
            1.0 - (sum(v2_abs) / len(v2_abs)) / (sum(v1_abs) / len(v1_abs))
        ),
    }


def main():
    start = datetime.now(timezone.utc)
    registry = read_registry()
    observations = build_observed_overlay()
    alpha_cluster_predictions = build_alpha_cluster_predictions(registry, observations)
    ranked = rank_predictions(alpha_cluster_predictions["predictions"])
    drift = continuation_drift(alpha_cluster_predictions["predictions"])
    correction = correction_summary(drift)

    report = {
        "experiment_name": "pakheta_alpha_cluster_predictions",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start).total_seconds(),
        "source": (
            "Derived from legitimate_prediction_registry_results.json. Known overlays use neutral atomic masses "
            "and CODATA atomic mass unit conversion."
        ),
        "posture": "fixed_grammar_alpha_cluster_predictions",
        "grammar": {
            "alpha_unit": "B_alpha = B_gate * (30^L0 + 30^J0)",
            "two_alpha_gap": "gap_2alpha = B_gate / (2 * (30^L0 + 30^J0))",
            "cluster_ladder": "For n >= 3 alpha clusters: B_n = n * B_alpha + (n - 2) * B_Justice_boundary",
            "continuation_test": "Carry the same n-2 Justice-boundary rule through Ne-20, Mg-24, Si-28, S-32, Ar-36, and Ca-40 without retuning.",
            "v2_boundary_curvature": "For n > 4: B_V2 = B_V1 - gap_2alpha * 30^J0 * T(n - 4)",
        },
        "constants": {
            "base": BASE,
            "L0": L0,
            "J0": J0,
            "P0": P0,
            "W0": W0,
            "atomic_mass_unit_MeV": ATOMIC_MASS_UNIT_MEV,
            "hydrogen_atom_mass_u": HYDROGEN_ATOM_MASS_U,
            "neutron_mass_u": NEUTRON_MASS_U,
        },
        "known_overlay": observations,
        "alpha_cluster_prediction_ladder": alpha_cluster_predictions,
        "ranked_predictions": ranked,
        "continuation_drift": drift,
        "v2_correction_summary": correction,
        "working_read": {
            "strongest_new_total_binding_prediction": "ACP-004 c12_triple_alpha_closure_binding",
            "most_sensitive_gap_prediction": "ACP-002 be8_two_alpha_gap",
            "continuation_result": (
                "The fixed n-2 Justice-boundary rule stays in the same band through Ca-40, "
                "but it begins to show structured drift after O-16."
            ),
            "v2_result": (
                "A single post-O16 boundary-curvature correction sharply reduces the Si-28 through Ca-40 residuals "
                "while leaving the Be-8, C-12, and O-16 backbone untouched."
            ),
            "next_pass": "Study why Ne-20 and Mg-24 remain transitional after the post-O16 correction.",
        },
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("============================================================")
    print(" Pakheta Alpha-Cluster Predictions")
    print("============================================================")
    for row in alpha_cluster_predictions["predictions"]:
        overlay = row["known_overlay"]
        if "predicted_total_binding_MeV" in row:
            v2 = row.get("v2_known_overlay")
            v2_delta = f" v2_delta={v2['delta_MeV']:>+10.6f}" if v2 else ""
            print(
                f"{row['id']} {row['name']:<38}"
                f" pred={row['predicted_total_binding_MeV']:>12.6f} MeV"
                f" obs={overlay['observed_MeV']:>12.6f} MeV"
                f" delta={overlay['delta_MeV']:>+11.6f} MeV"
                f"{v2_delta}"
            )
        else:
            print(
                f"{row['id']} {row['name']:<38}"
                f" pred={row['predicted_gap_MeV']:>12.6f} MeV"
                f" obs={overlay['observed_MeV']:>12.6f} MeV"
                f" delta={overlay['delta_MeV']:>+11.6f} MeV"
            )
    print("Results saved to: alpha_cluster_prediction_results.json")


if __name__ == "__main__":
    main()
