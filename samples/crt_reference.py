from sympy import symbols, Poly
from sympy.ntheory.modular import crt

# Example: polynomial coefficients under RNS with moduli [97, 101, 103]
# Suppose your polynomial is of degree < N, and you have:
#   coeffs_rns[j] = [c0_j, c1_j, c2_j]   for coefficient j
# where c0_j in mod 97, c1_j in mod 101, c2_j in mod 103

moduli = [97, 101, 103]

# Example: coeffs_rns[i] is the i‑th coefficient in RNS form
coeffs_rns = [
    [42, 75,  8],   # coefficient of x^0
    [50, 10, 30],   # coefficient of x^1
    [13, 88, 97],   # coefficient of x^2
]
n = len(coeffs_rns)   # degree + 1

# Convert each coefficient to canonical (big) integer via CRT
coeffs_canon = []
for rns_coeffs in coeffs_rns:
    c, _M = crt(moduli, rns_coeffs, symmetric=False)  # CRT gives (value, product)
    coeffs_canon.append(c)

# Reconstruct polynomial in canonical form
x = symbols("x")
P = Poly.from_list(coeffs_canon[::-1], x)  # from_list wants big‑endian
# or just use Expr if you prefer:
P_expr = sum(c * x**i for i, c in enumerate(coeffs_canon))

print("Canonical coefficients:", coeffs_canon)
print("Polynomial in canonical form:", P_expr)

