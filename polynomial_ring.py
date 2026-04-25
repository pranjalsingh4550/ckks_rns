"""
TurboHE's CKKS implementation using RNS.
This file has CKKS. RNS is in rns.py.
Sympy (symbolic python) supports infinite precision integers, polynomials,
rings, moduli, etc.

With a `modulus` attribute, sympy also uses balanced ring representatives as in
TurboHE.
So, `modulus = 200` -> coefficients in [-100, +100).
"""

import sympy
from sympy import Poly
from sympy.abc import x
import os
import numpy as np

verbose = False


try:
	n = int(os.getenv('DEGREE'))
except:
	n = 100

try:
	q = int(os.getenv('MODULUS'))
except:
	q = 1020304050607

if os.getenv('VERBOSE') == '1':
	verbose = True

mod_poly = Poly(x ** n + 1, x, modulus = q)

def failed():
	""" Perplexity-generated code. Does not run (let alone run correctly).
	"""
	mod2 = Poly(x ** 203 * 30405 + x + 601, x, domain = 'ZZ[200]')
	print(f"checking modulus: {mod2}\t{mod2 + 1}")
	mod2 = Poly(x ** 203 * 30405 + x + 601, x, domain = ZZ.map([200]))
	print(f"checking modulus: {mod2}\t{mod2 + 1}")

# Helpers
def print_list(l, depth = 0):
	for e in l:
		if isinstance(e, list):
			print_list(e, depth = depth + 1)
		else:
			ws = "\t" * depth
			print(f"{ws}{e}")
	print("\n")

def to_ciphertext(poln, mod = q):
	""" The plaintext space in TurboHE is Z[x]/(x^n + 1).
	The ciphertext space is the same modulo q.
	This does NOT encrypt @poln, just projects it to the ciphertext space.
	"""
	if verbose:
		print(f"# to_ciphertext: {mod}")

	as_sympy_poln = Poly(poln, modulus = mod)
	as_sympy_poln.degree() < n
	return as_sympy_poln

def make_random_poly(mod = q, deg = n, max_coeff = None):
	""" To generate small polynomials, use @mod = domain modulus, but change
	@max_coeff.
	Don't change the @mod, that is a headache waiting to strike.
	"""
	if max_coeff is None:
		max_coeff = mod
	if max_coeff <= 1:
		max_coeff = 2
	if verbose:
		print(f"# make_random_poly: q={mod} n={deg} max_coeff={max_coeff}")

	assert max_coeff > 1

	rnd = sympy.random_poly(x, deg - 1, 0, max_coeff - 1)
	return to_ciphertext(rnd, mod = mod)

def coeffs(poln):
	""" Highest first (Leading coefficient first)
	"""
	return Poly(poln).all_coeffs()

def assert_is_ct(ciphertext):
	""" Check datatypes, etc
	"""
	assert isinstance(ciphertext[0], Poly)
	assert isinstance(ciphertext[1], Poly)
	assert len(ciphertext) == 2
	assert ciphertext[0].domain.mod == ciphertext[1].domain.mod

def get_coprime(num):
	""" Get a coprime to a single number.
	Need to make this better.
	"""
	assert num.is_integer()
	if verbose:
		print(f"get_coprime({num})")
	# return sympy.ntheory.nextprime(num)
	start = num * 2 + 100
	while True:
		if sympy.ntheory.modular.gcd(num, start) == 1:
			return start
		start += 1

	# main

def coeffs_list(poln):
	""" Highest first (leading coefficient)
	"""
	assert isinstance(poln, Poly)
	l = Poly(poln).all_coeffs()

	if verbose:
		print(f"# coefficients are {l[:30]} ...")
		pass

	assert "is_integer" in dir(l[0])
	assert l[0].is_integer

	j = [ int(t) for t in l ]
	return j

