# Integrals

## Introduction to Integration

**Integration:** Reverse process of differentiation.

If d/dx[F(x)] = f(x), then ∫f(x)dx = F(x) + C

**C:** Constant of integration (indefinite integral)

## Standard Integrals

**Power Functions:**
- ∫xⁿ dx = xⁿ⁺¹/(n+1) + C, n ≠ -1
- ∫x⁻¹ dx = ∫(1/x) dx = ln|x| + C
- ∫dx = x + C

**Exponential and Logarithmic:**
- ∫eˣ dx = eˣ + C
- ∫aˣ dx = aˣ/ln(a) + C
- ∫eᵃˣ dx = eᵃˣ/a + C

**Trigonometric:**
- ∫sin x dx = -cos x + C
- ∫cos x dx = sin x + C
- ∫tan x dx = -ln|cos x| + C = ln|sec x| + C
- ∫cot x dx = ln|sin x| + C
- ∫sec x dx = ln|sec x + tan x| + C
- ∫cosec x dx = ln|cosec x - cot x| + C
- ∫sec²x dx = tan x + C
- ∫cosec²x dx = -cot x + C
- ∫sec x tan x dx = sec x + C
- ∫cosec x cot x dx = -cosec x + C

**Inverse Trigonometric:**
- ∫1/√(1-x²) dx = sin⁻¹x + C
- ∫-1/√(1-x²) dx = cos⁻¹x + C
- ∫1/(1+x²) dx = tan⁻¹x + C
- ∫1/(x√(x²-1)) dx = sec⁻¹|x| + C

## Integration Methods

**1. Substitution Method:**
If ∫f(g(x))g'(x)dx, let u = g(x), then du = g'(x)dx

**Example:** ∫2x·eˣ² dx
Let u = x², du = 2x dx
= ∫eᵘ du = eᵘ + C = eˣ² + C

**2. Integration by Parts:**
∫u·v dx = u∫v dx - ∫(du/dx × ∫v dx)dx

**ILATE Rule for choosing u:**
I - Inverse trigonometric
L - Logarithmic
A - Algebraic
T - Trigonometric
E - Exponential

**Example:** ∫x·eˣ dx
u = x, v = eˣ
= x·eˣ - ∫eˣ dx = x·eˣ - eˣ + C = eˣ(x-1) + C

**3. Partial Fractions:**
For rational functions P(x)/Q(x) where deg(P) < deg(Q)

**Types:**
- Linear factors: A/(x-a)
- Repeated linear: A/(x-a) + B/(x-a)²
- Quadratic: (Ax+B)/(x²+px+q)

## Special Integrals

**Formulas:**
- ∫1/(x²+a²) dx = (1/a)tan⁻¹(x/a) + C
- ∫1/(x²-a²) dx = (1/2a)ln|(x-a)/(x+a)| + C
- ∫1/(a²-x²) dx = (1/2a)ln|(a+x)/(a-x)| + C
- ∫1/√(x²+a²) dx = ln|x + √(x²+a²)| + C
- ∫1/√(x²-a²) dx = ln|x + √(x²-a²)| + C
- ∫1/√(a²-x²) dx = sin⁻¹(x/a) + C
- ∫√(x²+a²) dx = (x/2)√(x²+a²) + (a²/2)ln|x + √(x²+a²)| + C
- ∫√(x²-a²) dx = (x/2)√(x²-a²) - (a²/2)ln|x + √(x²-a²)| + C
- ∫√(a²-x²) dx = (x/2)√(a²-x²) + (a²/2)sin⁻¹(x/a) + C

## Definite Integrals

**Definition:**
∫ₐᵇ f(x)dx = F(b) - F(a) where F'(x) = f(x)

**Properties:**
1. ∫ₐᵇ f(x)dx = -∫ᵇₐ f(x)dx
2. ∫ₐᵇ f(x)dx = ∫ₐᶜ f(x)dx + ∫ᶜᵇ f(x)dx
3. ∫ₐᵇ f(x)dx = ∫ₐᵇ f(a+b-x)dx
4. ∫₀ᵃ f(x)dx = ∫₀ᵃ f(a-x)dx
5. ∫₀²ᵃ f(x)dx = 2∫₀ᵃ f(x)dx if f(2a-x) = f(x)
   = 0 if f(2a-x) = -f(x)
6. ∫₋ₐᵃ f(x)dx = 2∫₀ᵃ f(x)dx if f is even
   = 0 if f is odd

## Area Under Curves

**Area between curve and x-axis:**
A = ∫ₐᵇ |y| dx = ∫ₐᵇ |f(x)| dx

**Area between curve and y-axis:**
A = ∫ᶜᵈ |x| dy = ∫ᶜᵈ |g(y)| dy

**Area between two curves:**
A = ∫ₐᵇ |f(x) - g(x)| dx

where f(x) is upper curve, g(x) is lower curve.

## Gamma Function (For reference)

∫₀^∞ xⁿe⁻ˣ dx = n!

**Useful:**
- ∫₀^∞ e⁻ˣ² dx = √π/2
- ∫₀^(π/2) sinⁿx dx = ∫₀^(π/2) cosⁿx dx (reduction formulas)







