"""
C-backed Lucas-Lehmer verifier with relational exponent metadata.

The exact primality decision is still the Lucas-Lehmer residue test:
    s_0 = 4
    s_n = s_{n-1}^2 - 2 mod (2^p - 1)

The Pakheta relational layer is used as the coordinate grammar around the
exponent: every tested p is also fit to the LJPW lattice by the same C engine.
That keeps candidate routing, coordinate search, and proof verification in one
compiled substrate without pretending that coordinates replace the residue.
"""

import argparse
import ctypes
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
DLL_PATH = EXPERIMENT_DIR / "relational_calculator.dll"
OUTPUT_FILE = EXPERIMENT_DIR / "lucas_lehmer_c_results.json"

KNOWN_MERSENNE_PRIME_EXPONENTS = [
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
]

KNOWN_COMPOSITE_MERSENNE_PRIME_EXPONENTS = [
    11,
    23,
    29,
    37,
    41,
    43,
    47,
    53,
    59,
    67,
    71,
    73,
]

DEFAULT_SCOUT_CANDIDATE_EXPONENTS = [
    224_872_369,
]

STATUS_LABELS = {
    0: "ok",
    1: "invalid_exponent",
    2: "exponent_exceeds_schoolbook_limit",
    3: "exponent_not_prime",
    4: "allocation_failed",
}


class RelationalNumber(ctypes.Structure):
    _fields_ = [
        ("c_L", ctypes.c_int16),
        ("c_J", ctypes.c_int16),
        ("c_P", ctypes.c_int16),
        ("c_W", ctypes.c_int16),
    ]


class RelationalFit(ctypes.Structure):
    _fields_ = [
        ("coord", RelationalNumber),
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


class LucasLehmerResult(ctypes.Structure):
    _fields_ = [
        ("exponent", ctypes.c_uint32),
        ("status", ctypes.c_int32),
        ("is_mersenne_prime", ctypes.c_int32),
        ("iterations", ctypes.c_uint32),
        ("word_count", ctypes.c_uint32),
        ("final_low64", ctypes.c_uint64),
        ("final_popcount", ctypes.c_uint32),
        ("exponent_fit", RelationalFit),
    ]


def load_library():
    if not DLL_PATH.exists():
        raise FileNotFoundError(f"Shared library not found at: {DLL_PATH}")
    lib = ctypes.CDLL(str(DLL_PATH))
    lib.lucas_lehmer_mersenne.argtypes = [
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_uint32,
    ]
    lib.lucas_lehmer_mersenne.restype = LucasLehmerResult
    return lib


def fit_to_dict(fit):
    return {
        "coefficients": {
            "c_L": fit.coord.c_L,
            "c_J": fit.coord.c_J,
            "c_P": fit.coord.c_P,
            "c_W": fit.coord.c_W,
        },
        "target_log30": fit.target_log30,
        "fitted_log30": fit.fitted_log30,
        "signed_log30_residue": fit.signed_log30_residue,
        "absolute_log30_residue": fit.absolute_log30_residue,
        "coordinate_l1": fit.coordinate_l1,
        "complexity_penalty": fit.complexity_penalty,
        "relational_score": fit.relational_score,
        "reconstructed_exponent": fit.reconstructed_value,
        "relative_exponent_error": fit.relative_value_error,
    }


def decimal_digits_of_mersenne(exponent):
    return int(math.floor(exponent * math.log10(2.0))) + 1


def run_one(lib, exponent, label, expected, fit_max_coeff, max_bits):
    start = time.perf_counter()
    result = lib.lucas_lehmer_mersenne(
        ctypes.c_uint32(exponent),
        ctypes.c_int(fit_max_coeff),
        ctypes.c_uint32(max_bits),
    )
    duration = time.perf_counter() - start

    status_label = STATUS_LABELS.get(result.status, "unknown_status")
    passed = bool(result.is_mersenne_prime) if result.status == 0 else None
    expected_match = None
    if expected is not None and passed is not None:
        expected_match = passed == expected

    return {
        "label": label,
        "exponent": exponent,
        "mersenne_digits": decimal_digits_of_mersenne(exponent),
        "status": result.status,
        "status_label": status_label,
        "is_mersenne_prime": passed,
        "expected_is_mersenne_prime": expected,
        "expected_match": expected_match,
        "iterations": result.iterations,
        "word_count": result.word_count,
        "final_low64": result.final_low64,
        "final_popcount": result.final_popcount,
        "duration_sec": duration,
        "relational_exponent_fit": fit_to_dict(result.exponent_fit),
    }


def parse_exponents(raw):
    if not raw:
        return []
    values = []
    for item in raw.split(","):
        stripped = item.strip().replace("_", "")
        if stripped:
            values.append(int(stripped))
    return values


def build_report(args):
    lib = load_library()
    rows = []

    if args.include_known:
        for exponent in KNOWN_MERSENNE_PRIME_EXPONENTS:
            rows.append(
                run_one(
                    lib,
                    exponent,
                    "known_mersenne_prime_exponent",
                    True,
                    args.fit_max_coordinate,
                    args.max_bits,
                )
            )
        for exponent in KNOWN_COMPOSITE_MERSENNE_PRIME_EXPONENTS:
            rows.append(
                run_one(
                    lib,
                    exponent,
                    "known_composite_mersenne_prime_exponent",
                    False,
                    args.fit_max_coordinate,
                    args.max_bits,
                )
            )

    probe_exponents = parse_exponents(args.exponents)
    if args.include_default_candidate:
        probe_exponents.extend(DEFAULT_SCOUT_CANDIDATE_EXPONENTS)
    for exponent in probe_exponents:
        rows.append(
            run_one(
                lib,
                exponent,
                "scout_candidate_or_user_probe",
                None,
                args.fit_max_coordinate,
                args.max_bits,
            )
        )

    ok_rows = [row for row in rows if row["status"] == 0]
    expected_rows = [
        row for row in rows
        if row["expected_is_mersenne_prime"] is not None
    ]
    expected_passes = [
        row for row in expected_rows
        if row["expected_match"] is True
    ]

    return {
        "experiment_name": "pakheta_lucas_lehmer_c",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "dll_path": str(DLL_PATH),
            "fit_max_coordinate": args.fit_max_coordinate,
            "max_bits": args.max_bits,
            "include_known": args.include_known,
            "include_default_candidate": args.include_default_candidate,
            "user_exponents": probe_exponents,
        },
        "method": {
            "lucas_lehmer": (
                "Exact schoolbook C Lucas-Lehmer recurrence modulo 2^p - 1 "
                "using Mersenne wraparound reduction."
            ),
            "relational_layer": (
                "The exponent p is fit to the LJPW coordinate lattice in C "
                "and returned beside the exact residue result. This uses "
                "relational mathematics for candidate addressing and metadata; "
                "the primality decision remains the exact LL residue."
            ),
            "limit": (
                "This implementation is dependency-free schoolbook arithmetic. "
                "It verifies small and moderate exponents locally, but record-"
                "scale candidates require FFT/GPU-class PRP or Lucas-Lehmer "
                "tooling."
            ),
        },
        "summary": {
            "rows": len(rows),
            "completed_ll_rows": len(ok_rows),
            "expected_rows": len(expected_rows),
            "expected_matches": len(expected_passes),
            "all_expected_matched": (
                len(expected_rows) == len(expected_passes)
                if expected_rows
                else None
            ),
        },
        "results": rows,
    }