def coeffs_to_polynomial(cf_list, mod = q):
	assert isinstance(cf_list, list)
	assert cf_list[0].is_integer()

	degree = len(cf_list)
	retval = Poly(0 * x, x, modulus = mod)

	if verbose:
		print(f"# coeffs_to_polynomial: mod={mod} degree={degree}")

	for cf in cf_list:
		degree -= 1
		retval += Poly(x ** degree, x, modulus = mod)

	if verbose:
		print(f"coeffs_to_polynomial: mod {mod}\n{cf_list}\n{retval}")

	return retval

def polynomial_new_domain(poln, new_mod):
	l = coeffs_list(poln)
	ret = coeffs_to_polynomial(l, mod = new_mod)
	
	return ret

def poly_mult(p1, p2, mod = q, divisor_degree = n):
	""" Gentle reminder: all expressions are of degree `n - 1`, and the divisor
	is of degree `n`.
	Finds the remainder against the cyclotomic polynomial.
	"""
	assert isinstance(p1, Poly)
	assert isinstance(p2, Poly)
	assert p1.degree() == p2.degree()
	if verbose:
		print(f"# poly_mult: degree={divisor_degree}")
		print(f"# poly_mult: moduli are {mod}, {p1.domain.mod}, {p2.domain.mod}")

	mod = Poly(x ** divisor_degree + 1, x, modulus = mod)

	return (p1 * p2).rem(mod)

# Encryption helpers start here.

def get_encryption_key_distribution(mod = q, deg = n):
	""" \\Chi_{enc}
	Values need not be small or large or something.
	Using uniform random polynomials.

	Correction: I think we need to use small moduli.
	"""
	if verbose:
		print(f"# get_encryption_key_distribution: {mod} {deg}")
	return make_random_poly(mod = mod, deg = deg , max_coeff = 5)

def get_noise(mod = q, deg = n, max_coeff = 5):
	""" \\Chi_{err}.
	Might be incorrect.
	Returns small-coefficient polynomials.
	"""
	# return Poly(0, x, modulus = mod)
	assert max_coeff.is_integer()

	""" attempt 2 - get values in {-1, 0, 1}.
	"""
	coeffs = np.random.randint(9, high = 21, size = deg, dtype = int) // 10 - 1
	return coeffs_to_polynomial(list(coeffs), mod = mod)
	coeffs = coeffs // 10
	return make_random_poly(mod = mod, deg = deg, max_coeff = 5)

def get_key(mod = q, deg = n):
	""" \\Chi_{key}.
	The encryption key is supposed to be small.
	"""
	return make_random_poly(mod, deg, max_coeff = 3)

def get_domain_inverse(num, mod = q):
	""" inverse of @num in GF(q)
	num * retval == 1 in GF(mod)
	"""
	if verbose:
		print(f"# get_domain_inverse({num}) modulo {mod}")
		ret = sympy.mod_inverse(num, mod)
		print(f"# got inverse {ret}")
		assert (int(ret) * int(num)) % int(mod) == 1
		return ret

	else:
		return sympy.mod_inverse(num, mod)

def generate_evaluation_key(rns_context, mod = q, deg = n):
	""" Hard-code the KSK/key-switching-key definition to run on s' = s^2.
	Why is the error sampled from \\Chi_{err}? Why not from the new modulus?
	"""
	assert len(rns_context['sk']) == 2
	assert (rns_context['sk'][0]).is_integer()
	sk = rns_context['sk'][1]
	assert isinstance(sk, Poly)

	if verbose:
		print(f"# generate evaluation key: on sk={sk}\n")

	# new modulus
	pq = int(mod) * int(rns_context['P'])

	a_new = make_random_poly(mod = pq, deg = deg)
	e_new = get_noise(mod = pq, deg = deg)

	sk_coeffs = coeffs_list(sk)
	sk_new_domain = coeffs_to_polynomial(sk_coeffs, mod = pq)
	sk_squared = poly_mult(sk_new_domain, sk_new_domain, mod = pq,
			divisor_degree = deg)

	# evk = (-b', a')
	# Possible error 1: when doing a * s', should I do s^2 in the domain q
	# or P.q?
	evk = (
		- poly_mult(a_new, sk_new_domain, mod = pq, divisor_degree = deg) + \
			rns_context['P'] * sk_squared + \
			e_new,
		a_new,
		)

	return evk


