#include "relational_calculator.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <string.h>

#define BASE 30.0
#define DEFAULT_FIT_MAX_COEFF 10
#define TWO_PI 6.283185307179586476925286766559

static double L0 = 0.0;
static double J0 = 0.0;
static double P0 = 0.0;
static double W0 = 0.0;

typedef struct {
    double exponent;
    RelationalNumber coord;
} LatticeItem;

static LatticeItem* lattice = NULL;
static int lattice_size = 0;

static void ensure_constants() {
    if (L0 == 0.0 && J0 == 0.0 && P0 == 0.0 && W0 == 0.0) {
        L0 = (sqrt(5.0) - 1.0) / 2.0;
        J0 = sqrt(2.0) - 1.0;
        P0 = exp(1.0) - 2.0;
        W0 = log(2.0);
    }
}

int compare_items(const void* a, const void* b) {
    double exp_a = ((LatticeItem*)a)->exponent;
    double exp_b = ((LatticeItem*)b)->exponent;
    if (exp_a < exp_b) return -1;
    if (exp_a > exp_b) return 1;
    return 0;
}

EXPORT int init_lattice(int max_coeff) {
    ensure_constants();

    if (lattice) {
        free_lattice();
    }

    int count_per_dim = 2 * max_coeff + 1;
    lattice_size = count_per_dim * count_per_dim * count_per_dim * count_per_dim;

    lattice = (LatticeItem*)malloc(lattice_size * sizeof(LatticeItem));
    if (!lattice) {
        return -1; // Out of memory
    }

    int idx = 0;
    for (int c_l = -max_coeff; c_l <= max_coeff; c_l++) {
        for (int c_j = -max_coeff; c_j <= max_coeff; c_j++) {
            for (int c_p = -max_coeff; c_p <= max_coeff; c_p++) {
                for (int c_w = -max_coeff; c_w <= max_coeff; c_w++) {
                    double exponent = c_l * L0 + c_j * J0 + c_p * P0 + c_w * W0;
                    lattice[idx].exponent = exponent;
                    lattice[idx].coord.c_L = (int16_t)c_l;
                    lattice[idx].coord.c_J = (int16_t)c_j;
                    lattice[idx].coord.c_P = (int16_t)c_p;
                    lattice[idx].coord.c_W = (int16_t)c_w;
                    idx++;
                }
            }
        }
    }

    qsort(lattice, lattice_size, sizeof(LatticeItem), compare_items);
    return lattice_size;
}

EXPORT void free_lattice() {
    if (lattice) {
        free(lattice);
        lattice = NULL;
        lattice_size = 0;
    }
}

EXPORT int get_lattice_size() {
    return lattice_size;
}

