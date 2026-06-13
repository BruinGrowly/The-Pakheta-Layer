"""
Pakheta Transition Atlas.

This is the second constructive layer after the Prediction Atlas. It reads the
relationship-first prediction output and organizes it as transition families:

1. The nuclear binding chain opened by the cosmological mass anchor.
2. Inverse LJPW compression branches below the mass anchor.
3. Direct LJPW amplification branches above the mass anchor.
4. Coordinate-field transitions around PMNS, electroweak, and cosmic anchors.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
PREDICTION_FILE = EXPERIMENT_DIR / "prediction_atlas_results.json"
OUTPUT_FILE = EXPERIMENT_DIR / "transition_atlas_results.json"

ELECTROWEAK_ANCHORS = [
    "w_to_proton_mass",
    "z_to_proton_mass",
    "higgs_to_proton_mass",
]

PMNS_ANCHORS = [
    "theta12_pmns",
    "theta23_pmns",
    "theta13_pmns",
]

COSMIC_PHASE_ANCHORS = [
    "cosmological_constant",
    "dark_energy_to_matter",
    "dark_matter_to_baryon",
    "hubble_late_to_early",
]


def read_prediction_atlas():
    with open(PREDICTION_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def interpreted_scalar(interpreted):
    if "mass_GeV" in interpreted:
        return "mass_GeV", interpreted["mass_GeV"]
    if "angle_degrees" in interpreted:
        return "angle_degrees", interpreted["angle_degrees"]
    if "implied_late_H0_km_s_Mpc" in interpreted:
        return "implied_late_H0_km_s_Mpc", interpreted["implied_late_H0_km_s_Mpc"]
    if "log10_lambda" in interpreted:
        return "log10_lambda", interpreted["log10_lambda"]
    if "ratio" in interpreted:
        return "ratio", interpreted["ratio"]
    if "late_to_early_ratio" in interpreted:
        return "late_to_early_ratio", interpreted["late_to_early_ratio"]
    if "ratio_to_proton" in interpreted:
        return "ratio_to_proton", interpreted["ratio_to_proton"]
    return "raw_value", None


def scalar_envelope(anchor):
    base_label, base_value = interpreted_scalar(anchor["interpreted_value"])
    values = []
    operator_steps = []

    for neighbor in anchor["one_step_neighbors"]:
        label, value = interpreted_scalar(neighbor["interpreted_value"])
        if value is not None:
            values.append(value)
        operator_steps.append({
            "operator": neighbor["operator"],
            "direction": neighbor["direction"],
            "coefficients": neighbor["coefficients"],
            "scalar_label": label,
            "scalar_value": value,
            "raw_value": neighbor["raw_value"],
            "interpreted_value": neighbor["interpreted_value"],
        })

    return {
        "base_scalar_label": base_label,
        "base_scalar_value": base_value,
        "neighbor_min": min(values) if values else None,
        "neighbor_max": max(values) if values else None,
        "neighbor_count": len(anchor["one_step_neighbors"]),
        "operator_steps": operator_steps,
    }


def build_binding_transitions(core):
    gate = core["nuclear_binding_gate"]
    position = core["mass_position"]
    observed = gate["observed_deuteron_binding_MeV"]
    delta = gate["binding_delta_MeV"]
    relative_delta = delta / observed if observed else None

    return {
        "transition_family": "nuclear_binding_chain",
        "read_as": "A hierarchy relation compiles into a mass anchor, then the mass anchor opens a binding offset.",
        "chain": [
            {
                "name": "hierarchy_to_mass_anchor",
                "source": "R_LJPW = 30^(10 * sum(LJPW))",
                "target": "m_star",
                "relation": "compiled_mass_anchor",
                "value_MeV": core["mass_anchor_MeV"],
                "value_u": core["mass_anchor_u"],
            },
            {
                "name": "mass_anchor_to_one_u_offset",
                "source": "m_star",
                "target": "m_star - 1u",
                "relation": "binding_offset_reference",
                "value_MeV": position["delta_from_1u_MeV"],
            },
            {
                "name": "offset_to_deuteron_binding_gate",
                "source": "m_star - 1u",
                "target": "predicted_deuteron_binding",
                "relation": "nuclear_binding_gate",
                "value_MeV": gate["predicted_deuteron_binding_MeV"],
            },
            {
                "name": "binding_gate_to_observed_deuteron_binding",
                "source": "predicted_deuteron_binding",
                "target": "observed_deuteron_binding",
                "relation": "near_lock",
                "observed_MeV": observed,
                "delta_MeV": delta,
                "relative_delta": relative_delta,
            },
        ],
        "constructive_next_step": (
            "Build a light-nuclear ladder that treats m_star - 1u as the first binding gate "
            "and asks whether deuteron, triton, helion, and alpha offsets share a transition grammar."
        ),
    }


def build_mass_transition(row):
    if row["direction"] == "inverse":
        question = (
            "What low-energy mediator, lepton/meson threshold, or oscillation gate sits on this "
            "operator-compressed branch?"
        )
    else:
        question = (
            "What resonance, threshold, or bound-state family sits on this operator-amplified branch?"
        )

    return {
        "operator": row["operator"],
        "direction": row["direction"],
        "relation_type": row["relation_type"],
        "relational_role": row["relational_role"],
        "thread": row["thread"],
        "factor": row["factor"],
        "mass_MeV": row["mass_MeV"],
        "mass_GeV": row["mass_GeV"],
        "physical_regime": row["physical_regime"],
        "nearest_landmarks": row["nearest_landmarks"],
        "transition_question": question,
    }


def build_mass_transition_families(mass_neighbors):
    compression = [
        build_mass_transition(row)
        for row in mass_neighbors
        if row["direction"] == "inverse"
    ]
    amplification = [
        build_mass_transition(row)
        for row in mass_neighbors
        if row["direction"] == "direct"
    ]

    return {
        "compression_transitions": {
            "transition_family": "inverse_operator_compression",
            "read_as": "The mass anchor is compressed by one inverse LJPW step into low-energy threshold bands.",
            "mass_band_MeV": [
                min(row["mass_MeV"] for row in compression),
                max(row["mass_MeV"] for row in compression),
            ],
            "transitions": compression,
        },
        "amplification_transitions": {
            "transition_family": "direct_operator_amplification",
            "read_as": "The mass anchor is amplified by one direct LJPW step into multi-GeV threshold bands.",
            "mass_band_MeV": [
                min(row["mass_MeV"] for row in amplification),
                max(row["mass_MeV"] for row in amplification),
            ],
            "transitions": amplification,
        },
    }


def summarize_coordinate_anchor(name, anchor, transition_reading):
    envelope = scalar_envelope(anchor)
    return {
        "anchor": name,
        "kind": anchor["kind"],
        "coefficients": anchor["coefficients"],
        "base_raw_value": anchor["raw_value"],
        "base_interpreted_value": anchor["interpreted_value"],
        "transition_reading": transition_reading,
        "neighbor_count": envelope["neighbor_count"],
        "scalar_label": envelope["base_scalar_label"],
        "base_scalar_value": envelope["base_scalar_value"],
        "one_step_neighbor_min": envelope["neighbor_min"],
        "one_step_neighbor_max": envelope["neighbor_max"],
        "operator_steps": envelope["operator_steps"],
    }


def build_coordinate_field_transitions(coordinate_neighbors):
    all_fields = []
    for name, anchor in coordinate_neighbors.items():
        all_fields.append(summarize_coordinate_anchor(
            name,
            anchor,
            "A fixed physical coordinate becomes a local field when each LJPW operator is stepped by +/- 1.",
        ))

    pmns = [
        summarize_coordinate_anchor(
            name,
            coordinate_neighbors[name],
            "A neutrino mixing angle is read as a relational rotation with adjacent rotation states.",
        )
        for name in PMNS_ANCHORS
    ]

    electroweak = [
        summarize_coordinate_anchor(
            name,
            coordinate_neighbors[name],
            "An electroweak mass coordinate is read as a proton-relative mass ladder with adjacent thresholds.",
        )
        for name in ELECTROWEAK_ANCHORS
    ]

    cosmic = [
        summarize_coordinate_anchor(
            name,
            coordinate_neighbors[name],
            "A cosmological coordinate is read as a phase relation with adjacent cosmic-scale states.",
        )
        for name in COSMIC_PHASE_ANCHORS
    ]

    return {
        "coordinate_field_transitions": {
            "transition_family": "one_step_coordinate_fields",
            "read_as": "Every known coordinate is treated as a local relationship field before naming possible objects.",
            "anchor_count": len(all_fields),
            "fields": all_fields,
        },
        "mixing_transitions": {
            "transition_family": "pmns_rotation_field",
            "read_as": "PMNS angles form a rotation field; the generated neighbors are adjacent relational rotations.",
            "anchors": pmns,
        },
        "electroweak_transitions": {
            "transition_family": "electroweak_neighbor_ladder",
            "read_as": "W, Z, and Higgs coordinates become a proton-relative neighbor ladder.",
            "anchors": electroweak,
        },
        "cosmological_phase_transitions": {
            "transition_family": "cosmic_phase_coordinate_field",
            "read_as": "Cosmological constant, energy-budget, and Hubble coordinates become adjacent phase relations.",
            "anchors": cosmic,
        },
    }


def build_threads_to_follow(binding, mass_families, coordinate_families):
    return {
        "nuclear_binding_ladder": {
            "starting_relation": "m_star - 1u ~= deuteron binding",
            "why_it_points": "The bridge does not merely land near a nucleon mass; its offset opens the deuteron binding gate.",
            "next_constructive_test": binding["constructive_next_step"],
            "first_outputs_to_generate": [
                "deuteron binding gate residual",
                "triton/helion per-nucleon offset comparison",
                "alpha per-nucleon binding relation",
            ],
        },
        "sub_hadronic_inverse_branch": {
            "starting_relation": "m_star / 30^operator",
            "why_it_points": "The inverse branch is compact and lands in a shared low-energy band rather than scattering everywhere.",
            "mass_band_MeV": mass_families["compression_transitions"]["mass_band_MeV"],
            "next_constructive_test": "Build a low-energy threshold atlas for lepton, pion, muon, and meson-adjacent scales.",
        },
        "multi_gev_resonance_branch": {
            "starting_relation": "m_star * 30^operator",
            "why_it_points": "The direct branch opens a separate multi-GeV amplification family.",
            "mass_band_MeV": mass_families["amplification_transitions"]["mass_band_MeV"],
            "next_constructive_test": "Compare direct branch ordering against known resonance and heavy-flavor threshold families.",
        },
        "pmns_rotation_field": {
            "starting_relation": "theta_ij PMNS coordinates +/- one LJPW step",
            "why_it_points": "The mixing anchors become local angle fields, not isolated fitted numbers.",
            "anchor_count": len(coordinate_families["mixing_transitions"]["anchors"]),
            "next_constructive_test": "Map one-step PMNS neighbors into possible rotation sum rules and angle hierarchy relations.",
        },
        "electroweak_neighbor_ladder": {
            "starting_relation": "W/Z/H proton-relative mass coordinates +/- one LJPW step",
            "why_it_points": "The electroweak anchors now have generated adjacent mass thresholds.",
            "anchor_count": len(coordinate_families["electroweak_transitions"]["anchors"]),
            "next_constructive_test": "Build a proton-relative electroweak ladder and ask which adjacent thresholds are physically meaningful.",
        },
        "cosmic_phase_coordinate_field": {
            "starting_relation": "cosmic phase coordinates +/- one LJPW step",
            "why_it_points": "Cosmological constant, energy budget, and Hubble ratio anchors sit in one transition family.",
            "anchor_count": len(coordinate_families["cosmological_phase_transitions"]["anchors"]),
            "next_constructive_test": "Build a cosmic phase atlas that follows how Lambda, matter ratios, and H0 relation shift together.",
        },
    }


def build_transition_map(binding, mass_families, coordinate_families, threads):
    nodes = [
        {"id": "transition_atlas", "kind": "atlas", "label": "Pakheta transition atlas"},
        {"id": "nuclear_binding_chain", "kind": "transition_family", "label": "nuclear binding chain"},
        {"id": "inverse_operator_compression", "kind": "transition_family", "label": "inverse operator compression"},
        {"id": "direct_operator_amplification", "kind": "transition_family", "label": "direct operator amplification"},
        {"id": "one_step_coordinate_fields", "kind": "transition_family", "label": "one-step coordinate fields"},
    ]
    edges = [
        {
            "source": "transition_atlas",
            "target": "nuclear_binding_chain",
            "relation_type": "opens_binding_transition",
        },
        {
            "source": "transition_atlas",
            "target": "inverse_operator_compression",
            "relation_type": "opens_compression_transition",
        },
        {
            "source": "transition_atlas",
            "target": "direct_operator_amplification",
            "relation_type": "opens_amplification_transition",
        },
        {
            "source": "transition_atlas",
            "target": "one_step_coordinate_fields",
            "relation_type": "opens_coordinate_field_transition",
        },
    ]

    previous = "nuclear_binding_chain"
    for step in binding["chain"]:
        node_id = f"binding_step_{step['name']}"
        nodes.append({
            "id": node_id,
            "kind": "binding_step",
            "label": step["name"],
            "relation": step["relation"],
        })
        edges.append({
            "source": previous,
            "target": node_id,
            "relation_type": step["relation"],
        })
        previous = node_id

    for family_key, root_id in [
        ("compression_transitions", "inverse_operator_compression"),
        ("amplification_transitions", "direct_operator_amplification"),
    ]:
        for row in mass_families[family_key]["transitions"]:
            node_id = f"{root_id}_{row['operator'].lower()}"
            nodes.append({
                "id": node_id,
                "kind": "mass_transition",
                "label": f"{row['operator']} {row['direction']}",
                "mass_MeV": row["mass_MeV"],
                "physical_regime": row["physical_regime"],
            })
            edges.append({
                "source": root_id,
                "target": node_id,
                "relation_type": row["relation_type"],
                "operator": row["operator"],
                "direction": row["direction"],
            })

    for field in coordinate_families["coordinate_field_transitions"]["fields"]:
        node_id = f"coordinate_field_{field['anchor']}"
        nodes.append({
            "id": node_id,
            "kind": "coordinate_field",
            "label": field["anchor"],
            "value_kind": field["kind"],
            "neighbor_count": field["neighbor_count"],
        })
        edges.append({
            "source": "one_step_coordinate_fields",
            "target": node_id,
            "relation_type": "has_coordinate_field",
        })

    thread_sources = {
        "nuclear_binding_ladder": "nuclear_binding_chain",
        "sub_hadronic_inverse_branch": "inverse_operator_compression",
        "multi_gev_resonance_branch": "direct_operator_amplification",
        "pmns_rotation_field": "one_step_coordinate_fields",
        "electroweak_neighbor_ladder": "one_step_coordinate_fields",
        "cosmic_phase_coordinate_field": "one_step_coordinate_fields",
    }

    for name, thread in threads.items():
        node_id = f"thread_{name}"
        nodes.append({
            "id": node_id,
            "kind": "follow_thread",
            "label": name,
            "next_constructive_test": thread["next_constructive_test"],
        })
        edges.append({
            "source": thread_sources[name],
            "target": node_id,
            "relation_type": "opens_follow_thread",
        })

    return {
        "posture": "relationship_first_transition_map",
        "method": "Read each anchor as a transition family before treating generated values as objects.",
        "nodes": nodes,
        "edges": edges,
    }


def main():
    start = datetime.now(timezone.utc)
    prediction = read_prediction_atlas()
    core = prediction["core_bridge_anchor"]
    mass_neighbors = prediction["mass_anchor_one_step_neighbors"]
    coordinate_neighbors = prediction["coordinate_anchor_neighbors"]

    binding = build_binding_transitions(core)
    mass_families = build_mass_transition_families(mass_neighbors)
    coordinate_families = build_coordinate_field_transitions(coordinate_neighbors)
    threads = build_threads_to_follow(binding, mass_families, coordinate_families)
    transition_map = build_transition_map(binding, mass_families, coordinate_families, threads)

    report = {
        "experiment_name": "pakheta_transition_atlas",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start).total_seconds(),
        "source": "Derived from prediction_atlas_results.json.",
        "posture": "relationship_first",
        "method": "Organize generated values by transition family, not object identity.",
        "binding_transitions": binding,
        "compression_transitions": mass_families["compression_transitions"],
        "amplification_transitions": mass_families["amplification_transitions"],
        "coordinate_field_transitions": coordinate_families["coordinate_field_transitions"],
        "mixing_transitions": coordinate_families["mixing_transitions"],
        "electroweak_transitions": coordinate_families["electroweak_transitions"],
        "cosmological_phase_transitions": coordinate_families["cosmological_phase_transitions"],
        "threads_to_follow": threads,
        "transition_map": transition_map,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("============================================================")
    print(" Pakheta Transition Atlas")
    print("============================================================")
    gate = binding["chain"][-1]
    print(
        "Nuclear binding chain:"
        f" delta={gate['delta_MeV']:+.9f} MeV,"
        f" relative_delta={gate['relative_delta']:+.6%}"
    )
    compression = mass_families["compression_transitions"]
    amplification = mass_families["amplification_transitions"]
    print(
        "Inverse compression band:"
        f" {compression['mass_band_MeV'][0]:.6f}"
        f" - {compression['mass_band_MeV'][1]:.6f} MeV"
    )
    print(
        "Direct amplification band:"
        f" {amplification['mass_band_MeV'][0]:.6f}"
        f" - {amplification['mass_band_MeV'][1]:.6f} MeV"
    )
    print(
        "Coordinate fields:"
        f" {coordinate_families['coordinate_field_transitions']['anchor_count']} anchors,"
        " 8 one-step neighbors each"
    )
    print(f"Threads to follow: {len(threads)}")
    print("Results saved to: transition_atlas_results.json")


if __name__ == "__main__":
    main()
