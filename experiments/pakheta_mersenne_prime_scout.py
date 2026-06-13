"""
Pakheta Mersenne Prime Scout.

This is a relational-guided candidate scout, not a proof engine.  It starts
from the latest known GIMPS frontier, generates prime exponents beyond it,
filters candidates with a small Mersenne-factor screen, then ranks the
survivors by their fit to a frozen LJPW coordinate grammar.

The mathematical proof step for any surviving candidate remains a real
Mersenne PRP or Lucas-Lehmer class computation.
"""

import argparse
import ctypes
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = EXPERIMENT_DIR / "mersenne_prime_scout_results.json"

BASE = 30.0
L0 = (math.sqrt(5.0) - 1.0) / 2.0
J0 = math.sqrt(2.0) - 1.0
P0 = math.e - 2.0
W0 = math.log(2.0)

KNOWN_MERSENNE_EXPONENTS = [
    2,
    3,
    5,
    7,
    13,
    17,
    19,
    31,
    61,
    89,
    107,
    127,
    521,
    607,
    1279,
    2203,
    2281,
    3217,
    4253,
    4423,
    9689,
    9941,
    11213,
    19937,
    21701,
    23209,
    44497,
    86243,
    110503,
    132049,
    216091,
    756839,
    859433,
    1257787,
    1398269,
    2976221,
    3021377,
    6972593,
    13466917,
    20996011,
    24036583,
    25964951,
    30402457,
    32582657,
    37156667,
    42643801,
    43112609,
    57885161,
    74207281,
    77232917,
    82589933,
    136279841,
]

CURRENT_RECORD_EXPONENT = KNOWN_MERSENNE_EXPONENTS[-1]
GIMPS_SOURCE_URL = "https://www.mersenne.org/primes/"

MR_BASES_64BIT = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

ACTIVE_FIT_ENGINE = "python"
ACTIVE_C_FIT_LIB = None
ACTIVE_C_FIT_LIBRARY_PATH = None


class CRelationalNumber(ctypes.Structure):
    _fields_ = [
        ("c_L", ctypes.c_int16),
        ("c_J", ctypes.c_int16),
        ("c_P", ctypes.c_int16),
        ("c_W", ctypes.c_int16),
    ]


class CRelationalFit(ctypes.Structure):
    _fields_ = [
        ("coord", CRelationalNumber),
        ("target_log30", ctypes.c_double),
        ("fitted_log30", ctypes.c_double),
        ("signed_log30_residue", ctypes.c_double),
        ("absolute_log30_residue", ctypes.c_double),
        ("coordinate_l1", ctypes.c_int32),
        ("complexity_penalty", ctypes.c_double),
        ("relational_score", ctypes.c_double),
        ("reconstructed_value", ctypes.c_double),
        ("relative_value_error", ctypes.c_double),
    ]


def load_c_fit_library():
    candidate_paths = [
        EXPERIMENT_DIR / "relational_calculator.dll",
        EXPERIMENT_DIR / "relational_calculator.so",
        EXPERIMENT_DIR / "librelational_calculator.so",
        EXPERIMENT_DIR / "librelational_calculator.dylib",
    ]
    for path in candidate_paths:
        if not path.exists():
            continue
        lib = ctypes.CDLL(str(path))
        lib.fit_log30_target.argtypes = [ctypes.c_double, ctypes.c_int]
        lib.fit_log30_target.restype = CRelationalFit
        return lib, path
    raise FileNotFoundError("No compiled relational calculator library found.")


def configure_fit_engine(requested_engine):
    global ACTIVE_FIT_ENGINE
    global ACTIVE_C_FIT_LIB
    global ACTIVE_C_FIT_LIBRARY_PATH

    if requested_engine == "python":
        ACTIVE_FIT_ENGINE = "python"
        ACTIVE_C_FIT_LIB = None
        ACTIVE_C_FIT_LIBRARY_PATH = None
        return

    try:
        ACTIVE_C_FIT_LIB, ACTIVE_C_FIT_LIBRARY_PATH = load_c_fit_library()
        ACTIVE_FIT_ENGINE = "c"
    except (FileNotFoundError, OSError, AttributeError):
        if requested_engine == "c":
            raise
        ACTIVE_FIT_ENGINE = "python"
        ACTIVE_C_FIT_LIB = None
        ACTIVE_C_FIT_LIBRARY_PATH = None