def setup_encryption(mod = q, deg = n):
	""" Returns sk and pk.
	Possible mistake: all operations here are already mod q.
	This is the KeyGen step in the TurboHE paper.
	Also includes P, evk, and more.

	precompute p_inv here.
	"""
	rns_context = {}
	if (verbose):
		print(f"# setup_encryption: {mod} {deg}")
	s = get_key(mod, deg)
	a = make_random_poly(mod, deg)
	err = get_noise(mod, deg)

	assert a.domain.mod == s.domain.mod
	assert err.domain.mod == a.domain.mod

	sk = (1, s)
	b = - poly_mult(a, s, mod = mod, divisor_degree = deg) + err
	pk = (b, a)

	P = get_coprime(mod)

	rns_context['sk'] = sk
	rns_context['pk'] = pk
	rns_context['P']  = P
	rns_context['P_inv'] = get_domain_inverse(P, mod)

	rns_context['evk'] = generate_evaluation_key(rns_context, mod = q, deg = n)

	return rns_context

def key_switching_key(keys, s_new, mod = q, deg = n):
	""" Not sure about the semantics here: what is s and s'?
	s_new is s', or s-prime. The domain does not have a modulus.
	ksk = [ - (a')(s) + P.s' + e' ] mod (P.q)
	Change domain from q to P.q

	NOT USING this function at the moment.
	It appears that s' in the paper text is just a placeholder for
	something-not-s, which is s^2 for us.
	"""
	sk = keys['sk']
	assert len(sk) == 2
	assert (sk[0]).is_integer()
	s_old = sk[1]
	assert isinstance(s_old, Poly)
	assert s_new.domain.is_IntegerRing # an integer ring without a modulus.
	assert 'mod' not in s_new.domain.__dir__()

	# new modulus
	pq = mod * keys['P']

	a_new = make_random_poly(mod = pq, deg = deg)
	e_new = get_noise(mod, deg)

	# Convert s_old.
	s_old_coeffs = coeffs_list(s_old)
	s_old_mod_changed = coeffs_to_polynomial(s_old_coeffs, mod = pq)

	ksk = (
		- poly_mult(a_new, s_old_mod_changed),
		# Working here!!!
		)


def encrypt_plaintext(pt_poln, keys, mod = q, deg = n):
	""" Encrypts polynomials, not plaintext. Not at the moment.
	@pt_poln: plaintext polynomial
	DOUBT: is @pt_poln already mod @q? I have assumed yes.
	@keys: {'sk': XXX, 'pk': YYY}
	This samples errors e0, e1, which can be "forgotten" this point onwards.
	"""
	assert isinstance(keys, dict)
	assert 'sk' in keys
	assert 'pk' in keys
	assert isinstance(pt_poln, Poly)

	v = get_encryption_key_distribution(mod = mod, deg = deg)
	e0 = get_noise(mod = mod, deg = deg)
	e1 = get_noise(mod = mod, deg = deg)

	""" Operation: ct = (c0, c1) = v.pk + (m + e0, e1) mod q
	"""

	if verbose:
		print(f"# encrypt_plaintext: completed v, e0, e1. Will multiply now\n")

	ciphertext = (
		(poly_mult(v, keys['pk'][0], mod = mod, divisor_degree = deg) \
			+ pt_poln + e0),
		(poly_mult(v, keys['pk'][1], mod = mod, divisor_degree = deg) + e1)
	)

	return ciphertext

