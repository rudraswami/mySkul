# Sets and Functions

## Sets

**Definition:**
A well-defined collection of distinct objects.

**Notation:**
- Roster form: A = {1, 2, 3, 4}
- Set-builder form: A = {x : x is a positive integer less than 5}

**Standard Sets:**
- N: Natural numbers {1, 2, 3, ...}
- W: Whole numbers {0, 1, 2, 3, ...}
- Z: Integers {..., -2, -1, 0, 1, 2, ...}
- Q: Rational numbers
- R: Real numbers
- C: Complex numbers

## Types of Sets

**Empty Set (∅):**
Contains no elements. ∅ = { }

**Singleton Set:**
Contains exactly one element.

**Finite Set:**
Contains countable number of elements.
n(A) = number of elements (cardinality)

**Infinite Set:**
Contains uncountable elements.

**Equal Sets:**
A = B if both have exactly same elements.

**Equivalent Sets:**
A ~ B if n(A) = n(B)

## Subsets

**Definition:**
A ⊆ B if every element of A is in B.

**Properties:**
- Every set is subset of itself: A ⊆ A
- Empty set is subset of every set: ∅ ⊆ A
- If A ⊆ B and B ⊆ A, then A = B

**Proper Subset:**
A ⊂ B if A ⊆ B and A ≠ B

**Power Set:**
P(A) = set of all subsets of A
If n(A) = n, then n(P(A)) = 2ⁿ

## Operations on Sets

**Union:**
A ∪ B = {x : x ∈ A or x ∈ B}

**Intersection:**
A ∩ B = {x : x ∈ A and x ∈ B}

**Difference:**
A - B = {x : x ∈ A and x ∉ B}

**Complement:**
A' = {x : x ∈ U and x ∉ A}

**Symmetric Difference:**
A Δ B = (A - B) ∪ (B - A) = (A ∪ B) - (A ∩ B)

## Properties of Set Operations

**Commutative:**
- A ∪ B = B ∪ A
- A ∩ B = B ∩ A

**Associative:**
- (A ∪ B) ∪ C = A ∪ (B ∪ C)
- (A ∩ B) ∩ C = A ∩ (B ∩ C)

**Distributive:**
- A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C)
- A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)

**De Morgan's Laws:**
- (A ∪ B)' = A' ∩ B'
- (A ∩ B)' = A' ∪ B'

## Counting Formulas

**For two sets:**
n(A ∪ B) = n(A) + n(B) - n(A ∩ B)

**For three sets:**
n(A ∪ B ∪ C) = n(A) + n(B) + n(C) - n(A ∩ B) - n(B ∩ C) - n(C ∩ A) + n(A ∩ B ∩ C)

## Relations

**Definition:**
A relation R from set A to B is a subset of A × B.

**Domain:** Set of first elements
**Range:** Set of second elements
**Co-domain:** Set B

**Types of Relations:**
- Empty relation: R = ∅
- Universal relation: R = A × A
- Identity relation: R = {(a, a) : a ∈ A}

**Properties:**
- Reflexive: (a, a) ∈ R for all a ∈ A
- Symmetric: (a, b) ∈ R ⟹ (b, a) ∈ R
- Transitive: (a, b) ∈ R and (b, c) ∈ R ⟹ (a, c) ∈ R
- Equivalence: Reflexive + Symmetric + Transitive

## Functions

**Definition:**
A relation f from A to B where each element of A has exactly one image in B.

**Notation:**
f: A → B, f(a) = b

**Types of Functions:**

**One-One (Injective):**
f(a₁) = f(a₂) ⟹ a₁ = a₂

**Onto (Surjective):**
Range of f = Co-domain (B)

**Bijective:**
Both one-one and onto.

**Important Functions:**
- Identity: f(x) = x
- Constant: f(x) = c
- Polynomial: f(x) = aₙxⁿ + ... + a₀
- Rational: f(x) = p(x)/q(x)
- Modulus: f(x) = |x|
- Greatest Integer: f(x) = [x]

## Composition of Functions

**(g ∘ f)(x) = g(f(x))**

**Properties:**
- Generally not commutative: f ∘ g ≠ g ∘ f
- Associative: (f ∘ g) ∘ h = f ∘ (g ∘ h)

## Inverse Functions

**Exists only for bijective functions.**

f⁻¹: B → A such that f⁻¹(f(x)) = x

**Properties:**
- f⁻¹ ∘ f = Identity on A
- f ∘ f⁻¹ = Identity on B