def c_fit_to_dict(c_fit):
    return {
        "coefficients": {
            "c_L": c_fit.coord.c_L,
            "c_J": c_fit.coord.c_J,
            "c_P": c_fit.coord.c_P,
            "c_W": c_fit.coord.c_W,
        },
        "target_log30": c_fit.target_log30,
        "fitted_log30": c_fit.fitted_log30,
        "signed_log30_residue": c_fit.signed_log30_residue,
        "absolute_log30_residue": c_fit.absolute_log30_residue,
        "coordinate_l1": c_fit.coordinate_l1,
        "complexity_penalty": c_fit.complexity_penalty,
        "relational_score": c_fit.relational_score,
        "reconstructed_exponent": c_fit.reconstructed_value,
        "relative_exponent_error": c_fit.relative_value_error,
    }


def is_prime(n):
    """Deterministic Miller-Rabin for the integer sizes used in this scout."""
    if n < 2:
        return False
    small_primes = MR_BASES_64BIT
    for prime in small_primes:
        if n == prime:
            return True
        if n % prime == 0:
            return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for base in small_primes:
        if base >= n:
            continue
        x = pow(base, d, n)
        if x == 1 or x == n - 1:
            continue
        witness_found = True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                witness_found = False
                break
        if witness_found:
            return False
    return True


def next_prime_exponents(start_exclusive, count):
    exponents = []
    candidate = start_exclusive + 1
    if candidate <= 2:
        candidate = 2
    if candidate > 2 and candidate % 2 == 0:
        candidate += 1

    while len(exponents) < count:
        if is_prime(candidate):
            exponents.append(candidate)
        candidate += 1 if candidate == 2 else 2
    return exponents


def previous_prime_exponents(start_exclusive, count):
    exponents = []
    candidate = start_exclusive - 1
    if candidate % 2 == 0:
        candidate -= 1
    while candidate >= 2 and len(exponents) < count:
        if is_prime(candidate):
            exponents.append(candidate)
        candidate -= 2
    return exponents


def decimal_digits_of_mersenne(exponent):
    return int(math.floor(exponent * math.log10(2.0))) + 1


def build_coordinate_triples(max_coordinate):
    triples = []
    for c_l in range(-max_coordinate, max_coordinate + 1):
        l_part = c_l * L0
        for c_j in range(-max_coordinate, max_coordinate + 1):
            lj_part = l_part + c_j * J0
            for c_p in range(-max_coordinate, max_coordinate + 1):
                partial = lj_part + c_p * P0
                l1_without_w = abs(c_l) + abs(c_j) + abs(c_p)
                triples.append((c_l, c_j, c_p, partial, l1_without_w))
    return triples


def relational_fit_for_log30_target(target_log30, triples, max_coordinate):
    if ACTIVE_FIT_ENGINE == "c":
        c_fit = ACTIVE_C_FIT_LIB.fit_log30_target(
            ctypes.c_double(target_log30),
            ctypes.c_int(max_coordinate),
        )
        return c_fit_to_dict(c_fit)

    best = None
    target_value = BASE ** target_log30

    for c_l, c_j, c_p, partial, l1_without_w in triples:
        raw_w = (target_log30 - partial) / W0
        center_w = int(round(raw_w))
        for c_w in (center_w - 1, center_w, center_w + 1):
            if c_w < -max_coordinate or c_w > max_coordinate:
                continue
            fitted_log30 = partial + c_w * W0
            signed_residue = fitted_log30 - target_log30
            residue = abs(signed_residue)
            l1 = l1_without_w + abs(c_w)
            complexity_penalty = 1.0 + l1 / (4.0 * max_coordinate)
            score = residue * complexity_penalty

            if best is None or score < best["relational_score"]:
                reconstructed = BASE ** fitted_log30
                best = {
                    "coefficients": {
                        "c_L": c_l,
                        "c_J": c_j,
                        "c_P": c_p,
                        "c_W": c_w,
                    },
                    "target_log30": target_log30,
                    "fitted_log30": fitted_log30,
                    "signed_log30_residue": signed_residue,
                    "absolute_log30_residue": residue,
                    "coordinate_l1": l1,
                    "complexity_penalty": complexity_penalty,
                    "relational_score": score,
                    "reconstructed_exponent": reconstructed,
                    "relative_exponent_error": reconstructed / target_value - 1.0,
                }

    return best