def decrypt_ciphertext(ciphertext, keys, mod = q, deg = n):
	""" ciphertext = (c0, c1).
	Operation: return m = < ct, sk > = (c0 + c1.secret_key) mod q
	"""
	assert isinstance(ciphertext, tuple)
	assert isinstance(ciphertext[0], Poly)
	assert isinstance(ciphertext[1], Poly)

	pt = ciphertext[0] + poly_mult(ciphertext[1], keys['sk'][1], mod = mod,
				divisor_degree = deg)
	return pt

def ciphertext_add(ct1, ct2, mod = n, deg = q):
	""" Doesn't use the degree.
	"""
	if verbose:
		print(f"ciphertext_add(): mod {mod}\n")

	assert isinstance(ct1[0], Poly)
	assert isinstance(ct2[1], Poly)
	assert len(ct1) == len(ct2) == 2
	assert ct1[0].domain.mod == ct2[0].domain.mod
	assert_is_ct(ct1)
	assert_is_ct(ct2)

	return (ct1[0] + ct2[0], ct1[1] + ct2[1])

def ciphertext_multiply(ct1, ct2, keys, mod = n, deg = q,
                        decrypt_and_return = False):
	""" Following notation from section 2D.
	Explanation from ChatGPT:
	- The multiplied **ciphertext** is
		(c0, c1, c2)
			= (a0*b0,
			   a0*b1 + a1 * b0,
			   a1*b1)
	- And this can be decrypted as:
		output_plaintext = c0 + c1*s + c2* s^2,
	  analogous to decryption of simple plaintext (c0 + c1*s)
	- Or, we can RELINEARIZE this into ct_{mult}, another 2-tuple, and
	  further add/multiply with more numbers:
		ct_{mult} = (c0, c1) + [ P^{-1} \\cdot c2 \\cdot evk ] \\mod q

	  The second term is a 2-tuple because evk is a 2-tuple.

        This function does option 1 if @decrypt_and_return == True.
	"""
	assert_is_ct(ct1)
	assert_is_ct(ct2)

	P = keys['P']
	assert P.is_integer()

	c0 = poly_mult(ct1[0], ct2[0], mod = mod, divisor_degree = deg)
	c1 = poly_mult(ct1[0], ct2[1], mod = mod, divisor_degree = deg)	\
	     + poly_mult(ct1[1], ct2[0], mod = mod, divisor_degree = deg)
	c2 = poly_mult(ct1[1], ct2[1], mod = mod, divisor_degree = deg)

	if decrypt_and_return:
		sk = keys['sk'][1]
		output = c0 + \
		         poly_mult(c1, sk, mod = mod, divisor_degree = deg) + \
		         poly_mult(sk,
		                   poly_mult(c2, sk, mod = mod, divisor_degree = deg),
		                   mod = mod,
		                   divisor_degree = deg)

		return output

	P_inv = keys['P_inv']
	evk = keys['evk']

	assert isinstance(evk, tuple)
	assert isinstance(evk[0], Poly)
	assert isinstance(evk[1], Poly)
	assert len(evk) == 2

	evk0 = polynomial_new_domain(evk[0], mod)
	evk1 = polynomial_new_domain(evk[1], mod)

	ct_mult = (
		c0 + (P_inv * poly_mult(c2, evk0)),
		c1 + (P_inv * poly_mult(c2, evk1))
		)

	return ct_mult


def get_ratios(pt1, pt2):
	""" compare plaintexts
	"""
	assert isinstance(pt1, Poly)
	assert isinstance(pt2, Poly)

	mod = pt1.domain.mod
	assert mod == pt2.domain.mod

	if (verbose):
		print(f"get_ratios()")

	difference = pt1 - pt2
	diff_ratio = [ abs(int(t)) / mod for t in coeffs_list(difference) ]
	avg = sum(diff_ratio) / len(diff_ratio)
	print(f"average difference ratio: {avg} | {diff_ratio[:15]} ...")

	if verbose:
		print(f"differences are {diff_ratio}\n***************");


