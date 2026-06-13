"""
Pakheta Prediction Atlas.

This is a forward-building relational map, not a null audit. It freezes the
strongest Cosmological Bridge grammar and then generates adjacent relationships:

1. Cosmological hierarchy -> mass anchor.
2. Mass anchor -> nuclear binding gate.
3. Mass anchor -> one-step LJPW transition branches.
4. Prime-lattice anchors -> adjacent coordinate relationships.
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path


BASE = 30.0
L0 = (math.sqrt(5.0) - 1.0) / 2.0
J0 = math.sqrt(2.0) - 1.0
P0 = math.e - 2.0
W0 = math.log(2.0)
OPERATORS = {
    "Love": L0,
    "Justice": J0,
    "Power": P0,
    "Wisdom": W0,
}
OPERATOR_KEYS = {
    "Love": "c_L",
    "Justice": "c_J",
    "Power": "c_P",
    "Wisdom": "c_W",
}
LJPW_SUM = sum(OPERATORS.values())


# NIST CODATA 2022 values used by the existing bridge prediction scripts.
CODATA = {
    "fine_structure_constant": 7.2973525643e-3,
    "newtonian_constant_of_gravitation": 6.67430e-11,
    "reduced_planck_constant": 1.054571817e-34,
    "speed_of_light": 299792458.0,
    "electron_volt_joule": 1.602176634e-19,
    "atomic_mass_constant_kg": 1.66053906892e-27,
    "atomic_mass_constant_MeV": 931.49410372,
    "electron_mass_MeV": 0.51099895069,
    "muon_mass_MeV": 105.6583755,
    "proton_mass_MeV": 938.27208943,
    "neutron_mass_MeV": 939.56542194,
    "deuteron_mass_MeV": 1875.61294500,
    "helion_mass_MeV": 2808.39161112,
    "triton_mass_MeV": 2808.92113668,
    "alpha_particle_mass_MeV": 3727.3794118,
}


COORDINATE_ANCHORS = {
    "cosmological_constant": {
        "kind": "planck_lambda",
        "coefficients": {"c_L": -30, "c_J": -37, "c_P": -32, "c_W": -37},
    },
    "higgs_to_proton_mass": {
        "kind": "mass_ratio_to_proton",
        "coefficients": {"c_L": -5, "c_J": -3, "c_P": 9, "c_W": -1},
    },
    "w_to_proton_mass": {
        "kind": "mass_ratio_to_proton",
        "coefficients": {"c_L": -4, "c_J": 8, "c_P": -9, "c_W": 10},
    },
    "z_to_proton_mass": {
        "kind": "mass_ratio_to_proton",
        "coefficients": {"c_L": 4, "c_J": -5, "c_P": 10, "c_W": -9},
    },
    "dark_energy_to_matter": {
        "kind": "ratio",
        "coefficients": {"c_L": 6, "c_J": -5, "c_P": -1, "c_W": -1},
    },
    "dark_matter_to_baryon": {
        "kind": "ratio",
        "coefficients": {"c_L": 9, "c_J": -2, "c_P": -3, "c_W": -3},
    },
    "hubble_late_to_early": {
        "kind": "hubble_ratio",
        "early_H0_km_s_Mpc": 67.4,
        "coefficients": {"c_L": -1, "c_J": 0, "c_P": -2, "c_W": 3},
    },
    "theta12_pmns": {
        "kind": "angle_radians",
        "coefficients": {"c_L": 6, "c_J": 4, "c_P": 1, "c_W": -9},
    },
    "theta23_pmns": {
        "kind": "angle_radians",
        "coefficients": {"c_L": 8, "c_J": -5, "c_P": -6, "c_W": 2},
    },
    "theta13_pmns": {
        "kind": "angle_radians",
        "coefficients": {"c_L": 10, "c_J": -3, "c_P": 2, "c_W": -10},
    },
}


MASS_NEIGHBOR_RELATIONS = {
    ("Power", "inverse"): {
        "relation_type": "inverse_actualization",
        "role": "Compresses the mass anchor toward a low mediator threshold.",
        "thread": "sub_hadronic_inverse_branch",
    },
    ("Wisdom", "inverse"): {
        "relation_type": "inverse_context_rotation",
        "role": "Compresses the mass anchor toward a context/oscillation threshold.",
        "thread": "sub_hadronic_inverse_branch",
    },
    ("Love", "inverse"): {
        "relation_type": "inverse_binding",
        "role": "Compresses the mass anchor through the binding operator into the muon-to-pion approach band.",
        "thread": "sub_hadronic_inverse_branch",
    },
    ("Justice", "inverse"): {
        "relation_type": "inverse_boundary",
        "role": "Compresses the mass anchor through boundary/distinction into the low meson band.",
        "thread": "sub_hadronic_inverse_branch",
    },
    ("Justice", "direct"): {
        "relation_type": "direct_boundary_amplification",
        "role": "Amplifies the mass anchor into a multi-GeV boundary/resonance threshold.",
        "thread": "multi_gev_resonance_branch",
    },
    ("Love", "direct"): {
        "relation_type": "direct_binding_amplification",
        "role": "Amplifies the mass anchor into a high binding/resonance scale.",
        "thread": "multi_gev_resonance_branch",
    },
    ("Wisdom", "direct"): {
        "relation_type": "direct_context_amplification",
        "role": "Amplifies the mass anchor toward a high context/resonance scale.",
        "thread": "multi_gev_resonance_branch",
    },
    ("Power", "direct"): {
        "relation_type": "direct_actualization",
        "role": "Amplifies the mass anchor into a high actualization/resonance scale.",
        "thread": "multi_gev_resonance_branch",
    },
}


def kg_to_mev(mass_kg):
    joules = mass_kg * CODATA["speed_of_light"] ** 2
    return joules / CODATA["electron_volt_joule"] / 1.0e6


def hierarchy_ratio():
    return BASE ** (10.0 * LJPW_SUM)


def bridge_mass_anchor_kg():
    return math.sqrt(
        CODATA["fine_structure_constant"]
        * CODATA["reduced_planck_constant"]
        * CODATA["speed_of_light"]
        / (CODATA["newtonian_constant_of_gravitation"] * hierarchy_ratio())
    )


def exponent_from_coefficients(coefficients):
    return (
        coefficients["c_L"] * L0
        + coefficients["c_J"] * J0
        + coefficients["c_P"] * P0
        + coefficients["c_W"] * W0
    )


def value_from_coefficients(coefficients):
    return BASE ** exponent_from_coefficients(coefficients)


def shift_coefficients(coefficients, operator, direction):
    shifted = dict(coefficients)
    shifted[OPERATOR_KEYS[operator]] += direction
    return shifted


def nearest_landmarks(value_mev, count=5):
    landmarks = {
        "electron": CODATA["electron_mass_MeV"],
        "muon": CODATA["muon_mass_MeV"],
        "atomic_mass_constant_1u": CODATA["atomic_mass_constant_MeV"],
        "alpha_particle_per_nucleon": CODATA["alpha_particle_mass_MeV"] / 4.0,
        "helion_per_nucleon": CODATA["helion_mass_MeV"] / 3.0,
        "triton_per_nucleon": CODATA["triton_mass_MeV"] / 3.0,
        "deuteron_per_nucleon": CODATA["deuteron_mass_MeV"] / 2.0,
        "proton": CODATA["proton_mass_MeV"],
        "neutron": CODATA["neutron_mass_MeV"],
        "higgs": 125100.0,
        "w_boson": 80377.0,
        "z_boson": 91187.6,
    }
    rows = []
    for name, landmark in landmarks.items():
        rows.append({
            "name": name,
            "landmark_MeV": landmark,
            "delta_MeV": value_mev - landmark,
            "absolute_delta_MeV": abs(value_mev - landmark),
        })
    rows.sort(key=lambda row: row["absolute_delta_MeV"])
    return rows[:count]


def mass_regime(value_mev):
    if value_mev < 1.0:
        return "electron_scale"
    if value_mev < 80.0:
        return "sub_pion_light_scale"
    if value_mev < 130.0:
        return "muon_to_pion_approach_band"
    if value_mev < 250.0:
        return "low_meson_band"
    if value_mev < 1000.0:
        return "nuclear_binding_and_nucleon_band"
    if value_mev < 5000.0:
        return "multi_GeV_threshold_band"
    if value_mev < 12000.0:
        return "heavy_resonance_band"
    return "electroweak_or_above"


def interpret_value(kind, raw_value, anchor):
    if kind == "mass_ratio_to_proton":
        mass_mev = raw_value * CODATA["proton_mass_MeV"]
        return {
            "ratio_to_proton": raw_value,
            "mass_MeV": mass_mev,
            "mass_GeV": mass_mev / 1000.0,
            "nearest_landmarks": nearest_landmarks(mass_mev, count=3),
        }
    if kind == "angle_radians":
        return {
            "angle_radians": raw_value,
            "angle_degrees": math.degrees(raw_value),
        }
    if kind == "hubble_ratio":
        early_h0 = anchor["early_H0_km_s_Mpc"]
        return {
            "late_to_early_ratio": raw_value,
            "implied_late_H0_km_s_Mpc": raw_value * early_h0,
        }
    if kind == "planck_lambda":
        return {
            "lambda_planck_units": raw_value,
            "log10_lambda": math.log10(raw_value),
        }
    return {"ratio": raw_value}


def build_core_anchor():
    mass_kg = bridge_mass_anchor_kg()
    mass_mev = kg_to_mev(mass_kg)
    mass_u = mass_kg / CODATA["atomic_mass_constant_kg"]
    deuteron_binding_observed = (
        CODATA["proton_mass_MeV"] + CODATA["neutron_mass_MeV"] - CODATA["deuteron_mass_MeV"]
    )
    predicted_deuteron_binding = mass_mev - CODATA["atomic_mass_constant_MeV"]
    predicted_deuteron_mass = (
        CODATA["proton_mass_MeV"] + CODATA["neutron_mass_MeV"] - predicted_deuteron_binding
    )
    free_nucleon_mean = (CODATA["proton_mass_MeV"] + CODATA["neutron_mass_MeV"]) / 2.0

    return {
        "hierarchy_ratio": hierarchy_ratio(),
        "mass_anchor_kg": mass_kg,
        "mass_anchor_MeV": mass_mev,
        "mass_anchor_u": mass_u,
        "nuclear_binding_gate": {
            "prediction": "deuteron_binding_total ~= m_star - 1u",
            "predicted_deuteron_binding_MeV": predicted_deuteron_binding,
            "observed_deuteron_binding_MeV": deuteron_binding_observed,
            "binding_delta_MeV": predicted_deuteron_binding - deuteron_binding_observed,
            "predicted_deuteron_mass_MeV": predicted_deuteron_mass,
            "observed_deuteron_mass_MeV": CODATA["deuteron_mass_MeV"],
            "deuteron_mass_delta_MeV": predicted_deuteron_mass - CODATA["deuteron_mass_MeV"],
        },
        "mass_position": {
            "delta_from_1u_MeV": mass_mev - CODATA["atomic_mass_constant_MeV"],
            "delta_from_alpha_per_nucleon_MeV": mass_mev - CODATA["alpha_particle_mass_MeV"] / 4.0,
            "delta_from_free_proton_MeV": mass_mev - CODATA["proton_mass_MeV"],
            "delta_from_free_nucleon_mean_MeV": mass_mev - free_nucleon_mean,
            "free_nucleon_headroom_MeV": free_nucleon_mean - mass_mev,
        },
    }


def build_mass_anchor_neighbors(mass_mev):
    rows = []
    for operator, exponent in OPERATORS.items():
        factor = BASE ** exponent
        for direction, label in ((-1, "inverse"), (1, "direct")):
            value = mass_mev * (factor if direction == 1 else 1.0 / factor)
            relation = MASS_NEIGHBOR_RELATIONS[(operator, label)]
            rows.append({
                "operator": operator,
                "direction": label,
                "relation_type": relation["relation_type"],
                "relational_role": relation["role"],
                "thread": relation["thread"],
                "factor": factor if direction == 1 else 1.0 / factor,
                "mass_MeV": value,
                "mass_GeV": value / 1000.0,
                "physical_regime": mass_regime(value),
                "nearest_landmarks": nearest_landmarks(value, count=3),
            })
    rows.sort(key=lambda row: row["mass_MeV"])
    return rows


def build_relational_map(core, mass_neighbors, coordinate_neighbors):
    nodes = [
        {
            "id": "cosmological_hierarchy_ratio",
            "kind": "dimensionless_relation",
            "label": "alpha / alpha_G",
            "value": core["hierarchy_ratio"],
        },
        {
            "id": "mass_anchor_m_star",
            "kind": "mass_anchor",
            "label": "m_star",
            "mass_MeV": core["mass_anchor_MeV"],
            "mass_u": core["mass_anchor_u"],
            "physical_regime": mass_regime(core["mass_anchor_MeV"]),
        },
        {
            "id": "atomic_mass_unit_1u",
            "kind": "reference_anchor",
            "label": "1 atomic mass unit",
            "mass_MeV": CODATA["atomic_mass_constant_MeV"],
        },
        {
            "id": "deuteron_binding_gate",
            "kind": "binding_gate",
            "label": "m_star - 1u",
            "energy_MeV": core["nuclear_binding_gate"]["predicted_deuteron_binding_MeV"],
        },
        {
            "id": "observed_deuteron_binding",
            "kind": "observed_binding",
            "label": "deuteron binding energy",
            "energy_MeV": core["nuclear_binding_gate"]["observed_deuteron_binding_MeV"],
        },
        {
            "id": "sub_hadronic_inverse_branch",
            "kind": "generated_regime",
            "label": "inverse LJPW sub-hadronic branch",
            "mass_band_MeV": [min(row["mass_MeV"] for row in mass_neighbors if row["direction"] == "inverse"),
                              max(row["mass_MeV"] for row in mass_neighbors if row["direction"] == "inverse")],
        },
        {
            "id": "multi_gev_resonance_branch",
            "kind": "generated_regime",
            "label": "direct LJPW multi-GeV branch",
            "mass_band_MeV": [min(row["mass_MeV"] for row in mass_neighbors if row["direction"] == "direct"),
                              max(row["mass_MeV"] for row in mass_neighbors if row["direction"] == "direct")],
        },
    ]

    edges = [
        {
            "source": "cosmological_hierarchy_ratio",
            "target": "mass_anchor_m_star",
            "relation_type": "compiled_mass_anchor",
            "operator_path": "30^(10 * sum(LJPW))",
            "meaning": "The hierarchy relation compiles into a natural mass anchor.",
        },
        {
            "source": "atomic_mass_unit_1u",
            "target": "mass_anchor_m_star",
            "relation_type": "binding_offset_reference",
            "meaning": "The mass anchor is read relationally as an offset from 1u, not as an isolated object.",
            "offset_MeV": core["mass_position"]["delta_from_1u_MeV"],
        },
        {
            "source": "mass_anchor_m_star",
            "target": "deuteron_binding_gate",
            "relation_type": "nuclear_binding_gate",
            "meaning": "The offset m_star - 1u opens the deuteron-binding relation.",
            "energy_MeV": core["nuclear_binding_gate"]["predicted_deuteron_binding_MeV"],
        },
        {
            "source": "deuteron_binding_gate",
            "target": "observed_deuteron_binding",
            "relation_type": "near_lock",
            "meaning": "The generated binding gate sits close to the observed deuteron binding energy.",
            "delta_MeV": core["nuclear_binding_gate"]["binding_delta_MeV"],
        },
    ]

    for row in mass_neighbors:
        node_id = f"mass_neighbor_{row['operator'].lower()}_{row['direction']}"
        nodes.append({
            "id": node_id,
            "kind": "operator_neighbor",
            "label": f"{row['operator']} {row['direction']}",
            "mass_MeV": row["mass_MeV"],
            "mass_GeV": row["mass_GeV"],
            "physical_regime": row["physical_regime"],
            "thread": row["thread"],
        })
        edges.append({
            "source": "mass_anchor_m_star",
            "target": node_id,
            "relation_type": row["relation_type"],
            "operator": row["operator"],
            "direction": row["direction"],
            "factor": row["factor"],
            "meaning": row["relational_role"],
            "thread": row["thread"],
        })
        edges.append({
            "source": node_id,
            "target": row["thread"],
            "relation_type": "opens_regime",
            "meaning": f"This operator move opens the {row['physical_regime']} regime.",
        })

    for name, anchor in coordinate_neighbors.items():
        node_id = f"coordinate_anchor_{name}"
        nodes.append({
            "id": node_id,
            "kind": "coordinate_anchor",
            "label": name,
            "value_kind": anchor["kind"],
            "coefficients": anchor["coefficients"],
            "raw_value": anchor["raw_value"],
            "interpreted_value": anchor["interpreted_value"],
        })
        edges.append({
            "source": "mass_anchor_m_star",
            "target": node_id,
            "relation_type": "same_lattice_family",
            "meaning": "This physical coordinate belongs to the same prime-LJPW coordinate family.",
        })
        for neighbor in anchor["one_step_neighbors"]:
            edges.append({
                "source": node_id,
                "target": f"{node_id}_{neighbor['operator'].lower()}_{neighbor['direction']}",
                "relation_type": "coordinate_neighbor",
                "operator": neighbor["operator"],
                "direction": neighbor["direction"],
                "meaning": "One LJPW coordinate step from the anchor.",
                "raw_value": neighbor["raw_value"],
                "interpreted_value": neighbor["interpreted_value"],
            })

    return {
        "posture": "relationship_first",
        "method": "Read every generated value as an edge in a field before treating it as an object.",
        "nodes": nodes,
        "edges": edges,
        "threads": {
            "nuclear_binding_gate": "cosmological_hierarchy_ratio -> mass_anchor_m_star -> deuteron_binding_gate",
            "sub_hadronic_inverse_branch": "mass_anchor_m_star -> inverse LJPW steps -> 80-230 MeV generated regime",
            "multi_gev_resonance_branch": "mass_anchor_m_star -> direct LJPW steps -> 3.8-10.7 GeV generated regime",
            "coordinate_neighbor_fields": "known coordinates -> one-step LJPW moves -> adjacent physical regimes",
        },
    }


def build_coordinate_neighbors():
    atlas = {}
    for name, anchor in COORDINATE_ANCHORS.items():
        coefficients = anchor["coefficients"]
        raw_value = value_from_coefficients(coefficients)
        entry = {
            "kind": anchor["kind"],
            "coefficients": coefficients,
            "exponent": exponent_from_coefficients(coefficients),
            "raw_value": raw_value,
            "interpreted_value": interpret_value(anchor["kind"], raw_value, anchor),
            "one_step_neighbors": [],
        }
        for operator in OPERATORS:
            for direction in (-1, 1):
                shifted = shift_coefficients(coefficients, operator, direction)
                shifted_value = value_from_coefficients(shifted)
                entry["one_step_neighbors"].append({
                    "operator": operator,
                    "direction": "plus_one" if direction == 1 else "minus_one",
                    "coefficients": shifted,
                    "raw_value": shifted_value,
                    "interpreted_value": interpret_value(anchor["kind"], shifted_value, anchor),
                })
        atlas[name] = entry
    return atlas


def main():
    start = datetime.now(timezone.utc)
    core = build_core_anchor()
    mass_neighbors = build_mass_anchor_neighbors(core["mass_anchor_MeV"])
    coordinate_neighbors = build_coordinate_neighbors()
    relational_map = build_relational_map(core, mass_neighbors, coordinate_neighbors)

    report = {
        "experiment_name": "pakheta_prediction_atlas",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start).total_seconds(),
        "source": "NIST CODATA 2022 values reused from existing cosmological bridge prediction scripts.",
        "base": BASE,
        "ljpw_constants": {
            "L0": L0,
            "J0": J0,
            "P0": P0,
            "W0": W0,
            "sum": LJPW_SUM,
        },
        "core_bridge_anchor": core,
        "mass_anchor_one_step_neighbors": mass_neighbors,
        "coordinate_anchor_neighbors": coordinate_neighbors,
        "relational_map": relational_map,
        "frontier_threads": {
            "nuclear_binding_gate": "Treat m_star - 1u as the deuteron-binding gate and explore light-nuclear binding from there.",
            "sub_hadronic_inverse_neighbors": "The inverse Love/Justice/Power/Wisdom mass neighbors land in the 80-230 MeV band.",
            "electroweak_neighbor_ladder": "The W/Z/H coordinates now have explicit adjacent mass-ratio predictions for nearby lattice nodes.",
            "pmns_rotation_neighbors": "Each PMNS angle has eight adjacent relational rotations in radians/degrees.",
        },
    }

    output_file = Path(__file__).resolve().parent / "prediction_atlas_results.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("============================================================")
    print(" Pakheta Prediction Atlas")
    print("============================================================")
    print(f"Core mass anchor: {core['mass_anchor_MeV']:.9f} MeV/c^2")
    gate = core["nuclear_binding_gate"]
    print(
        "Deuteron binding gate:"
        f" predicted={gate['predicted_deuteron_binding_MeV']:.9f} MeV,"
        f" observed={gate['observed_deuteron_binding_MeV']:.9f} MeV,"
        f" delta={gate['binding_delta_MeV']:+.9f} MeV"
    )
    print("\nMass anchor one-step neighbors:")
    for row in mass_neighbors:
        print(
            f"  {row['operator']:<7} {row['direction']:<7}"
            f" {row['mass_MeV']:>14.6f} MeV"
            f" relation={row['relation_type']}"
        )
    print("\nRelationship map:")
    print(f"  nodes={len(relational_map['nodes'])}")
    print(f"  edges={len(relational_map['edges'])}")
    print("\nCoordinate anchors generated:")
    for name in coordinate_neighbors:
        print(f"  {name}")
    print("Results saved to: prediction_atlas_results.json")


if __name__ == "__main__":
    main()