def relational_fit_for_exponent(exponent, triples, max_coordinate):
    return relational_fit_for_log30_target(
        math.log(exponent, BASE),
        triples,
        max_coordinate,
    )


def relational_fit_for_ratio(ratio, triples, max_coordinate):
    return relational_fit_for_log30_target(
        math.log(ratio, BASE),
        triples,
        max_coordinate,
    )


def mersenne_small_factor_screen(exponent, k_limit):
    """Return the first small factor q = 2kp + 1 found for 2^p - 1."""
    scanned_k = 0
    residue_eligible_q = 0
    prime_q_tested = 0

    for k in range(1, k_limit + 1):
        scanned_k += 1
        q = 2 * k * exponent + 1
        if q % 8 not in (1, 7):
            continue
        residue_eligible_q += 1
        if not is_prime(q):
            continue
        prime_q_tested += 1
        if pow(2, exponent, q) == 1:
            return {
                "has_factor": True,
                "factor": q,
                "k": k,
                "scanned_k": scanned_k,
                "residue_eligible_q": residue_eligible_q,
                "prime_q_tested": prime_q_tested,
            }

    return {
        "has_factor": False,
        "factor": None,
        "k": None,
        "scanned_k": scanned_k,
        "residue_eligible_q": residue_eligible_q,
        "prime_q_tested": prime_q_tested,
    }


def summarize(values):
    if not values:
        return {}
    sorted_values = sorted(values)
    return {
        "count": len(sorted_values),
        "min": sorted_values[0],
        "median": statistics.median(sorted_values),
        "mean": statistics.fmean(sorted_values),
        "max": sorted_values[-1],
    }


def known_exponent_baseline(triples, max_coordinate):
    rows = []
    for rank, exponent in enumerate(KNOWN_MERSENNE_EXPONENTS, start=1):
        fit = relational_fit_for_exponent(exponent, triples, max_coordinate)
        rows.append({
            "rank": rank,
            "exponent": exponent,
            "mersenne_digits": decimal_digits_of_mersenne(exponent),
            "fit": fit,
        })

    high_rows = [row for row in rows if row["exponent"] >= 1_000_000]
    return {
        "all_known_summary": summarize(
            [row["fit"]["relational_score"] for row in rows]
        ),
        "high_exponent_summary": summarize(
            [row["fit"]["relational_score"] for row in high_rows]
        ),
        "current_record_fit": rows[-1],
        "best_known_high_exponents": sorted(
            high_rows,
            key=lambda row: row["fit"]["relational_score"],
        )[:10],
    }


def known_transition_baseline(triples, max_coordinate, min_previous_exponent):
    rows = []
    transition_rank = 0
    for rank in range(2, len(KNOWN_MERSENNE_EXPONENTS) + 1):
        previous_exponent = KNOWN_MERSENNE_EXPONENTS[rank - 2]
        exponent = KNOWN_MERSENNE_EXPONENTS[rank - 1]
        if previous_exponent < min_previous_exponent:
            continue
        transition_rank += 1
        ratio = exponent / previous_exponent
        fit = relational_fit_for_ratio(ratio, triples, max_coordinate)
        rows.append({
            "transition_rank": transition_rank,
            "known_rank_from": rank - 1,
            "known_rank_to": rank,
            "previous_exponent": previous_exponent,
            "exponent": exponent,
            "gap": exponent - previous_exponent,
            "ratio": ratio,
            "fit": fit,
        })

    return {
        "min_previous_exponent": min_previous_exponent,
        "transition_count": len(rows),
        "score_summary": summarize(
            [row["fit"]["relational_score"] for row in rows]
        ),
        "rows": rows,
        "best_transition_templates": sorted(
            rows,
            key=lambda row: row["fit"]["relational_score"],
        )[:10],
        "most_recent_transitions": rows[-10:],
    }


