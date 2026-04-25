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

Replace $c_0 + c_1 \dot s + c_2 \dot s^2$ with $d_0 + d_1 \dot s$, whose
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

I have picked coefficients in $[0, 5)$. Some others pick ${-1, 0, 1}$.   
Better to have a mean value of zero, or errors will be monotonically increasing.  

### Error Propagation in Multiplication

Ciphertexts: $m_1 \rightarrow (-v_1 \cdot a \cdot s + m_1 + e_{11}, v_1 \cdot a + e_{12})$
or $(A_0, A_1)$,    
and $m_2 \rightarrow (-v_2 \cdot a \cdot s + m_2 + e_{21}, v_2 \cdot a + e_{22})$,
or $(B_0, B_1)$.  

Evaluation key: $(-a' \cdot s + P \cdot s^2 + e_{evk}, a')$ is muliplied with
$c_2 = A_1 \cdot B_1$.

The error term is $(e_{evk} \cdot A_1 \cdot B_1 + evk[0] \cdot (e_{12} \cdot v_1 + e_{22} \cdot v_2), a' \cdot (e_{12} \cdot v_2 + e_{22} \cdot v_1) )$

Terms of the form $e \cdot a$ cannot be ignored, as $a$ is a random polynomial.  
It is not clear how this error is managed.
