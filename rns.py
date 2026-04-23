from polynomial_ring import *
from sympy.ntheory.modular import crt

""" Useful functions:
sympy.factorint(60)	= {2: 2, 3: 1, 5: 1}
sympy.nextprime(1 << 64)	= 18446744073709551629
list(sympy.primerange(90, 110)	= [97, 101, 103, 107, 109]
"""

""" RNS representation:
poly_to_rns(polynomial) factorizes polynomial.domain.mod, and returns a
list of polynomials [p1, p2, p3, p4, ... ].
Use *.domain.mod to get the modulus for each polynomial. The terms will
probably be in sorted order.

References:
https://www.geeksforgeeks.org/python/python-sympy-crt-method/
https://github.com/sympy/sympy/blob/master/sympy/ntheory/residue_ntheory.py

Converting residues to a number: no in-built function for polynomials. We'll do
it for each coefficient.
	help(sympy.polys.galoistools.gf_crt)
	help(sympy.ntheory.modular.crt)
"""

# Helpers
def is_valid_modulus(q):
	""" Check if q has any multiplicities, i.e. if any prime factor occurs
	twice.
	Returns False or the list of factors.
	"""
	if verbose:
		print(f"# is_valid_modulus({q})")
	assert q > 2
	assert q.is_integer()

	factors = sympy.factorint(q)
	for power in factors.values():
		if power == 1:
			continue
		if verbose:
			print(f"Not valid modulus: {q}\n{dict(sympy.factorint(q))}")
		return False

	return list(sympy.factorint(q))

def random_composite_modulus():
	""" Incomplete function.
	Returns a "valid" modulus which passes is_valid_modulus().
	"""
	factors = sympy.primerange(90, 110)
	product = 1
	for f in factors:
		product *= f

	if verbose:
		print(f"random composite modulus: {product}")
	return product

# RNS

def poly_to_rns_components(poln):
	""" Returns a list of per-factor components.
	"""
	assert isinstance(poln, Poly)
	mod = poln.domain.mod

	if verbose:
		print(f"# poly_to_rns_components: q={mod}\n{poln}")

	factors = is_valid_modulus(mod)
	if factors is None:
		print(f"Invalid modulus")
		return None

	components = []
	for factor in factors:
		residue = Poly(poln, modulus = factor)
		components.append(residue)

	return components

def residues_to_basis(rs):
	assert isinstance(rs[0], Poly)
	return [t.domain.mod for t in rs]

def residues_to_domain(rs):
	assert isinstance(rs[0], Poly)
	product = 1
	for t in rs:
		product *= t.domain.mod

	assert product > 10
	return product

def add_residues(rs1, rs2, ckks = False):
	""" Add two sets of residues
	Use CKKS if ckks == True.
	"""
	assert isinstance(rs1, list)
	assert isinstance(rs2, list)
	assert isinstance(rs1[0], Poly)
	assert isinstance(rs2[0], Poly)
	assert len(rs1) == len(rs2)

	ret = [None] * len(rs1)

	try:
		for i in range(len(rs1)):
			if ckks == False:
				ret[i] = rs1[i] + rs2[i]
			if ckks == True:
				modulus = rs1[i].domain.mod
				ret[i] = ckks_add_wrapper(rs1[i], rs2[i],
						      mod = modulus)

			assert ret[i] is not None
			if verbose:
				print(f"added [{i}])")
		return ret
	except Exception as e:
		print(f"Error in addition. Bases are\n"
			f"{residues_to_basis(rs1)}\n"
			f"{residues_to_basis(rs2)}"
		)
		print(e)
		exit(-1)
	return None

def residues_to_canonical(rs, deg = None):
	""" Find the basis, the "baseline" domain which is their product, and
	the original polynomial in the the baseline domain.

	There might be a simple, optimized, inbuilt routine. For now, we find
	each coefficient separately.
	Pitfall: big-endian and little-endian polynomial coefficient ordering.
	Pitfall: rs might not be sorted.
	"""
	basis = residues_to_basis(rs)
	if deg is None:
		deg = n

	mod = 1
	moduli = []

	for pol in rs:
		t = pol.domain.mod
		moduli.append(t)
		mod *= t

	c = Poly(0, x, modulus = mod)
	for exponent in range(deg):
		monomial = x ** exponent
		remainder = [pol.coeff_monomial(monomial) for pol in rs]
		coeff = sympy.ntheory.modular.crt(moduli, remainder, check = True)
		assert coeff[1] == mod
		coeff = coeff[0]
		# Do check=False after testing.

		if verbose:
			print(f"x**{exponent}: moduli {moduli} coeffs"
				f"{remainder}, coeff {coeff}")
		c += Poly(coeff * monomial, x, modulus = mod)

	if verbose:
		print(f"retval {c}")

	return c

def driver(composite_modulus = None):
	if composite_modulus is None:
		composite_modulus = random_composite_modulus()

	assert is_valid_modulus(composite_modulus)
	pt1 = make_random_poly(mod = composite_modulus)
	pt2 = make_random_poly(mod = composite_modulus)
	print(f"plaintext\n{pt1}\n{pt2}")
	rs1 = poly_to_rns_components(pt1)
	rs2 = poly_to_rns_components(pt2)
	print(f"residues")
	print_list(rs1)
	print_list(rs2)

	simple_sum = pt1 + pt2
	rs_sum = add_residues(rs1, rs2)
	rs_sum_ckks = add_residues(rs1, rs2, ckks = True)

	old = residues_to_canonical(rs_sum)
	decrypted = residues_to_canonical(rs_sum_ckks)
	print(f"reference {pt1 + pt2}")
	print(f"retval    {old}")
	print(f"ckks output {decrypted}")
	print(f"difference in canonical {old - pt1 - pt2}")
	print(f"\ndifference in ckks {old - decrypted}")

if __name__ == "__main__":
	driver()