def trial(mod, deg):
	""" Encrypt and decrypt a random polynomial.
	Returns (true_value + v.e_pk + e0 + sk.e1)
	e_pk from setup_encryption()
	e0, e1 from encrypt_plaintext()
	"""

	pt = make_random_poly(mod, deg)
	print(f"Made random polynomial plaintext {pt}")
	k = setup_encryption(mod, deg)
	if verbose:
		print(f"*** ***\nkeys: {k}\n*** ***\n")
	ct = encrypt_plaintext(pt, k, mod, deg)
	print(f"generated ciphertext (c0, c1):\n{ct[0]}\n{ct[1]}")
	decrypted = decrypt_ciphertext(ct, k, mod, deg)
	difference = decrypted - pt
	diff_coeff = coeffs(difference)
	diff_ratio = [int(t) / mod for t in diff_coeff]

	print(f"-----------------\nOriginal PT:\n{pt}\nDecrypyted pt:\n{decrypted}"
	      f"\nDifference\n{difference}\n{diff_ratio}")

	print(f"\n\n--------------------------------------\nMULTIPLICATION\n")
	trial_mul_ciphertext(mod, deg)


def ckks_add_wrapper(p1, p2, mod = q, deg = n):
	k = setup_encryption(mod, deg)
	ct1 = encrypt_plaintext(p1, k, mod, deg)
	ct2 = encrypt_plaintext(p2, k, mod, deg)

	ct_sum = ciphertext_add(ct1, ct2)
	if verbose:
		print(f"add_wrapper: completed\n")
	p_out = decrypt_ciphertext(ct_sum, k, mod, deg)

	return p_out

def trial_add(mod, deg):
	""" m1 and m2 use different encryption key values (v1, v2), but the same
	pk and sk.
	Error: same error term as trial(), for two terms.
	"""
	pt1 = make_random_poly(mod, deg)
	pt2 = make_random_poly(mod, deg)
	k = setup_encryption(mod, deg)
	print(f"\n\nADDITION\n{pt1}\n{pt2}\n{k}")
	ct1 = encrypt_plaintext(pt1, k, mod, deg)
	ct2 = encrypt_plaintext(pt2, k, mod, deg)

	ct = ciphertext_add(ct1, ct2)
	print(f"Completed addition")
	pt_out = decrypt_ciphertext(ct, k, mod, deg)
	print(f"decrypted output:\n{pt_out}")
	print(f"correct output:\n{pt1 + pt2}")

def trial_mul_ciphertext(mod, deg):
	""" m1 and m2 use different encryption key values (v1, v2), but the same
	pk and sk.
	Error: same error term as trial(), for two terms.
	Use moderately small m1, m2 values to avoid integer overflow.
	"""
	pt1 = make_random_poly(mod = mod, deg = deg, max_coeff = 10000)
	pt2 = make_random_poly(mod = mod, deg = deg, max_coeff = 10000)
	k = setup_encryption(mod, deg)
	print(f"\n\nMULTIPLICATION\n{pt1}\n{pt2}\n")
	ct1 = encrypt_plaintext(pt1, k, mod, deg)
	ct2 = encrypt_plaintext(pt2, k, mod, deg)

	ct = ciphertext_multiply(ct1, ct2, k, mod = mod, deg = deg)
	early_output = ciphertext_multiply(ct1, ct2, k, mod = mod, deg = deg,
			decrypt_and_return = True)
	print(f"Completed multiplication")
	pt_out = decrypt_ciphertext(ct, k, mod, deg)

	true_val = poly_mult(pt1, pt2, mod = mod, divisor_degree = deg)

	print(f"decrypted output:\n{pt_out}")
	print(f"correct output:\n{true_val}")

	get_ratios(pt_out, true_val)

	print(f"\nEarly output: {early_output}")
	print(f"\n------\nEarly decryption output:")
	get_ratios(early_output, true_val)


def main():
	print(f"Using n = {n}, q = {q}.\nModulus polynomial: {mod_poly}")
	trial(q, n)



if __name__ == "__main__":
	main()