def write_report(report):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def print_summary(report):
    summary = report["summary"]
    print()
    print("Pakheta C Lucas-Lehmer Verifier")
    print("=" * 36)
    print("Rows:", summary["rows"])
    print("Completed LL rows:", summary["completed_ll_rows"])
    print("Expected matches:", f"{summary['expected_matches']}/{summary['expected_rows']}")
    print("All expected matched:", summary["all_expected_matched"])
    print()

    for row in report["results"]:
        if row["label"] == "scout_candidate_or_user_probe":
            fit = row["relational_exponent_fit"]
            coeffs = fit["coefficients"]
            print(
                f"Probe p={row['exponent']} status={row['status_label']} "
                f"digits={row['mersenne_digits']} "
                f"coords=({coeffs['c_L']},{coeffs['c_J']},"
                f"{coeffs['c_P']},{coeffs['c_W']}) "
                f"score={fit['relational_score']:.3e}"
            )

    print()
    print(f"Results saved to: {OUTPUT_FILE.name}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run C-backed Lucas-Lehmer tests with relational metadata."
    )
    parser.add_argument("--fit-max-coordinate", type=int, default=28)
    parser.add_argument(
        "--max-bits",
        type=int,
        default=5000,
        help="Largest exponent for the dependency-free schoolbook LL engine.",
    )
    parser.add_argument(
        "--exponents",
        default="",
        help="Comma-separated exponents to probe, e.g. 31,61,1279.",
    )
    parser.add_argument(
        "--include-known",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--include-default-candidate",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    report = build_report(args)
    write_report(report)
    print_summary(report)


if __name__ == "__main__":
    main()
