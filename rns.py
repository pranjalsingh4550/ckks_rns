from polynomial_ring import *

""" Useful functions:
sympy.factorint(60)	= {2: 2, 3: 1, 5: 1}
sympy.nextprime(1 << 64)	= 18446744073709551629
list(sympy.primerange(90, 110)	= [97, 101, 103, 107, 109]
"""

def is_valid_modulus(q):
	""" Check if q has any multiplicities, i.e. if any prime factor occurs
	twice.
	Returns False or the list of factors.
	"""
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

def driver(composite_modulus = None):
	if composite_modulus is None:
		composite_modulus = random_composite_modulus()

	assert is_valid_modulus(composite_modulus)

if __name__ == "__main__":
	driver()
