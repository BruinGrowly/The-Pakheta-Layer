#include "relational_calculator.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define BASE 30.0

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

int compare_items(const void* a, const void* b) {
    double exp_a = ((LatticeItem*)a)->exponent;
    double exp_b = ((LatticeItem*)b)->exponent;
    if (exp_a < exp_b) return -1;
    if (exp_a > exp_b) return 1;
    return 0;
}

EXPORT int init_lattice(int max_coeff) {
    L0 = (sqrt(5.0) - 1.0) / 2.0;
    J0 = sqrt(2.0) - 1.0;
    P0 = exp(1.0) - 2.0;
    W0 = log(2.0);

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
    if (val <= 0) {
        RelationalNumber zero = {0, 0, 0, 0};
        return zero;
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
    double exponent = num.c_L * L0 + num.c_J * J0 + num.c_P * P0 + num.c_W * W0;
    return pow(BASE, exponent);
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