EXPORT RelationalNumber encode_value(double val) {
    ensure_constants();

    if (val <= 0) {
        RelationalNumber zero = {0, 0, 0, 0};
        return zero;
    }

    if (!lattice || lattice_size <= 0) {
        return fit_value(val, DEFAULT_FIT_MAX_COEFF).coord;
    }

    double target_exponent = log(val) / log(BASE);
    
    // Binary search lookup
    int low = 0;
    int high = lattice_size - 1;
    int best_idx = 0;
    double min_diff = 1e30;

    while (low <= high) {
        int mid = low + (high - low) / 2;
        double exp_mid = lattice[mid].exponent;
        double diff = fabs(target_exponent - exp_mid);

        if (diff < min_diff) {
            min_diff = diff;
            best_idx = mid;
        }

        if (exp_mid < target_exponent) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    return lattice[best_idx].coord;
}

EXPORT double decode_value(RelationalNumber num) {
    ensure_constants();

    double exponent = num.c_L * L0 + num.c_J * J0 + num.c_P * P0 + num.c_W * W0;
    return pow(BASE, exponent);
}

EXPORT RelationalFit fit_log30_target(double target_log30, int max_coeff) {
    ensure_constants();

    RelationalFit best;
    best.coord.c_L = 0;
    best.coord.c_J = 0;
    best.coord.c_P = 0;
    best.coord.c_W = 0;
    best.target_log30 = target_log30;
    best.fitted_log30 = 0.0;
    best.signed_log30_residue = 0.0;
    best.absolute_log30_residue = DBL_MAX;
    best.coordinate_l1 = 0;
    best.complexity_penalty = 0.0;
    best.relational_score = DBL_MAX;
    best.reconstructed_value = 1.0;
    best.relative_value_error = 0.0;

    double target_value = pow(BASE, target_log30);

    if (max_coeff <= 0) {
        best.fitted_log30 = 0.0;
        best.signed_log30_residue = -target_log30;
        best.absolute_log30_residue = fabs(target_log30);
        best.coordinate_l1 = 0;
        best.complexity_penalty = 1.0;
        best.relational_score = best.absolute_log30_residue;
        best.reconstructed_value = 1.0;
        best.relative_value_error = 1.0 / target_value - 1.0;
        return best;
    }

    for (int c_l = -max_coeff; c_l <= max_coeff; c_l++) {
        double l_part = c_l * L0;
        for (int c_j = -max_coeff; c_j <= max_coeff; c_j++) {
            double lj_part = l_part + c_j * J0;
            for (int c_p = -max_coeff; c_p <= max_coeff; c_p++) {
                double partial = lj_part + c_p * P0;
                int l1_without_w = abs(c_l) + abs(c_j) + abs(c_p);
                double raw_w = (target_log30 - partial) / W0;
                int center_w = (int)llround(raw_w);

                for (int delta_w = -1; delta_w <= 1; delta_w++) {
                    int c_w = center_w + delta_w;
                    if (c_w < -max_coeff || c_w > max_coeff) {
                        continue;
                    }

                    double fitted_log30 = partial + c_w * W0;
                    double signed_residue = fitted_log30 - target_log30;
                    double residue = fabs(signed_residue);
                    int l1 = l1_without_w + abs(c_w);
                    double complexity_penalty = 1.0 + ((double)l1 / (4.0 * (double)max_coeff));
                    double score = residue * complexity_penalty;

                    if (score < best.relational_score) {
                        double reconstructed = pow(BASE, fitted_log30);
                        best.coord.c_L = (int16_t)c_l;
                        best.coord.c_J = (int16_t)c_j;
                        best.coord.c_P = (int16_t)c_p;
                        best.coord.c_W = (int16_t)c_w;
                        best.target_log30 = target_log30;
                        best.fitted_log30 = fitted_log30;
                        best.signed_log30_residue = signed_residue;
                        best.absolute_log30_residue = residue;
                        best.coordinate_l1 = l1;
                        best.complexity_penalty = complexity_penalty;
                        best.relational_score = score;
                        best.reconstructed_value = reconstructed;
                        best.relative_value_error = reconstructed / target_value - 1.0;
                    }
                }
            }
        }
    }

    return best;
}

EXPORT RelationalFit fit_value(double val, int max_coeff) {
    ensure_constants();

    if (val <= 0.0) {
        return fit_log30_target(0.0, max_coeff);
    }

    return fit_log30_target(log(val) / log(BASE), max_coeff);
}

EXPORT void batch_fit_log30_targets(RelationalFit* out, const double* target_log30_values, int count, int max_coeff) {
    if (!out || !target_log30_values || count <= 0) {
        return;
    }

    for (int i = 0; i < count; i++) {
        out[i] = fit_log30_target(target_log30_values[i], max_coeff);
    }
}

static int is_u32_prime(uint32_t n) {
    if (n < 2) {
        return 0;
    }
    if (n == 2 || n == 3) {
        return 1;
    }
    if ((n % 2u) == 0u) {
        return 0;
    }
    for (uint32_t d = 3; (uint64_t)d * (uint64_t)d <= n; d += 2) {
        if ((n % d) == 0u) {
            return 0;
        }
    }
    return 1;
}

static uint32_t top_word_mask(uint32_t bit_count) {
    uint32_t used = bit_count % 32u;
    if (used == 0u) {
        return 0xffffffffu;
    }
    return (uint32_t)((1ull << used) - 1ull);
}

static void mask_top_word(uint32_t* value, uint32_t words, uint32_t bit_count) {
    if (!value || words == 0u) {
        return;
    }
    value[words - 1u] &= top_word_mask(bit_count);
}

static void set_zero_words(uint32_t* value, uint32_t words) {
    memset(value, 0, (size_t)words * sizeof(uint32_t));
}

static void set_small_words(uint32_t* value, uint32_t words, uint32_t small) {
    set_zero_words(value, words);
    if (words > 0u) {
        value[0] = small;
    }
}

static int words_are_zero(const uint32_t* value, uint32_t words) {
    for (uint32_t i = 0; i < words; i++) {
        if (value[i] != 0u) {
            return 0;
        }
    }
    return 1;
}

static uint32_t words_popcount(const uint32_t* value, uint32_t words) {
    uint32_t total = 0u;
    for (uint32_t i = 0; i < words; i++) {
        total += (uint32_t)__builtin_popcount(value[i]);
    }
    return total;
}

static uint64_t words_low64(const uint32_t* value, uint32_t words) {
    uint64_t low = 0u;
    if (words > 0u) {
        low |= (uint64_t)value[0];
    }
    if (words > 1u) {
        low |= ((uint64_t)value[1] << 32);
    }
    return low;
}

static int get_cyclic_bit(const uint32_t* value, uint32_t bit_position) {
    return (value[bit_position / 32u] >> (bit_position % 32u)) & 1u;
}

static double binary_entropy_from_density(double density) {
    if (density <= 0.0 || density >= 1.0) {
        return 0.0;
    }
    return (
        -density * (log(density) / log(2.0))
        - (1.0 - density) * (log(1.0 - density) / log(2.0))
    );
}

static void unique_sorted_sample_steps(uint32_t iterations, uint32_t* steps, uint32_t* count) {
    uint32_t candidates[LL_PSEUDO_SAMPLE_COUNT] = {
        0u,
        1u,
        2u,
        iterations / 4u,
        iterations / 2u,
        (3u * iterations) / 4u,
        iterations
    };
    uint32_t candidate_count = LL_PSEUDO_SAMPLE_COUNT;
    *count = 0u;

    for (uint32_t i = 0u; i < candidate_count; i++) {
        uint32_t step = candidates[i];
        if (step > iterations) {
            continue;
        }

        int exists = 0;
        for (uint32_t j = 0u; j < *count; j++) {
            if (steps[j] == step) {
                exists = 1;
                break;
            }
        }
        if (exists) {
            continue;
        }

        uint32_t insert_at = *count;
        while (insert_at > 0u && steps[insert_at - 1u] > step) {
            steps[insert_at] = steps[insert_at - 1u];
            insert_at--;
        }
        steps[insert_at] = step;
        (*count)++;
    }
}

static void collect_bit_positions(
    const uint32_t* value,
    uint32_t p,
    uint32_t* positions,
    uint32_t* position_count
) {
    *position_count = 0u;
    for (uint32_t bit = 0u; bit < p; bit++) {
        if (get_cyclic_bit(value, bit)) {
            positions[*position_count] = bit;
            (*position_count)++;
        }
    }
}

static void resonance_for_constant(
    const uint32_t* positions,
    uint32_t position_count,
    double constant,
    double* resonance
) {
    if (position_count == 0u) {
        *resonance = 0.0;
        return;
    }

    double real = 0.0;
    double imag = 0.0;
    for (uint32_t i = 0u; i < position_count; i++) {
        double angle = TWO_PI * constant * (double)positions[i];
        real += cos(angle);
        imag += sin(angle);
    }

    *resonance = hypot(real, imag) / (double)position_count;
}

static void formal_square_feature_stats(
    const uint32_t* positions,
    uint32_t position_count,
    uint32_t p,
    uint32_t* buckets,
    double* carry_pressure,
    double* coefficient_entropy,
    uint32_t* occupied_cycle_sites,
    uint32_t* max_bucket
) {
    memset(buckets, 0, (size_t)p * sizeof(uint32_t));
    *carry_pressure = 0.0;
    *coefficient_entropy = 0.0;
    *occupied_cycle_sites = 0u;
    *max_bucket = 0u;

    uint64_t total_pairs = (uint64_t)position_count * (uint64_t)position_count;
    if (total_pairs == 0u) {
        return;
    }

    for (uint32_t left = 0u; left < position_count; left++) {
        for (uint32_t right = 0u; right < position_count; right++) {
            uint32_t bucket = (positions[left] + positions[right]) % p;
            buckets[bucket] += 1u;
        }
    }

    double entropy = 0.0;
    for (uint32_t i = 0u; i < p; i++) {
        uint32_t count = buckets[i];
        if (count == 0u) {
            continue;
        }
        (*occupied_cycle_sites)++;
        if (count > *max_bucket) {
            *max_bucket = count;
        }
        double probability = (double)count / (double)total_pairs;
        entropy -= probability * (log(probability) / log(2.0));
    }

    *carry_pressure = ((double)total_pairs - (double)(*occupied_cycle_sites)) / (double)total_pairs;
    *coefficient_entropy = p > 1u ? entropy / (log((double)p) / log(2.0)) : 0.0;
}

static RelationalLLSample relational_ll_sample_features(
    const uint32_t* value,
    uint32_t p,
    uint32_t step,
    uint32_t iterations,
    uint32_t* positions,
    uint32_t* buckets
) {
    RelationalLLSample sample;
    memset(&sample, 0, sizeof(RelationalLLSample));
    sample.step = step;
    sample.fraction = iterations == 0u ? 1.0 : (double)step / (double)iterations;

    uint32_t position_count = 0u;
    collect_bit_positions(value, p, positions, &position_count);
    sample.popcount = position_count;
    sample.density = (double)position_count / (double)p;
    sample.binary_entropy = binary_entropy_from_density(sample.density);
    sample.balance = 1.0 - fabs((2.0 * sample.density) - 1.0);

    uint32_t transitions = 0u;
    uint32_t longest_one_run = 0u;
    uint32_t longest_zero_run = 0u;
    uint32_t current_one_run = 0u;
    uint32_t current_zero_run = 0u;

    for (uint32_t i = 0u; i < 2u * p; i++) {
        uint32_t bit_index = i % p;
        int bit = get_cyclic_bit(value, bit_index);
        if (i < p) {
            int next_bit = get_cyclic_bit(value, (bit_index + 1u) % p);
            if (bit != next_bit) {
                transitions++;
            }
        }

        if (bit) {
            current_one_run++;
            current_zero_run = 0u;
            if (current_one_run > longest_one_run) {
                longest_one_run = current_one_run;
            }
        } else {
            current_zero_run++;
            current_one_run = 0u;
            if (current_zero_run > longest_zero_run) {
                longest_zero_run = current_zero_run;
            }
        }
    }

    if (longest_one_run > p) {
        longest_one_run = p;
    }
    if (longest_zero_run > p) {
        longest_zero_run = p;
    }

    sample.cyclic_transition_rate = (double)transitions / (double)p;
    sample.longest_one_run_fraction = (double)longest_one_run / (double)p;
    sample.longest_zero_run_fraction = (double)longest_zero_run / (double)p;

    resonance_for_constant(positions, position_count, L0, &sample.love_resonance);
    resonance_for_constant(positions, position_count, J0, &sample.justice_resonance);
    resonance_for_constant(positions, position_count, P0, &sample.power_resonance);
    resonance_for_constant(positions, position_count, W0, &sample.wisdom_resonance);

    double resonance_values[4] = {
        sample.love_resonance,
        sample.justice_resonance,
        sample.power_resonance,
        sample.wisdom_resonance
    };
    sample.ljpw_resonance_mean = (
        resonance_values[0] + resonance_values[1] + resonance_values[2] + resonance_values[3]
    ) / 4.0;
    double spread = 0.0;
    for (int i = 0; i < 4; i++) {
        double delta = resonance_values[i] - sample.ljpw_resonance_mean;
        spread += delta * delta;
    }
    sample.ljpw_resonance_spread = sqrt(spread / 4.0);

    formal_square_feature_stats(
        positions,
        position_count,
        p,
        buckets,
        &sample.carry_pressure,
        &sample.coefficient_entropy,
        &sample.occupied_cycle_sites,
        &sample.max_bucket
    );

    sample.pseudo_likeness = (
        (1.0 - sample.carry_pressure)
        + sample.ljpw_resonance_mean
        + 0.25 * sample.ljpw_resonance_spread
        - 0.25 * fabs(0.5 - sample.density)
    );

    return sample;
}

static void set_mersenne_modulus_bits(uint32_t* value, uint32_t p, uint32_t words) {
    for (uint32_t i = 0; i < words; i++) {
        value[i] = 0xffffffffu;
    }
    mask_top_word(value, words, p);
}

static int words_are_mersenne_modulus(const uint32_t* value, uint32_t p, uint32_t words) {
    if (words == 0u) {
        return 0;
    }
    for (uint32_t i = 0; i + 1u < words; i++) {
        if (value[i] != 0xffffffffu) {
            return 0;
        }
    }
    return value[words - 1u] == top_word_mask(p);
}

static int words_less_than_small(const uint32_t* value, uint32_t words, uint32_t small) {
    for (uint32_t i = 1; i < words; i++) {
        if (value[i] != 0u) {
            return 0;
        }
    }
    return words == 0u || value[0] < small;
}

static void subtract_small_nonmod(uint32_t* value, uint32_t words, uint32_t small) {
    uint64_t borrow = small;
    uint32_t i = 0u;
    while (borrow != 0u && i < words) {
        uint64_t current = value[i];
        if (current >= borrow) {
            value[i] = (uint32_t)(current - borrow);
            borrow = 0u;
        } else {
            value[i] = (uint32_t)((1ull << 32) + current - borrow);
            borrow = 1u;
            i++;
        }
    }
}

static void subtract_small_mod_mersenne(uint32_t* value, uint32_t p, uint32_t words, uint32_t small) {
    if (!words_less_than_small(value, words, small)) {
        subtract_small_nonmod(value, words, small);
        mask_top_word(value, words, p);
        return;
    }

    uint32_t current = words > 0u ? value[0] : 0u;
    uint32_t deficit = small - current;
    set_mersenne_modulus_bits(value, p, words);
    subtract_small_nonmod(value, words, deficit);
    mask_top_word(value, words, p);
}

static void add_bit_count(uint32_t* counts, uint32_t p, uint32_t bit_position) {
    counts[bit_position % p] += 1u;
}

static void normalize_bit_counts_mod_mersenne(uint32_t* counts, uint32_t p) {
    uint64_t carry = 0u;
    for (uint32_t i = 0; i < p; i++) {
        uint64_t total = (uint64_t)counts[i] + carry;
        counts[i] = (uint32_t)(total & 1u);
        carry = total >> 1;
    }

    while (carry != 0u) {
        for (uint32_t i = 0; i < p && carry != 0u; i++) {
            uint64_t total = (uint64_t)counts[i] + (carry & 1u);
            counts[i] = (uint32_t)(total & 1u);
            carry = (carry >> 1) + (total >> 1);
        }
    }
}

static void counts_to_words(const uint32_t* counts, uint32_t p, uint32_t* out, uint32_t words) {
    set_zero_words(out, words);
    for (uint32_t i = 0; i < p; i++) {
        if (counts[i] != 0u) {
            out[i / 32u] |= (uint32_t)(1u << (i % 32u));
        }
    }
    mask_top_word(out, words, p);
}

static void reduce_product_mod_mersenne(
    const uint32_t* product,
    uint32_t product_words,
    uint32_t p,
    uint32_t* counts,
    uint32_t* out,
    uint32_t words
) {
    memset(counts, 0, (size_t)p * sizeof(uint32_t));
    uint32_t max_product_bits = 2u * p;
    uint32_t available_bits = product_words * 32u;
    if (max_product_bits > available_bits) {
        max_product_bits = available_bits;
    }

    for (uint32_t bit = 0; bit < max_product_bits; bit++) {
        uint32_t word = bit / 32u;
        uint32_t mask = (uint32_t)(1u << (bit % 32u));
        if ((product[word] & mask) != 0u) {
            add_bit_count(counts, p, bit);
        }
    }

    normalize_bit_counts_mod_mersenne(counts, p);
    counts_to_words(counts, p, out, words);

    if (words_are_mersenne_modulus(out, p, words)) {
        set_zero_words(out, words);
    }
}

static void square_mod_mersenne(
    const uint32_t* value,
    uint32_t p,
    uint32_t words,
    uint32_t* product,
    uint32_t product_words,
    uint32_t* counts,
    uint32_t* out
) {
    memset(product, 0, (size_t)product_words * sizeof(uint32_t));

    for (uint32_t i = 0; i < words; i++) {
        uint64_t carry = 0u;
        for (uint32_t j = 0; j < words; j++) {
            uint64_t current =
                (uint64_t)value[i] * (uint64_t)value[j]
                + (uint64_t)product[i + j]
                + carry;
            product[i + j] = (uint32_t)current;
            carry = current >> 32;
        }

        uint32_t k = i + words;
        while (carry != 0u && k < product_words) {
            uint64_t current = (uint64_t)product[k] + carry;
            product[k] = (uint32_t)current;
            carry = current >> 32;
            k++;
        }
    }

    reduce_product_mod_mersenne(product, product_words, p, counts, out, words);
}

EXPORT LucasLehmerResult lucas_lehmer_mersenne(uint32_t exponent, int fit_max_coeff, uint32_t max_bits) {
    ensure_constants();

    LucasLehmerResult result;
    result.exponent = exponent;
    result.status = 0;
    result.is_mersenne_prime = 0;
    result.iterations = 0u;
    result.word_count = 0u;
    result.final_low64 = 0u;
    result.final_popcount = 0u;
    result.exponent_fit = fit_value((double)exponent, fit_max_coeff);

    if (exponent < 2u) {
        result.status = 1;
        return result;
    }
    if (max_bits > 0u && exponent > max_bits) {
        result.status = 2;
        return result;
    }
    if (!is_u32_prime(exponent)) {
        result.status = 3;
        return result;
    }
    if (exponent == 2u) {
        result.is_mersenne_prime = 1;
        result.word_count = 1u;
        result.final_low64 = 0u;
        result.final_popcount = 0u;
        return result;
    }

    uint32_t words = (exponent + 31u) / 32u;
    uint32_t product_words = words * 2u + 2u;
    uint32_t* state = (uint32_t*)calloc(words, sizeof(uint32_t));
    uint32_t* next_state = (uint32_t*)calloc(words, sizeof(uint32_t));
    uint32_t* product = (uint32_t*)calloc(product_words, sizeof(uint32_t));
    uint32_t* counts = (uint32_t*)calloc(exponent, sizeof(uint32_t));

    if (!state || !next_state || !product || !counts) {
        free(state);
        free(next_state);
        free(product);
        free(counts);
        result.status = 4;
        return result;
    }

    set_small_words(state, words, 4u);
    mask_top_word(state, words, exponent);

    for (uint32_t iteration = 0u; iteration < exponent - 2u; iteration++) {
        square_mod_mersenne(
            state,
            exponent,
            words,
            product,
            product_words,
            counts,
            next_state
        );
        subtract_small_mod_mersenne(next_state, exponent, words, 2u);

        uint32_t* swap = state;
        state = next_state;
        next_state = swap;
        result.iterations = iteration + 1u;
    }

    result.word_count = words;
    result.final_low64 = words_low64(state, words);
    result.final_popcount = words_popcount(state, words);
    result.is_mersenne_prime = words_are_zero(state, words) ? 1 : 0;

    free(state);
    free(next_state);
    free(product);
    free(counts);
    return result;
}

EXPORT RelationalLLPseudoResult relational_ll_pseudo_probe(uint32_t exponent, int fit_max_coeff, uint32_t max_bits) {
    ensure_constants();

    RelationalLLPseudoResult result;
    memset(&result, 0, sizeof(RelationalLLPseudoResult));
    result.exponent = exponent;
    result.exponent_fit = fit_value((double)exponent, fit_max_coeff);

    if (exponent < 2u) {
        result.status = 1;
        return result;
    }
    if (max_bits > 0u && exponent > max_bits) {
        result.status = 2;
        return result;
    }
    if (!is_u32_prime(exponent)) {
        result.status = 3;
        return result;
    }

    uint32_t iterations = exponent > 2u ? exponent - 2u : 0u;
    uint32_t words = (exponent + 31u) / 32u;
    uint32_t product_words = words * 2u + 2u;
    uint32_t sample_steps[LL_PSEUDO_SAMPLE_COUNT] = {0u};
    uint32_t sample_count = 0u;
    unique_sorted_sample_steps(iterations, sample_steps, &sample_count);

    uint32_t* state = (uint32_t*)calloc(words, sizeof(uint32_t));
    uint32_t* next_state = (uint32_t*)calloc(words, sizeof(uint32_t));
    uint32_t* product = (uint32_t*)calloc(product_words, sizeof(uint32_t));
    uint32_t* reduction_counts = (uint32_t*)calloc(exponent, sizeof(uint32_t));
    uint32_t* positions = (uint32_t*)calloc(exponent, sizeof(uint32_t));
    uint32_t* feature_buckets = (uint32_t*)calloc(exponent, sizeof(uint32_t));

    if (!state || !next_state || !product || !reduction_counts || !positions || !feature_buckets) {
        free(state);
        free(next_state);
        free(product);
        free(reduction_counts);
        free(positions);
        free(feature_buckets);
        result.status = 4;
        return result;
    }

    if (exponent == 2u) {
        set_zero_words(state, words);
    } else {
        set_small_words(state, words, 4u);
        mask_top_word(state, words, exponent);
    }

    result.status = 0;
    result.iterations = iterations;
    result.word_count = words;
    result.sample_count = sample_count;

    uint32_t next_sample_index = 0u;
    for (uint32_t step = 0u; step <= iterations; step++) {
        if (
            next_sample_index < sample_count
            && step == sample_steps[next_sample_index]
        ) {
            result.samples[next_sample_index] = relational_ll_sample_features(
                state,
                exponent,
                step,
                iterations,
                positions,
                feature_buckets
            );
            next_sample_index++;
        }

        if (step < iterations) {
            square_mod_mersenne(
                state,
                exponent,
                words,
                product,
                product_words,
                reduction_counts,
                next_state
            );
            subtract_small_mod_mersenne(next_state, exponent, words, 2u);

            uint32_t* swap = state;
            state = next_state;
            next_state = swap;
        }
    }

    result.final_low64 = words_low64(state, words);
    result.final_popcount = words_popcount(state, words);
    result.is_mersenne_prime = words_are_zero(state, words) ? 1 : 0;

    free(state);
    free(next_state);
    free(product);
    free(reduction_counts);
    free(positions);
    free(feature_buckets);
    return result;
}

EXPORT void batch_relational_ll_pseudo_probe(
    RelationalLLPseudoResult* out,
    const uint32_t* exponents,
    int count,
    int fit_max_coeff,
    uint32_t max_bits
) {
    if (!out || !exponents || count <= 0) {
        return;
    }

    for (int i = 0; i < count; i++) {
        out[i] = relational_ll_pseudo_probe(exponents[i], fit_max_coeff, max_bits);
    }
}

EXPORT RelationalNumber relational_mul(RelationalNumber a, RelationalNumber b) {
    RelationalNumber res = {
        (int16_t)(a.c_L + b.c_L),
        (int16_t)(a.c_J + b.c_J),
        (int16_t)(a.c_P + b.c_P),
        (int16_t)(a.c_W + b.c_W)
    };
    return res;
}

EXPORT RelationalNumber relational_div(RelationalNumber a, RelationalNumber b) {
    RelationalNumber res = {
        (int16_t)(a.c_L - b.c_L),
        (int16_t)(a.c_J - b.c_J),
        (int16_t)(a.c_P - b.c_P),
        (int16_t)(a.c_W - b.c_W)
    };
    return res;
}

EXPORT void batch_mul(RelationalNumber* out, const RelationalNumber* a, const RelationalNumber* b, int count) {
    for (int i = 0; i < count; i++) {
        out[i].c_L = a[i].c_L + b[i].c_L;
        out[i].c_J = a[i].c_J + b[i].c_J;
        out[i].c_P = a[i].c_P + b[i].c_P;
        out[i].c_W = a[i].c_W + b[i].c_W;
    }
}

EXPORT void batch_div(RelationalNumber* out, const RelationalNumber* a, const RelationalNumber* b, int count) {
    for (int i = 0; i < count; i++) {
        out[i].c_L = a[i].c_L - b[i].c_L;
        out[i].c_J = a[i].c_J - b[i].c_J;
        out[i].c_P = a[i].c_P - b[i].c_P;
        out[i].c_W = a[i].c_W - b[i].c_W;
    }
}

EXPORT double run_internal_benchmark(RelationalNumber a, RelationalNumber b, int64_t iterations) {
    RelationalNumber out = a;
    for (int64_t i = 0; i < iterations; i++) {
        out.c_L = out.c_L + b.c_L + (int16_t)(i % 2);
        out.c_J = out.c_J + b.c_J;
        out.c_P = out.c_P + b.c_P;
        out.c_W = out.c_W + b.c_W;
        
        out.c_L = out.c_L - b.c_L;
        out.c_J = out.c_J - b.c_J;
        out.c_P = out.c_P - b.c_P;
        out.c_W = out.c_W - b.c_W;
    }
    return decode_value(out);
}