def local_historical_calibration(triples, max_coordinate, neighbors_each_side):
    calibration_rows = []
    target_exponents = [
        exponent
        for exponent in KNOWN_MERSENNE_EXPONENTS
        if exponent >= 1_000_000
    ]

    for exponent in target_exponents:
        neighbors = (
            previous_prime_exponents(exponent, neighbors_each_side)
            + [exponent]
            + next_prime_exponents(exponent, neighbors_each_side)
        )
        scored = []
        for local_exponent in neighbors:
            fit = relational_fit_for_exponent(
                local_exponent,
                triples,
                max_coordinate,
            )
            scored.append({
                "exponent": local_exponent,
                "relational_score": fit["relational_score"],
            })
        scored.sort(key=lambda row: row["relational_score"])
        rank = next(
            index + 1
            for index, row in enumerate(scored)
            if row["exponent"] == exponent
        )
        calibration_rows.append({
            "known_exponent": exponent,
            "local_prime_exponent_count": len(scored),
            "rank_by_relational_score": rank,
            "percentile": rank / len(scored),
            "known_relational_score": next(
                row["relational_score"]
                for row in scored
                if row["exponent"] == exponent
            ),
            "best_local_exponent": scored[0]["exponent"],
            "best_local_score": scored[0]["relational_score"],
        })

    percentiles = [row["percentile"] for row in calibration_rows]
    first_decile_hits = [
        row for row in calibration_rows if row["percentile"] <= 0.10
    ]

    return {
        "method": (
            "For each known high Mersenne exponent, compare its LJPW score "
            "against nearby prime exponents without using Mersenne proof data."
        ),
        "neighbors_each_side": neighbors_each_side,
        "summary": {
            "known_exponents_tested": len(calibration_rows),
            "median_percentile": statistics.median(percentiles) if percentiles else None,
            "first_decile_hits": len(first_decile_hits),
            "first_decile_hit_rate": (
                len(first_decile_hits) / len(calibration_rows)
                if calibration_rows
                else None
            ),
        },
        "rows": calibration_rows,
    }


def nearby_prime_exponents(center_value, each_side):
    center = max(3, int(round(center_value)))
    previous_side = previous_prime_exponents(center + 1, each_side + 1)
    next_side = next_prime_exponents(center - 1, each_side + 1)
    primes = sorted(set(previous_side + next_side))
    primes.sort(key=lambda exponent: (abs(exponent - center_value), exponent))
    return primes[: (2 * each_side + 1)]


