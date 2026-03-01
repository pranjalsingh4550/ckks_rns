# CKKS Using RNS

### Resources

- Existing homomorphic encryption libraries:
  [https://www.abhishek-tiwari.com/pdf/exploring-homomorphic-encryption-with-python.pdf](https://www.abhishek-tiwari.com/pdf/exploring-homomorphic-encryption-with-python.pdf).
  The linked libraries, `phe` and `concrete-python` use C/C++ backends.
- [https://openmined.org/blog/build-an-homomorphic-encryption-scheme-from-scratch-with-python](https://openmined.org/blog/build-an-homomorphic-encryption-scheme-from-scratch-with-python)
- A toy implementation using `np.int64`:
  [https://github.com/bit-ml/he-scheme/blob/main/main.py](https://github.com/bit-ml/he-scheme/blob/main/main.py)
  [https://bit-ml.github.io/blog/post/homomorphic-encryption-toy-implementation-in-python/](https://bit-ml.github.io/blog/post/homomorphic-encryption-toy-implementation-in-python/)
- SymPy:
  [https://adamgyenge.gitlab.io/teaching/info3/2025/lec4.pdf](https://adamgyenge.gitlab.io/teaching/info3/2025/lec4.pdf)

### Running It

- Interactive python:
```py
import polynomial_ring
# or
from polynomial_ring import *
```
- Start with a trial (`-i` starts a console):
```sh
python3 -i polynomial_ring.py

# or

python3 -i -c "import polynomial_ring; polynomial_ring.trial(1024, 10)"
```
- Debugging: use the environment variable `export VERBOSE=1` or
  `polynomial_ring.verbose = True`
- Specifying `n` and `q`: you can use environment variables `DEGREE` and
  `MODULUS`.

### TODO

#### Polynomial
- Change `modulus = q` wherever used to `domain = GF(q)`.
- See `help(sympy.polys.domains.finitefield.GF)`
