#ifndef RELATIONAL_CALCULATOR_H
#define RELATIONAL_CALCULATOR_H

#include <stdint.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

typedef struct {
    int16_t c_L;
    int16_t c_J;
    int16_t c_P;
    int16_t c_W;
} RelationalNumber;

EXPORT int init_lattice(int max_coeff);
EXPORT void free_lattice();
EXPORT int get_lattice_size();
EXPORT RelationalNumber encode_value(double val);
EXPORT double decode_value(RelationalNumber num);
EXPORT RelationalNumber relational_mul(RelationalNumber a, RelationalNumber b);
EXPORT RelationalNumber relational_div(RelationalNumber a, RelationalNumber b);
EXPORT void batch_mul(RelationalNumber* out, const RelationalNumber* a, const RelationalNumber* b, int count);
EXPORT void batch_div(RelationalNumber* out, const RelationalNumber* a, const RelationalNumber* b, int count);

#endif // RELATIONAL_CALCULATOR_H