def transition_branch_scout(
    transition_baseline,
    k_limit,
    template_count,
    snap_primes_each_side,
):
    templates = sorted(
        transition_baseline["rows"],
        key=lambda row: row["fit"]["relational_score"],
    )[:template_count]

    best_by_exponent = {}
    for template in templates:
        projected = CURRENT_RECORD_EXPONENT * template["ratio"]
        for exponent in nearby_prime_exponents(projected, snap_primes_each_side):
            if exponent <= CURRENT_RECORD_EXPONENT:
                continue
            snap_log30_residue = abs(math.log(exponent / projected, BASE))
            factor_screen = mersenne_small_factor_screen(exponent, k_limit)
            branch_score = (
                template["fit"]["relational_score"]
                + snap_log30_residue
            )
            row = {
                "exponent": exponent,
                "mersenne_digits": decimal_digits_of_mersenne(exponent),
                "projected_exponent": projected,
                "snap_delta": exponent - projected,
                "snap_relative_delta": exponent / projected - 1.0,
                "snap_log30_residue": snap_log30_residue,
                "branch_score": branch_score,
                "small_factor_screen": factor_screen,
                "status": (
                    "rejected_small_factor"
                    if factor_screen["has_factor"]
                    else "survives_small_factor_screen"
                ),
                "template": {
                    "known_rank_from": template["known_rank_from"],
                    "known_rank_to": template["known_rank_to"],
                    "previous_exponent": template["previous_exponent"],
                    "exponent": template["exponent"],
                    "gap": template["gap"],
                    "ratio": template["ratio"],
                    "fit": template["fit"],
                },
            }
            current = best_by_exponent.get(exponent)
            if current is None or row["branch_score"] < current["branch_score"]:
                best_by_exponent[exponent] = row

    rows = list(best_by_exponent.values())
    survivors = [row for row in rows if row["status"] == "survives_small_factor_screen"]
    rejected = [row for row in rows if row["status"] == "rejected_small_factor"]

    return {
        "method": (
            "Fit high-exponent known Mersenne exponent ratios to the LJPW "
            "grammar, apply the strongest transition templates to the current "
            "frontier exponent, snap each projection to nearby prime exponents, "
            "then run the same bounded small-factor screen."
        ),
        "template_count": template_count,
        "snap_primes_each_side": snap_primes_each_side,
        "candidate_count": len(rows),
        "rejected_by_small_factor": len(rejected),
        "survivors": len(survivors),
        "branch_score_summary": summarize(
            [row["branch_score"] for row in survivors]
        ),
        "top_surviving_branches": sorted(
            survivors,
            key=lambda row: row["branch_score"],
        )[:20],
        "rows": sorted(rows, key=lambda row: row["branch_score"]),
    }


def extended_small_factor_validation(label, rows, k_limit):
    validation_rows = []
    for row in rows:
        exponent = row["exponent"]
        screen = mersenne_small_factor_screen(exponent, k_limit)
        validation_rows.append({
            "source": label,
            "exponent": exponent,
            "mersenne_digits": decimal_digits_of_mersenne(exponent),
            "extended_small_factor_k_limit": k_limit,
            "extended_small_factor_screen": screen,
            "extended_status": (
                "rejected_small_factor"
                if screen["has_factor"]
                else "survives_extended_small_factor_screen"
            ),
        })
    return validation_rows


def score_candidate_exponents(candidate_exponents, triples, max_coordinate, k_limit):
    rows = []
    for index, exponent in enumerate(candidate_exponents, start=1):
        fit = relational_fit_for_exponent(exponent, triples, max_coordinate)
        factor_screen = mersenne_small_factor_screen(exponent, k_limit)
        rows.append({
            "candidate_index_after_record": index,
            "exponent": exponent,
            "mersenne_digits": decimal_digits_of_mersenne(exponent),
            "fit": fit,
            "small_factor_screen": factor_screen,
            "status": (
                "rejected_small_factor"
                if factor_screen["has_factor"]
                else "survives_small_factor_screen"
            ),
        })
    return rows


