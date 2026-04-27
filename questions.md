# Explanation and Questions/Doubts

Reference: http://doi.org/10.1109/IPDPS54959.2023.00084   
TurboHE: Accelerating Fully Homomorphic Encryption Using FPGA Clusters

### Key Switching Key

This paper uses only the special case where $s' = s^2$.   
The "use" of the evaluation key, $evk = KSGen_{sk} (s ^2)$, as per chatGPT is to
have a linear representation of $s^2$:

$s^2 = A + B \cdot s$

for easy substitution when three-term multiplication ciphertext is being reduced
to two terms:

Replace $c_0 + c_1 \cdot s + c_2 \cdot s^2$ with $d_0 + d_1 \cdot s$, whose
ciphertext representation is like normal ciphertext: $(d_0, d_1)$.

See comments in `ciphertext_multiply()`.

#### Noise in EVK - Temporary Domain Change

`KSGen` in the paper samples error from $R_{q}$ and adds it to other terms from
$R_{P.q}$.   
Assuming all coefficients are small, I have sampled both from the larger field.   
In our implementation, addition/multiplication is easier on the same domain.   

The relinearization term is $P^{-1} \cdot c_2 \cdot evk$.  
Out of the 3 terms in `evk[0]`, the one whose domain matters ($Pq$ instead of
$q$) is NOT clear.

### Other Clarifications/FAQs

- For a binary operation on 2 ciphertexts, `a`, `sk`, `pk`, are the same, but
  `v` is different. The errors are also different, and hopefully will not
  matter.
- $a$, $a'$ are random values. $v$, $e$ are expected to be small.
- In integer-field based, encryption, small cannot be small like 0.0001, it is
  some integer like 1, 2, sometimes 0.
  $a \cdot e$ is not a "small" value to be ignored.
- Instead, try to dwarf it using scaling, such that $m_1 \cdot m_2$ is much
  larger than $m_1 \cdot e_2$, etc.

### Noise Distribution

I have picked coefficients in $[0, 5)$. Some others pick $\{-1, 0, 1\}$.   
Better to have a mean value of zero, or errors will be monotonically increasing.  

### Error Propagation in Multiplication

Integer overflow does not cause problems.  

Ciphertexts: $m_A \rightarrow (-v_A \cdot a \cdot s + m_A + e_{A1}, v_A \cdot a + e_{A2})$
or $(A_0, A_1)$,    
and $m_B \rightarrow (-v_B \cdot a \cdot s + m_B + e_{B1}, v_B \cdot a + e_{B2})$,
or $(B_0, B_1)$.  

Evaluation key: $(-a' \cdot s + P \cdot s^2 + e_{evk}, a')$ is muliplied with
$c_2 = A_1 \cdot B_1$.

The error term is $(e_{evk} \cdot A_1 \cdot B_1 + evk[0] \cdot (e_{12} \cdot v_1 + e_{22} \cdot v_2), a' \cdot a \cdot (e_{12} \cdot v_2 + e_{22} \cdot v_1) )$.  
With simplification, it is $(e_{evk} \cdot v_1 v_2 a^2 + evk[0] \cdot  e_* v_*, a' \cdot a \cdot e_* v_*) $

#### Random Error Terms

Terms of the form $e \cdot a$ cannot be ignored, as $a$ is a random polynomial.  
But $e_* v_*$ and $e_i e_j$ are negligible.
It is not clear how this error is managed.

Error in $c_0 = A_0 \cdot B_0$: $-a \cdot s \cdot (v_A e_{B1} + v_B e_{A1} ) - 2 a v_1 v_2 s e_{pk}$.
(Excluding negligible terms.)

Error in $c_1 = A_0 B_1 + A_1 B_0$: $-as(v_B e_{A2} + v_A e_{B2}) + 2 a v_A v_B e_{pk} + a (e_{A1} v_B + e_{B1} v_A)$.

Error in $c_2 = A_1 B_1$ is $a (v_A e_{B2} + v_B e_{A2})$, with no other negligible terms.

Thus, all three terms have some serious random-valued error as well as some small error terms.  
However, decryption using $m_A \cdot m_B =  c_0 + c_1 s + c_2 s^2$ succeeds as they cancel each other.  

In the current code version, multiplication succeeds when
- Decrypting using above formula instead of going through the
  $ct_{mult} = (c_0, c_1) + P^{-1} \cdot c_2 \cdot evk$ formula
- Setting $e_{evk} = 0$ in the code.

To check: uncomment `e_new = 0` in `generate_evaluation_key()`.  
To debug: `export DEGREE=1` to get only monomial polynomials.  

Further, multiplying three terms is not possible this way, as it needs to
compute an intermediate ciphertext value.  
