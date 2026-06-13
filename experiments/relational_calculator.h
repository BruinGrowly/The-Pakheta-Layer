#ifndef RELATIONAL_CALCULATOR_H
#define RELATIONAL_CALCULATOR_H

#include <stdint.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

#define LL_PSEUDO_SAMPLE_COUNT 7

typedef struct {
    int16_t c_L;
    int16_t c_J;
    int16_t c_P;
    int16_t c_W;
} RelationalNumber;

typedef struct {
    RelationalNumber coord;
    double target_log30;
    double fitted_log30;
    double signed_log30_residue;
    double absolute_log30_residue;
    int32_t coordinate_l1;
    double complexity_penalty;
    double relational_score;
    double reconstructed_value;
    double relative_value_error;
} RelationalFit;

typedef struct {
    uint32_t exponent;
    int32_t status;
    int32_t is_mersenne_prime;
    uint32_t iterations;
    uint32_t word_count;
    uint64_t final_low64;
    uint32_t final_popcount;
    RelationalFit exponent_fit;
} LucasLehmerResult;

typedef struct {
    uint32_t step;
    double fraction;
    uint32_t popcount;
    double density;
    double binary_entropy;
    double cyclic_transition_rate;
    double longest_one_run_fraction;
    double longest_zero_run_fraction;
    double balance;
    double love_resonance;
    double justice_resonance;
    double power_resonance;
    double wisdom_resonance;
    double ljpw_resonance_mean;
    double ljpw_resonance_spread;
    double carry_pressure;
    double coefficient_entropy;
    uint32_t occupied_cycle_sites;
    uint32_t max_bucket;
    double pseudo_likeness;
} RelationalLLSample;

typedef struct {
    uint32_t exponent;
    int32_t status;
    int32_t is_mersenne_prime;
    uint32_t iterations;
    uint32_t word_count;
    uint64_t final_low64;
    uint32_t final_popcount;
    RelationalFit exponent_fit;
    uint32_t sample_count;
    RelationalLLSample samples[LL_PSEUDO_SAMPLE_COUNT];
} RelationalLLPseudoResult;

EXPORT int init_lattice(int max_coeff);
EXPORT void free_lattice();
EXPORT int get_lattice_size();
EXPORT RelationalNumber encode_value(double val);
EXPORT double decode_value(RelationalNumber num);
EXPORT RelationalFit fit_log30_target(double target_log30, int max_coeff);
EXPORT RelationalFit fit_value(double val, int max_coeff);
EXPORT void batch_fit_log30_targets(RelationalFit* out, const double* target_log30_values, int count, int max_coeff);
EXPORT LucasLehmerResult lucas_lehmer_mersenne(uint32_t exponent, int fit_max_coeff, uint32_t max_bits);
EXPORT RelationalLLPseudoResult relational_ll_pseudo_probe(uint32_t exponent, int fit_max_coeff, uint32_t max_bits);
EXPORT void batch_relational_ll_pseudo_probe(RelationalLLPseudoResult* out, const uint32_t* exponents, int count, int fit_max_coeff, uint32_t max_bits);
EXPORT RelationalNumber relational_mul(RelationalNumber a, RelationalNumber b);
EXPORT RelationalNumber relational_div(RelationalNumber a, RelationalNumber b);
EXPORT void batch_mul(RelationalNumber* out, const RelationalNumber* a, const RelationalNumber* b, int count);
EXPORT void batch_div(RelationalNumber* out, const RelationalNumber* a, const RelationalNumber* b, int count);
EXPORT double run_internal_benchmark(RelationalNumber a, RelationalNumber b, int64_t iterations);

#endif // RELATIONAL_CALCULATOR_H