def build_report(args):
    configure_fit_engine(args.fit_engine)
    triples = [] if ACTIVE_FIT_ENGINE == "c" else build_coordinate_triples(args.max_coordinate)
    baseline = known_exponent_baseline(triples, args.max_coordinate)
    transition_baseline = known_transition_baseline(
        triples,
        args.max_coordinate,
        args.transition_min_previous_exponent,
    )
    calibration = local_historical_calibration(
        triples,
        args.max_coordinate,
        args.calibration_neighbors_each_side,
    )

    candidate_exponents = next_prime_exponents(
        CURRENT_RECORD_EXPONENT,
        args.candidate_count,
    )
    candidate_rows = score_candidate_exponents(
        candidate_exponents,
        triples,
        args.max_coordinate,
        args.small_factor_k_limit,
    )
    transition_branches = transition_branch_scout(
        transition_baseline,
        args.small_factor_k_limit,
        args.transition_template_count,
        args.transition_snap_primes_each_side,
    )
    survivors = [
        row
        for row in candidate_rows
        if row["status"] == "survives_small_factor_screen"
    ]
    rejected = [
        row
        for row in candidate_rows
        if row["status"] == "rejected_small_factor"
    ]
    top_survivors = sorted(
        survivors,
        key=lambda row: row["fit"]["relational_score"],
    )[:args.top_n]
    extended_immediate = extended_small_factor_validation(
        "immediate_lattice_candidate",
        top_survivors,
        args.extended_small_factor_k_limit,
    )
    extended_transition = extended_small_factor_validation(
        "transition_branch_candidate",
        transition_branches["top_surviving_branches"][:args.top_n],
        args.extended_small_factor_k_limit,
    )

    report = {
        "experiment_name": "pakheta_mersenne_prime_scout",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "source": {
            "known_mersenne_prime_frontier": GIMPS_SOURCE_URL,
            "source_note": (
                "GIMPS lists 52 known Mersenne primes; the latest listed "
                "frontier exponent is 136,279,841."
            ),
        },
        "configuration": {
            "base": BASE,
            "fit_engine_requested": args.fit_engine,
            "fit_engine_used": ACTIVE_FIT_ENGINE,
            "c_fit_library_path": (
                str(ACTIVE_C_FIT_LIBRARY_PATH)
                if ACTIVE_C_FIT_LIBRARY_PATH is not None
                else None
            ),
            "constants": {
                "L0": L0,
                "J0": J0,
                "P0": P0,
                "W0": W0,
            },
            "max_coordinate": args.max_coordinate,
            "candidate_count": args.candidate_count,
            "small_factor_k_limit": args.small_factor_k_limit,
            "top_n": args.top_n,
            "calibration_neighbors_each_side": (
                args.calibration_neighbors_each_side
            ),
            "transition_min_previous_exponent": (
                args.transition_min_previous_exponent
            ),
            "transition_template_count": args.transition_template_count,
            "transition_snap_primes_each_side": (
                args.transition_snap_primes_each_side
            ),
            "extended_small_factor_k_limit": args.extended_small_factor_k_limit,
        },
        "known_mersenne_frontier": {
            "known_count": len(KNOWN_MERSENNE_EXPONENTS),
            "current_record_exponent": CURRENT_RECORD_EXPONENT,
            "current_record_mersenne_digits": decimal_digits_of_mersenne(
                CURRENT_RECORD_EXPONENT
            ),
            "known_exponents": KNOWN_MERSENNE_EXPONENTS,
        },
        "known_exponent_baseline": baseline,
        "known_transition_baseline": transition_baseline,
        "historical_local_calibration": calibration,
        "candidate_generation": {
            "start_after_exponent": CURRENT_RECORD_EXPONENT,
            "first_candidate_exponent": candidate_exponents[0],
            "last_candidate_exponent": candidate_exponents[-1],
            "candidate_count": len(candidate_exponents),
        },
        "filters": {
            "necessary_exponent_filter": "p must be prime",
            "small_factor_filter": (
                "For prime exponent p, scan q = 2kp + 1 through k limit; "
                "only q == 1 or 7 mod 8 can divide M_p, then test "
                "pow(2, p, q) == 1."
            ),
            "small_factor_limit_note": (
                "Passing this screen is not evidence of primality; it only "
                "means no factor was found in this bounded small-factor pass."
            ),
        },
        "candidate_summary": {
            "rejected_by_small_factor": len(rejected),
            "survivors": len(survivors),
            "survivor_score_summary": summarize(
                [row["fit"]["relational_score"] for row in survivors]
            ),
        },
        "top_surviving_candidates": top_survivors,
        "transition_branch_scout": transition_branches,
        "extended_small_factor_validation": {
            "method": (
                "Re-screen the top immediate candidates and top transition "
                "branches through a deeper k limit."
            ),
            "top_immediate_candidates": extended_immediate,
            "top_transition_branches": extended_transition,
            "summary": {
                "immediate_rejects": len([
                    row for row in extended_immediate
                    if row["extended_status"] == "rejected_small_factor"
                ]),
                "transition_rejects": len([
                    row for row in extended_transition
                    if row["extended_status"] == "rejected_small_factor"
                ]),
            },
        },
        "candidate_rows": candidate_rows,
        "interpretation": {
            "plain_read": (
                "The scout does not find or prove the next Mersenne prime. "
                "It creates a relationally ordered short list of prime "
                "exponents beyond the current record that also survive a "
                "bounded small-factor screen."
            ),
            "next_required_step": (
                "Run real PRP or Lucas-Lehmer style Mersenne tests on the "
                "top surviving exponents, preferably through GIMPS-compatible "
                "tooling so results are reproducible and comparable."
            ),
        },
    }
    return report


def write_report(report):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def print_summary(report):
    candidate_summary = report["candidate_summary"]
    calibration = report["historical_local_calibration"]["summary"]
    print()
    print("Pakheta Mersenne Prime Scout")
    print("=" * 34)
    print(
        "Fit engine:",
        report["configuration"]["fit_engine_used"],
        f"| max coordinate={report['configuration']['max_coordinate']}",
    )
    print(
        "Current known frontier exponent:",
        report["known_mersenne_frontier"]["current_record_exponent"],
    )
    print(
        "Generated candidate prime exponents:",
        report["candidate_generation"]["candidate_count"],
    )
    print(
        "Small-factor rejects:",
        candidate_summary["rejected_by_small_factor"],
    )
    print("Survivors:", candidate_summary["survivors"])
    print(
        "Historical local calibration median percentile:",
        f"{calibration['median_percentile']:.3f}",
    )
    print(
        "Historical first-decile hit rate:",
        f"{calibration['first_decile_hit_rate']:.3f}",
    )
    print()
    print("Top surviving relational candidates:")
    for row in report["top_surviving_candidates"][:10]:
        fit = row["fit"]
        coeffs = fit["coefficients"]
        print(
            f"  p={row['exponent']} "
            f"digits={row['mersenne_digits']} "
            f"score={fit['relational_score']:.3e} "
            f"residue={fit['absolute_log30_residue']:.3e} "
            f"coords=({coeffs['c_L']},{coeffs['c_J']},"
            f"{coeffs['c_P']},{coeffs['c_W']})"
        )
    print()
    transition = report["transition_branch_scout"]
    print("Top forward transition branches:")
    for row in transition["top_surviving_branches"][:10]:
        template = row["template"]
        coeffs = template["fit"]["coefficients"]
        print(
            f"  p={row['exponent']} "
            f"digits={row['mersenne_digits']} "
            f"branch_score={row['branch_score']:.3e} "
            f"ratio={template['ratio']:.6f} "
            f"source={template['previous_exponent']}->{template['exponent']} "
            f"coords=({coeffs['c_L']},{coeffs['c_J']},"
            f"{coeffs['c_P']},{coeffs['c_W']})"
        )
    extended = report["extended_small_factor_validation"]
    print()
    print(
        "Extended top-candidate factor rejects:",
        f"immediate={extended['summary']['immediate_rejects']}",
        f"transition={extended['summary']['transition_rejects']}",
    )
    print()
    print(f"Results saved to: {OUTPUT_FILE.name}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Relational-guided scout for post-frontier Mersenne exponents."
    )
    parser.add_argument("--candidate-count", type=int, default=500)
    parser.add_argument("--small-factor-k-limit", type=int, default=5000)
    parser.add_argument("--max-coordinate", type=int, default=28)
    parser.add_argument(
        "--fit-engine",
        choices=["auto", "c", "python"],
        default="auto",
    )
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument(
        "--calibration-neighbors-each-side",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--transition-min-previous-exponent",
        type=int,
        default=1_000_000,
    )
    parser.add_argument("--transition-template-count", type=int, default=12)
    parser.add_argument(
        "--transition-snap-primes-each-side",
        type=int,
        default=8,
    )
    parser.add_argument(
        "--extended-small-factor-k-limit",
        type=int,
        default=100_000,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    report = build_report(args)
    write_report(report)
    print_summary(report)


if __name__ == "__main__":
    main()
